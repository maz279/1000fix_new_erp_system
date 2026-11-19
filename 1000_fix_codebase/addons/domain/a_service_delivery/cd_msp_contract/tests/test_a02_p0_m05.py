"""A02 audit P0 for M05 Remote Support & MSP (findings M05-1 to M05-13).

The A02 probes (working/A02_evidence/probes/m05_m06/probe_m05.py) proved
each gap as a plain internal user. Every control here is tested both ways:
the bypass is refused, and the legitimate path still works. Every actor is a
NON-ADMIN user holding only the M05 role it needs, because the system user
is trusted by the guards and would hide a gap.

``odoo_env`` (addons/conftest.py): rolled back after every test.
"""

import itertools
import json
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError

_SEQ = itertools.count(1)
GUARD = "changes only through its workflow"
ENG = "cd_msp_contract.group_msp_engineer"
CAB = "cd_msp_contract.group_msp_cab_member"
CM = "cd_msp_contract.group_msp_change_manager"
FIN = "cd_msp_contract.group_msp_credit_approver"
TIER4 = "cd_entity_config.group_dofa_tier_4"


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def m5(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    n = next(_SEQ)

    def user(key, *groups):
        ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "A02 M05 %s %d" % (key, n),
                    "login": "a02.p0.m05.%s.%d@a02.test" % (key, n),
                    "group_ids": [(6, 0, ids)],
                    "operating_unit_ids": [(6, 0, ou.ids)],
                    "default_operating_unit_id": ou.id,
                }
            )
        )

    eng = user("eng", ENG)
    eng2 = user("eng2", ENG)
    cab = user("cab", CAB)
    cab2 = user("cab2", CAB)
    cab_eng = user("cabeng", CAB, ENG)
    cm = user("cm", CM)
    fin = user("fin", FIN)
    fin_eng = user("fineng", FIN, ENG)
    cfo = user("cfo", TIER4)
    plain = user("plain")
    emp = env["hr.employee"].create({"name": "A02 M05 Eng Emp %d" % n, "user_id": eng.id})
    tech = env["hr.employee"].create({"name": "A02 M05 Tech %d" % n})
    customer = env["res.partner"].create(
        {"name": "A02 M05 Client %d" % n, "is_company": True, "phone": "01711000111"}
    )
    contact = env["res.partner"].create(
        {"name": "A02 M05 Client IT lead", "parent_id": customer.id, "phone": "01711000222"}
    )
    contract = env["fix.contract"].create(
        {
            "name": "A02 M05 Contract %d" % n,
            "customer_id": customer.id,
            "family": "managed",
            "state": "active",  # A02 audit M05-P2: MSP work needs a term in force
            "operating_unit_id": ou.id,
            "date_start": fields.Date.today(),
            "date_end": fields.Date.today() + timedelta(days=365),
            "annual_value": 240000.0,
        }
    )
    msp = env["fix.msp.contract"].create(
        {
            "name": "A02 M05 MSP %d" % n,
            "contract_id": contract.id,
            "operating_unit_id": ou.id,
            "device_count": 4,
            "per_device_monthly": 2500.0,
            "sla_target_pct": 95.0,
        }
    )
    other = env["fix.msp.contract"].create(
        {
            "name": "A02 M05 Other MSP %d" % n,
            "contract_id": contract.id,
            "operating_unit_id": ou.id,
            # A02 ERP audit M05-F4: no enrolment without a contracted count
            "device_count": 4,
        }
    )
    asset = env["fix.monitored.asset"].create(
        {
            "msp_contract_id": msp.id,
            "agent_id": "AGT-A2P0-%d" % n,
            "hostname": "ws-a2p0-%d" % n,
            "operating_unit_id": ou.id,
        }
    )
    other_asset = env["fix.monitored.asset"].create(
        {"msp_contract_id": other.id, "agent_id": "AGT-A2P0-O-%d" % n, "operating_unit_id": ou.id}
    )
    return SimpleNamespace(
        env=env,
        ou=ou,
        eng=eng,
        eng2=eng2,
        cab=cab,
        cab2=cab2,
        cab_eng=cab_eng,
        cm=cm,
        fin=fin,
        fin_eng=fin_eng,
        cfo=cfo,
        plain=plain,
        emp=emp,
        tech=tech,
        customer=customer,
        contact=contact,
        msp=msp,
        other=other,
        asset=asset,
        other_asset=other_asset,
    )


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


