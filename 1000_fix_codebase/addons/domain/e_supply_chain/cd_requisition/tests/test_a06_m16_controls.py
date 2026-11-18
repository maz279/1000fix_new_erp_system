# A06 control suite, M16 Procurement & Sourcing (A06 workflow audit 2026-11-03).
#
# One test per gap probe of working/A06_evidence/probes/m16/probe_m16.py (named
# after the probe id): the same attack, run as a NON-ADMIN user created in the
# transaction, now refused, plus proper-path tests showing each role can still
# do its job. Everything runs in the rolled-back odoo_env.
import types
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

try:
    from psycopg2 import IntegrityError
except Exception:  # pragma: no cover
    IntegrityError = Exception

REFUSED = (UserError, ValidationError, AccessError, IntegrityError)
GB = "cd_requisition.group_fix_procurement_buyer"
GR = "cd_requisition.group_fix_procurement_receiver"
GA = "cd_requisition.group_fix_procurement_approver"
GM = "cd_requisition.group_fix_procurement_manager"
T = {n: "cd_entity_config.group_dofa_tier_%d" % n for n in range(1, 6)}
GUARD = "changes only through its workflow"
ACK_DATE = date.today() + timedelta(days=14)


def _user(env, login, groups=()):
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def _active_supplier(env, partner):
    """An active M42 supplier with verified documents (seeded as the system)."""
    sup = env["fix.supplier"].create(
        {"name": partner.name, "partner_id": partner.id, "status": "active"}
    )
    for doc_type in ("trade_licence", "tin", "vat"):
        env["fix.supplier.document"].create(
            {
                "supplier_id": sup.id,
                "doc_type": doc_type,
                "number": "A06-%s" % doc_type,
                "file_ref": "dms://a06/%s" % doc_type,
                "state": "valid",
                "valid_to": date.today() + timedelta(days=365),
            }
        )
    return sup


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.requester = _user(env, "a06m16t_requester")
    x.clerk2 = _user(env, "a06m16t_clerk2")
    x.buyer = _user(env, "a06m16t_buyer", [GB])
    x.buyer2 = _user(env, "a06m16t_buyer2", [GB])
    x.receiver = _user(env, "a06m16t_receiver", [GR])
    x.t2 = _user(env, "a06m16t_t2", [T[2]])
    x.t3 = _user(env, "a06m16t_t3", [T[3]])
    x.cfo = _user(env, "a06m16t_cfo", [T[4]])
    x.md = _user(env, "a06m16t_md", [T[5]])
    x.manager = _user(env, "a06m16t_manager", [GM])
    x.manager2 = _user(env, "a06m16t_manager2", [GM])
    x.papprover = _user(env, "a06m16t_papprover", [GA])
    x.emp = env["hr.employee"].create({"name": "A06M16T Requester", "user_id": x.requester.id})
    categ = env["product.category"].create({"name": "A06M16T Compressors"})
    x.prod = env["product.product"].create({"name": "A06M16T Compressor", "categ_id": categ.id})
    x.prod2 = env["product.product"].create({"name": "A06M16T Capacitor", "categ_id": categ.id})
    x.vendor, x.vendor2, x.vendor3, x.vendor4 = env["res.partner"].create(
        [
            {"name": "A06M16T Vendor Active", "is_company": True},
            {"name": "A06M16T Vendor Prospect", "is_company": True},
            {"name": "A06M16T Vendor Unregistered", "is_company": True},
            {"name": "A06M16T Vendor Active Two", "is_company": True},
        ]
    )
    x.sup = _active_supplier(env, x.vendor)
    x.sup4 = _active_supplier(env, x.vendor4)
    x.vendor5 = env["res.partner"].create(
        {"name": "A06M16T Vendor Active Three", "is_company": True}
    )
    _active_supplier(env, x.vendor5)
    return x


APPROVER_BY_TIER = {"tier_2": "t2", "tier_3": "t3", "tier_4": "cfo", "tier_5": "md"}


def _approver(c, record):
    return getattr(c, APPROVER_BY_TIER[record._dofa_current_tier()])


def _inbox(record, approver):
    return record.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )


def _decide(record, approver=None, c=None):
    approver = approver or _approver(c, record)
    task = _inbox(record, approver)
    assert task, "no inbox task for %s (routed to %s)" % (
        approver.login,
        record.approval_request_id.task_ids.mapped("assigned_user_id.login"),
    )
    task.with_user(approver).action_approve(comment="ok")
    return task


def _req(c, amount=20000.0, user=None, **kw):
    vals = {
        "operating_unit_id": c.ou.id,
        "requested_by": c.emp.id,
        "description": "A06M16T requisition",
        "justification": "Stock-out on compressors for AMC visits",
        "estimate_amount": amount,
        "product_id": c.prod.id,
        "qty": 2,
        "vendor_id": c.vendor.id,
        "cost_centre": "CC-A06M16T",
        "required_by": ACK_DATE,
    }
    vals.update(kw)
    return c.env["fix.requisition"].with_user(user or c.requester).create(vals)


def _approved_req(c, amount=20000.0, **kw):
    r = _req(c, amount, **kw)
    r.with_user(c.requester).action_submit()
    _decide(r, c=c)
    assert r.state == "approved"
    return r


def _approved_po(c, amount=20000.0, qty=2, **kw):
    r = _approved_req(c, amount, qty=qty, **kw)
    r.with_user(c.buyer).action_convert_to_po()
    po = r.purchase_order_id
    po.with_user(c.buyer).action_submit_for_approval()
    _decide(po, c=c)
    assert po.approval_state == "approved"
    return po


def _sent_po(c, amount=20000.0, qty=2, **kw):
    po = _approved_po(c, amount, qty, **kw)
    po.with_user(c.buyer).action_send()
    assert po.state == "sent"
    return po


def _receive(c, po, qty=None, inspect_accept=None):
    line = po.line_ids[:1]
    po.with_user(c.receiver).action_record_receipt({line.id: qty or line.qty_ordered})
    rline = po.receipt_ids.line_ids[-1:]
    if inspect_accept is not None:
        insp = (
            c.env["fix.procurement.inspection"]
            .with_user(c.receiver)
            .create({"receipt_line_id": rline.id, "qty_accepted": inspect_accept})
        )
        insp.with_user(c.receiver).action_confirm()
    return rline


def _bill(c, po, qty, price, ref, product=None):
    return c.env["fix.vendor.invoice"].create(
        {
            "vendor_id": po.vendor_id.id,
            "invoice_ref": ref,
            "requisition_id": po.id,
            "operating_unit_id": c.ou.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": (product or c.prod).id,
                        "description": "A06M16T line",
                        "quantity": qty,
                        "unit_price": price,
                        "tds_category": "supply_of_goods",
                    },
                )
            ],
        }
    )


