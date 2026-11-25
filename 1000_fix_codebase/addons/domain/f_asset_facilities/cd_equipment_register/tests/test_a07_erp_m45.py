"""A07 ERP audit (2026-11-20), M45 findings M45-01..30 (stream S2).

Live ORM (``odoo_env``, rolled back). Every attack runs as a NON-ADMIN user
holding the role they would really hold (and without it where the role is the
control). Owner decisions applied: D7(a) evidence on every pass, D7(b) both B9
switches ON, D9 HR-approved recharge, D10 write-off on the M49 NBV.
"""

import base64
import hashlib
import itertools
import json
import types
from datetime import date, timedelta

import pytest
from freezegun import freeze_time
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = "A7ERP45"
ROLE_QM = "cd_equipment_register.group_quality_manager"
ROLE_CAL = "cd_equipment_register.group_calibration_technician"
ROLE_KEEPER = "cd_equipment_register.group_equipment_custodian"
ROLE_FIN = "account.group_account_manager"
ROLE_HR = "hr.group_hr_manager"
TIER_2 = "cd_entity_config.group_dofa_tier_2"
PARAM_ROLE = "cd_equipment_register.calibration_requires_role"
PARAM_DECISION = "cd_equipment_register.usage_decision_required"
REFUSED = (UserError, ValidationError, AccessError)
PDF_BYTES = b"%PDF-1.4 A07 calibration certificate"
PDF = base64.b64encode(PDF_BYTES).decode()
_SEQ = itertools.count(1)


def _user(env, tag, groups=(), ous=None):
    n = next(_SEQ)
    ous = ous if ous is not None else env["operating.unit"].search([], limit=1)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %s %d" % (TAG, tag, n),
                "login": "%s.%s.%d@a07.test" % (TAG.lower(), tag, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ous.ids)],
                "default_operating_unit_id": ous[:1].id,
            }
        )
    )
    user.employee_id = env["hr.employee"].create(
        {"name": "%s %s %d (emp)" % (TAG, tag, n), "user_id": user.id}
    )
    return user


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


def events(env, event_type, aggregate, res_id):
    rows = env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", res_id),
        ],
        order="id",
    )
    return [json.loads(r.payload) for r in rows]


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, n=0)
    x.today = fields.Date.context_today(env["fix.equipment"].with_context(tz="Asia/Dhaka"))
    x.ou1 = env["operating.unit"].search([], limit=1)
    x.ou2 = env["operating.unit"].create(
        {
            "name": "%s OU 2" % TAG,
            "code": "A7E2",
            "partner_id": env.company.partner_id.id,
            "company_id": env.company.id,
        }
    )
    x.clerk = _user(env, "clerk")
    x.clerk2 = _user(env, "clerk2")
    x.tech = _user(env, "tech", [ROLE_CAL])
    x.qm = _user(env, "qm", [ROLE_QM])
    x.qm2 = _user(env, "qm2", [ROLE_QM])
    x.keeper = _user(env, "keeper", [ROLE_KEEPER])
    x.keeper2 = _user(env, "keeper2", [ROLE_KEEPER], ous=x.ou1 | x.ou2)
    x.finance = _user(env, "finance", [ROLE_FIN])
    x.hr = _user(env, "hr", [ROLE_HR])
    x.manager = _user(env, "manager", [TIER_2])
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "A7E45", "legal_name": "%s Entity" % TAG, "company_id": env.company.id})
    x.br1 = env["fix.branch"].create(
        {
            "name": "%s B1" % TAG,
            "code": "A7E45B1",
            "entity_id": entity.id,
            "operating_unit_id": x.ou1.id,
        }
    )
    x.br2 = env["fix.branch"].create(
        {
            "name": "%s B2" % TAG,
            "code": "A7E45B2",
            "entity_id": entity.id,
            "operating_unit_id": x.ou2.id,
        }
    )
    x.lab = env["res.partner"].create({"name": "%s Calibration Lab" % TAG, "is_company": True})
    ICP = env["ir.config_parameter"].sudo()
    ICP.set_param(PARAM_ROLE, False)
    ICP.set_param(PARAM_DECISION, False)
    return x


