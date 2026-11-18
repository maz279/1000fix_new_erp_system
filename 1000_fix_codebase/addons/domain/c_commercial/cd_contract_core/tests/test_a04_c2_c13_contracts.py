"""A04 C2-C13 build (2026-11-04): M08 contract controls, as non-admin users.

Live ORM, rolled back per test. Every attack runs as a user created in the
transaction with the role they would really hold (Contract Officer, Contract
Manager, Legal Reviewer, a DOFA tier, Finance) or without it where the role
is the control. Approvals go through the M63 inbox (approve_via_inbox); a
direct call of the approve method is shown to be refused.
"""

from __future__ import annotations

import json
import types
import uuid
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = uuid.uuid4().hex[:6].upper()
OFFICER = "cd_contract_core.group_contract_officer"
MANAGER = "cd_contract_core.group_contract_manager"
LEGAL = "cd_contract_core.group_contract_legal"
FINANCE = "account.group_account_manager"


def _tier(n):
    return "cd_entity_config.group_dofa_tier_%d" % n


def _user(env, login, *groups):
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": "%s_%s" % (login, TAG),
                "group_ids": [(6, 0, ids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(r.payload) for r in env["fix.event.outbox"].search(domain, order="id")]


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["fix.contract"])
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.clerk = _user(env, "a4b1_clerk")
    x.officer = _user(env, "a4b1_officer", OFFICER)
    x.officer2 = _user(env, "a4b1_officer2", OFFICER)
    x.manager = _user(env, "a4b1_manager", MANAGER)
    x.legal = _user(env, "a4b1_legal", LEGAL)
    x.legal2 = _user(env, "a4b1_legal2", LEGAL)
    x.finance = _user(env, "a4b1_finance", FINANCE)
    x.tier = {n: _user(env, "a4b1_tier%d" % n, _tier(n)) for n in (1, 2, 3, 4, 5)}
    x.customer = env["res.partner"].create(
        {"name": "A04B1 Customer %s" % TAG, "phone": "01711000801"}
    )
    x.other = env["res.partner"].create({"name": "A04B1 Other %s" % TAG})
    brand = env["fix.brand"].create({"name": "A04B1 Brand %s" % TAG, "code": "B1%s" % TAG})
    x.model = env["fix.device.model"].create({"name": "A04B1 Model", "brand_id": brand.id})
    x.branch = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if not x.branch:
        company = env["res.company"].create({"name": "A04B1 Co %s" % TAG})
        entity = env["fix.entity"].create(
            {"legal_name": "A04B1 Entity", "code": "A4B1E%s" % TAG, "company_id": company.id}
        )
        x.branch = env["fix.branch"].create(
            {
                "name": "A04B1 Branch",
                "code": "A4B1-BR",
                "entity_id": entity.id,
                "operating_unit_id": x.ou.id,
            }
        )
    x.n = 0
    return x


def _device(c, owner=None):
    c.n += 1
    vals = {
        "device_model_id": c.model.id,
        "owner_id": (owner or c.customer).id,
        "serial_number": "A4B1-%s-%03d" % (TAG, c.n),
    }
    if c.branch:
        vals["branch_id"] = c.branch.id
    return c.env["fix.device"].create(vals)


def _contract(c, user=None, value=120000.0, **kw):
    vals = {
        "name": "A04B1 AMC",
        "family": "amc",
        "customer_id": c.customer.id,
        "operating_unit_id": c.ou.id,
        "date_start": c.today - timedelta(days=10),
        "date_end": c.today + timedelta(days=355),
        "annual_value": value,
        "stamp_duty_cert_no": "SD-%s" % TAG,
        "stamp_duty_amount": 300.0,
    }
    vals.update(kw)
    return c.env["fix.contract"].with_user(user or c.officer).create(vals)


