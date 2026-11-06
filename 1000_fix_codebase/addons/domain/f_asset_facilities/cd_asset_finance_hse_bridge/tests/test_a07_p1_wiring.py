"""A07 P1 wiring (builder H, 2026-11-04): the FF-48 events this bridge now consumes.

Live ORM, rolled back. Every event is delivered through its REGISTERED
subscription by the relay's own delivery step (`_deliver` hands over every
row of the type for the record, so each earlier row is redelivered too).
M45 losses, recoveries and transfers come from M45's own paths; the M47
lease events are published with their contract's payload on a real lease,
as the hand-off tests do.
"""

from __future__ import annotations

import json
from datetime import timedelta

from odoo.addons.cd_asset_finance_hse_bridge.tests import test_a07_p1_handoffs as _shared
from odoo.addons.cd_asset_finance_hse_bridge.tests.test_a07_p1_handoffs import (
    MOD,
    _as,
    _deliver,
    _refused,
    _site_lease,
)

from libs.py.fix_events import publish

# the shared fixture of the module's own tests (pytest finds it by this name)
c = _shared.c

WIRED = {
    "consumer_equipment_lost_risk": ("equipment.lost", "fix.risk.register"),
    "consumer_equipment_lost_m49": ("equipment.lost", "fix.asset.finance.request"),
    "consumer_equipment_recovered_risk": ("equipment.recovered", "fix.risk.register"),
    "consumer_equipment_recovered_m49": ("equipment.recovered", "fix.asset.finance.request"),
    "consumer_equipment_transferred": ("equipment.transferred", "fix.asset.transfer"),
    "consumer_lease_modified": ("lease.modified", "fix.lease"),
    "consumer_lease_renewal_decision_required": (
        "lease.renewal_decision_required",
        "fix.risk.register",
    ),
    "consumer_lease_critical_date_due": ("lease.critical_date_due", "fix.risk.register"),
    "consumer_site_compliance_expiring": ("site.compliance_expiring", "fix.risk.register"),
}


def test_every_wired_consumer_is_registered_and_callable(c):
    for xmlid, (event_type, model) in WIRED.items():
        sub = c.env.ref("%s.%s" % (MOD, xmlid))
        assert sub.active and sub.event_type == event_type and sub.model == model
        assert callable(getattr(c.env[model], sub.method, None)), sub.method


def test_extensions_are_pure_inherits_of_their_models(c):
    """FF-20/21: no redundant _name on the M49 link extensions (and no stray model)."""
    for model in ("fix.equipment", "fleet.vehicle", "fix.site.asset"):
        assert "fixed_asset_id" in c.env[model]._fields
    names = set(c.env["ir.model"].search([]).mapped("model"))
    assert not {"fix.equipment.m49", "fleet.vehicle.m49", "fix.site.asset.m49"} & names


# ------------------------------------------------------------ M45 loss
def _capitalised(c, code, cost=40000.0):
    eq = c.env["fix.equipment"].create(
        {
            "code": code,
            "name": "Bridge %s" % code,
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
            "acquisition_cost": cost,
        }
    )
    req = c.env["fix.asset.finance.request"].search(
        [("source_model", "=", "fix.equipment"), ("source_res_id", "=", eq.id)]
    )
    mine = _as(c, c.acct, "fix.asset.finance.request").browse(req.id)
    mine.write(
        {"category_id": c.category.id, "acquisition_line_id": _shared._cost_item(c, cost).id}
    )
    mine.action_accept()
    return eq


def _count(c, eq, found):
    return c.env["fix.equipment.verification"].create(
        {"equipment_id": eq.id, "campaign_ref": "A7W-COUNT", "found": found}
    )


def _lost_events(c, verification, event_type):
    for xmlid in ("consumer_%s_risk", "consumer_%s_m49"):
        name = event_type.split(".")[1]
        _deliver(c, xmlid % ("equipment_" + name), event_type, verification)


