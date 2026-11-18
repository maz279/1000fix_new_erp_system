# M08 Contract Lifecycle (AMC): capture audit, second pass (18 Nov 2026).
#
# The user again saw M08 sub-module pages without a relevant capture. After
# the 13 Nov pass every page had a "+ New", but against the M08 spec several
# captured the wrong record and what the spec asks a person to enter had no
# model at all:
#   6  PM Schedules        "+ PM Schedule" made ONE ad-hoc visit; the visit
#                          frequency was a constant per family
#   3  Coverage Scope      no cover by asset type / brand / site; an AMC
#                          contract activated covering nothing (BRU-CTR-01)
#   4  Entitlement Engine  no top-up of a live contract, no movement ledger,
#                          a cancelled order never gave its entitlement back
#   5  SLA & Credits       no service credit scheme (FR-CTR-028)
#   9  Churn & Win-Back    no dispute / legal hold (BRU-CTR-12); resume with
#                          no declared treatment of the suspended period
#   11 Documents & Sign.   only an e-signature envelope activated a contract:
#                          a contract signed in ink could never go live
#   1  Creation            no named owner (BRU-CTR-19), no master agreement
# Every save below runs through the workspace endpoints, as non-admin users
# holding only the M08 roles.
from __future__ import annotations

import base64
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta
from odoo.addons.cd_contract_core.tests.test_a04_c2_c13_contracts import (  # noqa: F401
    MANAGER,
    _active,
    _amc_order,
    _approve_value,
    _contract,
    _device,
    _events,
    _user,
    c,
    p03,
)
from odoo.addons.cd_p03_portal.controllers.a04 import m08 as m08_surfaces
from odoo.addons.cd_p03_portal.controllers.a04.writable import WRITABLE
from odoo.addons.cd_p03_portal.tests.test_m08_submodule_capture import reg  # noqa: F401
from odoo.exceptions import UserError, ValidationError

PASS2 = {
    "3": ("M08-form-coverage", {"Coverage Rule"}),
    "4": ("M08-form-topup", {"Entitlement Top-Up", "Entitlement"}),
    "5": ("M08-form-creditscheme", {"Service Credit Scheme", "SLA Credit"}),
    "6": ("M08-form-pmplan", {"PM Schedule", "PM Visit"}),
    "9": ("M08-form-termination", {"Contract Dispute", "Reinstatement", "Lost Renewal"}),
    "11": ("M08-form-signature", {"Wet-Ink Signature Verification"}),
}
NEW_MODELS = (
    "fix.contract.pm.plan",
    "fix.contract.coverage.rule",
    "fix.contract.entitlement.movement",
    "fix.contract.entitlement.topup",
    "fix.contract.credit.scheme",
    "fix.contract.dispute",
)


# --- the pages ------------------------------------------------------------------
@pytest.mark.parametrize("no", sorted(PASS2, key=int))
def test_each_page_offers_the_record_the_spec_names(reg, no):  # noqa: F811 - the imported fixture
    sub = next(s for s in reg["subs"] if s["no"] == no)
    screen, chips = PASS2[no]
    assert sub["create"] and sub["create"]["screen"] == screen, sub["create"]
    assert chips <= set(sub["map"]["forms"]), sub["map"]["forms"]


def test_the_pm_schedule_chip_is_the_plan_not_one_visit(reg):  # noqa: F811 - the imported fixture
    assert reg["chips"]["M08:PM Schedule"] == "M08-form-pmplan"
    assert reg["forms"]["M08-form-pmplan"]["model"] == "fix.contract.pm.plan"
    assert reg["chips"]["M08:PM Visit"] == "M08-form-pm"


def test_every_new_register_is_served_and_the_ledger_cannot_be_typed():
    for model in NEW_MODELS:
        assert model in m08_surfaces.SURFACES, model
    assert WRITABLE["fix.contract.entitlement.movement"] == frozenset()
    assert {"action_resume", "action_verify_wet_signature"} <= m08_surfaces.SURFACES[
        "fix.contract"
    ]["actions"]