def _as(env_or_rec, user):
    return env_or_rec.with_user(user)


ROUTED = "approver's inbox"


def _approve(rec, approver, requester=None, justification=None):
    """A02 audit B1: CAB changes and SLA credits are decided from the M63
    inbox. Request as `requester` (default: the creator), decide as `approver`."""
    return approve_via_inbox(
        rec.with_user(approver), approver, requester=requester, justification=justification
    )


def _window(m5, user, start=-1, end=4, contract=True, name="Window"):
    now = fields.Datetime.now()
    return _as(m5.env["fix.msp.maintenance.window"], user).create(
        {
            "name": name,
            "msp_contract_id": m5.msp.id if contract else False,
            "start_at": now + timedelta(hours=start),
            "end_at": now + timedelta(hours=end),
            "operating_unit_id": m5.ou.id,
        }
    )


def _change(m5, user=None, **vals):
    base = {
        "name": "Reconfigure client firewall",
        "msp_contract_id": m5.msp.id,
        "risk": "medium",
        # BRU-RMS-08: every change carries its rollback plan
        "rollback_plan": "restore the saved configuration",
        "operating_unit_id": m5.ou.id,
    }
    base.update(vals)
    return _as(m5.env["fix.msp.change.record"], user or m5.eng).create(base)


# ===================================================== M05-1 change / CAB


def test_C1_requester_cannot_approve_own_change(m5):
    ch = _change(m5, risk="high", rollback_plan="restore config", requested_by=m5.emp.id)
    # B1: nobody approves by pressing the button, not even a CAB member
    with pytest.raises(UserError, match=ROUTED):
        _as(ch, m5.cab).action_approve()
    _as(ch, m5.eng).action_request_approval()
    assert m5.eng not in assigned(ch) and m5.cab in assigned(ch)
    # A CAB member's own change never reaches his inbox...
    own = _change(m5, user=m5.cab_eng, name="CAB member's own change")
    _as(own, m5.cab_eng).action_request_approval()
    assert m5.cab_eng not in assigned(own)
    # ...nor one that names him as the requester on someone else's record.
    cab_emp = m5.env["hr.employee"].create({"name": "CAB emp", "user_id": m5.cab.id})
    named = _change(m5, name="Requested by the CAB member", requested_by=cab_emp.id)
    _as(named, m5.eng).action_request_approval()
    assert m5.cab not in assigned(named)
    assert ch.state == own.state == named.state == "draft"


def test_cab_approval_is_stamped_with_the_acting_user(m5):
    ch = _change(m5, risk="high", rollback_plan="restore config", requested_by=m5.emp.id)
    _approve(ch, m5.cab)
    assert ch.state == "approved" and ch.approval_state == "approved"
    assert ch.cab_approver_id == m5.cab and ch.approved_at


def test_high_risk_change_needs_a_rollback_plan_before_approval(m5):
    ch = _change(m5, risk="high", rollback_plan="")
    with pytest.raises(UserError, match="rollback plan"):
        _as(ch, m5.eng).action_request_approval()
    _as(ch, m5.eng).write({"rollback_plan": "restore the switch config snapshot"})
    _approve(ch, m5.cab)
    assert ch.state == "approved"


def test_C2_C3_implement_only_inside_an_approved_open_window(m5):
    ch = _change(m5, rollback_plan="snapshot")
    _approve(ch, m5.cab)
    with pytest.raises(UserError, match="no maintenance window"):
        _as(ch, m5.eng).action_implement()
    # an approved window that opens next week
    later = _window(m5, m5.cm, start=24 * 7, end=24 * 7 + 4, name="Next week")
    _as(later, m5.cab).action_approve()
    _as(ch, m5.eng).write({"maintenance_window_id": later.id})
    with pytest.raises(UserError, match="only inside its approved maintenance window"):
        _as(ch, m5.eng).action_implement()
    # a running window nobody approved
    unapproved = _window(m5, m5.cm, name="Running, unapproved")
    _as(ch, m5.eng).write({"maintenance_window_id": unapproved.id})
    with pytest.raises(UserError, match="not approved"):
        _as(ch, m5.eng).action_implement()
    # an approved running window of another contract
    elsewhere = _as(m5.env["fix.msp.maintenance.window"], m5.cm).create(
        {
            "name": "Other client",
            "msp_contract_id": m5.other.id,
            "start_at": fields.Datetime.now() - timedelta(hours=1),
            "end_at": fields.Datetime.now() + timedelta(hours=3),
            "operating_unit_id": m5.ou.id,
        }
    )
    _as(elsewhere, m5.cab).action_approve()
    _as(ch, m5.eng).write({"maintenance_window_id": elsewhere.id})
    with pytest.raises(UserError, match="only inside its approved maintenance window"):
        _as(ch, m5.eng).action_implement()
    assert ch.state == "approved"
    # legitimate: the approved, open window of this contract
    window = _window(m5, m5.cm, name="Tonight")
    _as(window, m5.cab).action_approve()
    _as(ch, m5.eng).write({"maintenance_window_id": window.id})
    _as(ch, m5.eng).action_implement(note="done")
    assert ch.state == "implemented" and ch.implemented_by_id == m5.eng