def test_a_lost_capitalised_item_raises_one_risk_and_a_write_off_withdrawn_on_recovery(c):
    eq = _capitalised(c, "A7W-EQ1")
    assert eq.fixed_asset_id
    miss = _count(c, eq, found=False)
    _lost_events(c, miss, "equipment.lost")
    _lost_events(c, miss, "equipment.lost")
    Risk, Req = c.env["fix.risk.register"], c.env["fix.asset.finance.request"]
    risk = Risk.search([("bridge_subject_key", "=", "m60:fix.equipment:%s" % eq.id)])
    assert len(risk) == 1 and risk.state == "open" and risk.category == "operational"
    assert risk.bridge_trigger_count == 1 and miss.name in risk.bridge_lapse_log
    req = Req.search([("key", "=", "m49:dispose:fix.equipment:%s" % eq.id)])
    assert len(req) == 1 and req.kind == "dispose" and req.state == "pending"
    assert (req.disposal_kind, req.event_type, req.source_amount) == (
        "write_off",
        "equipment.lost",
        40000.0,
    )
    assert req.fixed_asset_id == eq.fixed_asset_id
    # found at the next count: the request is withdrawn, the risk stays open
    found = _count(c, eq, found=True)
    _lost_events(c, found, "equipment.recovered")
    _lost_events(c, found, "equipment.recovered")
    assert req.state == "withdrawn" and found.name in req.decision_note
    assert risk.state == "open" and risk.bridge_lapse_log.count("[rec:%s]" % found.id) == 1
    assert risk.bridge_trigger_count == 1
    # a withdrawn request is not decided by finance
    _refused(_as(c, c.acct, "fix.asset.finance.request").browse(req.id).action_accept)
    # missing again: the same request returns to pending, the same entry counts it
    again = _count(c, eq, found=False)
    _lost_events(c, again, "equipment.lost")
    assert Req.search_count([("key", "=", req.key)]) == 1 and req.state == "pending"
    assert risk.bridge_trigger_count == 2


def test_a_lost_item_never_capitalised_raises_the_risk_only(c):
    eq = c.env["fix.equipment"].create(
        {"code": "A7W-EQ2", "name": "Bridge Probe", "company_id": c.co.id}
    )
    miss = _count(c, eq, found=False)
    _lost_events(c, miss, "equipment.lost")
    assert c.env["fix.risk.register"].search_count(
        [("bridge_subject_key", "=", "m60:fix.equipment:%s" % eq.id)]
    )
    assert not c.env["fix.asset.finance.request"].search_count(
        [("key", "=", "m49:dispose:fix.equipment:%s" % eq.id)]
    )


