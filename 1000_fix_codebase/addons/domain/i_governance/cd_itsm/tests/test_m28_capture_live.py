"""M28 capture audit (2026-11-14): the two decision captures the sub-module pages
now offer, driven through /p03/model/form and /p03/model/action as NON-ADMIN
users with the kwargs m28.js sends. The superuser is trusted by the model
guards and would hide a gap.

  * Offline Sync - "Decide a Sync Conflict" (M28-form-conflict-resolve):
    action_resolve_decision runs the row buttons' _resolve, so the
    Integration Admin group, BRU-IPF-17 and the note rules still decide.
  * Reconciliation - "Record a Reconciliation Investigation"
    (M28-form-recon-investigation): action_resolve on an open divergence.
  * Gateway - "+ New API Rate Limit": a quota is saved from the workspace
    form within the ceiling.
"""

from __future__ import annotations

import types

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
IADMIN = "cd_itsm.group_integration_admin"


def _user(env, login, groups=()):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": login, "login": login, "group_ids": [(6, 0, gids)]})
    )
    env["hr.employee"].create({"name": login, "user_id": user.id})
    return user


@pytest.fixture
def c(odoo_env):
    x = types.SimpleNamespace(env=odoo_env)
    x.plain = _user(odoo_env, "m28cap_plain")
    x.admin = _user(odoo_env, "m28cap_admin", [IADMIN])
    return x


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()
    C = g.P03GenericApiController
    saved = g.request

    def _o(fn):
        return getattr(fn, "original_endpoint", fn)

    def as_user(user):
        g.request = types.SimpleNamespace(env=c.env(user=user.id))

    try:
        yield types.SimpleNamespace(
            write=lambda **k: _o(C.model_write)(ctl, **k),
            action=lambda **k: _o(C.model_action)(ctl, **k),
            form=lambda **k: _o(C.model_form)(ctl, **k),
            as_user=as_user,
        )
    finally:
        g.request = saved


def _audits(c, event):
    return c.env["fix.security.audit"].sudo().search_count([("event", "=", event)])


def _conflict(c, **kw):
    partner = c.env["res.partner"].sudo().create({"name": "M28 cap", "phone": "+880-server"})
    vals = {
        "device_ref": "DEV-CAP",
        "res_model": "res.partner",
        "res_id": partner.id,
        "field_name": "phone",
        "local_value": "+880-device",
        "remote_value": "+880-server",
    }
    vals.update(kw)
    return c.env["fix.sync.conflict"].sudo().create(vals), partner


def _decide(p03, conflict, decision, note=None):
    kwargs = {"decision": decision}
    if note:
        kwargs["note"] = note
    return p03.action(
        model="fix.sync.conflict",
        ids=[conflict.id],
        method="action_resolve_decision",
        kwargs=kwargs,
    )


# ------------------------------------------------------------ Offline Sync
def test_decision_form_opens_on_a_pending_conflict_with_the_decision_choices(c, p03):
    conflict, _partner = _conflict(c)
    p03.as_user(c.admin)
    out = p03.form(
        model="fix.sync.conflict",
        record_id=conflict.id,
        fields=[
            {"name": "device_ref", "readonly": True},
            {"name": "policy_class", "readonly": True},
            {
                "name": "resolution",
                "type": "selection",
                "choices": [["local_wins", "Local Wins"], ["remote_wins", "Remote Wins"]],
            },
            {"name": "resolution_note"},
        ],
    )
    assert not out.get("error"), out
    by_name = {f["name"]: f for f in out["fields"]}
    assert [c_["key"] for c_ in by_name["resolution"]["choices"]] == ["local_wins", "remote_wins"]
    assert out["record"]["policy_class"] == "client"


def test_admin_decides_a_client_field_conflict_from_the_page(c, p03):
    conflict, partner = _conflict(c)
    before = _audits(c, "integration.sync_conflict_resolved")
    p03.as_user(c.admin)
    out = _decide(p03, conflict, "local_wins")
    assert out.get("success"), out
    partner.invalidate_recordset()
    assert partner.phone == "+880-device"
    assert conflict.resolution == "local_wins"
    assert conflict.resolved_by_id == c.admin
    assert _audits(c, "integration.sync_conflict_resolved") == before + 1


def test_pending_is_not_a_decision(c, p03):
    conflict, _partner = _conflict(c)
    p03.as_user(c.admin)
    out = _decide(p03, conflict, "pending")
    assert not out.get("success")
    assert "Choose the decision" in out.get("error", "")
    assert conflict.resolution == "pending"


