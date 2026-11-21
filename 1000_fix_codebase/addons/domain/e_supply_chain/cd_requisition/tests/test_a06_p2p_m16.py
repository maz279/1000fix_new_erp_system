# A06 ERP audit (20 Nov 2026), stream P2P: M16 procurement controls.
#
# Findings P03 P07 P11 P16 P21 P22 P23 P24 P29 P37 P38 P39 P40 and the D8
# limits (three quotes above BDT 50,000, emergency ceiling BDT 25,000). Each
# attack runs as a non-admin user holding the real role; rolled back.
import types
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
GB = "cd_requisition.group_fix_procurement_buyer"
GR = "cd_requisition.group_fix_procurement_receiver"
GA = "cd_requisition.group_fix_procurement_approver"
GM = "cd_requisition.group_fix_procurement_manager"
T = {n: "cd_entity_config.group_dofa_tier_%d" % n for n in range(1, 6)}
SOON = date.today() + timedelta(days=14)


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


def _active_supplier(env, partner, categ):
    sup = env["fix.supplier"].create(
        {
            "name": partner.name,
            "partner_id": partner.id,
            "status": "active",
            "approved_category_ids": [(6, 0, categ.ids)],
        }
    )
    for doc_type in ("trade_licence", "tin", "vat"):
        env["fix.supplier.document"].create(
            {
                "supplier_id": sup.id,
                "doc_type": doc_type,
                "number": "P2P-%s" % doc_type,
                "file_ref": "dms://p2p/%s" % doc_type,
                "state": "valid",
                "valid_to": date.today() + timedelta(days=365),
            }
        )
    return sup


def _rate(env, currency, day, bdt_per_unit):
    Rate = env["res.currency.rate"]
    Rate.search(
        [("currency_id", "=", currency.id), ("name", "=", day), ("company_id", "=", env.company.id)]
    ).unlink()
    Rate.create(
        {
            "currency_id": currency.id,
            "name": day,
            "company_id": env.company.id,
            "rate": 1.0 / bdt_per_unit,
        }
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.requester = _user(env, "p2p_requester")
    x.requester2 = _user(env, "p2p_requester2")
    x.colleague = _user(env, "p2p_colleague")
    x.buyer = _user(env, "p2p_buyer", [GB])
    x.buyer2 = _user(env, "p2p_buyer2", [GB])
    x.receiver = _user(env, "p2p_receiver", [GR])
    x.inspector = _user(env, "p2p_inspector", [GR])
    x.t2 = _user(env, "p2p_t2", [T[2]])
    x.t3 = _user(env, "p2p_t3", [T[3]])
    x.manager = _user(env, "p2p_manager", [GM])
    x.papprover = _user(env, "p2p_papprover", [GA])
    x.emp = env["hr.employee"].create({"name": "P2P Requester", "user_id": x.requester.id})
    x.emp2 = env["hr.employee"].create({"name": "P2P Requester Two", "user_id": x.requester2.id})
    x.categ = env["product.category"].create({"name": "P2P Compressors"})
    x.prod = env["product.product"].create({"name": "P2P Compressor", "categ_id": x.categ.id})
    x.vendor, x.vendor2 = env["res.partner"].create(
        [
            {"name": "P2P Vendor One", "is_company": True},
            {"name": "P2P Vendor Two", "is_company": True},
        ]
    )
    _active_supplier(env, x.vendor, x.categ)
    _active_supplier(env, x.vendor2, x.categ)
    x.usd = (
        env.ref("base.BDT")
        if env.company.currency_id == env.ref("base.USD")
        else env.ref("base.USD")
    )
    x.usd.active = True
    x.today = fields.Date.context_today(env.user)
    _rate(env, x.usd, x.today, 120.0)
    env["ir.config_parameter"].set_param("cd_requisition.receipt_inspection_required", "1")
    return x


def _req(c, amount=20000.0, user=None, **kw):
    vals = {
        "operating_unit_id": c.ou.id,
        "requested_by": c.emp.id,
        "description": "P2P requisition",
        "justification": "Compressors for AMC visits this month",
        "estimate_amount": amount,
        "product_id": c.prod.id,
        "qty": 2,
        "vendor_id": c.vendor.id,
        "cost_centre": "CC-P2P",
        "required_by": SOON,
    }
    vals.update(kw)
    return c.env["fix.requisition"].with_user(user or c.requester).create(vals)


def _decide(c, record):
    approver = {"tier_2": c.t2, "tier_3": c.t3}[record._dofa_current_tier()]
    task = record.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )
    assert task, record.approval_request_id.task_ids.mapped("assigned_user_id.login")
    task.with_user(approver).action_approve(comment="ok")