def eq(c, **kw):
    c.n += 1
    vals = {
        "code": "%s-%02d" % (TAG, c.n),
        "name": "%s meter %d" % (TAG, c.n),
        "branch_id": c.br1.id,
    }
    vals.update(kw)
    return c.env["fix.equipment"].create(vals)


def evidence(c, e, **kw):
    vals = {
        "equipment_id": e.id,
        "calibrated_on": c.today - timedelta(days=10),
        "next_due": c.today + timedelta(days=355),
        "standard_ref": "STD-%s" % TAG,
        "result": "pass",
        "certificate_ref": "CERT-%s-%d" % (TAG, e.id),
        "performed_by": "Lab engineer",
        "provider_id": c.lab.id,
        "provider_accredited": True,
        "accreditation_ref": "BAB-17025-001",
        "certificate_file": PDF,
        "certificate_filename": "cert.pdf",
    }
    vals.update(kw)
    return vals


def cal(c, e, user=None, **kw):
    return c.env["fix.calibration"].with_user(user or c.tech).create(evidence(c, e, **kw))


def fit(c, **kw):
    e = eq(c, **kw)
    c.env["fix.calibration"].create(evidence(c, e))
    return e


def holds(c, e, hold_type=None):
    domain = [("equipment_id", "=", e.id), ("state", "=", "open")]
    if hold_type:
        domain.append(("hold_type", "=", hold_type))
    return c.env["fix.equipment.oos"].search(domain)


# ============================================================ M45-01 custody pinned
def test_m45_01_an_open_issue_cannot_be_repointed_backdated_or_extended_by_a_write(c):
    e = fit(c)
    issue = (
        c.env["fix.equipment.issue"]
        .with_user(c.keeper)
        .create(
            {
                "equipment_id": e.id,
                "custodian_id": c.clerk.employee_id.id,
                "due_on": c.today + timedelta(days=7),
            }
        )
    )
    mine = issue.with_user(c.clerk)
    assert refused(c.env, lambda: mine.write({"custodian_id": c.clerk2.employee_id.id}))
    assert refused(c.env, lambda: mine.write({"issued_on": c.today - timedelta(days=30)}))
    assert refused(c.env, lambda: mine.write({"due_on": c.today + timedelta(days=365)}))
    assert refused(
        c.env, lambda: issue.with_user(c.keeper).write({"due_on": c.today + timedelta(days=60)})
    )
    # the holder is still accountable: exit clearance reads the open issue
    held = c.env["fix.equipment.issue"].m45_open_custody_for_employee(c.clerk.employee_id)
    assert held == issue
    # Extend Due: a store keeper, with a reason; the first date is kept
    issue.with_user(c.clerk).write({"proposed_due_on": c.today + timedelta(days=30)})
    assert refused(c.env, lambda: mine.action_extend_due(reason="travel"), "role")
    keeper = issue.with_user(c.keeper)
    assert refused(c.env, lambda: keeper.action_extend_due(), "why")
    keeper.action_extend_due(reason="Field job in Sylhet extended")
    assert issue.due_on == c.today + timedelta(days=30)
    assert issue.due_original_on == c.today + timedelta(days=7)
    assert issue.due_extension_count == 1 and "Sylhet" in issue.due_extension_note
    assert not issue.proposed_due_on and issue.overdue_level == 0


# ============================================================ M45-15 issue / return roles
def test_m45_15_only_a_store_keeper_issues_and_a_holder_return_is_a_hand_in(c):
    e = fit(c)
    Issue = c.env["fix.equipment.issue"]
    vals = {"equipment_id": e.id, "custodian_id": c.clerk.employee_id.id}
    assert refused(c.env, lambda: Issue.with_user(c.clerk).create(dict(vals)), "role")
    assert refused(
        c.env,
        lambda: Issue.with_user(c.keeper).create(dict(vals, custodian_id=c.keeper.employee_id.id)),
        "themselves",
    )
    issue = Issue.with_user(c.keeper).create(vals)
    # the holder declares it serviceable: it waits for the store keeper's check
    issue.with_user(c.clerk).action_return(condition="good")
    assert issue.state == "returned" and issue.handed_in_by_holder
    assert not issue.return_condition
    assert e.operational_status == "out_of_service"
    assert holds(c, e, "inspection")
    # a store keeper's return of someone else's custody records the condition
    e2 = fit(c)
    issue2 = Issue.with_user(c.keeper).create(
        {"equipment_id": e2.id, "custodian_id": c.clerk.employee_id.id}
    )
    issue2.with_user(c.keeper2).action_return(condition="good")
    assert issue2.return_condition == "good" and not issue2.handed_in_by_holder
    assert e2.operational_status == "available"