def test_the_master_agreement_list_shows_masters_only(reg):  # noqa: F811 - the imported fixture
    assert reg["screens"]["M08-master"]["domain"] == [["is_master_agreement", "=", True]]


# --- 6 PM Schedules ---------------------------------------------------------------
def test_a_plan_drives_the_visits_generated_at_activation(c, p03):  # noqa: F811 - the imported fixture
    dev, other = _device(c), _device(c)
    k = _contract(c, covered_device_ids=[(6, 0, (dev | other).ids)], has_signed_contract_doc=True)
    out = p03(c.officer).write(
        model="fix.contract.pm.plan",
        values={
            "contract_id": k.id,
            "name": "Monthly calibration of the analyser",
            "schedule_type": "calibration",
            "device_id": dev.id,
            "interval_months": 1,
            "lead_days": 5,
            "access_window": "Sun-Thu 09:00-17:00",
        },
    )
    assert "error" not in out, out
    k.sudo().action_activate()
    visits = k.pm_visit_ids
    want = []
    day = k.date_start + relativedelta(months=1)
    while day <= k.date_end:
        want.append(day)
        day += relativedelta(months=1)
    assert sorted(visits.mapped("scheduled_date")) == want, "monthly, from the plan"
    assert set(visits.mapped("device_id").ids) == {dev.id}, "the plan's asset only"
    assert set(visits.mapped("visit_type")) == {"calibration"}
    v = visits[:1]
    assert v.dispatch_from == v.scheduled_date - timedelta(days=5)


def test_a_signed_contracts_plan_is_a_managers_and_retiring_skips_its_visits(c, p03):  # noqa: F811 - the imported fixture
    dev = _device(c)
    k = _active(c, devices=dev)
    family_visits = k.pm_visit_ids
    vals = {
        "contract_id": k.id,
        "name": "Quarterly inspection",
        "schedule_type": "inspection",
        "interval_months": 3,
    }
    out = p03(c.officer).write(model="fix.contract.pm.plan", values=vals)
    assert out.get("error"), "an officer does not change a signed contract's schedule"
    out = p03(c.manager).write(model="fix.contract.pm.plan", values=vals)
    assert "error" not in out, out
    plan = c.env["fix.contract.pm.plan"].browse(out["id"])
    assert plan.visit_ids and min(plan.visit_ids.mapped("scheduled_date")) >= c.today
    out = p03(c.manager).write(
        model="fix.contract.pm.plan", record_id=plan.id, values={"interval_months": 1}
    )
    assert out.get("error"), "the interval of a signed plan is fixed"
    out = p03(c.manager).write(
        model="fix.contract.pm.plan", record_id=plan.id, values={"active": False}
    )
    assert "error" not in out, out
    assert set(plan.visit_ids.mapped("state")) == {"skipped"}
    assert set(family_visits.mapped("state")) == {"scheduled"}, "other visits untouched"


