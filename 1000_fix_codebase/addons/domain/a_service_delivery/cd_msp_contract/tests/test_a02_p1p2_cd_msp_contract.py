"""A02 audit P1/P2 for M05 Remote Support & MSP (B1 routing, B4 crons, P2).

Every control is tested both ways (the bypass is refused, the legitimate
path works), acting as freshly created NON-ADMIN users holding only the M05
roles they need: the superuser is trusted by the guards and the engine.

  B1  CAB change, emergency change, SLA credit and the patch install
      exception are M63 routed approvals: a direct press is refused, the
      approver's inbox decides, requester / creator never receive the task.
  B4  monthly report + credit cron; maintenance-window open / close events.
  P2  entitlement follows the M08 contract (and its renewal); the alert
      ticket carries the contract; resolution needs the ticket outcome or a
      note; runbook evidence; on-call constraint and lock; SLA measured from
      resolution times.

``odoo_env`` (addons/conftest.py): rolled back after every test.
"""

import itertools
import json
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

_SEQ = itertools.count(1)
ROUTED = "approver's inbox"
GUARD = "changes only through its workflow"
ENG = "cd_msp_contract.group_msp_engineer"
CAB = "cd_msp_contract.group_msp_cab_member"
CM = "cd_msp_contract.group_msp_change_manager"
FIN = "cd_msp_contract.group_msp_credit_approver"
WINDOW_SWITCH = "cd_msp_contract.patch_install_requires_window"
TEST_SWITCH = "cd_msp_contract.patch_install_requires_test"
ENTITLEMENT_SWITCH = "cd_msp_contract.entitlement_required"
HASH_A = "a" * 64


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
                    "name": "A02 P1 M05 %s %d" % (key, n),
                    "login": "a02.p1.m05.%s.%d@a02.test" % (key, n),
                    "group_ids": [(6, 0, ids)],
                    "operating_unit_ids": [(6, 0, ou.ids)],
                    "default_operating_unit_id": ou.id,
                }
            )
        )

    eng, eng2 = user("eng", ENG), user("eng2", ENG)
    cab, cab2 = user("cab", CAB), user("cab2", CAB)
    cm, fin, fin2 = user("cm", CM), user("fin", FIN), user("fin2", FIN)
    plain = user("plain")
    tech = env["hr.employee"].create({"name": "A02 P1 M05 Tech %d" % n})
    entity = env["fix.entity"].create(
        {"code": "A2P1M5%d" % n, "legal_name": "A02 P1 M05 %d" % n, "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "A02 P1 Br %d" % n,
            "code": "A2P%d" % n,
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    customer = env["res.partner"].create(
        {"name": "A02 P1 M05 Client %d" % n, "is_company": True, "phone": "01711000111"}
    )
    brand = env["fix.brand"].create({"name": "A2P1Brand%d" % n, "code": "A2B%d" % n})
    model = env["fix.device.model"].create({"name": "A2P1 Laptop %d" % n, "brand_id": brand.id})
    device = env["fix.device"].create(
        {
            "device_model_id": model.id,
            "owner_id": customer.id,
            "branch_id": branch.id,
            "serial_number": "SN-A2P1-%d" % n,
        }
    )

    def contract(state="active", **vals):
        return env["fix.contract"].create(
            {
                "name": "A02 P1 Contract %d" % n,
                "customer_id": customer.id,
                "family": "managed",
                "state": state,
                "operating_unit_id": ou.id,
                "date_start": fields.Date.today() - timedelta(days=30),
                "date_end": fields.Date.today() + timedelta(days=335),
                "annual_value": 240000.0,
                **vals,
            }
        )

    term = contract()
    msp = env["fix.msp.contract"].create(
        {
            "name": "A02 P1 MSP %d" % n,
            "contract_id": term.id,
            "operating_unit_id": ou.id,
            "device_count": 4,
            "per_device_monthly": 2500.0,
            "sla_target_pct": 95.0,
        }
    )
    asset = env["fix.monitored.asset"].create(
        {
            "msp_contract_id": msp.id,
            "agent_id": "AGT-A2P1-%d" % n,
            "hostname": "ws-a2p1-%d" % n,
            "device_id": device.id,
            "operating_unit_id": ou.id,
        }
    )
    return SimpleNamespace(**locals())


def _as(rec, user):
    return rec.with_user(user)


def _change(m5, user=None, **vals):
    base = {
        "name": "Rotate firewall keys",
        "msp_contract_id": m5.msp.id,
        "risk": "medium",
        "operating_unit_id": m5.ou.id,
    }
    base.update(vals)
    return _as(m5.env["fix.msp.change.record"], user or m5.eng).create(base)


def _window(m5, start=-1, end=4, approve=True):
    now = fields.Datetime.now()
    win = _as(m5.env["fix.msp.maintenance.window"], m5.cm).create(
        {
            "name": "Tonight",
            "msp_contract_id": m5.msp.id,
            "start_at": now + timedelta(hours=start),
            "end_at": now + timedelta(hours=end),
            "operating_unit_id": m5.ou.id,
        }
    )
    if approve:
        _as(win, m5.cab).action_approve()
    return win


def _events(env, event_type, res_id):
    return env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", res_id)]
    )


# ============================================================ B1 · CAB change


def test_b1_change_is_decided_in_the_inbox_not_by_the_button(m5):
    ch = _change(m5, rollback_plan="snapshot")
    with pytest.raises(UserError, match=ROUTED):
        _as(ch, m5.cab).action_approve()
    assert ch.state == "draft"
    _as(ch, m5.eng).action_request_approval(justification="quarterly rotation")
    assert ch.approval_state == "pending"
    assert assigned(ch) == m5.cab | m5.cab2
    # a CAB member without a task cannot carry it either
    other = _change(m5, name="another")
    with pytest.raises(UserError, match=ROUTED):
        _as(other, m5.cab).with_context(fix_approval_task=inbox_task(ch, m5.cab)).action_approve()
    approve_via_inbox(ch, m5.cab2)
    assert (ch.state, ch.approval_state, ch.cab_approver_id) == ("approved", "approved", m5.cab2)


def test_b1_inbox_rejection_rejects_the_change(m5):
    ch = _change(m5)
    _as(ch, m5.eng).action_request_approval()
    with pytest.raises(UserError, match="State why"):
        _as(inbox_task(ch, m5.cab), m5.cab).action_reject()
    _as(inbox_task(ch, m5.cab), m5.cab).action_reject(comment="no rollback tested")
    assert ch.state == "rejected" and ch.approval_state == "rejected"


def test_b1_editing_a_pending_change_voids_the_request(m5):
    ch = _change(m5)
    _as(ch, m5.eng).action_request_approval()
    _as(ch, m5.eng).write({"risk": "low"})
    assert ch.approval_state == "none" and not inbox_task(ch, m5.cab)


def test_b1_emergency_change_goes_to_the_change_manager_only(m5):
    ch = _change(m5, change_type="emergency", risk="high")
    with pytest.raises(UserError, match="rollback plan"):
        _as(ch, m5.eng).action_request_approval()
    _as(ch, m5.eng).write({"rollback_plan": "revert config"})
    _as(ch, m5.eng).action_request_approval(justification="client outage")
    assert assigned(ch) == m5.cm
    approve_via_inbox(ch, m5.cm)
    assert ch.state == "approved" and ch.cab_approver_id == m5.cm


def test_b1_nobody_but_the_requester_holds_the_role(m5):
    """No other CAB member: the request is refused, it never self-routes."""
    m5.env.ref(CAB).sudo().write({"user_ids": [(3, m5.cab.id), (3, m5.cab2.id)]})
    m5.env.ref(CAB).sudo().write({"user_ids": [(4, m5.eng.id)]})
    ch = _change(m5)
    with pytest.raises(UserError, match="No one can approve"):
        _as(ch, m5.eng).action_request_approval()


def test_b1_pir_reviewer_is_not_the_implementer(m5):
    ch = _change(m5, change_type="emergency", rollback_plan="revert")
    approve_via_inbox(ch, m5.cm)
    _as(ch, m5.eng2).action_implement(note="done")
    m5.env.ref(CAB).sudo().write({"user_ids": [(4, m5.eng2.id)]})
    with pytest.raises(UserError, match="Segregation of duties"):
        _as(ch, m5.eng2).action_record_review(note="all fine")
    _as(ch, m5.cab).action_record_review(note="service restored in 4 minutes")
    assert ch.pir_by_id == m5.cab


# ============================================================ B1 · SLA credit


def _report(m5, period, attainment, alerts=10, within=5):
    return m5.env["fix.msp.service.report"].create(
        {
            "msp_contract_id": m5.msp.id,
            "period_label": period,
            "alert_count": alerts,
            "resolved_count": within,
            "sla_attainment": attainment,
            "operating_unit_id": m5.ou.id,
        }
    )


def _credit(m5, period):
    return m5.env["fix.msp.sla.credit"].search(
        [("msp_contract_id", "=", m5.msp.id), ("period_label", "=", period)]
    )


def test_b1_sla_credit_routed_to_a_credit_approver_who_did_not_raise_it(m5):
    _report(m5, "2026-05", 0.5)
    m5.env.ref(FIN).sudo().write({"user_ids": [(4, m5.eng.id)]})
    _as(m5.msp, m5.eng).action_compute_sla_credits()
    cr = _credit(m5, "2026-05")
    with pytest.raises(UserError, match=ROUTED):
        _as(cr, m5.fin).action_approve()
    _as(cr, m5.eng).action_request_approval()
    assert m5.eng not in assigned(cr) and assigned(cr) == m5.fin | m5.fin2
    approve_via_inbox(cr, m5.fin2)
    assert cr.state == "approved" and cr.approved_by_id == m5.fin2
    _as(cr, m5.fin).action_apply()
    payload = json.loads(_events(m5.env, "msp.sla_credit_applied", cr.id).payload)
    assert payload["partner_id"] == m5.customer.id
    assert payload["contract_id"] == m5.term.id and payload["period"] == "2026-05"
    assert payload["amount"] == 4500.0 and payload["approval_request"]


def test_b1_a_credit_on_a_term_never_in_force_is_not_requested(m5):
    draft = m5.contract(state="draft", name="draft term")
    msp = m5.env["fix.msp.contract"].create(
        {"name": "draft MSP", "contract_id": draft.id, "operating_unit_id": m5.ou.id}
    )
    cr = _as(m5.env["fix.msp.sla.credit"], m5.eng).create(
        {"msp_contract_id": msp.id, "period_label": "2026-04", "manual_amount": 0.0}
    )
    with pytest.raises(UserError, match="never came"):
        _as(cr, m5.eng).action_request_approval()


# ======================================================= B1 · patch exception


def _patch(m5, ident, severity="medium"):
    upd = _as(m5.env["fix.msp.patch.update"], m5.eng).create(
        {
            "msp_contract_id": m5.msp.id,
            "asset_id": m5.asset.id,
            "identifier": ident,
            "title": "Patch %s" % ident,
            "severity": severity,
            "operating_unit_id": m5.ou.id,
        }
    )
    _as(upd, m5.eng if severity != "critical" else m5.cab).action_approve()
    return upd


def test_b1_patch_install_today_needs_no_window(m5):
    upd = _patch(m5, "KB-TODAY")
    _as(upd, m5.eng).action_install()
    assert upd.state == "installed"


def test_b1_outside_window_install_needs_a_routed_exception(m5):
    m5.env["ir.config_parameter"].set_param(WINDOW_SWITCH, "1")
    upd = _patch(m5, "KB-WIN")
    with pytest.raises(UserError, match="approved maintenance window"):
        _as(upd, m5.eng).action_install()
    with pytest.raises(UserError, match="Justify"):
        _as(upd, m5.eng).action_request_window_exception(reason="now")
    with pytest.raises(UserError, match="MSP Engineer"):
        _as(upd, m5.plain).action_request_window_exception(reason="zero-day in the wild")
    _as(upd, m5.eng).action_request_window_exception(reason="zero-day in the wild")
    assert upd.exception_kind == "outside_window" and upd.approval_state == "pending"
    assert assigned(upd) == m5.cm  # a non-critical patch: the change manager
    with pytest.raises(UserError, match=ROUTED):
        _as(upd, m5.cm).action_approve_exception()
    with pytest.raises(UserError, match="approved maintenance window"):
        _as(upd, m5.eng).action_install()  # pending is not approved
    approve_via_inbox(upd, m5.cm)
    assert upd.exception_approved_by_id == m5.cm
    _as(upd, m5.eng).action_install()
    assert upd.state == "installed"


def test_b1_inside_an_open_window_needs_no_exception(m5):
    m5.env["ir.config_parameter"].set_param(WINDOW_SWITCH, "1")
    _window(m5)
    upd = _patch(m5, "KB-INWIN")
    _as(upd, m5.eng).action_install()
    assert upd.state == "installed"


def test_b1_critical_patch_exception_goes_to_the_cab(m5):
    m5.env["ir.config_parameter"].set_param(WINDOW_SWITCH, "1")
    upd = _patch(m5, "KB-CRIT", severity="critical")
    _as(upd, m5.eng).action_request_window_exception(reason="actively exploited CVE")
    assert assigned(upd) == m5.cab | m5.cab2


def test_b1_skipping_the_test_needs_an_exception_or_a_test(m5):
    m5.env["ir.config_parameter"].set_param(TEST_SWITCH, "1")
    upd = _patch(m5, "KB-TEST")
    with pytest.raises(UserError, match="pre-deployment test"):
        _as(upd, m5.eng).action_install()
    with pytest.raises(UserError, match=GUARD):
        _as(upd, m5.eng).write({"tested_at": fields.Datetime.now()})
    _as(upd, m5.eng).action_record_test(note="pilot ring: 3 hosts, no regressions")
    _as(upd, m5.eng).action_install()
    other = _patch(m5, "KB-SKIP")
    _as(other, m5.eng).action_request_test_exception(reason="vendor hotfix, no lab image")
    approve_via_inbox(other, m5.cm)
    _as(other, m5.eng).action_install()
    assert (upd.state, other.state) == ("installed", "installed")


# ======================================================== B4 · monthly cron


def _alert(m5, created, severity="minor", state="new", resolved_in=None):
    alert = m5.env["fix.msp.alert"].create(
        {
            "msp_contract_id": m5.msp.id,
            "asset_id": m5.asset.id,
            "message": "disk",
            "severity": severity,
            "state": state,
        }
    )
    m5.env.flush_all()
    m5.env.cr.execute(
        "UPDATE fix_msp_alert SET create_date = %s, resolved_at = %s WHERE id = %s",
        (created, created + timedelta(hours=resolved_in) if resolved_in else None, alert.id),
    )
    m5.env.invalidate_all()
    return alert


def test_b4_monthly_cron_reports_last_month_once_and_computes_credits(m5):
    Contract = m5.env["fix.msp.contract"]
    period = Contract._msp_previous_month()
    start = period[0] + timedelta(days=2)
    _alert(m5, start, state="resolved", resolved_in=2)  # within the 24 h minor target
    _alert(m5, start, state="resolved", resolved_in=30)  # resolved late
    _alert(m5, start, severity="major", state="resolved", resolved_in=6)  # late against 4 h
    draft_msp = m5.env["fix.msp.contract"].create(
        {
            "name": "draft",
            "contract_id": m5.contract(state="draft").id,
            "operating_unit_id": m5.ou.id,
        }
    )
    Contract.cron_monthly_service_reports()
    report = m5.msp.report_ids.filtered(lambda r: r.period_label == period[2])
    assert len(report) == 1
    assert (report.alert_count, report.resolved_count, report.breached_count) == (3, 1, 2)
    assert report.resolved_total_count == 3
    assert round(report.sla_attainment, 4) == round(1 / 3, 4)
    credit = _credit(m5, period[2])
    assert credit and credit.breach_count == 2 and credit.credit_amount > 0
    assert not draft_msp.report_ids
    Contract.cron_monthly_service_reports()  # idempotent
    assert len(m5.msp.report_ids.filtered(lambda r: r.period_label == period[2])) == 1
    assert len(_credit(m5, period[2])) == 1


def test_b4_crons_are_scheduled(m5):
    for xmlid in (
        "cd_msp_contract.ir_cron_msp_monthly_service_reports",
        "cd_msp_contract.ir_cron_msp_window_boundaries",
    ):
        cron = m5.env.ref(xmlid)
        assert cron.active
    consumer = m5.env.ref("cd_msp_contract.consumer_contract_renewed_msp")
    assert consumer.event_type == "contract.renewed"


# ======================================================== B4 · window events


def test_b4_window_open_and_close_are_published_once(m5):
    win = _window(m5)  # approving a running window opens it at once
    assert len(_events(m5.env, "msp.window_opened", win.id)) == 1
    m5.env["fix.msp.maintenance.window"].cron_window_boundaries()
    assert len(_events(m5.env, "msp.window_opened", win.id)) == 1
    assert not _events(m5.env, "msp.window_closed", win.id)
    _as(win, m5.cm).action_close()
    closed = _events(m5.env, "msp.window_closed", win.id)
    assert len(closed) == 1 and json.loads(closed.payload)["closed_early"] is True
    m5.env["fix.msp.maintenance.window"].cron_window_boundaries()
    assert len(_events(m5.env, "msp.window_closed", win.id)) == 1
    with pytest.raises(UserError, match=GUARD):
        _as(win, m5.cm).write({"opened_published_at": False})


def test_b4_cron_publishes_a_window_that_opened_and_ended_on_its_own(m5):
    win = _window(m5, start=2, end=3)
    assert not _events(m5.env, "msp.window_opened", win.id)
    future = fields.Datetime.now() + timedelta(hours=4)
    with mock.patch.object(fields.Datetime, "now", return_value=future):
        m5.env["fix.msp.maintenance.window"].cron_window_boundaries()
    assert len(_events(m5.env, "msp.window_opened", win.id)) == 1
    assert len(_events(m5.env, "msp.window_closed", win.id)) == 1


def test_b4_unapproved_or_early_closed_window_publishes_nothing(m5):
    win = _window(m5, start=2, end=3, approve=False)
    m5.env["fix.msp.maintenance.window"].cron_window_boundaries()
    approved = _window(m5, start=2, end=3)
    _as(approved, m5.cm).action_close()
    for w in (win, approved):
        assert not _events(m5.env, "msp.window_opened", w.id)
        assert not _events(m5.env, "msp.window_closed", w.id)


# ================================================ P2 · entitlement / renewal


def _draft_msp(m5):
    draft = m5.contract(state="draft", name="unsigned")
    msp = m5.env["fix.msp.contract"].create(
        {"name": "unsigned MSP", "contract_id": draft.id, "operating_unit_id": m5.ou.id}
    )
    asset = m5.env["fix.monitored.asset"].create(
        {
            "msp_contract_id": msp.id,
            "agent_id": "AGT-DRAFT-%d" % m5.n,
            "device_id": m5.device.id,
            "operating_unit_id": m5.ou.id,
        }
    )
    return msp, asset


def test_p2_no_ticket_or_session_on_a_term_not_in_force(m5):
    msp, asset = _draft_msp(m5)
    assert not msp.entitled and m5.msp.entitled
    alert = m5.env["fix.msp.alert"].create(
        {"msp_contract_id": msp.id, "asset_id": asset.id, "message": "offline"}
    )
    with pytest.raises(UserError, match="not entitled"):
        _as(alert, m5.eng).action_to_ticket()
    session = _as(m5.env["fix.remote.session"], m5.eng).create(
        {"msp_contract_id": msp.id, "asset_id": asset.id, "technician_id": m5.tech.id}
    )
    with pytest.raises(UserError, match="not entitled"):
        _as(session, m5.eng).action_request_consent()
    with pytest.raises(UserError, match="not entitled"):
        session._guarded().write({"consent_captured": True, "consent_token_ref": "x"})
        _as(session, m5.eng).action_start()
    # the business may switch the rule off while it brings terms into force
    m5.env["ir.config_parameter"].set_param(ENTITLEMENT_SWITCH, "0")
    _as(alert, m5.eng).action_to_ticket()
    assert alert.state == "ticketed"


def test_p2_expired_term_is_not_entitled(m5):
    m5.term.write(
        {
            "date_end": fields.Date.today() - timedelta(days=1),
            "date_start": fields.Date.today() - timedelta(days=300),
        }
    )
    alert = m5.env["fix.msp.alert"].create(
        {"msp_contract_id": m5.msp.id, "asset_id": m5.asset.id, "message": "offline"}
    )
    with pytest.raises(UserError, match="outside the M08 term"):
        _as(alert, m5.eng).action_to_ticket()


def test_p2_the_alert_ticket_carries_its_contract(m5):
    alert = m5.env["fix.msp.alert"].create(
        {"msp_contract_id": m5.msp.id, "asset_id": m5.asset.id, "message": "offline"}
    )
    _as(alert, m5.eng).action_to_ticket()
    assert alert.order_id.contract_id == m5.term
    assert alert.order_id._fix_zero_charge_basis().startswith("AMC contract")


def _relay(env):
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "=", "contract.renewed")])
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    return env["fix.event.outbox"].cron_relay()