def test_the_cab_approver_does_not_implement(m5):
    window = _window(m5, m5.cm)
    _as(window, m5.cab).action_approve()
    ch = _change(m5, maintenance_window_id=window.id)
    task = _approve(ch, m5.cab2)
    assert task.assigned_user_id == m5.cab2 and ch.cab_approver_id == m5.cab2
    with pytest.raises(UserError, match="Segregation of duties"):
        _as(ch, m5.cab2).action_implement()
    _as(ch, m5.eng2).action_implement()
    assert ch.state == "implemented"


def test_C4_emergency_change_has_its_own_path(m5):
    ch = _change(m5, name="Emergency reboot", change_type="emergency", risk="high")
    assert ch.emergency
    _as(ch, m5.eng).write({"rollback_plan": "power-cycle back"})
    with pytest.raises(UserError, match=ROUTED):
        _as(ch, m5.cm).action_approve()
    # B1: the emergency change is routed to the change manager, not the CAB
    _as(ch, m5.eng).action_request_approval(justification="core switch down")
    assert assigned(ch) == m5.cm
    _approve(ch, m5.cm)
    assert ch.cab_approver_id == m5.cm
    # implemented at once, with no window
    _as(ch, m5.eng).action_implement(note="rebooted")
    with pytest.raises(UserError, match="post-implementation review"):
        _as(ch, m5.eng).action_close()
    with pytest.raises(UserError, match="CAB Member or MSP Change Manager"):
        _as(ch, m5.eng).action_record_review(note="went fine")
    _as(ch, m5.cab).action_record_review(note="Rebooted; service back in 4 minutes.")
    assert ch.pir_by_id == m5.cab and ch.pir_at
    _as(ch, m5.eng).action_close(note="closed")
    assert ch.state == "closed"


def test_C5_C6_change_state_and_cab_approver_cannot_be_written(m5, call):
    ch = _change(m5, name="Forged change")
    with pytest.raises(UserError, match=GUARD):
        _as(ch, m5.eng).write({"state": "implemented"})
    with pytest.raises(UserError, match=GUARD):
        _as(ch, m5.eng).write({"cab_approver_id": m5.cab.id})
    res = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.change.record",
        record_id=ch.id,
        values={"state": "approved", "cab_approver_id": m5.eng.id},
    )
    assert res.get("error"), res
    ch.invalidate_recordset()
    assert ch.state == "draft" and not ch.cab_approver_id


def test_an_approved_change_is_frozen(m5):
    ch = _change(m5, rollback_plan="snapshot")
    _approve(ch, m5.cab)
    with pytest.raises(UserError, match="cannot change once the change record is approved"):
        _as(ch, m5.eng).write({"risk": "low"})
    assert "risk" in ch._fix_form_locked_fields()


# ================================================ M05-6 patch approval


def _patch(m5, ident, severity="medium", category="os"):
    return _as(m5.env["fix.msp.patch.update"], m5.eng).create(
        {
            "msp_contract_id": m5.msp.id,
            "asset_id": m5.asset.id,
            "identifier": ident,
            "title": "Patch %s" % ident,
            "severity": severity,
            "category": category,
            "operating_unit_id": m5.ou.id,
        }
    )


def test_P1_install_only_from_approved(m5):
    upd = _patch(m5, "KB-P1")
    with pytest.raises(UserError, match="only an approved patch"):
        _as(upd, m5.eng).action_install()
    _as(upd, m5.eng).action_defer(days=2, reason="vendor recall pending")  # M05-F18
    with pytest.raises(UserError, match="only an approved patch"):
        _as(upd, m5.eng).action_install()
    _as(upd, m5.eng).action_approve()
    assert upd.approved_by_id == m5.eng
    _as(upd, m5.eng).action_install()
    assert upd.state == "installed" and upd.installed_at