# --- 3 Coverage Scope ---------------------------------------------------------------
def test_a_coverage_rule_covers_the_customers_matching_assets(c, p03):  # noqa: F811 - the imported fixture
    Model = c.env["fix.device.model"]
    kind = Model._fields["device_type"].selection[0][0]
    c.model.write({"device_type": kind})
    listed_nothing = _contract(c, has_signed_contract_doc=True)
    out = p03(c.officer).write(
        model="fix.contract.coverage.rule",
        values={
            "contract_id": listed_nothing.id,
            "device_type": kind,
            "note": "Every unit of this type",
        },
    )
    assert "error" not in out, out
    k = listed_nothing
    mine, theirs = _device(c), _device(c, owner=c.other)
    Ent = c.env["fix.contract.entitlement"]
    Ent.with_user(c.officer).create(
        {"contract_id": k.id, "entitlement_type": "incidents", "quantity_included": 0}
    )
    k.sudo().action_activate()
    assert k._contract_covers_device(mine)
    assert not k._contract_covers_device(theirs), "another customer's asset"
    assert Ent.entitlement_active(mine.id, "amc"), "M01's AMC gate admits the rule-covered asset"
    assert not Ent.entitlement_active(theirs.id, "amc")
    assert mine in k.pm_visit_ids.mapped("device_id"), "rule-covered assets get their visits"
    if c.branch:  # the order's own entitlement line follows the rule too
        assert _amc_order(c, k, mine)._fix_zero_charge_basis().startswith("AMC contract")
        assert not _amc_order(c, k, theirs, customer=c.other)._fix_zero_charge_basis()
    out = p03(c.officer).write(
        model="fix.contract.coverage.rule",
        values={"contract_id": k.id, "brand_id": c.model.brand_id.id},
    )
    assert out.get("error"), "cover is a term: fixed once the contract leaves draft"
    with pytest.raises(ValidationError):
        c.env["fix.contract.coverage.rule"].with_user(c.officer).create(
            {"contract_id": _contract(c).id}
        )


def test_an_amc_contract_covering_nothing_does_not_activate(c):  # noqa: F811 - the imported fixture
    k = _contract(c)
    with pytest.raises(UserError, match="covers nothing"):
        k.action_activate()
    dev = _device(c)
    k2 = _contract(c, covered_device_ids=[(6, 0, dev.ids)])
    with pytest.raises(UserError) as err:
        k2.action_activate()
    assert "covers nothing" not in str(err.value), "a listed asset satisfies BRU-CTR-01"


# --- 4 Entitlement Engine -----------------------------------------------------------
def test_a_top_up_is_applied_by_a_manager_who_did_not_raise_it(c, p03):  # noqa: F811 - the imported fixture
    k = _active(
        c,
        devices=_device(c),
        entitlements=[{"entitlement_type": "incidents", "quantity_included": 2}],
    )
    ent = k.entitlement_ids
    assert ent.movement_ids.mapped("movement_type") == ["grant"]
    out = p03(c.officer).write(
        model="fix.contract.entitlement.topup",
        values={
            "name": "TU-1",
            "entitlement_id": ent.id,
            "quantity": 3,
            "customer_reference": "PO-7781",
            "amount": 4500,
        },
    )
    assert "error" not in out, out
    tu = c.env["fix.contract.entitlement.topup"].browse(out["id"])
    w = p03(c.officer)
    assert w.action(model=tu._name, ids=[tu.id], method="action_submit", kwargs={}).get("success")
    assert not w.action(model=tu._name, ids=[tu.id], method="action_apply", kwargs={}).get(
        "success"
    )
    c.officer.write({"group_ids": [(4, c.env.ref(MANAGER).id)]})
    refused = p03(c.officer).action(model=tu._name, ids=[tu.id], method="action_apply", kwargs={})
    assert "segregation" in (refused.get("error") or "").lower(), refused
    out = p03(c.manager).action(model=tu._name, ids=[tu.id], method="action_apply", kwargs={})
    assert out.get("success"), out
    ent.invalidate_recordset()
    assert ent.quantity_included == 5 and tu.state == "applied" and tu.decided_by == c.manager
    assert ent.movement_ids.sorted("id").mapped("movement_type") == ["grant", "topup"]
    assert _events(c.env, "contract.entitlement_topped_up", k.id)[0]["quantity"] == 3