def test_a_server_field_keeps_the_server_value(c, p03):
    partner = c.env["res.partner"].sudo().create({"name": "M28 cap", "ref": "server-ref"})
    conflict, _p = _conflict(
        c, res_id=partner.id, field_name="ref", local_value="device", remote_value="server"
    )
    assert conflict.policy_class == "server"
    p03.as_user(c.admin)
    refused = _decide(p03, conflict, "local_wins")
    assert not refused.get("success") and "server-authoritative" in refused.get("error", "")
    out = _decide(p03, conflict, "remote_wins")
    assert out.get("success"), out
    partner.invalidate_recordset()
    assert partner.ref == "server-ref"


def test_merge_and_close_need_a_note(c, p03):
    conflict, partner = _conflict(c)
    p03.as_user(c.admin)
    assert not _decide(p03, conflict, "merged").get("success")
    out = _decide(p03, conflict, "merged", note="agreed with the technician by phone")
    assert out.get("success"), out
    assert conflict.resolution_note == "agreed with the technician by phone"
    partner.invalidate_recordset()
    assert partner.phone == "+880-server", "a manual merge applies nothing"


def test_only_an_integration_admin_decides(c, p03):
    conflict, _partner = _conflict(c)
    p03.as_user(c.plain)
    out = _decide(p03, conflict, "remote_wins")
    assert not out.get("success")
    assert conflict.resolution == "pending"


def test_the_generic_write_still_cannot_set_a_decision(c, p03):
    conflict, _partner = _conflict(c)
    p03.as_user(c.admin)
    out = p03.write(
        model="fix.sync.conflict",
        record_id=conflict.id,
        values={"resolution": "local_wins", "resolution_note": "typed"},
    )
    assert out.get("error"), out
    conflict.invalidate_recordset()
    assert conflict.resolution == "pending" and not conflict.resolution_note


# ---------------------------------------------------------- Reconciliation
def _divergent(c, **kw):
    vals = {
        "company_id": c.env.company.id,
        "check_code": "relay_lag",
        "records_compared": 40,
        "divergences_found": 3,
        "state": "divergent",
    }
    vals.update(kw)
    return c.env["fix.integration.reconciliation.run"].sudo().create(vals)


def test_admin_records_an_investigation_from_the_page(c, p03):
    run = _divergent(c)
    before = _audits(c, "integration.reconciliation_resolved")
    p03.as_user(c.admin)
    out = p03.action(
        model="fix.integration.reconciliation.run",
        ids=[run.id],
        method="action_resolve",
        kwargs={"note": "Relay worker was stopped; restarted and the backlog drained."},
    )
    assert out.get("success"), out
    assert run.resolved_by_id == c.admin and run.resolved_at
    assert run.state == "divergent", "an investigation records, it does not absorb"
    assert _audits(c, "integration.reconciliation_resolved") == before + 1


def test_an_investigation_needs_its_note_and_an_open_divergence(c, p03):
    run = _divergent(c)
    clean = _divergent(c, state="clean", divergences_found=0)
    p03.as_user(c.admin)
    no_note = p03.action(
        model="fix.integration.reconciliation.run",
        ids=[run.id],
        method="action_resolve",
        kwargs={},
    )
    assert not no_note.get("success")
    on_clean = p03.action(
        model="fix.integration.reconciliation.run",
        ids=[clean.id],
        method="action_resolve",
        kwargs={"note": "nothing to see"},
    )
    assert not on_clean.get("success")


def test_a_plain_user_cannot_record_an_investigation(c, p03):
    run = _divergent(c)
    p03.as_user(c.plain)
    out = p03.action(
        model="fix.integration.reconciliation.run",
        ids=[run.id],
        method="action_resolve",
        kwargs={"note": "I looked at it"},
    )
    assert not out.get("success")
    assert not run.resolved_at


# ---------------------------------------------------------------- Gateway
def test_gateway_page_saves_a_rate_limit(c, p03):
    consumer = c.env["fix.api.consumer"].sudo().create({"name": "M28 cap consumer"})
    p03.as_user(c.admin)
    out = p03.write(
        model="fix.api.quota",
        values={"consumer_id": consumer.id, "requests_per_min": 30, "daily_quota": 5000},
    )
    assert out.get("id") and not out.get("error"), out
    quota = c.env["fix.api.quota"].sudo().search([("consumer_id", "=", consumer.id)])
    assert quota.requests_per_min == 30 and quota.state == "active"