def _approved_po(c, amount=20000.0, **kw):
    r = _req(c, amount, **kw)
    r.with_user(c.requester).action_submit()
    _decide(c, r)
    r.with_user(c.buyer).action_convert_to_po()
    po = r.purchase_order_id
    po.with_user(c.buyer).action_submit_for_approval()
    _decide(c, po)
    return po


def _sent_po(c, amount=20000.0, **kw):
    po = _approved_po(c, amount, **kw)
    po.with_user(c.buyer).action_send()
    return po


# ----------------------------------------------------------------- P29
def test_p29_approval_stamps_the_rate_and_send_keeps_it(c):
    """Mutation: drop _a06_stamp_fx_rate from _a06_after_approve -> the rate
    is only stamped at send, at the send-day rate (125 below)."""
    po = _approved_po(c, 200.0, currency_id=c.usd.id)
    assert (po.fx_rate, po.fx_rate_date) == (120.0, c.today)
    _rate(c.env, c.usd, c.today, 125.0)  # the market moves before the send
    po.with_user(c.buyer).action_send()
    assert po.fx_rate == 120.0
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        po.with_user(c.buyer).write({"fx_rate": 1.0})


# ----------------------------------------------------------------- P03 / D8
def _closed_rfq(c, bids, qty=10):
    rfq = (
        c.env["fix.procurement.rfq"]
        .with_user(c.buyer)
        .create(
            {
                "description": "P2P RFQ",
                "product_id": c.prod.id,
                "qty": qty,
                "invited_vendor_ids": [(6, 0, [v.id for v, _p, _cur in bids])],
                "response_deadline": SOON,
            }
        )
    )
    rfq.with_user(c.buyer).action_open()
    made = []
    for vendor, price, currency in bids:
        made.append(
            c.env["fix.procurement.bid"]
            .with_user(c.buyer)
            .create(
                {
                    "rfq_id": rfq.id,
                    "vendor_id": vendor.id,
                    "unit_price": price,
                    "currency_id": (currency or c.env.company.currency_id).id,
                }
            )
        )
    rfq.with_user(c.buyer).action_close()  # every invited supplier answered
    return rfq, made


def test_p03_bids_are_ranked_in_bdt(c):
    """USD 10 (BDT 1,200) against BDT 1,100: the BDT bid is the lowest.
    Mutation: rank on raw unit_price -> the USD bid 'wins' with no rationale."""
    rfq, (usd_bid, bdt_bid) = _closed_rfq(c, [(c.vendor, 10.0, c.usd), (c.vendor2, 1100.0, None)])
    assert usd_bid.unit_price_bdt == 1200.0
    Award = c.env["fix.procurement.award"].with_user(c.buyer)
    with pytest.raises(UserError, match="not the lowest compliant bid"), c.env.cr.savepoint():
        Award.create({"rfq_id": rfq.id, "bid_id": usd_bid.id})
    award = Award.create({"rfq_id": rfq.id, "bid_id": bdt_bid.id})
    assert award.state == "decided" and award.lowest_bid_id == bdt_bid


def test_d8_three_quotes_above_50000_bdt(c):
    """D8: one quote suffices up to BDT 50,000; above it three are needed.
    Mutation: default threshold 0 -> the 11,000 award needs an exception."""
    rfq, (bid,) = _closed_rfq(c, [(c.vendor, 1100.0, None)])
    award = (
        c.env["fix.procurement.award"]
        .with_user(c.buyer)
        .create({"rfq_id": rfq.id, "bid_id": bid.id})
    )
    assert award.state == "decided" and award.min_bids == 1
    rfq2, (bid2,) = _closed_rfq(c, [(c.vendor, 600.0, c.usd)])  # USD 6,000 = BDT 720,000
    with pytest.raises(UserError, match="BRU-PRO-06"), c.env.cr.savepoint():
        c.env["fix.procurement.award"].with_user(c.buyer).create(
            {"rfq_id": rfq2.id, "bid_id": bid2.id}
        )