def test_a_top_up_needs_a_contract_in_force_and_a_counted_entitlement(c):  # noqa: F811 - the imported fixture
    draft = _contract(c)
    ent = (
        c.env["fix.contract.entitlement"]
        .with_user(c.officer)
        .create({"contract_id": draft.id, "entitlement_type": "visits", "quantity_included": 4})
    )
    with pytest.raises(UserError, match="in force"):
        c.env["fix.contract.entitlement.topup"].with_user(c.officer).create(
            {"name": "TU-D", "entitlement_id": ent.id, "quantity": 1, "customer_reference": "PO"}
        )
    k = _active(
        c, devices=_device(c), entitlements=[{"entitlement_type": "hours", "quantity_included": 0}]
    )
    with pytest.raises(ValidationError, match="unlimited"):
        c.env["fix.contract.entitlement.topup"].with_user(c.officer).create(
            {
                "name": "TU-U",
                "entitlement_id": k.entitlement_ids.id,
                "quantity": 1,
                "customer_reference": "PO",
            }
        )


def test_the_ledger_records_every_movement_and_cannot_be_typed(c):  # noqa: F811 - the imported fixture
    dev = _device(c)
    k = _active(
        c, devices=dev, entitlements=[{"entitlement_type": "incidents", "quantity_included": 2}]
    )
    order = _amc_order(c, k, dev)
    order.sudo()._fix_consume_contract_entitlement()
    ent = k.entitlement_ids
    consume = ent.movement_ids.filtered(lambda m: m.movement_type == "consume")
    assert (
        consume.quantity == -1 and consume.source_ref == order.name and consume.balance_after == 1
    )
    order.sudo()._fix_advance("intake")  # a draft order is discarded, not cancelled
    order.sudo().action_cancel(reason_code="other", note="customer withdrew")
    ent.invalidate_recordset()
    assert ent.quantity_consumed == 0, "a cancelled order gives back what it drew (BRU-CTR-04)"
    assert ent.movement_ids.filtered(lambda m: m.movement_type == "restore").quantity == 1
    assert order.contract_entitlement_restored, "restored once: a second pass gives nothing back"
    Movement = c.env["fix.contract.entitlement.movement"]
    with pytest.raises(UserError):
        Movement.with_user(c.officer).sudo().create(
            {"entitlement_id": ent.id, "movement_type": "topup", "quantity": 99}
        )
    with pytest.raises(UserError):
        consume.sudo().write({"quantity": 5})
    with pytest.raises(UserError):
        consume.sudo().unlink()


# --- 5 SLA & Service Credits --------------------------------------------------------
def test_the_credit_scheme_is_a_term_and_computes_capped_credits(c, p03):  # noqa: F811 - the imported fixture
    k = _contract(c)
    out = p03(c.officer).write(
        model="fix.contract.credit.scheme",
        values={
            "contract_id": k.id,
            "breach_type": "response",
            "priority": "p1",
            "credit_basis": "pct_fee",
            "credit_value": 5,
            "cumulative_rule": "escalating",
            "cap_pct": 10,
        },
    )
    assert "error" not in out, out
    rule = c.env["fix.contract.credit.scheme"].browse(out["id"])
    assert rule._scheme_credit(1, 10000) == 500
    assert rule._scheme_credit(2, 10000) == 1000  # 5% + 10%, reaching the cap
    assert rule._scheme_credit(3, 10000) == 1000, "capped at 10% of the period fee"
    with pytest.raises(ValidationError):
        c.env["fix.contract.credit.scheme"].with_user(c.officer).create(
            {"contract_id": k.id, "credit_value": 5, "cap_pct": 0}
        )
    live = _active(c, devices=_device(c))
    out = p03(c.officer).write(
        model="fix.contract.credit.scheme",
        values={"contract_id": live.id, "credit_value": 2, "cap_pct": 5},
    )
    assert out.get("error"), "a signed contract's credit scheme is fixed"


# --- 9 Churn & Win-Back -------------------------------------------------------------
def _filed_document(ctx, k):
    att = ctx.env["ir.attachment"].create({"name": "signed.pdf", "raw": b"%PDF-1.4 m08p2"})
    return ctx.env["fix.document"].create(
        {
            "name": "Signed %s" % k.code,
            "attachment_id": att.id,
            "document_type": "contract",
            "res_model": "fix.contract",
            "res_id": k.id,
        }
    )


