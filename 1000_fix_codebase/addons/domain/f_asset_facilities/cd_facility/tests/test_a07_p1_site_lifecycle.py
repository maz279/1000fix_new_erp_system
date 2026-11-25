"""A07 P1/P2 (M47): the site lifecycle beyond P0 - readiness gate, licence
lapse -> operating-risk exception -> named continue-or-suspend decision ->
resumption, the fire -> trade licence dependency, and the closure project.

Live ORM, rolled back. Every attack runs as a NON-ADMIN user created in the
transaction with the role they would really hold. The records live in a
company of their own, so the approval engine routes only to users made here.
"""

from __future__ import annotations

import base64
import json
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
FM = "cd_facility.group_facility_manager"
BOL = "cd_facility.group_branch_operations_lead"
OPSDIR = "cd_facility.group_operations_director"
TIER = "cd_entity_config.group_dofa_tier_%d"
SCAN = base64.b64encode(b"%PDF-1.4 licence scan").decode()


def _user(env, login, company, ou, *groups):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, ids)],
                "company_ids": [(6, 0, company.ids)],
                "company_id": company.id,
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["fix.site"])
    x.co = env["res.company"].create({"name": "A07P1 M47 Site Co"})
    x.ou = env["operating.unit"].create(
        {
            "name": "A07P1 M47S OU",
            "code": "A7P1M47S",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.clerk = _user(env, "a07p1_m47s_clerk", x.co, x.ou)
    x.fm = _user(env, "a07p1_m47s_fm", x.co, x.ou, FM)
    x.bol = _user(env, "a07p1_m47s_bol", x.co, x.ou, BOL)
    x.od = _user(env, "a07p1_m47s_od", x.co, x.ou, OPSDIR)
    x.od2 = _user(env, "a07p1_m47s_od2", x.co, x.ou, OPSDIR)
    x.t4 = _user(env, "a07p1_m47s_t4", x.co, x.ou, TIER % 4)
    x.t5 = _user(env, "a07p1_m47s_t5", x.co, x.ou, TIER % 5)
    x.landlord = env["res.partner"].create({"name": "A07P1S Landlord"})
    return x


def _events(c, event_type, res_id):
    rows = c.env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", res_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


def _refused(fn, *args, match=None, **kw):
    with pytest.raises(REFUSED, match=match), fn.__self__.env.cr.savepoint():
        fn(*args, **kw)


def _make_ready(c, site):
    """Everything the readiness gate reads, recorded by the Facility Manager."""
    lease = (
        c.env["fix.site.lease"]
        .with_user(c.fm)
        .create(
            {
                "site_id": site.id,
                "lessor_id": c.landlord.id,
                "start_date": c.today,
                "end_date": c.today + timedelta(days=3 * 365),
                "monthly_rent": 80000.0,
            }
        )
    )
    # D6 (A07 ERP audit 2026-11-20): recorded once its commitment is approved
    lease.sudo()._guarded().write({"state": "active"})
    for ltype in ("trade", "fire"):
        c.env["fix.site.licence"].with_user(c.fm).create(
            {
                "site_id": site.id,
                "licence_type": ltype,
                "number": "%s-1" % ltype.upper(),
                "evidence_file": SCAN,
                "valid_to": c.today + timedelta(days=300),
            }
        )
    c.env["fix.site.safety"].with_user(c.fm).create(
        {"site_id": site.id, "next_check": c.today + timedelta(days=200)}
    )
    site.with_user(c.fm).write(
        {
            "accountable_manager_id": c.fm.id,
            "ready_power": True,
            "ready_connectivity": True,
            "ready_security": True,
            "ready_equipment": True,
            "ready_signage": True,
            "readiness_notes": "DESCO meter 44-1; BTCL link; guard contract G-7",
        }
    )


def _new_site(c, user=None):
    return (
        c.env["fix.site"]
        # A07 ERP audit (2026-11-20) M47-18: a Facility Manager registers a site
        .with_user(user or c.fm)
        .create({"name": "A07P1S New Branch", "company_id": c.co.id, "operating_unit_id": c.ou.id})
    )


# ------------------------------------------------------------ readiness gate
def test_new_site_is_planned_and_cannot_be_forged_operational(c, monkeypatch):
    site = _new_site(c)
    assert site.state == "planned"
    with pytest.raises(UserError, match="cannot be set directly"), c.env.cr.savepoint():
        c.env["fix.site"].with_user(c.fm).create(
            {"name": "A07P1S Born Active", "company_id": c.co.id, "state": "active"}
        )
    _refused(site.with_user(c.fm).write, {"state": "active"}, match="cannot be set directly")
    _refused(site.with_user(c.fm).action_open, match="readiness gate")
    # only a Branch Operations Lead requests the gate
    _refused(site.with_user(c.fm).action_request_approval, match="Branch Operations Lead")
    # with nothing set up, the request lists every outstanding item
    with pytest.raises(UserError) as err, c.env.cr.savepoint():
        site.with_user(c.bol).action_request_approval(justification="open")
    for item in (
        "accountable manager",
        "active lease",
        "trade licence",
        "fire",
        "safety equipment",
        "power connected",
        "signage",
    ):
        assert item in str(err.value).lower(), item


def test_readiness_gate_is_signed_by_the_operations_director_not_the_requester(c):
    site = _new_site(c)
    _make_ready(c, site)
    assert site._site_readiness_items() == []
    S = site.with_user(c.bol)
    S.action_request_approval(justification="All readiness items in place")
    assert set(assigned(site)) == {c.od, c.od2}
    _refused(site.with_user(c.od).action_approve_status_change, match="inbox")
    approve_via_inbox(site, c.od, requester=c.bol)
    assert site.status_opsdir_approved_by_id == c.od
    S.action_open()
    assert site.state == "active" and site.opened_on == c.today
    assert not site.status_opsdir_approved_by_id and site.approval_state == "none"
    gate = _events(c, "site.readiness_gate_passed", site.id)
    assert gate and gate[0]["signatory"] == c.od.name
    changed = _events(c, "site.status_changed", site.id)
    assert changed[-1]["from_status"] == "planned" and changed[-1]["to_status"] == "active"


def test_an_operations_director_who_requested_is_never_routed_it(c):
    site = _new_site(c)
    _make_ready(c, site)
    site.with_user(c.od).action_request_approval(justification="mine")
    assert c.od not in assigned(site) and assigned(site) == c.od2


def test_readiness_sign_off_is_pinned_to_the_checklist(c):
    site = _new_site(c)
    _make_ready(c, site)
    approve_via_inbox(site, c.od, requester=c.bol, justification="ready")
    assert site.status_opsdir_approved_by_id
    site.with_user(c.fm).write({"ready_signage": False})
    assert not site.status_opsdir_approved_by_id and site.approval_state == "none"
    _refused(site.with_user(c.bol).action_open, match="readiness gate")


def test_reopened_site_returns_to_planned(c):
    site = c.env["fix.site"].create(
        {"name": "A07P1S Closing", "company_id": c.co.id, "state": "active"}
    )
    approve_via_inbox(site, c.t4, requester=c.fm, justification="consolidation")
    approve_via_inbox(site, c.t5, requester=c.fm, justification="consolidation")
    site.with_user(c.fm).action_close()
    assert site.state == "closed"
    approve_via_inbox(site, c.t4, requester=c.fm, justification="re-let")
    approve_via_inbox(site, c.t5, requester=c.fm, justification="re-let")
    site.with_user(c.fm).action_reopen()
    assert site.state == "planned" and not site.opened_on
    assert [e["to_status"] for e in _events(c, "site.status_changed", site.id)] == [
        "closed",
        "planned",
    ]


# ------------------------------------------------- licence lapse and decision
def _operational_site_with_lapse(c):
    site = c.env["fix.site"].create(
        {
            "name": "A07P1S Lapse Branch",
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
            "state": "active",
            "accountable_manager_id": c.fm.id,
        }
    )
    licence = (
        c.env["fix.site.licence"]
        .with_user(c.bol)
        .create(
            {
                "site_id": site.id,
                "licence_type": "trade",
                "number": "TL-9",
                "evidence_file": SCAN,
                "valid_to": c.today - timedelta(days=2),
            }
        )
    )
    exc = c.env["fix.site.risk.exception"].search([("licence_id", "=", licence.id)])
    return site, licence, exc


def test_a_lapsed_licence_raises_an_exception_that_needs_a_named_decision(c):
    site, licence, exc = _operational_site_with_lapse(c)
    assert len(exc) == 1 and exc.state == "open" and exc.severity == "critical"
    assert _events(c, "site.risk_exception_raised", exc.id)[0]["licence_type"] == "trade"
    # nobody forges or deletes it
    _refused(exc.with_user(c.od).write, {"state": "continue"}, match="cannot be set directly")
    _refused(exc.with_user(c.bol).unlink)
    # the decision is the Operations Director's or the CEO's
    exc.with_user(c.bol).write({"decision_notes": "Renewal filed; chalan paid 2 Nov"})
    _refused(exc.with_user(c.fm).action_decide_suspend, match="Operations Director")
    # SoD: the person responsible for the renewal (its recorder, the
    # accountable manager) is not the decider
    licence_owner = c.env["res.users"].browse(licence.create_uid.id)
    licence_owner.group_ids = [(4, c.env.ref(OPSDIR).id)]
    _refused(exc.with_user(licence_owner).action_decide_suspend, match="Segregation")
    # a continue decision is dated, after today
    _refused(exc.with_user(c.od).action_decide_continue, match="dated")
    _refused(exc.with_user(c.od).action_decide_continue, review_due_on=str(c.today), match="dated")
    exc.with_user(c.od).action_decide_continue(review_due_on=str(c.today + timedelta(days=14)))
    assert (exc.state, exc.decided_by_id) == ("continue", c.od)
    assert _events(c, "site.risk_decision_recorded", exc.id)[0]["decision"] == "continue"
    _refused(exc.with_user(c.bol).write, {"decision_notes": "edited"}, match="basis")
    assert site.state == "active"  # BRU-FAC-02: no automatic suspension


def test_a_continue_decision_lapses_on_its_review_date(c, monkeypatch):
    _site, _licence, exc = _operational_site_with_lapse(c)
    exc.with_user(c.od).action_decide_continue(
        review_due_on=str(c.today + timedelta(days=3)), notes="Interim fire watch"
    )
    later = c.today + timedelta(days=4)
    monkeypatch.setattr(fields.Date, "context_today", staticmethod(lambda *a, **k: later))
    c.env["fix.site.licence"].sudo().cron_licence_expiry()
    assert exc.state == "open" and not exc.decision_notes


def test_suspend_then_resume_after_the_renewal(c):
    site, _licence, exc = _operational_site_with_lapse(c)
    exc.with_user(c.t5).action_decide_suspend(notes="Unlawful to trade; close the counter")
    assert site.state == "suspended" and exc.state == "suspend"
    assert _events(c, "site.status_changed", site.id)[-1]["to_status"] == "suspended"
    # it cannot resume while the lapse is unresolved
    _refused(site.with_user(c.bol).action_request_approval, match="unresolved")
    _refused(site.with_user(c.bol).action_resume, match="unresolved")
    # the renewal resolves the exception
    c.env["fix.site.licence"].with_user(c.fm).create(
        {
            "site_id": site.id,
            "licence_type": "trade",
            "number": "TL-10",
            "evidence_file": SCAN,
            "valid_to": c.today + timedelta(days=365),
        }
    )
    assert exc.state == "resolved" and exc.resolution.startswith("renewed by")
    _refused(site.with_user(c.bol).action_resume, match="Operations Director")
    approve_via_inbox(site, c.od, requester=c.bol, justification="Licence renewed")
    site.with_user(c.bol).action_resume()
    assert site.state == "active" and not site.suspended_reason


# ----------------------------------------------------- fire -> trade (BRU-FAC-03)
def test_trade_renewal_is_refused_while_the_fire_licence_is_expired(c):
    site = c.env["fix.site"].create(
        {"name": "A07P1S Fire Site", "company_id": c.co.id, "state": "active"}
    )
    c.env["fix.site.licence"].create(
        {
            "site_id": site.id,
            "licence_type": "fire",
            "state": "expired",
            "valid_to": c.today - timedelta(days=20),
        }
    )
    Lic = c.env["fix.site.licence"].with_user(c.fm)
    current = {
        "site_id": site.id,
        "number": "N-1",
        "evidence_file": SCAN,
        "valid_to": c.today + timedelta(days=365),
    }
    with pytest.raises(UserError, match="fire licence"), c.env.cr.savepoint():
        Lic.create(dict(current, licence_type="trade"))
    # a current fire licence first, then the trade renewal is accepted
    Lic.create(dict(current, licence_type="fire"))
    trade = Lic.create(dict(current, licence_type="trade"))
    assert trade.is_valid


# ------------------------------------------------------------ closure project
def test_closure_project_completes_only_after_the_site_closed(c):
    site = c.env["fix.site"].create(
        {"name": "A07P1S Closure", "company_id": c.co.id, "state": "active"}
    )
    project = (
        c.env["fix.site.project"]
        .with_user(c.fm)
        .create({"site_id": site.id, "project_type": "close"})
    )
    project.action_start()
    _refused(project.action_done, match="has closed")
    approve_via_inbox(site, c.t4, requester=c.fm, justification="lease ended")
    approve_via_inbox(site, c.t5, requester=c.fm, justification="lease ended")
    site.with_user(c.fm).action_close()
    project.action_done()
    assert project.state == "done"