# ============================================================ M45-14 verification role
def test_m45_14_only_a_store_keeper_records_an_item_not_found(c):
    e = fit(c)
    Verification = c.env["fix.equipment.verification"]
    vals = {"equipment_id": e.id, "campaign_ref": "ADHOC", "found": False}
    assert refused(c.env, lambda: Verification.with_user(c.clerk).create(dict(vals)), "role")
    assert e.operational_status == "available"
    Verification.with_user(c.keeper).create(vals)
    assert e.operational_status == "missing"


# ============================================================ M45-02 / M45-30 cost and basis
def test_m45_02_cost_is_finance_once_recorded_and_d10_writeoff_basis_is_nbv(c, monkeypatch):
    e = eq(c, acquisition_cost=80000.0)
    assert e._dofa_current_tier() == "tier_4"
    for user in (c.clerk, c.keeper, c.qm):
        assert refused(
            c.env, lambda u=user: e.with_user(u).write({"acquisition_cost": 20000.0}), "role"
        ), user.name
    assert e.acquisition_cost == 80000.0 and e._dofa_current_tier() == "tier_4"
    e.with_user(c.finance).write({"acquisition_cost": 82000.0})
    assert e.acquisition_cost == 82000.0
    # an unchanged echo (a P03 form posts every field) is not a change
    e.with_user(c.clerk).write({"acquisition_cost": 82000.0, "home_location": "Shelf 2"})
    # D10: capitalised -> the M49 net book value decides the tier
    fake = types.SimpleNamespace(book_nbv=18000.0, display_name="FA/0001", _fields={"book_nbv": 1})
    fake.sudo = lambda: fake
    monkeypatch.setattr(type(e), "_m45_fixed_asset", lambda self: fake)
    assert e._dofa_amount() == 18000.0
    assert e._dofa_current_tier() == "tier_2"
    assert "net book value" in e._dofa_amount_label()
    # and the cost is frozen once capitalised, finance included
    assert refused(c.env, lambda: e.with_user(c.finance).write({"acquisition_cost": 1.0}))


# ============================================================ M45-03 D7(a) evidence
def test_m45_03_d7a_a_pass_needs_certificate_file_provider_and_accreditation_ref(c):
    e = eq(c)
    for missing, match in (
        ({"certificate_file": False}, "certificate file"),
        ({"provider_id": False}, "provider"),
        ({"accreditation_ref": False}, "accreditation reference"),
    ):
        assert refused(c.env, lambda m=missing: cal(c, e, **m), match), match
    assert e.calibration_state == "never"
    rec = cal(c, e)
    assert rec.certificate_hash == hashlib.sha256(PDF_BYTES).hexdigest()
    assert e.calibration_state == "current"
    # the hash is evidence: never rewritten
    assert refused(c.env, lambda: rec.with_user(c.qm).write({"certificate_hash": "0" * 64}))


# ============================================================ M45-03 D7(b) switches ON
def test_m45_03_d7b_with_both_switches_on_a_technician_certifies_and_another_qm_accepts(c):
    ICP = c.env["ir.config_parameter"].sudo()
    ICP.set_param(PARAM_ROLE, "True")
    ICP.set_param(PARAM_DECISION, "True")
    e = eq(c)
    assert refused(c.env, lambda: cal(c, e, user=c.clerk), "role")
    rec = cal(c, e, user=c.tech)
    assert e.calibration_state == "pending"
    assert refused(c.env, lambda: e.action_assert_usable(), "usage decision")
    assert refused(c.env, lambda: rec.with_user(c.tech).action_accept_calibration(), "role")
    own = cal(c, eq(c), user=c.qm)
    assert refused(c.env, lambda: own.with_user(c.qm).action_accept_calibration(), "Segregation")
    rec.with_user(c.qm2).action_accept_calibration()
    assert rec.decision_state == "accepted" and e.calibration_state == "current"
    assert e.action_assert_usable()