def _active(c, value=120000.0, devices=None, entitlements=None, **kw):
    """An in-force contract, activated through the trusted path (the
    superuser stands in for a contract approved and signed earlier)."""
    k = _contract(c, value=value, has_signed_contract_doc=True, **kw)
    if devices:
        k.write({"covered_device_ids": [(6, 0, devices.ids)]})
    for ent in entitlements or []:
        c.env["fix.contract.entitlement"].with_user(c.officer).create(dict(ent, contract_id=k.id))
    k.sudo().action_activate()
    k.invalidate_recordset()
    assert k.state == "active"
    return k.with_user(c.officer)


def _signed_envelope(c, contract, signer=None, sign=True):
    """A completed M24 envelope, as the signing provider leaves it."""
    env = c.env
    att = env["ir.attachment"].create({"name": "contract.pdf", "raw": b"%PDF-1.4 a04b1"})
    Doc = env["fix.document"]
    dtype = Doc._fields["document_type"]._description_selection(env)[0][0]
    doc = Doc.create(
        {"name": "Signed %s" % contract.code, "attachment_id": att.id, "document_type": dtype}
    )
    envelope = env["fix.esignature.envelope"].create(
        {"name": "Sign %s" % contract.code, "operating_unit_id": c.ou.id, "document_id": doc.id}
    )
    env["fix.esignature.signer"].create(
        {
            "envelope_id": envelope.id,
            "partner_id": (signer or contract.customer_id).id,
            "role_label": "Customer",
        }
    )
    envelope.action_send()
    if sign:
        envelope.signer_ids.write(
            {"signed_at": fields.Datetime.now(), "signature_provider": "L6-SIG-%s" % TAG}
        )
        envelope.action_check_complete()
    return envelope


def _approve_value(c, k, tier=2, justification="Renewal of the bank AMC at list price"):
    approve_via_inbox(k, c.tier[tier], requester=c.officer, justification=justification)
    k.invalidate_recordset()
    return k


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    ma = getattr(
        g.P03GenericApiController.model_action,
        "original_endpoint",
        g.P03GenericApiController.model_action,
    )
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req
        return types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw)
        )

    try:
        yield as_user
    finally:
        g.request, s.request = old_g, old_s


# =========================================================================== roles and the guard
def test_plain_user_reads_but_cannot_create_a_contract(c):
    with pytest.raises(AccessError):
        _contract(c, user=c.clerk)
    k = _contract(c)
    assert k.with_user(c.clerk).read(["name"])[0]["name"] == "A04B1 AMC"


def test_state_cannot_be_typed_by_orm_or_p03(c, p03):
    k = _contract(c)
    with pytest.raises(UserError):
        k.write({"state": "active"})
    res = p03(c.officer).write(model="fix.contract", record_id=k.id, values={"state": "active"})
    k.invalidate_recordset()
    assert res.get("error") and k.state == "draft"
    with pytest.raises(UserError):
        _contract(c, state="active")


def test_terms_freeze_once_submitted_and_reopen_on_reset(c):
    k = _contract(c)
    k.action_request_approval(justification="Standard AMC")
    assert k.state == "pending_approval" and k.approval_state == "pending"
    with pytest.raises(UserError):
        k.write({"annual_value": 1.0})
    k.action_reset_to_draft()
    assert k.state == "draft" and k.approval_state == "none"
    k.write({"annual_value": 90000.0})
    assert k.annual_value == 90000.0


# =========================================================================== value approval and activation
def test_value_approval_is_routed_and_not_self_given(c):
    # the creator is an officer who also holds the very tier the value needs
    c.tier[2].write({"group_ids": [(4, c.env.ref(OFFICER).id)]})
    k = _contract(c, user=c.tier[2])
    with pytest.raises(UserError):  # the record's own approve button is not a way in
        k.with_user(c.tier[2]).action_dofa_approve()
    k.with_user(c.tier[2]).action_request_approval(justification="Bank AMC")
    assert c.tier[2] not in assigned(k)
    assert k.dofa_tier_required == "tier_2"