def test_a_critical_patch_needs_cab_approval(m5):
    upd = _patch(m5, "KB-CRIT", severity="critical")
    with pytest.raises(UserError, match="critical patch"):
        _as(upd, m5.eng).action_approve()
    _as(upd, m5.cab).action_approve()
    assert upd.state == "approved" and upd.approved_by_id == m5.cab


def test_P2_patch_state_cannot_be_forged(m5, call):
    upd = _patch(m5, "KB-P2")
    with pytest.raises(UserError, match=GUARD):
        _as(upd, m5.eng).write({"state": "installed"})
    res = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.patch.update",
        record_id=upd.id,
        values={"state": "installed"},
    )
    assert res.get("error"), res
    upd.invalidate_recordset()
    assert upd.state == "missing"


def test_P3_auto_approve_policy_is_a_cab_decision(m5):
    Policy = m5.env["fix.msp.patch.policy"]
    with pytest.raises(AccessError):
        _as(Policy, m5.eng).create({"name": "mine", "category": "os", "auto_approve": True})
    policy = _as(Policy, m5.cm).create(
        {"name": "auto OS", "msp_contract_id": m5.msp.id, "category": "os", "auto_approve": True}
    )
    # not approved yet: nothing is pre-approved
    assert _patch(m5, "KB-A1").state == "missing"
    with pytest.raises(UserError, match="Segregation of duties"):
        _as(policy, m5.cm).action_approve()
    _as(policy, m5.cab).action_approve()
    assert policy.approved_by_cab
    medium = _patch(m5, "KB-A2")
    critical = _patch(m5, "KB-A3", severity="critical")
    assert medium.state == "approved" and medium.auto_approved_policy_id == policy
    assert critical.state == "approved", "a CAB-approved policy may cover critical patches"
    # changing what the policy covers withdraws its approval
    _as(policy, m5.cm).write({"category": "firmware"})
    assert not policy.approved_at


def test_a_change_manager_approved_policy_never_covers_critical(m5):
    policy = _as(m5.env["fix.msp.patch.policy"], m5.cab).create(
        {
            "name": "auto OS (CM)",
            "msp_contract_id": m5.msp.id,
            "category": "os",
            "auto_approve": True,
        }
    )
    _as(policy, m5.cm).action_approve()
    assert not policy.approved_by_cab
    assert _patch(m5, "KB-B1").state == "approved"
    assert _patch(m5, "KB-B2", severity="critical").state == "missing"


# ===================================================== M05-2 SLA credits


def _report(m5, period, attainment=None, alerts=10, resolved=5):
    vals = {
        "msp_contract_id": m5.msp.id,
        "period_label": period,
        "alert_count": alerts,
        "resolved_count": resolved,
        "operating_unit_id": m5.ou.id,
    }
    if attainment is not None:
        vals["sla_attainment"] = attainment
    # The system writes the figures (action_monthly_report); a user cannot.
    return m5.env["fix.msp.service.report"].create(vals)


def _credit(m5, period):
    return m5.env["fix.msp.sla.credit"].search(
        [("msp_contract_id", "=", m5.msp.id), ("period_label", "=", period)]
    )


def test_S1_a_typed_credit_amount_is_refused(m5):
    with pytest.raises(UserError, match=GUARD):
        _as(m5.env["fix.msp.sla.credit"], m5.eng).create(
            {"msp_contract_id": m5.msp.id, "period_label": "A02-forged", "credit_amount": 5e6}
        )