def test_p2_a_renewal_repoints_the_msp_layer(m5):
    renewal = m5.term.action_renew()
    assert m5.msp.contract_id == m5.term
    _relay(m5.env)
    assert m5.msp.contract_id == renewal
    # the renewed term is a draft until it is activated: no entitlement yet
    assert not m5.msp.entitled
    renewal.state = "active"
    renewal.date_start = fields.Date.today() - timedelta(days=1)
    m5.msp.invalidate_recordset()
    assert m5.msp.entitled


def test_p2_the_renewal_consumer_is_the_relays_alone_and_idempotent(m5):
    event = {"aggregate_id": m5.term.id, "payload": {"old_code": m5.term.code}}
    with pytest.raises(AccessError):
        _as(m5.env["fix.msp.contract"], m5.eng).consume_contract_renewed(event)
    renewal = m5.contract(name="next term")
    event = {"aggregate_id": renewal.id, "payload": {"old_code": m5.term.code}}
    Msp = m5.env["fix.msp.contract"]
    assert Msp.consume_contract_renewed(event)["repointed"] == 1
    assert Msp.consume_contract_renewed(event)["repointed"] == 0
    assert m5.msp.contract_id == renewal


# ============================================== P2 · alert resolution, runbooks


def test_p2_a_ticketed_alert_resolves_on_its_order_outcome(m5):
    alert = m5.env["fix.msp.alert"].create(
        {"msp_contract_id": m5.msp.id, "asset_id": m5.asset.id, "message": "offline"}
    )
    _as(alert, m5.eng).action_to_ticket()
    with pytest.raises(UserError, match="resolves when service order"):
        _as(alert, m5.eng).action_resolve(note="fixed remotely")
    m5.env.flush_all()
    m5.env.cr.execute(
        "UPDATE fix_service_order SET state = 'delivered' WHERE id = %s", (alert.order_id.id,)
    )
    m5.env.invalidate_all()
    _as(alert, m5.eng).action_resolve()
    assert alert.state == "resolved" and alert.order_id.name in alert.resolution_note