def test_p23_losing_bidders_are_told(c):
    rfq, (_won, lost) = _closed_rfq(c, [(c.vendor, 1000.0, None), (c.vendor2, 1100.0, None)])
    award = (
        c.env["fix.procurement.award"]
        .with_user(c.buyer)
        .create({"rfq_id": rfq.id, "bid_id": _won.id})
    )
    assert lost.state == "lost"
    partner = c.vendor2.commercial_partner_id
    assert award.state == "decided"
    assert partner.message_ids.filtered(lambda m: partner in m.partner_ids and lost.name in m.body)


# ----------------------------------------------------------------- P22
def test_p22_rfq_closes_at_its_deadline_not_before(c):
    """Mutation: drop _a06_check_deadline_passed -> closed after one price."""
    rfq = (
        c.env["fix.procurement.rfq"]
        .with_user(c.buyer)
        .create(
            {
                "description": "P2P RFQ deadline",
                "product_id": c.prod.id,
                "qty": 1,
                "invited_vendor_ids": [(6, 0, (c.vendor | c.vendor2).ids)],
                "response_deadline": SOON,
            }
        )
    )
    rfq.with_user(c.buyer).action_open()
    c.env["fix.procurement.bid"].with_user(c.buyer).create(
        {"rfq_id": rfq.id, "vendor_id": c.vendor.id, "unit_price": 900.0}
    )
    with pytest.raises(UserError, match="open for bids until"), c.env.cr.savepoint():
        rfq.with_user(c.buyer).action_close()
    rfq._guarded().write({"response_deadline": c.today - timedelta(days=1)})
    assert rfq in c.env["fix.procurement.rfq"]._cron_close_due_rfqs()
    assert rfq.state == "closed"


def test_p22_close_cron_is_wired(c):
    cron = c.env.ref("cd_requisition.ir_cron_fix_procurement_rfq_close_due")
    assert cron.active and "_cron_close_due_rfqs" in cron.code
    assert cron.model_id.model == "fix.procurement.rfq"


# ----------------------------------------------------------------- P07
def test_p07_requester_unit_branch_and_kind_are_pinned_after_submit(c):
    """Mutation: drop REQ_IDENTITY pinning -> the colleague repoints it."""
    r = _req(c)
    r.with_user(c.requester).write({"requested_by": c.emp2.id})  # a draft is still open
    r.with_user(c.requester).write({"requested_by": c.emp.id})
    r.with_user(c.requester).action_submit()
    for vals in ({"requested_by": c.emp2.id}, {"purchase_kind": "service"}):
        with pytest.raises(UserError, match="fixed once it is submitted"), c.env.cr.savepoint():
            r.with_user(c.requester).write(vals)


# ----------------------------------------------------------------- P11
def test_p11_post_receipt_price_amendment_is_versioned_and_reapproved(c):
    """Mutations: approve without the tier / SoD check -> the buyer approves
    their own amendment; no write of approved_unit_price -> the bill stays
    blocked."""
    po = _sent_po(c, 20000.0)
    line = po.line_ids
    po.with_user(c.receiver).action_record_receipt({line.id: 2})
    insp = (
        c.env["fix.procurement.inspection"]
        .with_user(c.inspector)
        .create({"receipt_line_id": po.receipt_ids.line_ids.id, "qty_accepted": 2})
    )
    insp.with_user(c.inspector).action_confirm()
    Amend = c.env["fix.purchase.price.amendment"].with_user(c.buyer)
    amd = Amend.create(
        {
            "po_line_id": line.id,
            "new_price": 12000.0,
            "reason": "Supplier's documented copper surcharge from 15 Nov",
            "evidence_ref": "dms://p2p/surcharge-letter",
        }
    )
    assert amd.old_price == 10000.0
    amd.with_user(c.buyer).action_submit()
    for who in (c.buyer, c.requester, c.colleague):
        with pytest.raises(UserError), c.env.cr.savepoint():
            amd.with_user(who).action_approve()
    amd.with_user(c.t2).action_approve()
    assert (amd.state, amd.version, line.approved_unit_price) == ("approved", 1, 12000.0)
    events = c.env["fix.event.outbox"].search(
        [("event_type", "=", "po.amended"), ("aggregate_id", "=", po.id)]
    )
    assert events
    if "fix.vendor.invoice" in c.env:
        bill = c.env["fix.vendor.invoice"].create(
            {
                "vendor_id": po.vendor_id.id,
                "invoice_ref": "P2P-AMD-1",
                "requisition_id": po.id,
                "operating_unit_id": c.ou.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": c.prod.id,
                            "description": "Compressor",
                            "quantity": 2,
                            "unit_price": 12000.0,
                            "tds_category": "supply_of_goods",
                        },
                    )
                ],
            }
        )
        assert bill.match_state == "matched", bill.match_detail