def test_S1_a_manual_credit_needs_the_dofa_tier_and_is_capped(m5):
    Credit = m5.env["fix.msp.sla.credit"]
    with pytest.raises(ValidationError, match="monthly value"):
        _as(Credit, m5.eng).create(
            {"msp_contract_id": m5.msp.id, "period_label": "A02-huge", "manual_amount": 5e6}
        )
    cr = _as(Credit, m5.eng).create(
        {"msp_contract_id": m5.msp.id, "period_label": "A02-manual", "manual_amount": 5000.0}
    )
    assert cr.is_manual and cr.credit_amount == 5000.0 and cr.manual_set_by_id == m5.eng
    # B1: the CFO tier decides in the inbox; neither a button press...
    with pytest.raises(UserError, match=ROUTED):
        _as(cr, m5.cfo).action_approve()
    # ...nor the finance approver, who is not the tier BRU-RMS-06 asks for
    _as(cr, m5.eng).action_request_approval(justification="Outage credit agreed with the client")
    assert m5.cfo in assigned(cr) and m5.fin not in assigned(cr)
    _approve(cr, m5.cfo)
    assert cr.state == "approved" and cr.approved_by_id == m5.cfo and cr.approved_amount == 5000.0
    _as(cr, m5.fin).action_apply()
    assert cr.state == "applied"


def test_S1_the_raiser_cannot_approve_their_own_credit(m5):
    _report(m5, "2026-07", attainment=0.5)
    _as(m5.msp, m5.fin_eng).action_compute_sla_credits()
    cr = _credit(m5, "2026-07")
    assert cr.credit_amount == 4500.0
    _as(cr, m5.fin_eng).action_request_approval()
    assert m5.fin_eng not in assigned(cr) and m5.fin in assigned(cr)
    manual = _as(m5.env["fix.msp.sla.credit"], m5.eng).create(
        {
            "msp_contract_id": m5.msp.id,
            "period_label": "A02-own",
            "manual_amount": 100.0,
            "dofa_justification": "x",
        }
    )
    m5.env.ref(TIER4).sudo().write({"user_ids": [(4, m5.eng.id)]})
    _as(manual, m5.eng).action_request_approval(justification="client outage")
    assert m5.eng not in assigned(manual)


def test_a_computed_credit_is_approved_by_finance_and_applied(m5):
    _report(m5, "2026-09", attainment=0.5)
    _as(m5.msp, m5.eng).action_compute_sla_credits()
    cr = _credit(m5, "2026-09")
    assert cr.state == "draft" and not cr.is_manual
    assert cr.computed_amount == cr.credit_amount == 4500.0  # 45% of 4 x 2500
    with pytest.raises(UserError, match=ROUTED):
        _as(cr, m5.fin).action_approve()
    with pytest.raises(UserError, match="must be approved"):
        _as(cr, m5.fin).action_apply()
    _as(cr, m5.eng).action_request_approval()
    # a computed credit goes to the credit approvers, never to a DOFA tier
    assert assigned(cr) == m5.fin | m5.fin_eng
    _approve(cr, m5.fin)
    assert cr.approved_by_id == m5.fin and cr.approved_amount == 4500.0
    with pytest.raises(UserError, match="SLA Credit Approver"):
        _as(cr, m5.eng).action_apply()
    _as(cr, m5.fin).action_apply()
    event = m5.env["fix.event.outbox"].search(
        [("event_type", "=", "msp.sla_credit_applied"), ("aggregate_id", "=", cr.id)]
    )
    assert json.loads(event.payload)["amount"] == 4500.0


def test_S2_a_changed_amount_voids_the_approval(m5):
    cr = _as(m5.env["fix.msp.sla.credit"], m5.eng).create(
        {
            "msp_contract_id": m5.msp.id,
            "period_label": "A02-raise",
            "manual_amount": 4500.0,
            "dofa_justification": "agreed",
        }
    )
    _approve(cr, m5.cfo, justification="agreed")
    with pytest.raises(UserError, match=GUARD):
        _as(cr, m5.eng).write({"credit_amount": 450000.0})
    _as(cr, m5.eng).write({"manual_amount": 9000.0})
    assert cr.state == "draft" and not cr.approved_by_id and not cr.dofa_approved
    assert cr.approval_state == "none"  # the M63 approval goes with it
    with pytest.raises(UserError, match="must be approved"):
        _as(cr, m5.fin).action_apply()


def test_S2_apply_rechecks_the_pinned_amount(m5):
    report = _report(m5, "2026-10", attainment=0.5)
    _as(m5.msp, m5.eng).action_compute_sla_credits()
    cr = _credit(m5, "2026-10")
    _approve(cr, m5.fin, requester=m5.eng)
    # the system regenerates the figure after approval: the approval no longer covers it
    report.write({"sla_attainment": 0.0})
    cr.invalidate_recordset()
    assert cr.credit_amount == 9500.0
    with pytest.raises(UserError, match="approved again"):
        _as(cr, m5.fin).action_apply()