def test_full_lifecycle_needs_approval_and_a_real_signature(c):
    dev = _device(c)
    k = _contract(c, covered_device_ids=[(6, 0, dev.ids)])
    k.action_request_approval(justification="Bank AMC, 1 device")
    with pytest.raises(REFUSED):  # not yet approved, not yet pending signature
        k.action_activate()
    _approve_value(c, k)
    assert k.state == "pending_signature" and k.dofa_approved and k.dofa_approved_by == c.tier[2]
    with pytest.raises(UserError, match="no e-signature envelope"):
        k.action_activate()
    forged = _signed_envelope(c, k, sign=False)
    forged.write({"state": "completed"})  # typed 'completed' with no signature
    k.write({"esignature_envelope_id": forged.id})
    with pytest.raises(UserError, match="carry no provider signature"):
        k.action_activate()
    other = _signed_envelope(c, k, signer=c.other)  # signed, but not by the customer
    k.write({"esignature_envelope_id": other.id})
    with pytest.raises(UserError, match="not among the signers"):
        k.action_activate()
    k.write({"esignature_envelope_id": _signed_envelope(c, k).id})
    with pytest.raises(UserError):  # the right role is still required
        k.with_user(c.clerk).action_activate()
    k.action_activate()  # an officer with no accounting rights: the OCA sync is a service
    assert k.state == "active" and k.activated_by == c.officer
    assert k.has_signed_contract_doc and k.sudo().oca_contract_id
    assert k.pm_visit_ids, "activation generates the PM schedule"
    assert _events(c.env, "contract.activated", k.id)
    with pytest.raises(UserError):  # frozen once active
        k.write({"annual_value": 10.0})


def test_high_value_contract_needs_legal_review_by_someone_else(c):
    k = _contract(c, value=1_500_000.0)
    assert k.legal_review_required and k.dofa_tier_required == "tier_4"
    k.action_request_approval(justification="Managed estate, five sites")
    _approve_value(c, k, tier=4)
    assert k.state == "pending_approval", "the value is approved, Legal has not reviewed"
    c.legal.write({"group_ids": [(4, c.env.ref(OFFICER).id)]})
    own = _contract(c, user=c.legal, value=2_000_000.0)
    own.with_user(c.legal).action_request_approval(justification="x")
    with pytest.raises(UserError, match="Segregation of duties"):
        own.with_user(c.legal).action_legal_review()
    with pytest.raises(UserError):
        k.with_user(c.officer).action_legal_review()  # not a Legal reviewer
    k.with_user(c.legal2).action_legal_review(note="Liability cap acceptable")
    assert k.state == "pending_signature" and k.legal_reviewed_by == c.legal2


def test_stamp_exemption_is_a_finance_decision_by_someone_else(c):
    k = _contract(
        c,
        stamp_duty_applicable=False,
        stamp_duty_exemption_reason="Duty paid on master MSA",
        covered_device_ids=[(6, 0, _device(c).ids)],  # BRU-CTR-01: an AMC covers something
    )
    assert k.stamp_exemption_requested_by == c.officer
    k.action_request_approval(justification="Call-off under the MSA")
    _approve_value(c, k)
    k.write({"esignature_envelope_id": _signed_envelope(c, k).id})
    with pytest.raises(UserError, match="Finance has not"):
        k.action_activate()
    with pytest.raises(UserError):  # no Finance role
        k.with_user(c.officer2).action_approve_stamp_exemption()
    c.officer.write({"group_ids": [(4, c.env.ref(FINANCE).id)]})
    with pytest.raises(UserError, match="Segregation of duties"):
        k.with_user(c.officer).action_approve_stamp_exemption()
    k.with_user(c.finance).action_approve_stamp_exemption()
    k.action_activate()
    assert k.state == "active"


def test_activation_needs_the_right_from_state(c):
    k = _contract(c, has_signed_contract_doc=True)
    k.sudo()._guarded().write({"state": "terminated"})
    with pytest.raises(UserError, match="cannot be activated"):
        k.sudo().action_activate()
    with pytest.raises(UserError):
        k.action_activate()