def test_a_dispute_holds_the_documents_and_stops_auto_renewal(c, p03):  # noqa: F811 - the imported fixture
    # inside the 30-day window of an auto-renew contract: the cron would
    # announce it and draft the next term - the twin proves it does
    def amc():
        return _active(
            c,
            devices=_device(c),
            auto_renew=True,
            renewal_lead_days=60,
            date_end=c.today + timedelta(days=25),
        )

    k, twin = amc(), amc()
    doc = _filed_document(c, k)
    out = p03(c.officer).write(
        model="fix.contract.dispute",
        values={
            "contract_id": k.id,
            "name": "Billing for March visits",
            "raised_by_party": "customer",
            "opened_on": str(c.today),
            "description": "The customer says two visits never happened.",
        },
    )
    assert "error" not in out, out
    dispute = c.env["fix.contract.dispute"].browse(out["id"])
    doc.invalidate_recordset()
    k.invalidate_recordset()
    assert doc.legal_hold and doc in dispute.held_document_ids and k.in_dispute
    assert (
        c.env["fix.legal.hold"]
        .sudo()
        .search([("document_id", "=", doc.id), ("state", "=", "held")])
    )
    c.env["fix.contract"].cron_expiring_contracts()
    k.invalidate_recordset()
    twin.invalidate_recordset()
    assert twin.renewal_ids and _events(c.env, "contract.expiring", twin.id), "control"
    assert not k.renewal_ids, "BRU-CTR-12: a disputed contract does not auto-renew"
    assert not _events(c.env, "contract.expiring", k.id), "nor escalate"
    c.officer.write({"group_ids": [(4, c.env.ref(MANAGER).id)]})
    refused = p03(c.officer).action(
        model=dispute._name, ids=[dispute.id], method="action_resolve", kwargs={"resolution": "x"}
    )
    assert not refused.get("success"), "whoever opened it does not close it"
    out = p03(c.manager).action(
        model=dispute._name,
        ids=[dispute.id],
        method="action_resolve",
        kwargs={"resolution": "Visits proven by job cards"},
    )
    assert out.get("success"), out
    doc.invalidate_recordset()
    k.invalidate_recordset()
    assert not doc.legal_hold and not k.in_dispute and dispute.state == "resolved"


def _suspended(ctx, days, **kw):
    k = _active(ctx, devices=_device(ctx), **kw)
    k.sudo()._guarded().write(
        {"state": "suspended", "suspended_on": ctx.today - timedelta(days=days)}
    )
    return k


def test_reinstatement_declares_and_applies_the_suspended_period_treatment(c, p03):  # noqa: F811 - the imported fixture
    k = _suspended(c, 10)
    end = k.date_end
    w = p03(c.manager)
    out = w.action(model="fix.contract", ids=[k.id], method="action_resume", kwargs={})
    assert not out.get("success"), "a resume must declare the treatment"
    out = w.action(
        model="fix.contract",
        ids=[k.id],
        method="action_resume",
        kwargs={"treatment": "extend_term", "note": "Paid in full"},
    )
    assert out.get("success"), out
    k.invalidate_recordset()
    assert k.state == "active" and k.date_end == end + timedelta(days=10)
    assert k.reinstatement_treatment == "extend_term" and k.reinstated_by == c.manager
    p = _suspended(c, 73, entitlements=[{"entitlement_type": "visits", "quantity_included": 10}])
    out = w.action(
        model="fix.contract", ids=[p.id], method="action_resume", kwargs={"treatment": "prorate"}
    )
    assert out.get("success"), out
    ent = p.entitlement_ids
    ent.invalidate_recordset()
    term = (p.date_end - p.date_start).days + 1
    assert ent.quantity_included == pytest.approx(10 - round(10 * 73 / term, 2))
    assert ent.movement_ids.filtered(lambda m: m.movement_type == "prorate")
    out = p03(c.officer).action(
        model="fix.contract",
        ids=[_suspended(c, 1).id],
        method="action_resume",
        kwargs={"treatment": "forfeit"},
    )
    assert not out.get("success"), "a Contract Manager decides"