def test_S3_credit_state_cannot_be_forged(m5, call):
    _report(m5, "2026-06", attainment=0.5)
    _as(m5.msp, m5.eng).action_compute_sla_credits()
    cr = _credit(m5, "2026-06")
    res = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.sla.credit",
        record_id=cr.id,
        values={"state": "approved"},
    )
    assert res.get("error"), res
    with pytest.raises(UserError, match=GUARD):
        _as(cr, m5.eng).write({"approved_by_id": m5.fin.id})
    cr.invalidate_recordset()
    assert cr.state == "draft"


def test_S4_a_report_with_no_attainment_is_flagged_not_credited(m5):
    report = _report(m5, "2026-08")
    _as(m5.msp, m5.eng).action_compute_sla_credits()
    assert not _credit(m5, "2026-08")
    assert report.attainment_flagged
    # the figure itself cannot be typed to manufacture a credit
    with pytest.raises(UserError, match=GUARD):
        _as(report, m5.eng).write({"sla_attainment": 0.0})


# ======================================== M05-4 remote-session consent


def _session(m5, user=None, asset=None, contract=None, **vals):
    base = {
        "msp_contract_id": (contract or m5.msp).id,
        "asset_id": (asset or m5.asset).id,
        "technician_id": m5.tech.id,
        "operating_unit_id": m5.ou.id,
    }
    base.update(vals)
    return _as(m5.env["fix.remote.session"], user or m5.eng).create(base)


def _request_code(session):
    """Request consent; return the code the client contact received."""
    sent = {}

    def _send(self, partner, code, ttl_seconds):
        sent.update(partner=partner, code=code)
        return {"destination": "017*****222"}

    with mock.patch.object(type(session), "_consent_send_code", _send):
        session.action_request_consent()
    return sent


def test_R1_a_ticked_box_is_not_consent(m5, call):
    s = _session(m5)
    env = m5.env(user=m5.eng.id)
    res = call(
        env,
        "model_write",
        model="fix.remote.session",
        record_id=s.id,
        values={"consent_captured": True, "consent_token_ref": "made-up"},
    )
    assert res.get("error"), res
    with pytest.raises(UserError, match=GUARD):
        _as(s, m5.eng).write({"consent_captured": True})
    out = call(env, "model_action", model="fix.remote.session", ids=[s.id], method="action_start")
    assert not out.get("success") and "consent" in out["error"]
    s.invalidate_recordset()
    assert not s.started


def test_R1_the_client_consent_code_opens_the_session(m5, call):
    s = _session(m5, consent_partner_id=m5.contact.id)
    sent = _request_code(_as(s, m5.eng))
    assert sent["partner"] == m5.contact
    env = m5.env(user=m5.eng.id)
    wrong = call(
        env,
        "model_action",
        model="fix.remote.session",
        ids=[s.id],
        method="action_verify_consent",
        kwargs={"code": "000000" if sent["code"] != "000000" else "111111"},
    )
    assert not wrong.get("success") and "does not match" in wrong["error"]
    s.invalidate_recordset()
    assert not s.consent_captured
    ok = call(
        env,
        "model_action",
        model="fix.remote.session",
        ids=[s.id],
        method="action_verify_consent",
        kwargs={"code": sent["code"]},
    )
    assert ok.get("success"), ok
    s.invalidate_recordset()
    assert s.consent_captured and s.consent_token_ref.startswith("fix.otp.log,")
    assert s.consent_verified_by_id == m5.eng
    log = m5.env["fix.otp.log"].browse(int(s.consent_token_ref.split(",")[1]))
    assert log.partner_id == m5.contact and log.state == "verified"
    _as(s, m5.eng).action_start()
    assert s.started
    with pytest.raises(UserError, match="recording reference"):
        _as(s, m5.eng).action_end()
    _as(s, m5.eng).action_end(recording_url="mesh://rec/a02-1")
    assert s.ended_at and s.recording_url == "mesh://rec/a02-1"


def test_wrong_codes_void_the_consent_code(m5):
    s = _session(m5)
    sent = _request_code(_as(s, m5.eng))
    bad = "123456" if sent["code"] != "123456" else "654321"
    for attempt in range(1, 4):
        with pytest.raises(UserError, match="does not match"):
            _as(s, m5.eng).action_verify_consent(code=bad)
        assert s.consent_attempts == attempt
    with pytest.raises(UserError, match="No live consent code"):
        _as(s, m5.eng).action_verify_consent(code=sent["code"])
    assert not s.consent_captured