def _maverick_po(c, vendor=None, price=1000.0, qty=10.0, user=None, **kw):
    vals = {
        "operating_unit_id": c.ou.id,
        "vendor_id": (vendor or c.vendor).id,
        "line_ids": [(0, 0, {"product_id": c.prod.id, "qty_ordered": qty, "unit_price": price})],
    }
    vals.update(kw)
    return c.env["fix.purchase.order"].with_user(user or c.buyer).create(vals)


def _rfq(c, open_=True, **kw):
    # FR-PRO-011 (19 Nov 2026): an RFQ opens with its invited suppliers and a
    # response deadline; _bid invites a bidder the test brings in later
    vals = {
        "description": "A06M16T RFQ",
        "product_id": c.prod.id,
        "qty": 10,
        "target_price": 1000,
        "invited_vendor_ids": [(6, 0, (c.vendor | c.vendor4 | c.vendor5).ids)],
        "response_deadline": date.today() + timedelta(days=7),
    }
    vals.update(kw)
    r = c.env["fix.procurement.rfq"].with_user(c.buyer).create(vals)
    if open_:
        r.with_user(c.buyer).action_open()
    return r


def _bid(c, r, vendor, price, user=None, **kw):
    if r.state in ("draft", "open") and vendor not in r.invited_vendor_ids:
        r.sudo().write({"invited_vendor_ids": [(4, vendor.id)]})
    vals = {"rfq_id": r.id, "vendor_id": vendor.id, "unit_price": price}
    vals.update(kw)
    return c.env["fix.procurement.bid"].with_user(user or c.buyer).create(vals)


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
        req_ = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req_
        s.request = req_

    as_user(c.buyer)
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw), as_user=as_user
        )
    finally:
        g.request, s.request = old_g, old_s


@pytest.fixture
def portal(c, monkeypatch):
    from odoo.addons.cd_vendor_portal.controllers import vendor_api

    group = c.env.ref("cd_vendor_portal.group_fix_vendor_portal")
    user = (
        c.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A06M16T vendor login",
                "login": "a06m16t_vendor@vendor.test",
                "partner_id": c.vendor.id,
                "group_ids": [(6, 0, [group.id])],
            }
        )
    )
    monkeypatch.setattr(vendor_api, "request", types.SimpleNamespace(env=c.env(user=user.id)))
    return types.SimpleNamespace(ctl=vendor_api.VendorApiController(), user=user)


# =================================================================== R: requisition approval
def test_m16_R01_requester_cannot_approve_own_requisition(c):
    r = _req(c, 24000)
    r.with_user(c.requester).action_submit()
    assert r.state == "submitted" and r.approval_state == "pending"
    assigned = r.approval_request_id.task_ids.mapped("assigned_user_id")
    assert c.requester not in assigned and c.t2 in assigned
    with pytest.raises(UserError):
        r.with_user(c.requester).action_approve()
    # even a requester who holds the tier is never routed to and cannot decide
    holder = _user(c.env, "a06m16t_selfapprover", [T[2]])
    emp = c.env["hr.employee"].create({"name": "self", "user_id": holder.id})
    own = _req(c, 24000, user=holder, requested_by=emp.id)
    own.with_user(holder).action_submit()
    assert holder not in own.approval_request_id.task_ids.mapped("assigned_user_id")
    assert own.state == "submitted"


def test_m16_R02_plain_user_cannot_approve(c):
    r = _req(c, 30000)
    r.with_user(c.requester).action_submit()
    with pytest.raises(UserError):
        r.with_user(c.clerk2).action_approve()
    assert r.state == "submitted"


def test_m16_R03_cfo_tier_holder_approves_via_inbox(c):
    """The CFO approves a 1M requisition from the inbox (tier 4); the IT
    administrator (base.group_system) is no approver."""
    r = _req(c, 1_000_000)
    r.with_user(c.requester).action_submit()
    assert r._dofa_current_tier() == "tier_4"
    admin = c.env.ref("base.user_admin")
    assert admin not in r.approval_request_id.task_ids.mapped("assigned_user_id")
    _decide(r, c.cfo)
    assert r.state == "approved" and r.dofa_approved_by == c.cfo


def test_m16_R04_admin_cannot_approve_directly(c):
    r = _req(c, 5_000_000)
    r.with_user(c.requester).action_submit()
    with pytest.raises(UserError):
        r.with_user(c.env.ref("base.user_admin")).action_approve()
    assert r.state == "submitted" and r._dofa_current_tier() == "tier_5"


def test_m16_R05_state_write_refused(c):
    r = _req(c, 5_000_000)
    with pytest.raises(UserError, match=GUARD):
        r.with_user(c.requester).write({"state": "approved"})


def test_m16_R06_create_born_approved_refused(c):
    with pytest.raises(UserError, match=GUARD):
        _req(c, 5_000_000, state="approved")


def test_m16_R07_amount_raised_after_approval_voids(c):
    r = _approved_req(c, 20000)
    r.with_user(c.requester).write({"estimate_amount": 5_000_000})
    assert r.state == "draft" and not r.dofa_approved and r.approval_state == "none"
    assert c.requester in r.pinned_changed_by_ids
    with pytest.raises(UserError):
        r.with_user(c.buyer).action_convert_to_po()


def test_m16_R08_vendor_swapped_after_approval_voids(c):
    r = _approved_req(c, 20000)
    r.with_user(c.requester).write({"vendor_id": c.vendor3.id})
    assert r.state == "draft" and not r.dofa_approved
    with pytest.raises(UserError):
        r.with_user(c.buyer).action_convert_to_po()


def test_m16_R09_split_requisitions_summed_for_the_tier(c):
    """Three 24,999 requisitions of one requester for one category inside the
    window: the third is tiered on 74,997 (tier 3), not 24,999 (tier 2)."""
    reqs = []
    for _ in range(3):
        r = _req(c, 24999)
        r.with_user(c.requester).action_submit()
        reqs.append(r)
    third = reqs[-1]
    assert third.split_prior_amount == pytest.approx(49998)
    assert set(third.split_requisition_ids.ids) == {reqs[0].id, reqs[1].id}
    assert third._dofa_current_tier() == "tier_3"
    assert c.t3 in third.approval_request_id.task_ids.mapped("assigned_user_id")
    assert c.t2 not in third.approval_request_id.task_ids.mapped("assigned_user_id")


def test_m16_R09b_split_window_is_configurable(c):
    c.env["ir.config_parameter"].set_param("cd_requisition.split_window_days", "0")
    for _ in range(3):
        r = _req(c, 24999)
        r.with_user(c.requester).action_submit()
    assert r.split_prior_amount == 0 and r._dofa_current_tier() == "tier_2"


def test_m16_R10_approve_from_rejected_and_converted_refused(c):
    r = _req(c, 1000)
    r.with_user(c.requester).action_submit()
    task = _inbox(r, c.t2)
    task.with_user(c.t2).action_reject(comment="not needed")
    assert r.state == "rejected"
    with pytest.raises(UserError):
        r.with_user(c.t2).action_approve()
    r2 = _approved_req(c, 1000)
    r2.with_user(c.buyer).action_convert_to_po()
    with pytest.raises(UserError):
        r2.with_user(c.t2).action_approve()
    assert (r.state, r2.state) == ("rejected", "converted")


