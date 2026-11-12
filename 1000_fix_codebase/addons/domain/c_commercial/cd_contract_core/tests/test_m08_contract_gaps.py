"""M08 contract gaps (13 Nov 2026): scope amendments that change the cover,
parties, exclusions, the obligation register and churn on a lost renewal.

Live ORM, rolled back per test, as non-admin users with the roles they would
really hold. Approvals go through the M63 inbox (approve_via_inbox).
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from odoo.addons.cd_contract_core.tests.test_a04_c2_c13_contracts import (  # noqa: F401
    MANAGER,
    REFUSED,
    _active,
    _contract,
    _device,
    _events,
    _user,
    c,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox


@pytest.fixture
def m(c):  # noqa: F811 - the imported fixture
    c.manager2 = _user(c.env, "m08gap_manager2", MANAGER)
    return c


def _scope(m, k, lines, effective=None, user=None):
    return (
        m.env["fix.contract.amendment"]
        .with_user(user or m.manager)
        .create(
            {
                "name": "scope %s" % len(lines),
                "contract_id": k.id,
                "kind": "scope",
                "effective_from": effective or m.today,
                "line_ids": [(0, 0, line) for line in lines],
            }
        )
    )


def _approve(m, a):
    a.with_user(m.manager).action_request_approval()
    approve_via_inbox(a, m.manager2, requester=m.manager)
    a.invalidate_recordset()
    return a


# =========================================================================== scope amendments
def test_attach_on_a_live_contract_covers_schedules_and_signals_proration(m):
    k = _active(m, devices=_device(m))
    new = _device(m)
    a = _approve(m, _scope(m, k, [{"action": "attach_asset", "device_id": new.id}]))
    assert a.state == "applied" and a.version_no == 1
    k.invalidate_recordset()
    assert new in k.covered_device_ids
    visits = m.env["fix.contract.pm.visit"].search(
        [("contract_id", "=", k.id), ("device_id", "=", new.id)]
    )
    assert visits and min(visits.mapped("scheduled_date")) > m.today
    events = _events(m.env, "contract.asset_attached", k.id)
    assert events and events[-1]["device_id"] == new.id and events[-1]["effective_date"]


def test_detach_ends_cover_and_skips_the_future_visits(m):
    dev = _device(m)
    k = _active(m, devices=dev)
    future = m.env["fix.contract.pm.visit"].search(
        [("contract_id", "=", k.id), ("device_id", "=", dev.id), ("scheduled_date", ">", m.today)]
    )
    assert future
    _approve(m, _scope(m, k, [{"action": "detach_asset", "device_id": dev.id}]))
    k.invalidate_recordset()
    assert dev not in k.covered_device_ids
    future.invalidate_recordset()
    assert set(future.mapped("state")) == {"skipped"}
    assert _events(m.env, "contract.asset_detached", k.id)


def test_entitlements_slas_and_exclusions_change_by_amendment(m):
    k = _active(
        m,
        devices=_device(m),
        entitlements=[{"entitlement_type": "incidents", "quantity_included": 4}],
    )
    ent = k.entitlement_ids
    sla = m.env["fix.sla.policy"].search([], limit=1)
    lines = [
        {"action": "adjust_entitlement", "entitlement_id": ent.id, "quantity": 10},
        {"action": "add_entitlement", "entitlement_type": "visits", "quantity": 2},
        {
            "action": "add_exclusion",
            "exclusion_type": "accidental_damage",
            "exclusion_text": "Liquid damage",
        },
    ]
    if sla:
        lines.append({"action": "add_sla", "sla_policy_id": sla.id})
    _approve(m, _scope(m, k, lines))
    k.invalidate_recordset()
    assert ent.quantity_included == 10
    assert "visits" in k.entitlement_ids.mapped("entitlement_type")
    assert k.exclusion_ids.mapped("name") == ["Liquid damage"]
    if sla:
        assert sla in k.sla_policy_ids


def test_a_scope_amendment_must_change_something_valid(m):
    covered = _device(m)
    k = _active(m, devices=covered)
    with pytest.raises(REFUSED, match="changes nothing"):
        _scope(m, k, []).with_user(m.manager).action_request_approval()
    with pytest.raises(REFUSED, match="already covered"):
        _scope(m, k, [{"action": "attach_asset", "device_id": covered.id}]).with_user(
            m.manager
        ).action_request_approval()
    stranger = _device(m, owner=m.other)
    with pytest.raises(REFUSED, match="not to the contract's customer"):
        _scope(m, k, [{"action": "attach_asset", "device_id": stranger.id}]).with_user(
            m.manager
        ).action_request_approval()


def test_lines_are_fixed_once_submitted(m):
    k = _active(m, devices=_device(m))
    a = _scope(m, k, [{"action": "attach_asset", "device_id": _device(m).id}])
    a.with_user(m.manager).action_request_approval()
    with pytest.raises(REFUSED, match="lines are fixed"):
        a.line_ids.with_user(m.manager).write({"device_id": _device(m).id})


def test_a_future_scope_amendment_applies_on_its_date(m):
    k = _active(m, devices=_device(m))
    new = _device(m)
    a = _approve(
        m,
        _scope(
            m, k, [{"action": "attach_asset", "device_id": new.id}], m.today + timedelta(days=5)
        ),
    )
    assert a.state == "approved" and new not in k.covered_device_ids
    a.sudo().write({"effective_from": m.today})  # the date arrives
    m.env["fix.contract.amendment"].cron_apply_due_amendments()
    a.invalidate_recordset()
    k.invalidate_recordset()
    assert a.state == "applied" and new in k.covered_device_ids


# =========================================================================== parties
def test_parties_are_recorded_and_signatories_freeze_once_signed(m):
    k = _contract(m)
    Party = m.env["fix.contract.party"].with_user(m.officer)
    sig = Party.create(
        {
            "contract_id": k.id,
            "partner_id": m.customer.id,
            "role": "customer_signatory",
            "designation": "Managing Director",
        }
    )
    with pytest.raises(REFUSED, match="postal address or an e-mail"):
        Party.create({"contract_id": k.id, "partner_id": m.other.id, "role": "notice"})
    live = _active(m)
    Party.create({"contract_id": live.id, "partner_id": m.other.id, "role": "authorised_requester"})
    with pytest.raises(REFUSED, match="signatories"):
        Party.create(
            {"contract_id": live.id, "partner_id": m.other.id, "role": "customer_signatory"}
        )
    assert sig.contract_id == k
    with pytest.raises(REFUSED):
        m.env["fix.contract.party"].with_user(m.clerk).create(
            {"contract_id": k.id, "partner_id": m.other.id, "role": "billing"}
        )


# =========================================================================== exclusions
def test_exclusions_are_terms_editable_only_in_draft(m):
    k = _contract(m)
    Ex = m.env["fix.contract.exclusion"].with_user(m.officer)
    Ex.create({"contract_id": k.id, "exclusion_type": "consumable", "name": "Toner"})
    live = _active(m)
    with pytest.raises(REFUSED, match="approved scope amendment"):
        Ex.create({"contract_id": live.id, "exclusion_type": "consumable", "name": "Toner"})


# =========================================================================== obligations
def _obligation(m, k, **kw):
    vals = {
        "name": "Annual calibration certificate",
        "contract_id": k.id,
        "obligation_type": "calibration",
        "due_date": m.today + timedelta(days=3),
        "owner_id": m.officer.id,
    }
    vals.update(kw)
    return m.env["fix.contract.obligation"].with_user(m.officer).create(vals)


def test_an_obligation_is_discharged_with_evidence_and_recurs(m):
    ob = _obligation(m, _active(m), recurrence="yearly")
    with pytest.raises(REFUSED, match="evidence"):
        ob.action_complete()
    ob.action_complete(evidence="Certificate CAL-2026-114")
    assert ob.state == "done" and ob.completed_by == m.officer
    nxt = ob.next_obligation_id
    assert nxt.state == "open" and nxt.due_date == ob.due_date.replace(year=ob.due_date.year + 1)
    with pytest.raises(REFUSED):
        ob.write({"due_date": m.today})


def test_the_cron_reminds_then_marks_overdue_once(m):
    k = _active(m)
    soon = _obligation(m, k)
    late = _obligation(
        m,
        k,
        name="Insurance renewal",
        obligation_type="insurance",
        due_date=m.today - timedelta(days=2),
    )
    Ob = m.env["fix.contract.obligation"]
    assert Ob.cron_obligations_due() >= 1
    assert soon.activity_ids and soon.state == "open"
    late.invalidate_recordset()
    assert late.state == "overdue"
    assert any(
        e["obligation_id"] == late.id for e in _events(m.env, "contract.obligation_overdue", k.id)
    )
    before = len(_events(m.env, "contract.obligation_overdue", k.id))
    Ob.cron_obligations_due()
    assert len(_events(m.env, "contract.obligation_overdue", k.id)) == before


def test_waiving_is_a_managers_call_and_never_for_a_mandatory_one(m):
    k = _active(m)
    ob = _obligation(m, k, obligation_type="report", name="Quarterly report")
    with pytest.raises(REFUSED):
        ob.with_user(m.officer).action_waive(reason="customer declined")
    ob.with_user(m.manager).action_waive(reason="customer declined in writing")
    assert ob.state == "waived"
    must = _obligation(m, k, mandatory=True)
    with pytest.raises(REFUSED, match="mandatory"):
        must.with_user(m.manager).action_waive(reason="no time")
    with pytest.raises(REFUSED):
        must.with_user(m.officer).write({"state": "done"})


# =========================================================================== churn
def _renewal(m, k):
    return (
        m.env["fix.contract.renewal"]
        .with_user(m.officer)
        .create(
            {
                "name": "Renewal %s" % k.code,
                "contract_id": k.id,
                "proposed_start": k.date_end + timedelta(days=1),
                "proposed_end": k.date_end + timedelta(days=366),
                "propo_value": 130000.0,
            }
        )
    )


def test_a_lost_renewal_records_why(m):
    k = _active(m)
    r = _renewal(m, k)
    with pytest.raises(REFUSED, match="churn reason"):
        r.action_mark_lost()
    with pytest.raises(REFUSED, match="competitor"):
        r.action_mark_lost(reason="competitor")
    r.action_mark_lost(
        reason="competitor",
        competitor="Rival Tech Ltd",
        winback=True,
        note="Lost on price per device",
    )
    assert (r.state, r.churn_reason, r.competitor, r.winback_eligible) == (
        "lost",
        "competitor",
        "Rival Tech Ltd",
        True,
    )
    assert _events(m.env, "contract.renewal_lost", k.id)[-1]["winback_eligible"] is True
    with pytest.raises(REFUSED):
        _renewal(m, k).write({"churn_reason": "price"})