def test_an_expired_consent_code_is_refused(m5):
    s = _session(m5)
    sent = _request_code(_as(s, m5.eng))
    s._guarded().write({"consent_expires_at": fields.Datetime.now() - timedelta(minutes=1)})
    with pytest.raises(UserError, match="expired"):
        _as(s, m5.eng).action_verify_consent(code=sent["code"])


def test_the_code_goes_to_a_real_mobile_number(m5):
    m5.contact.write({"phone": False})
    s = _session(m5, consent_partner_id=m5.contact.id)
    with pytest.raises(UserError, match="no Bangladesh mobile number"):
        _as(s, m5.eng).action_request_consent()


def test_only_the_clients_own_contact_can_consent(m5):
    stranger = m5.env["res.partner"].create({"name": "Not the client", "phone": "01711000999"})
    with pytest.raises(ValidationError, match="not a contact of the contract's customer"):
        _session(m5, consent_partner_id=stranger.id)


def test_R5_a_session_on_another_contracts_asset_is_refused(m5):
    with pytest.raises(ValidationError, match="not covered by MSP contract"):
        _session(m5, asset=m5.other_asset)
    s = _session(m5, asset=m5.other_asset, contract=m5.other)
    assert s.asset_id == m5.other_asset


def test_the_consent_scope_is_frozen_once_the_code_is_out(m5):
    s = _session(m5)
    _request_code(_as(s, m5.eng))
    second = m5.env["fix.monitored.asset"].create(
        {"msp_contract_id": m5.msp.id, "agent_id": "AGT-A2P0-2ND", "operating_unit_id": m5.ou.id}
    )
    with pytest.raises(UserError, match="consent was requested"):
        _as(s, m5.eng).write({"asset_id": second.id})


def test_R3_started_and_ended_cannot_be_forged(m5):
    s = _session(m5)
    with pytest.raises(UserError, match=GUARD):
        _as(s, m5.eng).write({"started": True})
    with pytest.raises(UserError, match=GUARD):
        _as(s, m5.eng).write({"ended_at": fields.Datetime.now()})
    with pytest.raises(UserError, match=GUARD):
        _as(s, m5.eng).write({"recording_url": "forged"})


def test_the_recording_switch_can_be_turned_off(m5):
    m5.env["ir.config_parameter"].set_param(
        "cd_msp_contract.remote_session_recording_required", "0"
    )
    s = _session(m5)
    sent = _request_code(_as(s, m5.eng))
    _as(s, m5.eng).action_verify_consent(code=sent["code"])
    _as(s, m5.eng).action_start()
    _as(s, m5.eng).action_end()
    assert s.ended_at and not s.recording_url


# ================================================ M05-5 maintenance windows


def test_W1_an_engineer_cannot_raise_a_window(m5):
    with pytest.raises(AccessError):
        _window(m5, m5.eng)


def test_W1_a_forged_estate_window_does_not_silence_alerting(m5, call):
    win = _window(m5, m5.cm, end=24 * 30, contract=False, name="silent")
    res = call(
        m5.env(user=m5.cm.id),
        "model_write",
        model="fix.msp.maintenance.window",
        record_id=win.id,
        values={"state": "active"},
    )
    assert res.get("error"), res
    with pytest.raises(UserError, match=GUARD):
        _as(win, m5.cm).write({"approved_at": fields.Datetime.now()})
    assert win.state == "planned"
    m5.env["fix.monitored.asset"].ingest_telemetry(
        m5.asset.agent_id, "offline", fields.Datetime.now()
    )
    assert m5.env["fix.msp.alert"].search_count([("asset_id", "=", m5.asset.id)]) == 1


def test_an_estate_wide_window_needs_a_cab_member(m5):
    win = _window(m5, m5.cm, contract=False, name="estate")
    with pytest.raises(UserError, match="CAB Member"):
        _as(win, m5.cm).action_approve()
    _as(win, m5.cab).action_approve()
    assert win.approved_by_id == m5.cab and win.state == "active"
    assert m5.env["fix.msp.maintenance.window"].alerting_suppressed(m5.asset)
    m5.env["fix.monitored.asset"].ingest_telemetry(
        m5.asset.agent_id, "offline", fields.Datetime.now()
    )
    assert not m5.env["fix.msp.alert"].search_count([("asset_id", "=", m5.asset.id)])
    # state follows the approval and the clock, and an early close ends it
    assert win in m5.env["fix.msp.maintenance.window"].search([("state", "=", "active")])
    with pytest.raises(UserError, match="CAB Member or MSP Change Manager"):
        _as(win, m5.eng).action_close()
    _as(win, m5.cm).action_close()
    assert win.state == "closed"
    assert not m5.env["fix.msp.maintenance.window"].alerting_suppressed(m5.asset)