def test_m16_R11_convert_needs_approved(c):
    r = _req(c, 1000)
    with pytest.raises(UserError):
        r.with_user(c.buyer).action_convert_to_po()


def test_m16_R12_convert_to_prospect_or_unregistered_refused(c):
    c.env["fix.supplier"].create({"name": "prospect", "partner_id": c.vendor2.id})
    for vendor in (c.vendor2, c.vendor3):
        r = _approved_req(c, 1000, vendor_id=vendor.id)
        with pytest.raises(UserError, match="not an active supplier"):
            r.with_user(c.buyer).action_convert_to_po()
        assert r.state == "approved" and not r.purchase_order_id


def test_m16_R13_code_created_requisition_is_submitted_not_approved(c):
    """B3's contract: a requisition created by code and submitted goes into the
    routed approval, never born approved. It states its cost centre and date like
    any other; only one M43 raises from a plan is exempt (cd_demand_plan's suite)."""
    r = (
        c.env["fix.requisition"]
        .with_user(c.clerk2)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "requested_by": c.emp.id,
                "description": "Planned order",
                "product_id": c.prod.id,
                "qty": 1000,
                "estimate_amount": 10_000_000,
            }
        )
    )
    with pytest.raises(UserError, match="cost centre"):
        r.with_user(c.clerk2).action_submit()
    assert r.state == "draft"
    r.with_user(c.clerk2).write({"cost_centre": "CC-PLAN", "required_by": ACK_DATE})
    r.with_user(c.clerk2).action_submit()
    assert r.state == "submitted" and r.approval_state == "pending"
    assert c.md in r.approval_request_id.task_ids.mapped("assigned_user_id")
    assert c.clerk2 not in r.approval_request_id.task_ids.mapped("assigned_user_id")


def test_m16_R13b_submit_without_any_approver_stays_submitted(c):
    """With nobody holding the tier, submission still works by code and the
    requisition waits (it is never approved by default)."""
    c.md.write({"group_ids": [(3, c.env.ref(T[5]).id)]})
    r = _req(c, 10_000_000)
    r.with_user(c.requester).action_submit()
    holders = c.env.ref(T[5]).all_user_ids
    if holders - c.requester:
        pytest.skip("this database has tier-5 holders")
    assert r.state == "submitted" and r.approval_state == "none" and not r.dofa_approved


def test_m16_R14_zero_value_requisition_refused(c):
    r = _req(c, 0)
    with pytest.raises(UserError, match="zero-value"):
        r.with_user(c.requester).action_submit()


def test_m16_R15_matrix_group_cannot_redirect_approval(c):
    """The M63 rule book is user-writable: a row naming base.group_user does not
    route the requisition to a clerk."""
    c.env["fix.approval.matrix"].create(
        {
            "name": "A06 forged",
            "decision_domain": "requisition",
            "res_model": "fix.requisition",
            "approver_group_id": c.env.ref("base.group_user").id,
            "threshold": 0,
            "approver_role": "R00",
        }
    )
    r = _req(c, 20000)
    r.with_user(c.requester).action_submit()
    assigned = r.approval_request_id.task_ids.mapped("assigned_user_id")
    assert c.clerk2 not in assigned and c.t2 in assigned


# =================================================================== P: purchase order
def test_m16_P01_po_without_requisition_or_approval_cannot_be_sent(c):
    o = _maverick_po(c, price=500000, qty=10)
    with pytest.raises(UserError):
        o.with_user(c.buyer).action_send()
    with pytest.raises(UserError, match="BRU-PRO-01"):
        o.with_user(c.buyer).action_submit_for_approval(justification="urgent")
    assert o.state == "draft"
    with pytest.raises(AccessError):
        _maverick_po(c, user=c.clerk2)


def test_m16_P01b_manager_exception_then_approval_sends(c):
    o = _maverick_po(c, price=1000, qty=10)
    with pytest.raises(UserError, match="Procurement Manager"):
        o.with_user(c.buyer).action_record_requisition_exception(reason="x" * 20)
    own = _maverick_po(c, user=c.manager)
    with pytest.raises(UserError, match="Segregation"):
        own.with_user(c.manager).action_record_requisition_exception(
            reason="sole stockist for this part"
        )
    o.with_user(c.manager).action_record_requisition_exception(reason="sole stockist for this part")
    o.with_user(c.buyer).action_submit_for_approval()
    _decide(o, c.t2)
    o.with_user(c.buyer).action_send()
    assert o.state == "sent" and o.no_requisition_exception and o.exception_by_id == c.manager


def test_m16_P02_po_to_suspended_or_unregistered_supplier_refused(c):
    c.env["fix.supplier"].create(
        {"name": "susp", "partner_id": c.vendor2.id, "status": "suspended"}
    )
    for vendor in (c.vendor2, c.vendor3):
        o = _maverick_po(c, vendor=vendor)
        o.with_user(c.manager).action_record_requisition_exception(
            reason="test of the supplier gate"
        )
        with pytest.raises(UserError, match="not an active supplier"):
            o.with_user(c.buyer).action_submit_for_approval(justification="gate test")
        with pytest.raises(UserError):
            o.with_user(c.buyer).action_send()


def test_m16_P02b_supplier_suspended_after_approval_blocks_send(c):
    po = _approved_po(c)
    c.sup.sudo()._a06_set_status("suspended", "test")
    with pytest.raises(UserError, match="not an active supplier"):
        po.with_user(c.buyer).action_send()


def test_m16_P03_price_raised_after_acknowledgement_refused(c):
    po = _sent_po(c)
    po.with_user(c.buyer).action_acknowledge_on_behalf(
        evidence="vendor e-mail 2026-11-03 #4411", confirmed_date=ACK_DATE
    )
    with pytest.raises(UserError, match="change order"):
        po.line_ids.with_user(c.buyer).write({"unit_price": 100000})


def test_m16_P04_qty_and_vendor_changed_after_acknowledgement_refused(c):
    po = _sent_po(c)
    po.with_user(c.buyer).action_acknowledge_on_behalf(
        evidence="vendor e-mail 2026-11-03 #4412", confirmed_date=ACK_DATE
    )
    with pytest.raises(UserError):
        po.line_ids.with_user(c.buyer).write({"qty_ordered": 1000})
    with pytest.raises(UserError):
        po.with_user(c.buyer).write({"vendor_id": c.vendor4.id})


def test_m16_P05_line_added_after_acknowledgement_refused(c):
    po = _sent_po(c)
    with pytest.raises(UserError):
        po.with_user(c.buyer).write(
            {
                "line_ids": [
                    (0, 0, {"product_id": c.prod2.id, "qty_ordered": 500, "unit_price": 900})
                ]
            }
        )
    assert len(po.line_ids) == 1