# =========================================================================== amendments and price revision
def test_pricing_amendment_is_approved_applied_and_versioned(c, p03):
    k = _active(c, value=480_000.0)
    a = (
        c.env["fix.contract.amendment"]
        .with_user(c.officer)
        .create(
            {
                "name": "+150k scope uplift",
                "contract_id": k.id,
                "kind": "pricing",
                "delta_value": 150000.0,
                "effective_from": c.today,
            }
        )
    )
    res = p03(c.officer).write(
        model="fix.contract.amendment", record_id=a.id, values={"state": "approved"}
    )
    assert res.get("error") and a.state == "draft"
    with pytest.raises(UserError):
        a.write({"state": "applied"})
    a.action_request_approval(justification="Two more sites")
    with pytest.raises(UserError):
        a.write({"delta_value": 1_000_000.0})  # pinned once submitted
    approve_via_inbox(a, c.tier[2], requester=c.officer)
    a.invalidate_recordset()
    k.invalidate_recordset()
    assert a.state == "applied" and a.version_no == 1
    assert k.annual_value == 630_000.0 and k.amendment_version == 1
    assert a.value_before == 480_000.0 and a.value_after == 630_000.0
    assert _events(c.env, "contract.amended", k.id)


def test_price_revision_raises_an_amendment_instead_of_writing(c):
    k = _active(c, value=1_200_000.0)
    with pytest.raises(UserError):
        k.with_user(c.clerk).action_price_revision(1.0, "cut")
    amendment = k.with_user(c.officer2).action_price_revision(1_000_000.0, "renegotiated")
    k.invalidate_recordset()
    assert k.annual_value == 1_200_000.0 and amendment.state == "draft"
    assert amendment.delta_value == -200_000.0 and amendment.dofa_tier_required == "tier_2"


def test_billed_period_cannot_be_amended(c):
    k = _active(c)
    k.sudo().mark_billed_through(c.today + timedelta(days=30))
    with pytest.raises(UserError):
        k.mark_billed_through(c.today + timedelta(days=60))  # a person cannot move it
    a = (
        c.env["fix.contract.amendment"]
        .with_user(c.officer)
        .create(
            {
                "name": "retro",
                "contract_id": k.id,
                "kind": "pricing",
                "delta_value": -10000.0,
                "effective_from": c.today,
            }
        )
    )
    with pytest.raises(UserError, match="billed through"):
        a.action_request_approval(justification="x")


def test_scope_amendment_is_decided_by_another_manager(c):
    k = _active(c)
    a = (
        c.env["fix.contract.amendment"]
        .with_user(c.manager)
        .create(
            {
                "name": "exclude toner",
                "contract_id": k.id,
                "kind": "scope",
                "effective_from": c.today,
                # a scope amendment carries what it changes (M08 gaps, 13 Nov)
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "action": "add_exclusion",
                            "exclusion_type": "consumable",
                            "exclusion_text": "Toner and drums",
                        },
                    )
                ],
            }
        )
    )
    manager2 = _user(c.env, "a4b1_manager2", MANAGER)
    a.with_user(c.manager).action_request_approval()
    assert c.manager not in assigned(a) and manager2 in assigned(a)
    approve_via_inbox(a, manager2, requester=c.manager)
    a.invalidate_recordset()
    assert a.state == "applied"
    assert k.exclusion_ids.mapped("name") == ["Toner and drums"]