def test_a_contract_window_by_the_change_manager_never_their_own(m5):
    win = _window(m5, m5.cab, name="contract")
    with pytest.raises(UserError, match="Segregation of duties"):
        _as(win, m5.cab).action_approve()
    _as(win, m5.cm).action_approve()
    assert win.state == "active"
    future = _window(m5, m5.cab, start=48, end=50, name="future")
    _as(future, m5.cm).action_approve()
    assert future.state == "planned"


def test_an_approved_window_is_frozen(m5):
    win = _window(m5, m5.cm)
    _as(win, m5.cab).action_approve()
    with pytest.raises(UserError, match="approved maintenance window"):
        _as(win, m5.cm).write({"end_at": fields.Datetime.now() + timedelta(days=30)})
    assert "end_at" in win._fix_form_locked_fields()


# ==================================== A1 on the remaining surfaces, M05-12


def test_O1_on_call_state_is_guarded_and_primaries_do_not_overlap(m5, call):
    now = fields.Datetime.now()
    Shift = _as(m5.env["fix.msp.oncall.shift"], m5.eng)
    vals = {
        "technician_id": m5.tech.id,
        "start_at": now - timedelta(hours=1),
        "end_at": now + timedelta(hours=8),
        "operating_unit_id": m5.ou.id,
    }
    a = Shift.create(dict(vals, name="A"))
    # A02 audit M05-P2: the overlap is a constraint, not only an activation check
    with (
        pytest.raises(ValidationError, match="overlaps the planned primary shift A"),
        m5.env.cr.savepoint(),
    ):
        Shift.create(dict(vals, name="B"))
    b = Shift.create(dict(vals, name="B", level="secondary"))
    res = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.oncall.shift",
        record_id=a.id,
        values={"state": "active"},
    )
    assert res.get("error"), res
    a.action_activate()
    b.action_activate()
    assert (a.state, b.state) == ("active", "active")


def test_A4_alert_state_and_escalation_are_guarded(m5, call):
    alert = m5.env["fix.msp.alert"].create(
        {"msp_contract_id": m5.msp.id, "asset_id": m5.asset.id, "message": "offline 2"}
    )
    res = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.alert",
        record_id=alert.id,
        values={"state": "resolved"},
    )
    assert res.get("error"), res
    for forged in ({"escalated": True}, {"resolution_note": "fixed"}):
        with pytest.raises(UserError, match=GUARD):
            _as(alert, m5.eng).write(forged)
    _as(alert, m5.eng).action_escalate()
    _as(alert, m5.eng).action_resolve(note="replaced the NIC")
    assert alert.state == "resolved" and alert.escalated


def test_a_runbook_run_outcome_is_guarded(m5):
    book = _as(m5.env["fix.msp.runbook"], m5.eng).create(
        {"name": "Reboot", "script": "reboot", "operating_unit_id": m5.ou.id}
    )
    _as(book, m5.eng).action_execute(asset=m5.asset.id)
    run = m5.env["fix.msp.runbook.run"].search([("runbook_id", "=", book.id)])
    assert run.state == "success"
    with pytest.raises(UserError, match=GUARD):
        _as(run, m5.eng).write({"state": "failed"})


def test_a_plain_internal_user_has_no_msp_write(m5):
    with pytest.raises(AccessError):
        _change(m5, user=m5.plain)
    with pytest.raises(AccessError):
        _session(m5, user=m5.plain)


def test_the_monthly_report_button_still_works(m5, call):
    out = call(
        m5.env(user=m5.eng.id),
        "model_action",
        model="fix.msp.contract",
        ids=[m5.msp.id],
        method="action_generate_monthly_report",
    )
    assert out.get("success"), out
    report = m5.env["fix.msp.service.report"].browse(out["result"]["res_id"])
    assert report.msp_contract_id == m5.msp and report.sla_attainment == 1.0