def test_m16_P05b_change_order_is_a_new_approved_revision(c):
    po = _sent_po(c)
    po.with_user(c.buyer).action_acknowledge_on_behalf(
        evidence="vendor e-mail 2026-11-03 #4413", confirmed_date=ACK_DATE
    )
    co = c.env["fix.purchase.order"].browse(
        po.with_user(c.buyer).action_create_change_order()["change_order_ids"]
    )
    assert co.revision == 1 and co.revision_of_id == po and co.state == "draft"
    co.line_ids.with_user(c.buyer).write({"unit_price": 12000})
    with pytest.raises(UserError, match="not been approved"):
        co.with_user(c.buyer).action_send()
    co.with_user(c.buyer).action_submit_for_approval(justification="price change agreed")
    _decide(co, c=c)
    co.with_user(c.buyer).action_send()
    assert co.state == "sent" and po.state == "superseded"


def test_m16_P05c_draft_change_after_approval_voids_po_approval(c):
    po = _approved_po(c)
    po.line_ids.with_user(c.buyer).write({"unit_price": 99999})
    assert po.approval_state == "none" and not po.dofa_approved
    with pytest.raises(UserError):
        po.with_user(c.buyer).action_send()
    po.with_user(c.buyer).action_submit_for_approval()
    assert c.buyer not in po.approval_request_id.task_ids.mapped("assigned_user_id")
    with pytest.raises(UserError):
        po.with_user(c.buyer).action_approve()


def test_m16_P06_state_write_refused(c):
    o = _maverick_po(c)
    with pytest.raises(UserError, match=GUARD):
        o.with_user(c.buyer).write({"state": "received"})


def test_m16_P07_send_from_wrong_state_refused(c):
    o = _maverick_po(c)
    o.with_user(c.buyer).action_cancel(reason="duplicate")
    with pytest.raises(UserError):
        o.with_user(c.buyer).action_send()
    o2 = _sent_po(c)
    _receive(c, o2)
    with pytest.raises(UserError):
        o2.with_user(c.buyer).action_send()


def test_m16_P08_requester_or_buyer_cannot_receive(c):
    po = _sent_po(c)
    both = _user(c.env, "a06m16t_buyer_receiver", [GB, GR])
    po_own = _maverick_po(c, user=both)
    po_own.with_user(c.manager).action_record_requisition_exception(reason="sod test exception")
    po_own.with_user(both).action_submit_for_approval(justification="sod")
    _decide(po_own, c=c)
    po_own.with_user(both).action_send()
    with pytest.raises(UserError, match="SOD-02"):
        po_own.with_user(both).action_record_receipt({po_own.line_ids.id: 1})
    req_receiver = _user(c.env, "a06m16t_req_receiver", [GR])
    emp = c.env["hr.employee"].create({"name": "rr", "user_id": req_receiver.id})
    po2 = _sent_po(c, requested_by=emp.id)
    with pytest.raises(UserError, match="SOD-02"):
        po2.with_user(req_receiver).action_record_receipt({po2.line_ids.id: 1})
    with pytest.raises(UserError):
        po.with_user(c.buyer).action_record_receipt({po.line_ids.id: 1})


def test_m16_P09_receipt_on_draft_and_cancelled_refused(c):
    o = _maverick_po(c)
    o2 = _maverick_po(c)
    o2.with_user(c.buyer).action_cancel(reason="duplicate")
    for x in (o, o2):
        with pytest.raises(UserError, match="sent or acknowledged"):
            x.with_user(c.receiver).action_record_receipt({x.line_ids.id: 10})


def test_m16_P10_empty_po_never_received(c):
    o = (
        c.env["fix.purchase.order"]
        .with_user(c.buyer)
        .create({"operating_unit_id": c.ou.id, "vendor_id": c.vendor.id})
    )
    with pytest.raises(UserError):
        o.with_user(c.receiver).action_record_receipt({})
    with pytest.raises(UserError, match="no lines"):
        o.with_user(c.buyer).action_send()
    assert o.state == "draft"


def test_m16_P11_over_receipt_refused(c):
    po = _sent_po(c)
    with pytest.raises(UserError, match="outside"):
        po.with_user(c.receiver).action_record_receipt({po.line_ids.id: 3})


def test_m16_P12_non_positive_qty_refused(c):
    with pytest.raises(REFUSED):
        _maverick_po(c, qty=0)
        c.env.flush_all()


def test_m16_P13_qty_received_cannot_be_typed(c):
    po = _sent_po(c)
    with pytest.raises((UserError, AccessError)):
        po.line_ids.with_user(c.buyer).write({"qty_received": 2})
    inv = _bill(c, po, 2, 10000, "A06M16T-P13")
    assert inv.match_state == "blocked"


def test_m16_P14_receipt_needs_inspection_before_it_is_matchable(c):
    po = _sent_po(c)
    rline = _receive(c, po)
    assert po.state == "received" and rline.inspection_state == "pending"
    assert rline.qty_accepted == 0 and po.line_ids.qty_accepted == 0
    inv = _bill(c, po, 2, 10000, "A06M16T-P14")
    assert inv.match_state == "blocked" and "awaiting inspection" in inv.match_detail


def test_m16_P15_dates_not_editable(c):
    po = _approved_po(c)
    po.with_user(c.buyer).write({"promised_date": "2026-10-01"})
    assert po.approval_state == "none"
    po.with_user(c.buyer).action_submit_for_approval()
    _decide(po, c=c)
    po.with_user(c.buyer).action_send()
    _receive(c, po)
    with pytest.raises(UserError):
        po.with_user(c.buyer).write({"received_on": "2026-09-30"})
    with pytest.raises(UserError):
        po.with_user(c.buyer).write({"promised_date": "2026-12-31"})
    assert po.received_on == fields.Date.context_today(po)


def test_m16_P16_buyer_cannot_acknowledge_for_vendor_without_evidence(c):
    po = _sent_po(c)
    with pytest.raises(UserError, match="P05 portal"):
        po.with_user(c.buyer).action_acknowledge()
    with pytest.raises(UserError, match="confirmation"):
        po.with_user(c.buyer).action_acknowledge_on_behalf(evidence="")
    po.with_user(c.buyer).action_acknowledge_on_behalf(
        evidence="vendor letter ref GS/2026/118", confirmed_date=str(ACK_DATE)
    )
    assert po.state == "acknowledged" and po.ack_channel == "buyer_on_behalf"
    assert po.vendor_confirmed_date == ACK_DATE and po.ack_by_id == c.buyer


def test_m16_P17_requisition_link_cannot_be_forged(c):
    o = _maverick_po(c, price=50000)
    r = _req(c, amount=10)
    with pytest.raises(UserError, match=GUARD):
        o.with_user(c.buyer).write({"requisition_id": r.id})
    from odoo.addons.cd_p03_portal.controllers.a06 import m16 as rep

    pack = rep.maverick_spend(c.env(user=c.buyer.id))
    assert o.name in [row["po"] for row in pack["rows"]]