# ============================================================ M45-07 in-house standard
def test_m45_07_an_in_house_calibration_names_its_standard_not_a_typed_reference(c):
    cat = (
        c.env["fix.equipment.category"]
        .with_user(c.qm)
        .create({"code": "A7STD", "name": "Standards", "classification": "calibration_standard"})
    )
    std = fit(c, category_id=cat.id)
    e = eq(c)
    in_house = {
        "provider_id": c.env.company.partner_id.id,
        "provider_accredited": False,
        "accreditation_ref": False,
    }
    assert refused(
        c.env, lambda: cal(c, e, standard_ref=std.code, **in_house), "reference standard"
    )
    assert refused(
        c.env,
        lambda: cal(c, e, standard_equipment_id=std.id, standard_ref="STD-01", **in_house),
        "does not match",
    )
    rec = cal(c, e, standard_equipment_id=std.id, standard_ref="", **in_house)
    assert rec.standard_ref == std.code and not rec.non_accredited
    # an expired standard is still refused (BRU-EAM-04)
    lapsed = eq(c, category_id=cat.id)
    c.env["fix.calibration"].create(
        evidence(
            c,
            lapsed,
            calibrated_on=c.today - timedelta(days=400),
            next_due=c.today - timedelta(days=35),
        )
    )
    assert refused(
        c.env, lambda: cal(c, eq(c), standard_equipment_id=lapsed.id, standard_ref="", **in_house)
    )


# ============================================================ M45-24 non-accredited
def test_m45_24_a_non_accredited_certificate_is_flagged_and_produces_no_qc_result(c):
    e = eq(c)
    rec = cal(c, e, provider_accredited=False, accreditation_ref=False)
    assert rec.non_accredited and e.calibration_state == "current"
    Usage = c.env["fix.equipment.usage"]
    assert refused(c.env, lambda: Usage.m45_record_qc_use(e, "JOB-1", "pass"), "accredited")
    # non-conformity work (a use without a QC result) is still allowed
    Usage.with_user(c.clerk).create({"equipment_id": e.id, "job_ref": "JOB-2"})
    ok = eq(c)
    cal(c, ok)
    assert Usage.m45_record_qc_use(ok, "JOB-3", "pass")


# ============================================================ M45-19 calibration cost
def test_m45_19_a_charged_calibration_carries_the_ap_facts_to_the_m52_hand_off(c, monkeypatch):
    e = eq(c)
    assert refused(c.env, lambda: cal(c, e, calibration_cost=4500.0), "Paid By")
    assert refused(
        c.env, lambda: cal(c, e, calibration_cost=4500.0, payment_method="vendor_bill"), "invoice"
    )
    assert refused(
        c.env,
        lambda: cal(c, e, calibration_cost=4500.0, payment_method="employee_expense"),
        "employee",
    )
    no_ou = eq(c, branch_id=False)
    assert refused(
        c.env,
        lambda: cal(
            c, no_ou, calibration_cost=10.0, payment_method="vendor_bill", invoice_ref="INV-1"
        ),
        "operating unit",
    )
    captured = []
    Calibration = type(c.env["fix.calibration"])
    Entry, why = c.env["fix.calibration"]._m45_cost_entry_model()
    if Entry is None:
        # S6 has not landed the calibration_service cost type in this DB: the
        # facts M45 hands over are what is under test
        fake = types.SimpleNamespace(
            _fields={
                k: 1
                for k in (
                    "cost_type",
                    "company_id",
                    "operating_unit_id",
                    "amount",
                    "currency_id",
                    "cost_date",
                    "vendor_id",
                    "invoice_ref",
                    "payment_method",
                    "employee_id",
                    "detail",
                    "branch_id",
                )
            }
        )

        def queue(record, vals):
            captured.append((record, vals))
            return types.SimpleNamespace(display_name="M52COST/T1")

        fake._m52_queue = queue
        monkeypatch.setattr(Calibration, "_m45_cost_entry_model", lambda self: (fake, None))
    rec = cal(c, e, calibration_cost=4500.0, payment_method="vendor_bill", invoice_ref="LAB-INV-77")
    if captured:
        record, vals = captured[0]
        assert record == rec
    else:
        entry = c.env["fix.asset.cost.entry"].search(
            [("source_model", "=", "fix.calibration"), ("source_res_id", "=", rec.id)]
        )
        vals = {
            "cost_type": entry.cost_type,
            "amount": entry.amount,
            "vendor_id": entry.vendor_id.id,
            "invoice_ref": entry.invoice_ref,
            "operating_unit_id": entry.operating_unit_id.id,
            "payment_method": entry.payment_method,
        }
    assert vals["cost_type"] == "calibration_service"
    assert vals["amount"] == 4500.0 and vals["vendor_id"] == c.lab.id
    assert vals["invoice_ref"] == "LAB-INV-77" and vals["payment_method"] == "vendor_bill"
    assert vals["operating_unit_id"] == c.ou1.id
    assert rec.cost_entry_ref
    assert refused(c.env, lambda: rec.with_user(c.qm).write({"calibration_cost": 1.0}))