def test_p2_an_unticketed_alert_needs_a_note(m5):
    alert = m5.env["fix.msp.alert"].create(
        {"msp_contract_id": m5.msp.id, "asset_id": m5.asset.id, "message": "flap"}
    )
    with pytest.raises(UserError, match="resolution note"):
        _as(alert, m5.eng).action_resolve(note="ok")
    _as(alert, m5.eng).action_resolve(note="sensor flapping; threshold raised")
    assert alert.state == "resolved"


def test_p2_runbook_auto_resolve_needs_evidence_and_skips_tickets(m5):
    book = _as(m5.env["fix.msp.runbook"], m5.eng).create(
        {
            "name": "Clear temp",
            "script": "rm temp",
            "auto_resolve_alert": True,
            "scope_contract_id": m5.msp.id,
            "operating_unit_id": m5.ou.id,
        }
    )
    open_alert = m5.env["fix.msp.alert"].create(
        {"msp_contract_id": m5.msp.id, "asset_id": m5.asset.id, "message": "disk"}
    )
    with pytest.raises(UserError, match="record the evidence"):
        _as(book, m5.eng).action_execute_with_evidence(evidence="done")
    _as(book, m5.eng).action_execute_with_evidence(evidence="freed 12 GB; disk at 61%")
    assert open_alert.state == "resolved"
    assert "freed 12 GB" in open_alert.resolution_note
    ticketed = m5.env["fix.msp.alert"].create(
        {"msp_contract_id": m5.msp.id, "asset_id": m5.asset.id, "message": "disk again"}
    )
    _as(ticketed, m5.eng).action_to_ticket()
    _as(book, m5.eng).action_execute(alert_id=ticketed.id, evidence="freed 3 GB on the host")
    assert ticketed.state == "ticketed"  # its order decides