# =================================================================== M: three-way match
def test_m16_M01_price_above_po_blocks(c):
    po = _sent_po(c)
    _receive(c, po, inspect_accept=2)
    assert _bill(c, po, 2, 20000, "A06M16T-M01").match_state == "blocked"


def test_m16_M01b_proper_path_matches(c):
    po = _sent_po(c)
    _receive(c, po, inspect_accept=2)
    inv = _bill(c, po, 2, 10000, "A06M16T-M01b")
    assert inv.match_state == "matched", inv.match_detail


def test_m16_M02_received_po_price_cannot_be_raised(c):
    po = _sent_po(c)
    _receive(c, po, inspect_accept=2)
    inv = _bill(c, po, 2, 20000, "A06M16T-M02")
    with pytest.raises(UserError):
        po.line_ids.with_user(c.buyer).write({"unit_price": 20000})
    inv.invalidate_recordset()
    assert inv.match_state == "blocked"


def test_m16_M03_two_bills_for_one_receipt(c):
    po = _sent_po(c)
    _receive(c, po, inspect_accept=2)
    a = _bill(c, po, 2, 10000, "A06M16T-M03-A")
    b = _bill(c, po, 2, 10000, "A06M16T-M03-B")
    assert a.match_state == "matched" and b.match_state == "blocked"
    assert "already invoiced" in b.match_detail
    # rejecting the first bill releases the receipt for the second
    a.with_context(ap_internal=True).write({"approval_state": "rejected"})
    b.invalidate_recordset()
    assert b.match_state == "matched"


def test_m16_M04_split_lines_exceed_received(c):
    po = _sent_po(c)
    _receive(c, po, inspect_accept=2)
    inv = c.env["fix.vendor.invoice"].create(
        {
            "vendor_id": po.vendor_id.id,
            "invoice_ref": "A06M16T-M04",
            "requisition_id": po.id,
            "operating_unit_id": c.ou.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": c.prod.id,
                        "description": "a",
                        "quantity": 2,
                        "unit_price": 10000,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": c.prod.id,
                        "description": "b",
                        "quantity": 2,
                        "unit_price": 10000,
                    },
                ),
            ],
        }
    )
    assert inv.match_state == "blocked"


def test_m16_M05_failed_inspection_blocks(c):
    po = _sent_po(c)
    rline = _receive(c, po, inspect_accept=0)
    assert rline.inspection_state == "failed" and po.line_ids.qty_accepted == 0
    inv = _bill(c, po, 2, 10000, "A06M16T-M05")
    assert inv.match_state == "blocked" and "rejected at inspection" in inv.match_detail
    events = c.env["fix.event.outbox"].search([("event_type", "=", "inspection.rejected")])
    assert events


def test_m16_M06_raiser_receiver_cannot_approve_the_bill(c):
    acct = _user(c.env, "a06m16t_acct_buyer", ["account.group_account_user", GB])
    po = _sent_po(c)
    po.sudo()._guarded().write({"buyer_id": acct.id})
    _receive(c, po, inspect_accept=2)
    inv = _bill(c, po, 2, 10000, "A06M16T-M06")
    inv.with_context(ap_internal=True).write(
        {
            "approval_state": "to_approve",
            "approval_level": 0,
            "approval_levels_required": 2,
            "submitted_by": c.clerk2.id,
        }
    )
    with pytest.raises(UserError, match="SOD"):
        inv.with_user(acct).action_approve()
    receiver_acct = c.receiver
    receiver_acct.write({"group_ids": [(4, c.env.ref("account.group_account_user").id)]})
    with pytest.raises(UserError, match="SOD"):
        inv.with_user(receiver_acct).action_approve()


# =================================================================== B: RFQ / bids / award
def test_m16_B01_bid_on_draft_rfq_refused(c):
    r = _rfq(c, open_=False)
    with pytest.raises(UserError, match="open"):
        _bid(c, r, c.vendor, 900)


def test_m16_B02_late_bid_after_close_refused(c):
    r = _rfq(c)
    _bid(c, r, c.vendor, 1000)
    r.with_user(c.buyer).action_close()
    with pytest.raises(UserError, match="open"):
        _bid(c, r, c.vendor4, 500)


def test_m16_B03_bid_price_fixed_after_close(c):
    r = _rfq(c)
    b1 = _bid(c, r, c.vendor, 1000)
    _bid(c, r, c.vendor4, 800)
    r.with_user(c.buyer).action_close()
    with pytest.raises(UserError, match="sealed"):
        b1.with_user(c.buyer).write({"unit_price": 700})


def test_m16_B04_bids_sealed_while_open(c):
    r = _rfq(c)
    _bid(c, r, c.vendor, 1000)
    _bid(c, r, c.vendor4, 800)
    assert not c.env["fix.procurement.bid"].with_user(c.buyer2).search([("rfq_id", "=", r.id)])
    assert not c.env["fix.procurement.bid"].with_user(c.clerk2).search([("rfq_id", "=", r.id)])
    assert len(c.env["fix.procurement.bid"].with_user(c.buyer).search([("rfq_id", "=", r.id)])) == 2
    r.with_user(c.buyer).action_close()
    assert (
        len(c.env["fix.procurement.bid"].with_user(c.buyer2).search([("rfq_id", "=", r.id)])) == 2
    )


def _closed_rfq(c, prices):
    r = _rfq(c)
    vendors = [c.vendor, c.vendor4, c.vendor5]
    bids = [_bid(c, r, vendors[i], p) for i, p in enumerate(prices)]
    r.with_user(c.buyer).action_close()
    return r, bids


def test_m16_B05_non_lowest_needs_rationale_and_second_person(c):
    r, (high, low, _mid) = _closed_rfq(c, [1500, 900, 1200])
    Award = c.env["fix.procurement.award"].with_user(c.buyer)
    with pytest.raises(UserError, match="BRU-PRO-07"):
        Award.create({"rfq_id": r.id, "bid_id": high.id})
    a = Award.create(
        {"rfq_id": r.id, "bid_id": high.id, "rationale": "shorter lead time, warranty"}
    )
    assert a.state == "proposed" and a.needs_approval and not a.is_lowest and a.lowest_bid_id == low
    assert r.state == "closed"
    with pytest.raises(UserError):
        a.with_user(c.buyer).action_decide()
    evaluator_approver = _user(c.env, "a06m16t_eval_appr", [GB, GA])
    own = c.env["fix.procurement.award"]
    a.with_user(c.buyer).action_cancel(reason="re-propose")
    own = own.with_user(evaluator_approver).create(
        {"rfq_id": r.id, "bid_id": high.id, "rationale": "shorter lead time, warranty"}
    )
    with pytest.raises(UserError, match="Segregation"):
        own.with_user(evaluator_approver).action_decide()
    own.with_user(c.papprover).action_decide()
    assert own.state == "decided" and high.state == "awarded" and low.state == "lost"
    assert own.approved_by_id == c.papprover and r.state == "awarded"