# ------------------------------------------------------------ M45 transfer
def _branch(c, code, ou):
    entity = c.env["fix.entity"].search([("company_id", "=", c.co.id)], limit=1) or c.env[
        "fix.entity"
    ].create({"code": "A7WE", "legal_name": "A07 wiring entity", "company_id": c.co.id})
    return c.env["fix.branch"].create(
        {
            "name": "A07 Wiring %s" % code,
            "code": code,
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )


def test_a_received_transfer_of_a_capitalised_item_raises_one_draft_m49_transfer(c):
    eq = _capitalised(c, "A7W-EQ3")
    asset = eq.fixed_asset_id
    asset.write({"state": "active"})  # as M49 Activate leaves it
    ou2 = c.env["operating.unit"].create(
        {
            "name": "A07W Bridge OU2",
            "code": "A7W2",
            "company_id": c.co.id,
            "partner_id": c.co.partner_id.id,
        }
    )
    # the accountant of both branches (the transfer is read in its target branch)
    c.acct.write({"assigned_operating_unit_ids": [(4, ou2.id)]})
    keeper = c.env["hr.employee"].create({"name": "A7W Keeper", "company_id": c.co.id})
    move = c.env["fix.equipment.transfer"].create(
        {
            "equipment_id": eq.id,
            "to_branch_id": _branch(c, "A7W2", ou2).id,
            "to_custodian_id": keeper.id,
        }
    )
    move.action_dispatch()
    move.action_receive()
    _deliver(c, "consumer_equipment_transferred", "equipment.transferred", move)
    _deliver(c, "consumer_equipment_transferred", "equipment.transferred", move)
    Transfer = c.env["fix.asset.transfer"]
    draft = Transfer.search([("equipment_transfer_id", "=", move.id)])
    assert len(draft) == 1 and draft.state == "draft" and draft.asset_id == asset
    assert (draft.operating_unit_id, draft.to_custodian_id) == (ou2, keeper)
    assert asset.operating_unit_id == c.ou  # nothing moved until finance confirms
    _refused(
        _as(c, c.acct, "fix.asset.transfer").browse(draft.id).write,
        {"equipment_transfer_id": False},
    )
    _as(c, c.acct, "fix.asset.transfer").browse(draft.id).action_confirm()
    # A08 M49-12: the asset moves only when the receiver acknowledges (here the keeper
    # has no login, so finance does, as someone other than the sender)
    assert draft.state == "confirmed" and asset.operating_unit_id == c.ou
    other = _shared._user(c.env, "a07p1_brg_acct2", c.co, ou2, _shared.ACCOUNTANT)
    other.write({"assigned_operating_unit_ids": [(4, c.ou.id), (4, ou2.id)]})
    c.env["fix.asset.transfer"].with_user(other).browse(draft.id).action_acknowledge()
    assert draft.state == "done" and asset.operating_unit_id == ou2 and asset.custodian_id == keeper


# ------------------------------------------------------------ M47 lease
def _modify(c, ls, rent):
    before = {
        "end_date": str(ls.end_date),
        "monthly_rent": ls.monthly_rent,
        "escalation_pct": ls.escalation_pct,
    }
    ls.sudo()._guarded().write({"monthly_rent": rent})
    after = {
        "end_date": str(ls.end_date),
        "monthly_rent": rent,
        "escalation_pct": ls.escalation_pct,
    }
    publish(
        c.env,
        "lease.modified",
        "fix.site.lease",
        ls.id,
        {
            "lease": ls.name,
            "site": ls.site_id.name,
            "reason": "rent review",
            "before": before,
            "after": after,
        },
    )
    ls.sudo()._lease_publish_extract("modified")


def test_lease_modified_updates_the_draft_then_raises_one_modification_item(c):
    ls = _site_lease(c)
    _deliver(c, "consumer_lease_extract_published", "lease.extract_published", ls)
    lease = c.env["fix.lease"].search([("site_lease_id", "=", ls.id)])
    assert lease.state == "draft" and lease.site_extract_version == 1
    _modify(c, ls, 130000.0)
    _deliver(c, "consumer_lease_modified", "lease.modified", ls)
    assert lease.payment_amount == 130000.0 and lease.site_extract_version == 2
    _deliver(c, "consumer_lease_extract_published", "lease.extract_published", ls)
    assert not lease.modification_item_ids
    lease.sudo().write({"state": "active"})  # commenced
    _modify(c, ls, 150000.0)
    _deliver(c, "consumer_lease_modified", "lease.modified", ls)
    _deliver(c, "consumer_lease_extract_published", "lease.extract_published", ls)
    _deliver(c, "consumer_lease_modified", "lease.modified", ls)
    assert lease.payment_amount == 130000.0  # the book is finance's
    item = lease.modification_item_ids
    assert len(item) == 1 and item.version == 3 and "150000" in item.changes
    assert json.loads(item.extract)["monthly_rent"] == 150000.0


def test_lease_modified_without_its_extract_waits_as_an_exception(c):
    ls = _site_lease(c)
    publish(
        c.env,
        "lease.modified",
        "fix.site.lease",
        ls.id,
        {
            "lease": ls.name,
            "site": ls.site_id.name,
            "reason": "unpublished",
            "before": {},
            "after": {"end_date": "2031-01-01", "monthly_rent": 1.0, "escalation_pct": 0.0},
        },
    )
    _deliver(c, "consumer_lease_modified", "lease.modified", ls)
    exc = c.env["fix.bridge.exception"].search([("key", "=", "m49_lease:%s" % ls.id)])
    assert exc.state == "open" and "no published extract" in exc.message
    assert not c.env["fix.lease.modification.item"].search_count([("site_lease_id", "=", ls.id)])


def test_lease_continuity_alerts_share_one_open_risk_per_lease(c):
    ls = _site_lease(c)
    base = {"lease": ls.name, "site": ls.site_id.name, "responsible_role": "CFO"}
    deadline = str(c.today + timedelta(days=20))
    for days in (20, 19):
        publish(
            c.env,
            "lease.renewal_decision_required",
            "fix.site.lease",
            ls.id,
            dict(base, deadline=deadline, days_left=days),
        )
    publish(
        c.env,
        "lease.critical_date_due",
        "fix.site.lease",
        ls.id,
        dict(base, event_type="expiry", due_on=str(ls.end_date), days_left=90),
    )
    for _ in range(2):
        _deliver(
            c,
            "consumer_lease_renewal_decision_required",
            "lease.renewal_decision_required",
            ls,
        )
        _deliver(c, "consumer_lease_critical_date_due", "lease.critical_date_due", ls)
    risk = c.env["fix.risk.register"].search(
        [("bridge_subject_key", "=", "m60:fix.site.lease:%s" % ls.id)]
    )
    assert len(risk) == 1 and risk.state == "open" and risk.category == "operational"
    assert risk.bridge_trigger_count == 3 and risk.company_id == c.co
    assert "19 day(s) left" in risk.bridge_lapse_log and "expiry due" in risk.bridge_lapse_log


# ------------------------------------------------------------ M47 licence warning
def _licence(c, site, name):
    return (
        c.env["fix.site.licence"]
        .sudo()
        .create(
            {
                "site_id": site.id,
                "name": name,
                "licence_type": "trade",
                "valid_to": c.today + timedelta(days=30),
            }
        )
    )


def _expiring(c, licence, days):
    publish(
        c.env,
        "site.compliance_expiring",
        "fix.site.licence",
        licence.id,
        {
            "site": licence.site_id.name,
            "site_id": licence.site_id.id,
            "licence": licence.name,
            "licence_type": "trade",
            "expiry": str(licence.valid_to),
            "days_remaining": days,
        },
    )


def test_an_expiring_licence_opens_a_low_risk_or_logs_on_the_open_one(c):
    Risk = c.env["fix.risk.register"]
    key = "m60:fix.site:%s" % c.site.id
    licence = _licence(c, c.site, "A7W Trade Licence")
    _expiring(c, licence, 30)
    _deliver(c, "consumer_site_compliance_expiring", "site.compliance_expiring", licence)
    risk = Risk.search([("bridge_subject_key", "=", key)])
    assert len(risk) == 1 and (risk.likelihood, risk.impact, risk.risk_score) == ("2", "2", 4)
    _expiring(c, licence, 7)
    _deliver(c, "consumer_site_compliance_expiring", "site.compliance_expiring", licence)
    assert Risk.search_count([("bridge_subject_key", "=", key)]) == 1
    assert risk.bridge_trigger_count == 1 and "7 day(s) left" in risk.bridge_lapse_log
    assert risk.bridge_lapse_log.count("[exp:") == 2
    # a site with an open entry already: the warning is logged, the scoring kept
    site2 = c.env["fix.site"].create(
        {
            "name": "A07W Second Branch",
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
            "state": "active",
        }
    )
    other = _licence(c, site2, "A7W Fire Licence")
    publish(
        c.env,
        "site.compliance_expired",
        "fix.site.licence",
        other.id,
        {
            "site": site2.name,
            "site_id": site2.id,
            "licence": other.name,
            "licence_type": "fire",
            "expiry": "2026-10-01",
        },
    )
    _deliver(c, "consumer_site_compliance_expired", "site.compliance_expired", other)
    _expiring(c, other, 15)
    _deliver(c, "consumer_site_compliance_expiring", "site.compliance_expiring", other)
    risk2 = Risk.search([("bridge_subject_key", "=", "m60:fix.site:%s" % site2.id)])
    assert len(risk2) == 1 and risk2.risk_score == 9 and risk2.bridge_trigger_count == 1
    assert "15 day(s) left" in risk2.bridge_lapse_log


def test_payload_keys_read_by_the_wiring_are_in_the_contracts(c):
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[5] / "contracts" / "events"
    reads = {
        "equipment.lost": {"campaign", "custodian", "value"},
        "equipment.recovered": {"missing_since"},
        "lease.modified": {"after", "reason"},
        "lease.renewal_decision_required": {"deadline", "days_left", "responsible_role"},
        "lease.critical_date_due": {"event_type", "due_on", "days_left"},
        "site.compliance_expiring": {"licence", "licence_type", "expiry", "days_remaining"},
    }
    for event_type, keys in reads.items():
        contract = json.loads((root / (event_type.replace(".", "_") + ".json")).read_text())
        declared = set(contract["properties"]["payload"]["properties"])
        assert keys <= declared, (event_type, keys - declared)