def test_p11_amendment_only_after_receipt(c):
    po = _sent_po(c, 20000.0)
    amd = (
        c.env["fix.purchase.price.amendment"]
        .with_user(c.buyer)
        .create(
            {
                "po_line_id": po.line_ids.id,
                "new_price": 9000.0,
                "reason": "Supplier lowered the price before delivery",
                "evidence_ref": "dms://p2p/x",
            }
        )
    )
    with pytest.raises(UserError, match="change order"), c.env.cr.savepoint():
        amd.with_user(c.buyer).action_submit()


# ----------------------------------------------------------------- P21
def test_p21_receiver_does_not_inspect_own_receipt(c):
    """Mutation: drop the receiver check in action_confirm -> passes."""
    po = _sent_po(c)
    po.with_user(c.receiver).action_record_receipt({po.line_ids.id: 2})
    rline = po.receipt_ids.line_ids
    insp = (
        c.env["fix.procurement.inspection"]
        .with_user(c.receiver)
        .create({"receipt_line_id": rline.id, "qty_accepted": 2})
    )
    with (
        pytest.raises(UserError, match="another person records its inspection"),
        c.env.cr.savepoint(),
    ):
        insp.with_user(c.receiver).action_confirm()
    insp.with_user(c.inspector).action_confirm()
    assert rline.qty_accepted == 2


def test_p21_award_decider_does_not_approve_its_order(c):
    """Mutation: drop the award decider from _a06_extra_conflicts -> the buyer
    who decided the award approves the order another buyer raised."""
    rfq, (bid,) = _closed_rfq(c, [(c.vendor, 1000.0, None)])
    award = (
        c.env["fix.procurement.award"]
        .with_user(c.buyer)
        .create({"rfq_id": rfq.id, "bid_id": bid.id})
    )
    award.with_user(c.buyer2).action_create_po()
    po = award.purchase_order_id
    assert po.buyer_id == c.buyer2
    assert c.buyer in po._a06_conflicted_users()


# ----------------------------------------------------------------- P37 / P38
def test_p37_a_colleague_does_not_cancel_or_release_anothers_requisition(c):
    r = _req(c, 10000.0, urgency="emergency")
    with pytest.raises(UserError, match="requester"), c.env.cr.savepoint():
        r.with_user(c.colleague).action_cancel(reason="not needed")
    with pytest.raises(UserError, match="requester"), c.env.cr.savepoint():
        r.with_user(c.colleague).action_emergency_release(reason="Compressor dead on a running job")
    r.with_user(c.requester).action_cancel(reason="duplicate of another request")
    assert r.state == "cancelled"


def test_d8_emergency_ceiling_is_25000(c):
    """Mutation: default the ceiling to the 50,000 ladder band -> passes."""
    r = _req(c, 30000.0, urgency="emergency")
    with pytest.raises(UserError, match="limited to BDT 25000.00"), c.env.cr.savepoint():
        r.with_user(c.requester).action_emergency_release(reason="Compressor dead on a running job")


def test_p38_cancelled_po_reopens_its_requisition(c):
    """Mutation: drop the revert in action_cancel -> the requisition stays converted."""
    po = _sent_po(c)
    req = po.requisition_id
    po.with_user(c.buyer).action_cancel(reason="Vendor cannot deliver")
    assert (req.state, req.purchase_order_id) == ("approved", c.env["fix.purchase.order"])
    assert any(c.vendor.commercial_partner_id in m.partner_ids for m in po.message_ids)


# ----------------------------------------------------------------- P24 / P16
def test_p24_vendor_is_told_of_the_order(c):
    po = _sent_po(c)
    assert any(c.vendor.commercial_partner_id in m.partner_ids for m in po.message_ids)


def test_p16_on_behalf_date_does_not_move_otd(c):
    """Mutation: _a06_otd_due_date returns vendor_confirmed_date -> the
    buyer's late date becomes the yardstick."""
    po = _sent_po(c)
    po.sudo()._guarded().write({"promised_date": c.today + timedelta(days=3)})
    po.with_user(c.buyer).action_acknowledge_on_behalf(
        evidence="Phone call with the vendor's sales desk",
        confirmed_date=c.today + timedelta(days=30),
    )
    assert po._a06_otd_due_date() == c.today + timedelta(days=3)