def test_m16_B05b_lowest_with_enough_bids_is_decided_by_the_buyer(c):
    r, (b1, b2, b3) = _closed_rfq(c, [1000, 1100, 1200])
    a = c.env["fix.procurement.award"].with_user(c.buyer).create({"rfq_id": r.id, "bid_id": b1.id})
    assert a.state == "decided" and a.is_lowest and not a.needs_approval
    assert (b1.state, b2.state, b3.state, r.state) == ("awarded", "lost", "lost", "awarded")


def test_m16_B06_award_on_open_rfq_refused(c):
    r = _rfq(c)
    b = _bid(c, r, c.vendor, 1000)
    with pytest.raises(UserError, match="closes"):
        c.env["fix.procurement.award"].with_user(c.buyer).create(
            {"rfq_id": r.id, "bid_id": b.id, "rationale": "x", "exception_reason": "y"}
        )


def test_m16_B07_second_award_refused(c):
    r, (b1, b2, _b3) = _closed_rfq(c, [900, 1200, 1300])
    Award = c.env["fix.procurement.award"].with_user(c.buyer)
    Award.create({"rfq_id": r.id, "bid_id": b1.id})
    with pytest.raises(UserError):
        Award.create({"rfq_id": r.id, "bid_id": b2.id, "rationale": "changed mind"})
    assert b1.state == "awarded" and b2.state == "lost"


def test_m16_B08_award_foreign_bid_refused(c):
    r1 = _rfq(c)
    r2 = _rfq(c)
    b = _bid(c, r2, c.vendor, 1000)
    _bid(c, r1, c.vendor, 1000)
    r1.with_user(c.buyer).action_close()
    with pytest.raises(UserError, match="belong"):
        c.env["fix.procurement.award"].with_user(c.buyer).create({"rfq_id": r1.id, "bid_id": b.id})


def test_m16_B09_award_to_unregistered_expired_or_own_company_refused(c):
    r = _rfq(c)
    unreg = _bid(c, r, c.vendor3, 800)
    expired = _bid(c, r, c.vendor, 850, valid_until="2025-01-01")
    own_partner = c.env.company.partner_id
    own = _bid(c, r, own_partner, 700)
    r.with_user(c.buyer).action_close()
    Award = c.env["fix.procurement.award"].with_user(c.buyer)
    for bid, why in (
        (unreg, "not an active|supplier record"),
        (expired, "expired"),
        (own, "own partner"),
    ):
        with pytest.raises(UserError, match=why):
            Award.create(
                {"rfq_id": r.id, "bid_id": bid.id, "rationale": "x", "exception_reason": "y"}
            )


def test_m16_B10_minimum_bid_count_needs_exception_and_approver(c):
    r = _rfq(c)
    b = _bid(c, r, c.vendor, 1_000_000)
    r.with_user(c.buyer).action_close()
    Award = c.env["fix.procurement.award"].with_user(c.buyer)
    with pytest.raises(UserError, match="BRU-PRO-06"):
        Award.create({"rfq_id": r.id, "bid_id": b.id})
    a = Award.create({"rfq_id": r.id, "bid_id": b.id, "exception_reason": "OEM sole source letter"})
    assert a.state == "proposed" and a.needs_approval and r.state == "closed"
    a.with_user(c.papprover).action_decide()
    assert r.state == "awarded"


def test_m16_B11_rfq_and_bid_state_forgery_refused(c):
    r = _rfq(c, open_=False)
    r2 = _rfq(c)
    b = _bid(c, r2, c.vendor4, 5000)
    with pytest.raises(UserError, match=GUARD):
        r.with_user(c.buyer).write({"state": "awarded"})
    with pytest.raises(UserError, match=GUARD):
        b.with_user(c.buyer).write({"state": "awarded"})


def test_m16_B12_po_from_award_cannot_exceed_awarded_price(c):
    req = _approved_req(c, 10000, qty=10)
    r, (b1, _b2, _b3) = _closed_rfq(c, [1000, 1100, 1200])
    r.sudo()._guarded().write({"requisition_id": req.id})
    a = c.env["fix.procurement.award"].with_user(c.buyer).create({"rfq_id": r.id, "bid_id": b1.id})
    a.with_user(c.buyer).action_create_po()
    po = a.purchase_order_id
    assert po.award_id == a and po.requisition_id == req and req.state == "converted"
    assert po.line_ids.unit_price == 1000
    po.line_ids.with_user(c.buyer).write({"unit_price": 2000})
    with pytest.raises(UserError, match="awarded bid"):
        po.with_user(c.buyer).action_submit_for_approval(justification="award")
    po.line_ids.with_user(c.buyer).write({"unit_price": 1000})
    po.with_user(c.buyer).action_submit_for_approval()
    _decide(po, c=c)
    po.with_user(c.buyer).action_send()
    assert po.state == "sent"


def test_m16_B13_rfq_close_needs_bid(c):
    r = _rfq(c)
    with pytest.raises(UserError):
        r.with_user(c.buyer).action_close()
    with pytest.raises(UserError):
        r.with_user(c.buyer).action_open()


# =================================================================== K: blanket agreements
def _blanket(c, cap=100000, valid_from="2026-01-01", valid_to="2026-12-31", activate=True):
    k = (
        c.env["fix.procurement.blanket"]
        .with_user(c.buyer)
        .create(
            {
                "vendor_id": c.vendor.id,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "cap_amount": cap,
            }
        )
    )
    if activate:
        k.with_user(c.papprover).action_activate()
    return k


def test_m16_K01_blanket_cap_enforced_at_send(c):
    k = _blanket(c, cap=30000)
    po = _approved_po(c, 20000)
    po.with_user(c.buyer).write({"blanket_id": k.id})
    assert po.approval_state == "none"
    po.with_user(c.buyer).action_submit_for_approval()
    _decide(po, c=c)
    po.with_user(c.buyer).action_send()
    assert k.consumed_amount == pytest.approx(20000)
    po2 = _approved_po(c, 20000)
    po2.with_user(c.buyer).write({"blanket_id": k.id})
    with pytest.raises(UserError, match="exceed"):
        po2.with_user(c.buyer).action_submit_for_approval()


def test_m16_K02_only_linked_issued_call_offs_consume(c):
    k = _blanket(c)
    _maverick_po(c, price=1000, qty=10, date_order="2026-11-03 10:00:00")
    draft_linked = _maverick_po(c, price=1000, qty=10)
    draft_linked.with_user(c.buyer).write({"blanket_id": k.id})
    k.invalidate_recordset()
    assert k.consumed_amount == 0 and k.remaining_amount == 100000


def test_m16_K03_active_cap_cannot_be_raised(c):
    k = _blanket(c)
    with pytest.raises(UserError, match="Revise"):
        k.with_user(c.buyer).write({"cap_amount": 50_000_000, "valid_to": "2030-12-31"})
    k.with_user(c.buyer).action_revise()
    buyer_approver = _user(c.env, "a06m16t_buyer_approver", [GB, GA])
    k.with_user(buyer_approver).write({"cap_amount": 200000})
    with pytest.raises(UserError, match="Segregation"):
        k.with_user(buyer_approver).action_activate()
    k.with_user(c.papprover).action_activate()
    assert k.state == "active" and k.cap_amount == 200000