# ============================================================ M45-08 / 11 / 25 crons
@freeze_time("2026-11-20 18:05:00")
def test_m45_08_the_nightly_job_uses_the_dhaka_day_whatever_the_cron_users_tz(c):
    due = date(2026, 11, 20)
    e = eq(c)
    c.env["fix.calibration"].create(
        evidence(c, e, calibrated_on=due - timedelta(days=365), next_due=due)
    )
    Equipment = c.env["fix.equipment"].with_context(tz="Europe/Brussels")
    # Brussels still reads the 20th (the due day: current); Dhaka is on the 21st
    assert fields.Date.context_today(Equipment) == due
    Equipment.cron_calibration_status()
    assert holds(c, e, "calibration"), "lapse held a day late"
    assert e.operational_status == "out_of_service"
    # M45-11: the lapse is announced to the Quality Manager
    raised = events(c.env, "equipment.calibration.overdue", "fix.equipment", e.id)
    assert raised and raised[0]["due_date"] == "2026-11-20"


def test_m45_11_due_alerts_say_who_must_act_and_m45_25_never_calibrated_is_held(c):
    soon = eq(c)
    c.env["fix.calibration"].create(evidence(c, soon, next_due=c.today + timedelta(days=12)))
    sooner = eq(c)
    c.env["fix.calibration"].create(evidence(c, sooner, next_due=c.today + timedelta(days=5)))
    never = eq(c)
    c.env["fix.equipment"].cron_calibration_status()
    assert (
        events(c.env, "equipment.calibration_due", "fix.equipment", soon.id)[-1]["escalate_to"]
        == "quality_manager"
    )
    assert (
        events(c.env, "equipment.calibration_due", "fix.equipment", sooner.id)[-1]["escalate_to"]
        == "ops_director"
    )
    assert never.operational_status == "out_of_service"
    assert "baseline" in holds(c, never, "calibration").reason


# ============================================================ M45-09 operating unit
def test_m45_09_the_register_takes_its_branch_ou_and_moves_it_on_receipt(c):
    e = fit(c)
    assert e.operating_unit_id == c.ou1
    assert e.calibration_ids.operating_unit_id == c.ou1
    only_ou2 = _user(c.env, "ou2-only", ous=c.ou2)
    assert not c.env["fix.equipment"].with_user(only_ou2).search([("id", "=", e.id)])
    transfer = (
        c.env["fix.equipment.transfer"]
        .with_user(c.keeper)
        .create({"equipment_id": e.id, "to_branch_id": c.br2.id})
    )
    transfer.with_user(c.keeper).action_dispatch()
    transfer.with_user(c.keeper2).action_receive()
    assert e.branch_id == c.br2 and e.operating_unit_id == c.ou2
    assert c.env["fix.equipment"].with_user(only_ou2).search([("id", "=", e.id)])
    # the OU follows the branch: nobody types it
    assert refused(c.env, lambda: e.with_user(c.keeper2).write({"operating_unit_id": c.ou1.id}))
    assert c.env["fix.equipment"]._m45_backfill_operating_unit() == 0