# =========================================================================== termination
def test_termination_tier_is_derived_pinned_and_executed_by_a_manager(c):
    k = _active(c)
    t = (
        c.env["fix.contract.termination"]
        .with_user(c.officer)
        .create(
            {
                "name": "Customer exit",
                "contract_id": k.id,
                "kind": "termination",
                "reason": "Relocation",
                "effective_date": c.today,
                "penalty_amount": 5_000_000.0,
                "dofa_tier": "tier_1",  # a chosen tier is ignored
            }
        )
    )
    assert t.dofa_tier == "tier_5" and t.dofa_tier_required == "tier_5"
    with pytest.raises(UserError):
        t.write({"state": "approved", "dofa_approved": True})
    with pytest.raises(UserError) as exc:
        t.with_user(c.manager).action_execute_termination()
    assert not isinstance(exc.value, AttributeError)
    t.action_request_approval(justification="Board minute 14/2026")
    with pytest.raises(UserError):
        t.write({"penalty_amount": 9_000_000.0})  # pinned
    with pytest.raises(UserError):
        t.with_user(c.officer).action_dofa_approve()  # routed only
    approve_via_inbox(t, c.tier[5], requester=c.officer)
    t.invalidate_recordset()
    assert t.state == "approved" and t.dofa_approved_by == c.tier[5]
    with pytest.raises(UserError):
        t.with_user(c.officer).action_execute_termination()  # Contract Manager only
    t.with_user(c.manager).action_execute_termination()
    k.invalidate_recordset()
    assert t.state == "effective" and k.state == "terminated"
    assert _events(c.env, "contract.terminated", t.id)[0]["penalty_amount"] == 5_000_000.0


def test_backdated_termination_is_refused(c):
    k = _active(c)
    t = (
        c.env["fix.contract.termination"]
        .with_user(c.officer)
        .create(
            {
                "name": "back",
                "contract_id": k.id,
                "reason": "x",
                "effective_date": c.today - timedelta(days=60),
            }
        )
    )
    with pytest.raises(UserError, match="backdated"):
        t.action_request_approval(justification="x")


# =========================================================================== renewal
def test_renewal_drafts_the_next_term_and_keeps_cover(c):
    dev = _device(c)
    k = _active(
        c, devices=dev, entitlements=[{"entitlement_type": "incidents", "quantity_included": 5}]
    )
    Ent = c.env["fix.contract.entitlement"]
    renewal = k.action_renew()
    k.invalidate_recordset()
    assert k.state == "active" and Ent.entitlement_active(dev.id, "amc")
    assert renewal.state == "draft" and renewal.renewed_from_id == k
    assert renewal.date_start == k.date_end + timedelta(days=1)
    with pytest.raises(UserError, match="already has a renewal"):
        k.action_renew()
    renewal.write({"stamp_duty_cert_no": "SD-R-%s" % TAG, "has_signed_contract_doc": True})
    renewal.sudo().action_activate()
    assert _events(c.env, "contract.renewed", renewal.id)


def test_won_renewal_quote_creates_the_next_term(c):
    k = _active(c)
    r = (
        c.env["fix.contract.renewal"]
        .with_user(c.officer)
        .create(
            {
                "name": "Renewal 2027",
                "contract_id": k.id,
                "proposed_start": k.date_end + timedelta(days=1),
                "proposed_end": k.date_end + timedelta(days=366),
                "propo_value": 132000.0,
            }
        )
    )
    with pytest.raises(UserError):
        r.write({"state": "won"})
    with pytest.raises(UserError):
        r.action_mark_won()  # not yet quoted
    r.action_quote()
    r.action_mark_won()
    assert r.state == "won" and r.renewal_contract_id.annual_value == 132000.0
    assert r.renewal_contract_id.state == "draft" and r.renewal_contract_id.renewed_from_id == k


# =========================================================================== entitlement and M01
def test_entitlement_balance_cannot_be_reset(c, p03):
    k = _active(c, entitlements=[{"entitlement_type": "incidents", "quantity_included": 5}])
    e = k.entitlement_ids
    with pytest.raises(UserError):
        e.write({"quantity_consumed": 0, "quantity_included": 500})
    res = p03(c.officer).write(
        model="fix.contract.entitlement", record_id=e.id, values={"quantity_included": 500}
    )
    e.invalidate_recordset()
    assert res.get("error") and e.quantity_included == 5
    with pytest.raises(UserError):
        c.env["fix.contract.entitlement"].with_user(c.officer).create(
            {"contract_id": k.id, "entitlement_type": "visits", "quantity_included": 99}
        )
    with pytest.raises(UserError):
        e.with_user(c.clerk).consume(1.0)