def test_m16_K04_blanket_born_draft_and_expires_by_cron(c):
    k = _blanket(c, valid_from="2025-01-01", valid_to="2025-12-31", activate=False)
    assert k.state == "draft"
    with pytest.raises(UserError, match="ended"):
        k.with_user(c.papprover).action_activate()
    live = _blanket(c, valid_from="2026-01-01", valid_to=str(date.today() + timedelta(days=5)))
    live.sudo()._guarded().write({"valid_to": date.today() - timedelta(days=1)})
    c.env["fix.procurement.blanket"]._cron_expire_blankets()
    assert live.state == "expired"
    cron = c.env.ref("cd_requisition.ir_cron_fix_procurement_blanket_expiry")
    assert cron.active and "_cron_expire_blankets" in cron.code


def test_m16_K05_blanket_dates_constraint(c):
    with pytest.raises(REFUSED):
        c.env["fix.procurement.blanket"].with_user(c.buyer).create(
            {"vendor_id": c.vendor.id, "valid_from": "2026-12-31", "valid_to": "2026-01-01"}
        )
        c.env.flush_all()


# =================================================================== I/X: inspection, expediting
def test_m16_I01_accepted_above_received_refused(c):
    po = _sent_po(c)
    rline = _receive(c, po)
    with pytest.raises(REFUSED):
        c.env["fix.procurement.inspection"].with_user(c.receiver).create(
            {"receipt_line_id": rline.id, "qty_accepted": 9}
        )
        c.env.flush_all()


def test_m16_I02_outcome_derived_not_typed(c):
    po = _sent_po(c)
    rline = _receive(c, po)
    with pytest.raises(UserError, match=GUARD):
        c.env["fix.procurement.inspection"].with_user(c.receiver).create(
            {"receipt_line_id": rline.id, "qty_accepted": 0, "outcome": "accepted"}
        )
    i = (
        c.env["fix.procurement.inspection"]
        .with_user(c.receiver)
        .create({"receipt_line_id": rline.id, "qty_accepted": 0})
    )
    assert i.outcome == "rejected" and i.qty_received == 2 and i.product_id == c.prod
    unlinked = (
        c.env["fix.procurement.inspection"]
        .with_user(c.receiver)
        .create(
            {
                "receipt_ref": "GRN-X",
                "product_id": c.prod.id,
                "qty_received": 10,
                "qty_accepted": 10,
            }
        )
    )
    with pytest.raises(UserError, match="receipt line"):
        unlinked.with_user(c.receiver).action_confirm()


def test_m16_I03_done_inspection_is_final(c):
    po = _sent_po(c)
    rline = _receive(c, po, inspect_accept=1)
    i = rline.inspection_ids
    with pytest.raises(UserError, match="final"):
        i.with_user(c.receiver).write({"qty_accepted": 2})
    with pytest.raises(UserError):
        i.with_user(c.receiver).write({"state": "draft"})
    assert i.qty_accepted == 1 and rline.inspection_state == "partial"


def test_m16_X01_expedite_state_forgery_refused(c):
    o = _maverick_po(c)
    e = (
        c.env["fix.procurement.expedite"]
        .with_user(c.buyer)
        .create({"purchase_order_id": o.id, "reason": "late"})
    )
    with pytest.raises(UserError, match=GUARD):
        e.with_user(c.buyer).write({"state": "resolved"})
    with pytest.raises(UserError, match="resolved"):
        e.with_user(c.buyer).action_resolve()
    e.with_user(c.buyer).action_chase()
    e.with_user(c.buyer).action_resolve(note="vendor shipped 2026-11-04, AWB 7781")
    assert e.state == "resolved" and e.resolved_on


def test_m16_X02_overdue_po_cron_opens_expedite(c):
    po = _approved_po(c)
    po.sudo()._guarded().write({"promised_date": date.today() - timedelta(days=3)})
    po.with_user(c.buyer).action_send()
    made = c.env["fix.purchase.order"]._cron_open_overdue_expedites()
    assert po in made.mapped("purchase_order_id")
    assert (
        not c.env["fix.purchase.order"]
        ._cron_open_overdue_expedites()
        .filtered(lambda e: e.purchase_order_id == po)
    )
    cron = c.env.ref("cd_requisition.ir_cron_fix_purchase_order_overdue")
    assert cron.active and "_cron_open_overdue_expedites" in cron.code


# =================================================================== W: P03 workspace path
def test_m16_W01_forms_offer_no_guarded_field_and_surfaces_have_actions(c):
    from odoo.addons.cd_p03_portal.controllers import form_fields
    from odoo.addons.cd_p03_portal.controllers.a06 import m16 as surf

    editable = form_fields.editable_by_model()
    for model in surf.SURFACES:
        guarded = c.env[model].browse()._fix_guarded_fields()
        assert not guarded & editable.get(model, set()), (
            model,
            guarded & editable.get(model, set()),
        )
    assert "action_approve" not in surf.SURFACES["fix.requisition"]["actions"]
    assert {"action_send", "action_submit_for_approval"} <= surf.SURFACES["fix.purchase.order"][
        "actions"
    ]


def test_m16_W02_p03_requisition_state_refused(c, p03):
    r = _req(c, amount=5_000_000)
    p03.as_user(c.requester)
    out = p03.write(model="fix.requisition", record_id=r.id, values={"state": "approved"})
    r.invalidate_recordset()
    assert "error" in out and r.state == "draft"


def test_m16_W03_p03_po_line_price_after_ack_refused(c, p03):
    po = _sent_po(c)
    po.with_user(c.buyer).action_acknowledge_on_behalf(
        evidence="vendor e-mail 2026-11-03 #4414", confirmed_date=ACK_DATE
    )
    out = p03.write(
        model="fix.purchase.order",
        record_id=po.id,
        values={},
        lines={
            "field": "line_ids",
            "rows": [{"id": po.line_ids.id, "values": {"unit_price": 9999}}],
        },
    )
    po.line_ids.invalidate_recordset()
    assert "error" in out and po.line_ids.unit_price == 10000


def test_m16_W04_p03_po_state_and_receipt_refused(c, p03):
    o = _maverick_po(c)
    out1 = p03.write(model="fix.purchase.order", record_id=o.id, values={"state": "received"})
    out2 = p03.write(
        model="fix.purchase.order",
        record_id=o.id,
        values={},
        lines={
            "field": "line_ids",
            "rows": [{"id": o.line_ids.id, "values": {"qty_received": 10}}],
        },
    )
    o.invalidate_recordset()
    assert "error" in out1 and o.state == "draft"
    assert "error" in out2 and o.line_ids.qty_received == 0