# ============================================================ M45-04 control switch-off
def test_m45_04_switching_calibration_control_off_is_an_approval_and_holds_stay(c):
    Category = c.env["fix.equipment.category"].with_user(c.qm)
    controlled = Category.create(
        {"code": "A7DMM", "name": "DMM", "classification": "measuring_instrument"}
    )
    loose = Category.create({"code": "A7TOOL", "name": "Tools", "classification": "general_tool"})
    lapsed = eq(c, category_id=controlled.id)
    c.env["fix.calibration"].create(
        evidence(
            c,
            lapsed,
            calibrated_on=c.today - timedelta(days=400),
            next_due=c.today - timedelta(days=2),
        )
    )
    c.env["fix.equipment"].cron_calibration_status()
    hold = holds(c, lapsed, "calibration")
    assert hold
    # item level: a lapsed instrument does not escape into an uncontrolled class
    assert refused(
        c.env, lambda: lapsed.with_user(c.qm).write({"category_id": loose.id}), "not in calibration"
    )
    current = fit(c, category_id=controlled.id)
    current.with_user(c.qm).write({"category_id": loose.id})
    assert not current.measurement_critical
    # class level: never a tick
    assert refused(
        c.env, lambda: controlled.write({"requires_calibration": False}), "Request Approval"
    )
    assert refused(
        c.env, lambda: controlled.write({"classification": "general_tool"}), "Request Approval"
    )
    assert refused(c.env, lambda: controlled.action_request_approval(), "why")
    controlled.write({"control_change_reason": "DMMs re-graded as indicative only"})
    controlled.action_request_approval()
    assert controlled.approval_state == "pending"
    assert c.qm2 in assigned(controlled) and c.qm not in assigned(controlled)
    assert refused(c.env, lambda: controlled.action_apply_control_off(), "inbox")
    approve_via_inbox(controlled, c.qm2, requester=c.qm)
    assert not controlled.requires_calibration and not lapsed.measurement_critical
    # the open calibration hold stays until a re-calibration (BRU-EAM-01)
    assert refused(c.env, lambda: hold.with_user(c.keeper).action_resolve())
    assert refused(c.env, lambda: hold.with_user(c.qm2).action_resolve(), "passing calibration")
    assert lapsed.operational_status == "out_of_service"


# ============================================================ M45-05 / D9 recharge
def test_m45_05_a_recharge_reaches_payroll_only_on_an_hr_approved_decision(c):
    e = fit(c, acquisition_cost=2000.0)
    loss = (
        c.env["fix.equipment.loss"]
        .with_user(c.clerk)
        .create(
            {
                "equipment_id": e.id,
                "kind": "lost",
                "circumstances": "Left in a CNG on a field visit",
                "recharge_employee_id": c.clerk2.employee_id.id,
                "recharge_amount": 1500.0,
            }
        )
    )
    assert refused(c.env, lambda: loss.with_user(c.keeper).action_hr_approve_recharge(), "role")
    hr_reporter = _user(c.env, "hr-reporter", [ROLE_HR])
    loss2_item = fit(c, acquisition_cost=900.0)
    loss2 = (
        c.env["fix.equipment.loss"]
        .with_user(hr_reporter)
        .create(
            {
                "equipment_id": loss2_item.id,
                "kind": "lost",
                "circumstances": "x",
                "recharge_employee_id": c.clerk.employee_id.id,
                "recharge_amount": 100.0,
            }
        )
    )
    assert refused(
        c.env, lambda: loss2.with_user(hr_reporter).action_hr_approve_recharge(), "Segregation"
    )
    assert refused(c.env, lambda: loss.with_user(c.hr).action_hr_reject_recharge(), "why")
    loss.with_user(c.hr).action_hr_approve_recharge(note="BLA s.26 deduction, 3 instalments")
    assert loss.recharge_hr_decision == "approved"
    # pinned once HR decided
    assert refused(c.env, lambda: loss.with_user(c.clerk).write({"recharge_amount": 1.0}))
    assert not events(c.env, "equipment.recharge_requested", "fix.equipment.loss", loss.id)
    loss.with_user(c.keeper).action_request_writeoff()
    approve_via_inbox(e, c.manager, requester=c.keeper)
    assert loss.state == "written_off"
    sent = events(c.env, "equipment.recharge_requested", "fix.equipment.loss", loss.id)
    assert len(sent) == 1
    assert sent[0]["amount"] == 1500.0 and sent[0]["employee_id"] == c.clerk2.employee_id.id
    assert sent[0]["hr_approved_by_id"] == c.hr.id and sent[0]["operating_unit_id"] == c.ou1.id
    loss._m45_publish_recharge()
    assert len(events(c.env, "equipment.recharge_requested", "fix.equipment.loss", loss.id)) == 1