# ====================================================== P2 · on-call rota


def test_p2_on_call_overlap_is_a_constraint_and_live_shifts_are_locked(m5):
    now = fields.Datetime.now()
    Shift = _as(m5.env["fix.msp.oncall.shift"], m5.eng)
    live = Shift.create(
        {
            "name": "Live",
            "technician_id": m5.tech.id,
            "start_at": now - timedelta(hours=1),
            "end_at": now + timedelta(hours=4),
        }
    )
    live.action_activate()
    later = Shift.create(
        {
            "name": "Later",
            "technician_id": m5.tech.id,
            "start_at": now + timedelta(hours=5),
            "end_at": now + timedelta(hours=9),
        }
    )
    with (
        pytest.raises(ValidationError, match="overlaps the active primary shift Live"),
        m5.env.cr.savepoint(),
    ):
        later.write({"start_at": now + timedelta(hours=2)})
    with pytest.raises(UserError, match="cannot change on a shift that is active"):
        live.write({"end_at": now + timedelta(hours=12)})
    assert "end_at" in live._fix_form_locked_fields()
    later.write({"start_at": now + timedelta(hours=4, minutes=30)})  # no overlap: fine


def test_p2_on_call_activate_and_close_need_the_role(m5):
    now = fields.Datetime.now()
    shift = m5.env["fix.msp.oncall.shift"].create(
        {
            "name": "Rota",
            "technician_id": m5.tech.id,
            "start_at": now,
            "end_at": now + timedelta(hours=8),
        }
    )
    with pytest.raises(UserError, match="MSP Engineer"):
        _as(shift, m5.plain).action_activate()
    _as(shift, m5.eng2).action_activate()
    with pytest.raises(UserError, match="MSP Engineer"):
        _as(shift, m5.cab).action_close()
    _as(shift, m5.eng).action_close()
    assert shift.state == "closed"