def test_expiry_cron_ends_cover_and_is_idempotent(c):
    dev = _device(c)
    k = _active(
        c,
        devices=dev,
        entitlements=[{"entitlement_type": "incidents", "quantity_included": 0}],
        date_start=c.today - timedelta(days=400),
        date_end=c.today - timedelta(days=30),
    )
    Ent = c.env["fix.contract.entitlement"]
    assert not Ent.entitlement_active(dev.id, "amc"), "the lookup is bound to the term dates"
    c.env["fix.contract"].cron_expiring_contracts()
    k.invalidate_recordset()
    assert k.state == "expired"
    assert _events(c.env, "contract.expired", k.id)
    c.env["fix.contract"].cron_expiring_contracts()
    assert len(_events(c.env, "contract.expired", k.id)) == 1


def test_expiry_cron_announces_each_window_once_and_drafts_the_renewal(c):
    k = _active(c, date_start=c.today - timedelta(days=300), date_end=c.today + timedelta(days=20))
    Contract = c.env["fix.contract"]
    Contract.cron_expiring_contracts()
    Contract.cron_expiring_contracts()
    k.invalidate_recordset()
    windows = [e["window_days"] for e in _events(c.env, "contract.expiring", k.id)]
    assert windows == [30] and k.state == "expiring"
    assert k.renewal_ids.state == "draft"


def _amc_order(c, k, dev, customer=None, user=None):
    return (
        c.env["fix.service.order"]
        .with_user(user or c.clerk)
        .create(
            {
                "device_id": dev.id,
                "customer_id": (customer or c.customer).id,
                "branch_id": c.branch.id,
                "service_type": "walk_in",
                "order_category": "amc",
                "fault_description": "A04B1 AMC",
                "contract_id": k.id,
            }
        )
    )


def test_m01_amc_basis_is_the_contracts_own_entitlement(c):
    if not c.branch:
        pytest.fail("setup: no branch with an operating unit in this database")
    dev, stranger = _device(c), _device(c)
    draft = _contract(c, covered_device_ids=[(6, 0, dev.ids)])
    assert not _amc_order(c, draft, dev)._fix_zero_charge_basis(), "a draft contract"
    k = _active(
        c, devices=dev, entitlements=[{"entitlement_type": "incidents", "quantity_included": 1}]
    )
    assert not _amc_order(c, k, stranger)._fix_zero_charge_basis(), "a device it does not cover"
    assert not _amc_order(c, k, dev, customer=c.other)._fix_zero_charge_basis(), "another customer"
    order = _amc_order(c, k, dev)
    assert order._fix_zero_charge_basis().startswith("AMC contract")
    order.sudo()._fix_consume_contract_entitlement()
    ent = k.entitlement_ids
    ent.invalidate_recordset()
    assert ent.quantity_consumed == 1.0 and order.contract_entitlement_id == ent
    assert order._fix_zero_charge_basis(), "the order that drew it keeps its basis"
    order.sudo()._fix_consume_contract_entitlement()
    assert ent.quantity_consumed == 1.0, "drawn once per order"
    assert not _amc_order(c, k, dev)._fix_zero_charge_basis(), "the entitlement is used up"
    assert _events(c.env, "entitlement.consumed", ent.id)


def test_pm_dispatch_links_the_contract_and_completion_waits_for_the_order(c, p03):
    if not c.branch:
        pytest.fail("setup: no branch with an operating unit in this database")
    dev = _device(c)
    k = _active(c, devices=dev)
    visit = k.pm_visit_ids[:1].with_user(c.clerk)
    res = p03(c.officer).write(
        model="fix.contract.pm.visit", record_id=visit.id, values={"state": "completed"}
    )
    assert res.get("error")
    with pytest.raises(UserError):
        visit.with_user(c.officer).write({"state": "completed"})
    visit.action_create_service_order()
    assert visit.state == "dispatched" and visit.service_order_id.contract_id == k
    with pytest.raises(UserError, match="not delivered"):
        visit.action_complete()
    with pytest.raises(UserError):
        visit.with_user(c.officer).action_skip("x")  # Contract Manager only