def test_m45_05_without_hr_approval_a_written_off_loss_sends_no_recharge(c):
    e = fit(c, acquisition_cost=2000.0)
    loss = (
        c.env["fix.equipment.loss"]
        .with_user(c.clerk)
        .create(
            {
                "equipment_id": e.id,
                "kind": "lost",
                "circumstances": "lost",
                "recharge_employee_id": c.clerk2.employee_id.id,
                "recharge_amount": 500.0,
            }
        )
    )
    loss.with_user(c.keeper).action_request_writeoff()
    approve_via_inbox(e, c.manager, requester=c.keeper)
    assert loss.state == "written_off"
    assert not events(c.env, "equipment.recharge_requested", "fix.equipment.loss", loss.id)


# ============================================================ M45-06 resale facts
def test_m45_06_a_resale_records_buyer_and_proceeds_for_m49(c):
    e = fit(c, acquisition_cost=9000.0)
    e._guarded().write({"operational_status": "retired", "retired_on": c.today})
    retirement = (
        c.env["fix.equipment.retirement"]
        .with_user(c.keeper)
        .create({"equipment_id": e.id, "basis": "obsolete", "justification": "replaced"})
    )
    assert retirement.state == "approved"
    retirement.with_user(c.qm).write({"disposal_route": "resale", "disposal_ref": "SALE-1"})
    assert refused(c.env, lambda: retirement.with_user(c.qm).action_dispose(), "buyer")
    buyer = c.env["res.partner"].create({"name": "%s buyer" % TAG})
    retirement.with_user(c.qm).write({"buyer_partner_id": buyer.id, "sale_amount": 6000.0})
    retirement.with_user(c.qm).action_dispose()
    sent = events(c.env, "equipment.disposed", "fix.equipment.retirement", retirement.id)
    assert sent[-1]["sale_amount"] == 6000.0 and sent[-1]["buyer_partner_id"] == buyer.id
    assert sent[-1]["book_value"] == 9000.0


# ============================================================ M45-16 blind count
def test_m45_16_a_count_is_signed_by_someone_independent_and_reviewed(c):
    e1, e2 = fit(c), fit(c)
    Audit = c.env["fix.equipment.audit"]
    own = Audit.with_user(c.keeper).create(
        {"branch_id": c.br1.id, "counter_id": c.keeper.employee_id.id}
    )
    own.with_user(c.keeper).action_start()
    assert refused(c.env, lambda: own.with_user(c.keeper).action_complete(), "scheduled")
    audit = Audit.with_user(c.keeper).create(
        {"branch_id": c.br1.id, "counter_id": c.clerk.employee_id.id}
    )
    assert refused(c.env, lambda: audit.with_user(c.clerk).action_complete(), "Start Count")
    audit.with_user(c.keeper).action_start()
    c.env["fix.equipment.audit.line"].with_user(c.clerk).create(
        {"audit_id": audit.id, "scanned_code": e1.asset_tag}
    )
    assert audit.line_ids.equipment_id == e1
    audit.with_user(c.clerk).action_complete()
    assert audit.state == "review" and audit.missing_count >= 1
    assert e2.operational_status == "available", "not missing before the review"
    assert refused(c.env, lambda: audit.with_user(c.clerk).action_approve_count(reason="x"))
    assert refused(
        c.env, lambda: audit.with_user(c.keeper).action_approve_count(reason="x"), "Segregation"
    )
    assert refused(c.env, lambda: audit.with_user(c.keeper2).action_approve_count(), "why")
    audit.with_user(c.keeper2).action_approve_count(reason="Searched store and benches")
    assert audit.state == "done" and audit.reviewed_by_id == c.keeper2
    assert e2.operational_status == "missing" and e1.operational_status == "available"