def test_m16_W05_p03_bid_reprice_after_close_refused(c, p03):
    r = _rfq(c)
    b = _bid(c, r, c.vendor, 1000)
    r.with_user(c.buyer).action_close()
    out = p03.write(model="fix.procurement.bid", record_id=b.id, values={"unit_price": 1})
    b.invalidate_recordset()
    assert "error" in out and b.unit_price == 1000


def test_m16_W06_p03_approve_is_not_a_record_action(c, p03):
    r = _req(c, amount=30000)
    r.with_user(c.requester).action_submit()
    out = p03.action(model="fix.requisition", ids=[r.id], method="action_approve")
    r.invalidate_recordset()
    assert not out.get("success") and r.state == "submitted"


def test_m16_W07_p03_award_without_rationale_refused(c, p03):
    r, (high, _low, _mid) = _closed_rfq(c, [1500, 900, 1000])
    out = p03.write(model="fix.procurement.award", values={"rfq_id": r.id, "bid_id": high.id})
    assert "error" in out and r.state == "closed"


def test_m16_W08_p03_buyer_runs_the_po_flow(c, p03):
    """Proper path through the workspace: request approval and send."""
    r = _approved_req(c, 20000)
    p03.as_user(c.buyer)
    out = p03.action(model="fix.requisition", ids=[r.id], method="action_convert_to_po")
    assert out.get("success"), out
    po = r.purchase_order_id
    out = p03.action(
        model="fix.purchase.order",
        ids=[po.id],
        method="action_submit_for_approval",
        kwargs={"justification": "AMC stock"},
    )
    assert out.get("success"), out
    _decide(po, c=c)
    out = p03.action(model="fix.purchase.order", ids=[po.id], method="action_send")
    assert out.get("success") and po.state == "sent", out


# =================================================================== V: P05 vendor portal
def test_m16_V01_portal_cannot_write_po_or_line(c, portal):
    po = _sent_po(c)
    for model, rec, vals in (
        ("fix.purchase.order", po, {"state": "received"}),
        ("fix.purchase.order.line", po.line_ids, {"unit_price": 9999}),
    ):
        with pytest.raises((AccessError, UserError)):
            c.env[model].with_user(portal.user).browse(rec.id).write(vals)


def test_m16_V02_portal_cannot_self_record_delivery(c, portal):
    po = _sent_po(c)
    out = portal.ctl.purchase_orders(po_id=po.id, action="deliver", receipts={po.line_ids.id: 2})
    assert out.get("error", {}).get("code") == "forbidden" and po.line_ids.qty_received == 0


def test_m16_V03_portal_cannot_ack_foreign_po(c, portal):
    po = _sent_po(c, vendor_id=c.vendor4.id)
    out = portal.ctl.purchase_orders(po_id=po.id, action="acknowledge")
    assert out.get("error", {}).get("code") == "no_po" and po.state == "sent"


def test_m16_V03b_vendor_acknowledges_own_po_with_date(c, portal):
    po = _sent_po(c)
    out = portal.ctl.purchase_orders(po_id=po.id, action="acknowledge", delivery_date=str(ACK_DATE))
    assert out == {"purchase_order": {"id": po.id, "state": "acknowledged"}}
    assert po.ack_channel == "portal" and po.ack_by_id == portal.user
    assert po.vendor_confirmed_date == ACK_DATE
    draft = _approved_po(c)
    listed = [row["id"] for row in portal.ctl.purchase_orders()["purchase_orders"]]
    assert po.id in listed and draft.id not in listed


def test_m16_V04_portal_bill_above_po_blocked(c, portal):
    po = _sent_po(c)
    _receive(c, po, inspect_accept=2)
    out = portal.ctl.invoices(
        invoice_ref="A06M16T-V04",
        po_id=po.id,
        lines=[{"product_id": c.prod.id, "description": "x", "quantity": 2, "unit_price": 50000}],
    )
    assert out["invoice"]["match_state"] == "blocked", out


def test_m16_V05_portal_cannot_double_bill_one_receipt(c, portal):
    po = _sent_po(c)
    _receive(c, po, inspect_accept=2)
    line = [{"product_id": c.prod.id, "description": "x", "quantity": 2, "unit_price": 10000}]
    a = portal.ctl.invoices(invoice_ref="A06M16T-V05-1", po_id=po.id, lines=line)
    b = portal.ctl.invoices(invoice_ref="A06M16T-V05-2", po_id=po.id, lines=line)
    assert (a["invoice"]["match_state"], b["invoice"]["match_state"]) == ("matched", "blocked")


def test_m16_V06_portal_cannot_pick_tds_category(c, portal):
    po = _sent_po(c)
    _receive(c, po, inspect_accept=2)
    c.env["fix.vendor.tax.profile"].create(
        {
            "partner_id": c.vendor.id,
            "taxpayer_type": "company",
            "default_tds_category": "supply_of_goods",
        }
    )
    out = portal.ctl.invoices(
        invoice_ref="A06M16T-V06",
        po_id=po.id,
        lines=[
            {
                "product_id": c.prod.id,
                "description": "x",
                "quantity": 2,
                "unit_price": 10000,
                "tds_category": "manpower_gross",
            }
        ],
    )
    inv = c.env["fix.vendor.invoice"].browse(out["invoice"]["id"])
    assert inv.line_ids.tds_category == "supply_of_goods"


def test_m16_V07_portal_refused_on_p03(c, p03, portal):
    po = _maverick_po(c)
    p03.as_user(portal.user)
    with pytest.raises(AccessError):
        p03.write(
            model="fix.purchase.order", record_id=po.id, values={"promised_date": "2026-12-01"}
        )


# =================================================================== events (P2)
def test_m16_E01_goods_received_carries_vendor_and_dates(c):
    import json

    po = _sent_po(c)
    _receive(c, po)
    row = c.env["fix.event.outbox"].search(
        [("event_type", "=", "goods.received"), ("aggregate_id", "=", po.line_ids.id)], limit=1
    )
    payload = json.loads(row.payload)
    assert payload["vendor_id"] == c.vendor.id and payload["po_id"] == po.id
    assert payload["received_on"] == str(fields.Date.context_today(po))
    assert payload["receipt_ref"].startswith("PGRN/")


# =================================================================== proper path, end to end
def test_m16_proper_path_requisition_to_matched_bill(c):
    po = _sent_po(c, 20000, qty=2)
    po.with_user(c.buyer).action_acknowledge_on_behalf(
        evidence="vendor e-mail 2026-11-03 #4420", confirmed_date=ACK_DATE
    )
    rline = _receive(c, po, inspect_accept=2)
    assert po.state == "received" and rline.inspection_state == "passed"
    assert po.line_ids.qty_received == 2 and po.line_ids.qty_accepted == 2
    inv = _bill(c, po, 2, 10000, "A06M16T-END")
    assert inv.match_state == "matched", inv.match_detail
    po.with_user(c.buyer).action_close()
    assert po.state == "closed"