# --- 11 Documents & Signature ---------------------------------------------------------
def test_a_contract_signed_in_ink_activates_on_its_verified_scan(c, p03):  # noqa: F811 - the imported fixture
    dev = _device(c)
    k = _contract(c, covered_device_ids=[(6, 0, dev.ids)])
    k.action_request_approval(justification="Bank AMC signed at the branch")
    _approve_value(c, k)
    assert k.state == "pending_signature"
    with pytest.raises(UserError, match="no e-signature envelope"):
        k.action_activate()
    scan = base64.b64encode(b"%PDF-1.4 signed in ink").decode()
    out = p03(c.officer).write(
        model="fix.contract",
        record_id=k.id,
        values={
            "signature_method": "wet",
            "wet_signed_on": str(c.today),
            "wet_signed_file_id": {"upload": scan, "filename": "signed.pdf"},
        },
    )
    assert "error" not in out, out
    k.invalidate_recordset()
    assert k.wet_signed_document_id.attachment_id and k.wet_signature_recorded_by == c.officer
    with pytest.raises(UserError, match="not verified"):
        k.action_activate()
    w = p03(c.officer)
    out = w.action(
        model="fix.contract", ids=[k.id], method="action_verify_wet_signature", kwargs={}
    )
    assert not out.get("success"), "whoever recorded the scan does not verify it"
    out = p03(c.officer2).action(
        model="fix.contract", ids=[k.id], method="action_verify_wet_signature", kwargs={}
    )
    assert out.get("success"), out
    k.invalidate_recordset()
    k.action_activate()
    assert k.state == "active" and k.has_signed_contract_doc
    assert k.wet_signed_document_id.signature_locked
    out = w.write(
        model="fix.contract",
        record_id=k.id,
        values={"wet_signed_on": str(c.today - timedelta(days=3))},
    )
    assert out.get("error") or k.wet_signed_on == c.today, "how it was signed is fixed once active"


def test_a_future_signing_date_is_refused_at_verification(c):  # noqa: F811 - the imported fixture
    k = _contract(c, covered_device_ids=[(6, 0, _device(c).ids)])
    att = c.env["ir.attachment"].create({"name": "s.pdf", "raw": b"%PDF-1.4"})
    k.write(
        {
            "signature_method": "wet",
            "wet_signed_on": c.today + timedelta(days=2),
            "wet_signed_file_id": att.id,
        }
    )
    with pytest.raises(UserError, match="future"):
        k.with_user(c.officer2).action_verify_wet_signature()


# --- 1 Template-Driven Creation -------------------------------------------------------
def test_a_contract_carries_its_owner_and_its_master_agreement(c, p03):  # noqa: F811 - the imported fixture
    master = _contract(c)
    assert master.owner_id == c.officer, "BRU-CTR-19: the creator owns it"
    out = p03(c.officer).write(
        model="fix.contract",
        values={
            "name": "Branch 2 subsidiary",
            "family": "amc",
            "customer_id": c.customer.id,
            "operating_unit_id": c.ou.id,
            "date_start": str(c.today),
            "date_end": str(c.today + timedelta(days=200)),
            "annual_value": 30000,
            "parent_contract_id": master.id,
            "owner_id": c.officer2.id,
        },
    )
    assert "error" not in out, out
    sub = c.env["fix.contract"].browse(out["id"])
    master.invalidate_recordset()
    assert (
        sub.owner_id == c.officer2 and master.is_master_agreement and master.subsidiary_count == 1
    )
    with pytest.raises(ValidationError):
        _contract(c, customer_id=c.other.id, parent_contract_id=master.id)
    with pytest.raises(ValidationError):
        _contract(c, parent_contract_id=sub.id)  # one level: a subsidiary is no master