# ============================================================ M45-29 usage plan
def test_m45_29_a_usage_plan_counts_uses_after_the_completion_day(c):
    e = fit(c)
    plan = (
        c.env["fix.equipment.pm.plan"]
        .with_user(c.keeper)
        .create(
            {
                "equipment_id": e.id,
                "trigger_type": "usage",
                "interval_value": 3,
                "interval_unit": "uses",
                "task": "clean",
                "start_on": c.today - timedelta(days=5),
            }
        )
    )
    Usage = c.env["fix.equipment.usage"]
    Usage.create(
        {"equipment_id": e.id, "job_ref": "J1", "uses": 3, "used_on": c.today - timedelta(days=5)}
    )
    assert not plan._m45_due(e, c.today)[0]
    Usage.create(
        {"equipment_id": e.id, "job_ref": "J2", "uses": 3, "used_on": c.today - timedelta(days=1)}
    )
    assert plan._m45_due(e, c.today)[0]


# ============================================================ M45-17 / 18 reports
def test_m45_17_kpis_and_packs_measure_compliance_fence_and_dates(c):
    import odoo.addons.cd_p03_portal.controllers.a07.m45 as ctl

    current, lapsed = fit(c), eq(c)
    c.env["fix.calibration"].create(
        evidence(
            c,
            lapsed,
            calibrated_on=c.today - timedelta(days=400),
            next_due=c.today - timedelta(days=3),
        )
    )
    retired = eq(c)
    c.env["fix.calibration"].create(
        evidence(
            c,
            retired,
            calibrated_on=c.today - timedelta(days=400),
            next_due=c.today - timedelta(days=3),
        )
    )
    retired._guarded().write({"operational_status": "retired", "retired_on": c.today})
    env = c.env(user=c.qm.id, su=False)
    k = ctl.kpis(env)
    mine = ctl._equipment(env)
    assert current in mine and retired in mine
    assert k["calibration_overdue"] == len(
        mine.filtered(lambda e: e.operational_status != "retired" and e.calibration_overdue)
    )
    for key in (
        "calibration_compliance_pct",
        "availability_pct",
        "mttr_hours",
        "mtbf_days",
        "custody_overdue_pct",
    ):
        assert key in k
    assert k["calibration_compliance_pct"] < 100.0
    # OU fence: a user of the other OU does not see branch-1 items in a pack
    only_ou2 = _user(c.env, "pack-ou2", [ROLE_QM], ous=c.ou2)
    assert current not in ctl._equipment(c.env(user=only_ou2.id, su=False))
    # date filters
    reg = ctl.certificate_register(
        env, date_from=str(c.today - timedelta(days=11)), date_to=str(c.today)
    )
    codes = {r["code"] for r in reg["rows"]}
    assert current.code in codes and lapsed.code not in codes
    row = next(r for r in reg["rows"] if r["code"] == current.code)
    assert row["sha256"] == hashlib.sha256(PDF_BYTES).hexdigest()[:16]
    for pack in ("asset_tags", "custody_slips", "writeoff_memos"):
        assert ctl.REPORTS[pack](env)["title"]


def test_m45_17_loss_register_lists_a_count_once_and_not_after_recovery(c):
    import odoo.addons.cd_p03_portal.controllers.a07.m45 as ctl

    e = fit(c, acquisition_cost=1000.0)
    Verification = c.env["fix.equipment.verification"].with_user(c.keeper)
    Verification.create({"equipment_id": e.id, "campaign_ref": "C1", "found": False})
    env = c.env(user=c.qm.id, su=False)
    rows = [r for r in ctl.loss_writeoff(env)["rows"] if r["code"] == e.code]
    assert len(rows) == 1
    Verification.create(
        {"equipment_id": e.id, "campaign_ref": "C2", "found": True, "location": "Bench 3"}
    )
    assert not [r for r in ctl.loss_writeoff(env)["rows"] if r["code"] == e.code]