# ----------------------------------------------------------------- P39
def test_p39_blanket_cap_converts_currency_and_counts_a_revision_once(c):
    """Mutations: sum amount_total raw -> a USD call-off counts 200, not
    24,000; no revision exclusion -> the change order counts twice."""
    env = c.env
    blanket = env["fix.procurement.blanket"].create(
        {
            "vendor_id": c.vendor.id,
            "valid_from": c.today - timedelta(days=1),
            "valid_to": c.today + timedelta(days=60),
            "cap_amount": 30000.0,
        }
    )
    blanket._guarded().write({"state": "active"})
    usd = env["fix.purchase.order"].create(
        {
            "operating_unit_id": c.ou.id,
            "vendor_id": c.vendor.id,
            "currency_id": c.usd.id,
            "blanket_id": blanket.id,
            "line_ids": [(0, 0, {"product_id": c.prod.id, "qty_ordered": 2, "unit_price": 100.0})],
        }
    )
    usd._guarded().write({"state": "sent", "fx_rate": 120.0})
    assert blanket._consumed_amount() == 24000.0
    revision = env["fix.purchase.order"].create(
        {
            "operating_unit_id": c.ou.id,
            "vendor_id": c.vendor.id,
            "currency_id": c.usd.id,
            "blanket_id": blanket.id,
            "line_ids": [(0, 0, {"product_id": c.prod.id, "qty_ordered": 2, "unit_price": 110.0})],
        }
    )
    revision._guarded().write({"revision_of_id": usd.id, "fx_rate": 120.0})
    assert blanket._consumed_amount(exclude=revision) == 0.0
    revision._a06_check_blanket()  # 26,400 within 30,000: the original is not added


# ----------------------------------------------------------------- P33
def _events(env, event_type, aggregate_id):
    return env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)]
    )


def test_p33_requisition_lifecycle_events(c):
    """Mutation: drop _a06_publish calls -> no requisition.* events."""
    r = _req(c, 5000.0)
    r.with_user(c.requester).action_submit()
    assert _events(c.env, "requisition.submitted", r.id)
    _decide(c, r)
    assert _events(c.env, "requisition.approved", r.id)
    e = _req(c, 10000.0, urgency="emergency")
    e.with_user(c.requester).action_emergency_release(reason="Compressor dead on a running job")
    assert _events(c.env, "requisition.emergency_released", e.id)


def test_p33_overdue_po_publishes_po_overdue(c):
    po = _sent_po(c)
    po.sudo()._guarded().write({"promised_date": c.today - timedelta(days=1)})
    c.env["fix.purchase.order"]._cron_open_overdue_expedites()
    assert _events(c.env, "po.overdue", po.id)


def test_p33_unacknowledged_po_is_chased_once_per_sla(c):
    """Mutation: drop the ack_chased_at check -> chased again the same day."""
    po = _sent_po(c)
    c.env["ir.config_parameter"].set_param("cd_vendor_portal.ack_sla_days", "2")
    po.sudo()._guarded().write({"sent_at": fields.Datetime.now() - timedelta(days=3)})
    Order = c.env["fix.purchase.order"]
    assert po in Order._cron_chase_acknowledgements()
    assert po.ack_chased_at and _events(c.env, "po.ack_chased", po.id)
    assert po.activity_ids.filtered(lambda a: a.user_id == po.buyer_id)
    assert po not in Order._cron_chase_acknowledgements()


def test_p33_ack_chase_cron_is_wired(c):
    cron = c.env.ref("cd_requisition.ir_cron_fix_purchase_order_ack_chase")
    assert cron.active and "_cron_chase_acknowledgements" in cron.code
    assert cron.model_id.model == "fix.purchase.order"


# ----------------------------------------------------------------- P27
def test_p27_converted_po_takes_the_approved_source_price(c):
    """Mutation: no _a06_apply_reference_prices -> the PO line keeps the
    requester's estimate (10,000) instead of the agreed 9,000."""
    src = (
        c.env["fix.procurement.approved.source"]
        .with_user(c.buyer)
        .create({"product_id": c.prod.id, "vendor_id": c.vendor.id, "agreed_price": 9000.0})
    )
    src._guarded().write({"state": "approved"})
    r = _req(c, 20000.0)
    r.with_user(c.requester).action_submit()
    _decide(c, r)
    r.with_user(c.buyer).action_convert_to_po()
    assert r.purchase_order_id.line_ids.unit_price == 9000.0