# =================================================== P2 · SLA from response times


def test_p2_within_sla_is_measured_from_resolution_times(m5):
    t0 = datetime(2026, 6, 3, 9, 0)
    a = _alert(m5, t0, severity="major", state="resolved", resolved_in=3)  # within 4 h
    b = _alert(m5, t0, severity="major", state="resolved", resolved_in=5)  # late
    c = _alert(m5, t0, state="resolved")  # no resolution time: no evidence
    d = _alert(m5, t0)  # open past its target
    measure = m5.msp._msp_period_sla(a | b | c | d, as_of=datetime(2026, 7, 1))
    assert measure == {"within": 1, "breached": 3, "pending": 0, "attainment": 0.25}
    fresh = _alert(m5, datetime(2026, 6, 30, 23, 0))
    pending = m5.msp._msp_period_sla(fresh, as_of=datetime(2026, 7, 1, 0, 30))
    assert pending == {"within": 0, "breached": 0, "pending": 1, "attainment": 1.0}
    m5.msp.alert_resolve_hours_major = 6
    assert m5.msp._msp_period_sla(a | b, as_of=datetime(2026, 7, 1))["within"] == 2
    report = m5.msp.action_monthly_report(
        (datetime(2026, 6, 1), datetime(2026, 6, 30, 23, 59, 59), "2026-06")
    )
    assert report.alert_count == 5 and report.resolved_total_count == 3
    assert (report.resolved_count, report.pending_count) == (2, 0)
    with pytest.raises(UserError, match=GUARD):
        _as(report, m5.eng).write({"breached_count": 0})