# =========================================================================== template sign-off
def test_template_signoff_is_legal_and_not_the_authors(c):
    T = c.env["fix.contract.template"]
    t = T.with_user(c.legal).create(
        {
            "name": "A04B1 tmpl",
            "code": "A4B1-%s" % TAG,
            "standard_terms": "Terms",
            "terms_bn": "শর্ত",
        }
    )
    with pytest.raises(UserError, match="Segregation of duties"):
        t.with_user(c.legal).action_legal_signoff()
    with pytest.raises(UserError):
        t.with_user(c.officer).action_legal_signoff()
    with pytest.raises(UserError):
        t.with_user(c.legal).write({"legal_reviewed_by": c.legal2.id})
    t.with_user(c.legal2).action_legal_signoff()
    assert t.is_publishable and t.legal_reviewed_by == c.legal2
    t.with_user(c.officer).write({"standard_terms": "Changed terms"})
    assert not t.legal_reviewed_by and not t.is_publishable
    t.with_user(c.legal2).write({"terms_bn": "নতুন শর্ত"})
    with pytest.raises(UserError, match="Segregation of duties"):
        t.with_user(c.legal2).action_legal_signoff()  # the last editor cannot sign


# =========================================================================== wiring
CRONS = {
    "cd_contract_core.ir_cron_contract_expiry": ("fix.contract", "cron_expiring_contracts"),
    "cd_contract_core.ir_cron_contract_amendments_due": (
        "fix.contract.amendment",
        "cron_apply_due_amendments",
    ),
    "cd_contract_core.ir_cron_contract_terminations_due": (
        "fix.contract.termination",
        "cron_execute_due_terminations",
    ),
    "cd_contract_core.ir_cron_contract_pm_visits": ("fix.contract.pm.visit", "cron_sync_pm_visits"),
}


@pytest.mark.parametrize("xmlid", sorted(CRONS))
def test_cron_record_exists_is_active_and_names_its_method(c, xmlid):
    model, method = CRONS[xmlid]
    cron = c.env.ref(xmlid)
    assert cron.active and cron.model_id.model == model and method in cron.code
    assert hasattr(c.env[model], method)
    getattr(c.env[model], method)()
    getattr(c.env[model], method)()  # idempotent: a second run raises nothing


def test_due_amendment_and_termination_run_on_their_date(c):
    k = _active(c)
    a = (
        c.env["fix.contract.amendment"]
        .with_user(c.officer)
        .create(
            {
                "name": "Q1 uplift",
                "contract_id": k.id,
                "kind": "pricing",
                "delta_value": 1000.0,
                "effective_from": c.today + timedelta(days=5),
            }
        )
    )
    a.action_request_approval()
    approve_via_inbox(a, c.tier[1], requester=c.officer)
    a.invalidate_recordset()
    assert a.state == "approved", "future-dated: waits for its date"
    a.sudo()._guarded().write({"effective_from": c.today})  # the date arrives
    assert c.env["fix.contract.amendment"].cron_apply_due_amendments() >= 1
    a.invalidate_recordset()
    assert a.state == "applied"


def test_workspace_runs_the_lifecycle_actions(c, p03):
    from odoo.addons.cd_p03_portal.controllers.a04 import m08

    assert "action_activate" in m08.SURFACES["fix.contract"]["actions"]
    assert "action_execute_termination" in m08.SURFACES["fix.contract.termination"]["actions"]
    k = _contract(c)
    res = p03(c.officer).action(
        model="fix.contract",
        ids=[k.id],
        method="action_request_approval",
        kwargs={"justification": "AMC"},
    )
    k.invalidate_recordset()
    assert res.get("success") and k.state == "pending_approval"
    res = p03(c.clerk).action(model="fix.contract", ids=[k.id], method="action_reset_to_draft")
    assert not res.get("success")
