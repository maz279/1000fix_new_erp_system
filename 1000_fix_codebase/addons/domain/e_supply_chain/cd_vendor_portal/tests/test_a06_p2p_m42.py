# A06 ERP audit (20 Nov 2026), stream P2P: M42 supplier controls and the P05
# portal's bill submission. Findings P02 (portal) P04 P08 P09 P10 P14 (portal)
# P20 P35 P43 P45. Non-admin users with the real roles; rolled back.
import types
from datetime import timedelta
from types import SimpleNamespace

import pytest
from odoo import fields
from odoo.addons.cd_vendor_portal.controllers import vendor_api
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
GS = "cd_vendor_portal.group_fix_supplier_steward"
GSA = "cd_vendor_portal.group_fix_supplier_approver"
GB = "cd_requisition.group_fix_procurement_buyer"
ACC = "account.group_account_user"


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
def m(odoo_env, monkeypatch):
    env = odoo_env
    monkeypatch.setattr(vendor_api, "request", SimpleNamespace(env=env))
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env.user)
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.steward = _user(env, "p2p42_steward", [GS])
    x.steward2 = _user(env, "p2p42_steward2", [GS])
    x.approver = _user(env, "p2p42_approver", [GSA])
    x.buyer = _user(env, "p2p42_buyer", [GB])
    x.acc = _user(env, "p2p42_acc", [ACC])
    x.categ = env["product.category"].create({"name": "P2P42 Panels"})
    x.other_categ = env["product.category"].create({"name": "P2P42 Stationery"})
    x.prod = env["product.product"].create({"name": "P2P42 Panel", "categ_id": x.categ.id})
    x.pen = env["product.product"].create({"name": "P2P42 Pen", "categ_id": x.other_categ.id})
    x.vendor = env["res.partner"].create({"name": "P2P42 Panel House", "is_company": True})
    x.sup = env["fix.supplier"].create(
        {
            "name": x.vendor.name,
            "partner_id": x.vendor.id,
            "status": "active",
            "approved_category_ids": [(6, 0, x.categ.ids)],
        }
    )
    for doc_type in ("trade_licence", "tin", "vat"):
        env["fix.supplier.document"].create(
            {
                "supplier_id": x.sup.id,
                "doc_type": doc_type,
                "number": "P2P42-%s" % doc_type,
                "file_ref": "dms://p2p42/%s" % doc_type,
                "state": "valid",
                "valid_to": x.today + timedelta(days=365),
            }
        )
    x.usd = (
        env.ref("base.BDT")
        if env.company.currency_id == env.ref("base.USD")
        else env.ref("base.USD")
    )
    x.usd.active = True
    _rate(env, x.usd, x.today, 120.0)
    x.ctl = vendor_api.VendorApiController()
    return x


def _po(m, product=None, price=100.0, currency=None, qty=2.0):
    return m.env["fix.purchase.order"].create(
        {
            "operating_unit_id": m.ou.id,
            "vendor_id": m.vendor.id,
            "currency_id": (currency or m.env.company.currency_id).id,
            "line_ids": [
                (
                    0,
                    0,
                    {"product_id": (product or m.prod).id, "qty_ordered": qty, "unit_price": price},
                )
            ],
        }
    )


def _send(po):
    po.action_record_requisition_exception(reason="P2P42 test order without requisition")
    po._guarded().write(
        {
            "approval_state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": po._dofa_current_tier(),
            "dofa_approved_amount": po._dofa_amount(),
        }
    )
    po.action_send()
    return po


# ----------------------------------------------------------------- P08
def test_p08_category_gate_is_on_by_default(m):
    """Mutation: default "0" again -> the stationery order is sent."""
    m.env["ir.config_parameter"].search(
        [("key", "=", "cd_vendor_portal.po_category_gate")]
    ).unlink()
    with pytest.raises(UserError, match="BRU-PRO-02"), m.env.cr.savepoint():
        _send(_po(m, product=m.pen))
    assert _send(_po(m)).state == "sent"


def test_p08_categories_come_from_an_approved_qualification(m):
    """Mutation: drop approved_category_ids from SUPPLIER_GUARDED -> the
    steward widens what the supplier may supply by a plain edit."""
    with pytest.raises(REFUSED), m.env.cr.savepoint():
        m.sup.with_user(m.steward).write({"approved_category_ids": [(4, m.other_categ.id)]})
    qual = (
        m.env["fix.supplier.qualification"]
        .with_user(m.steward)
        .create({"supplier_id": m.sup.id, "score": 90, "category_ids": [(6, 0, m.other_categ.ids)]})
    )
    qual.with_user(m.steward).action_start()
    qual.with_user(m.approver).action_approve()
    assert m.other_categ in m.sup.approved_category_ids


# ----------------------------------------------------------------- P04
def test_p04_agreed_price_in_another_currency_still_caps_the_order(m):
    """An agreed USD 1.00 (BDT 120) price; a BDT order at 130 is refused.
    Mutation: search with the order currency only -> no agreed price, passes."""
    env = m.env
    agreement = env["fix.supplier.agreement"].create(
        {
            "supplier_id": m.sup.id,
            "agreement_type": "framework",
            "reference": "P2P42-FA",
            "term_from": m.today - timedelta(days=10),
            "term_to": m.today + timedelta(days=365),
            "currency_id": m.usd.id,
        }
    )
    agreement._guarded().write({"state": "active"})
    price = env["fix.supplier.price.list"].create(
        {
            "agreement_id": agreement.id,
            "product_id": m.prod.id,
            "price": 1.0,
            "valid_from": m.today - timedelta(days=5),
        }
    )
    price._guarded().write({"state": "approved"})
    with pytest.raises(UserError, match="BRU-SRM2-14"), env.cr.savepoint():
        _po(m, price=130.0)._a06_check_agreed_prices()
    _po(m, price=115.0)._a06_check_agreed_prices()


# ----------------------------------------------------------------- P10 / P09
def _posted_bill(m, po, qty, price):
    bill = m.env["fix.vendor.invoice"].create(
        {
            "vendor_id": m.vendor.id,
            "invoice_ref": "P2P42-%s" % po.id,
            "requisition_id": po.id,
            "currency_id": po.currency_id.id,
            "operating_unit_id": m.ou.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": m.prod.id,
                        "description": "Panel",
                        "quantity": qty,
                        "unit_price": price,
                        "tds_category": "supply_of_goods",
                    },
                )
            ],
        }
    )
    return bill


def test_p10_deactivated_supplier_is_never_paid(m):
    """Mutation: drop _a06_check_payable_supplier -> the request goes out."""
    m.env["ir.config_parameter"].set_param("cd_requisition.receipt_inspection_required", "0")
    po = _send(_po(m))
    po.action_record_receipt({po.line_ids.id: 2})
    bill = _posted_bill(m, po, 2, 100.0)
    bill._guarded().write({"approval_state": "approved", "move_id": False})
    m.sup._a06_set_status("deactivated", "Sanctions list hit")
    with pytest.raises(UserError, match="deactivated"), m.env.cr.savepoint():
        bill.with_user(m.acc).action_request_payment()


def test_p09_deactivated_supplier_gets_no_non_po_bill(m):
    m.sup._a06_set_status("deactivated", "Sanctions list hit")
    service = m.env["product.product"].create({"name": "P2P42 Courier", "type": "service"})
    bill = m.env["fix.vendor.invoice"].create(
        {
            "vendor_id": m.vendor.id,
            "invoice_ref": "P2P42-NONPO",
            "bill_type": "non_po",
            "operating_unit_id": m.ou.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": service.id,
                        "description": "Courier",
                        "quantity": 1,
                        "unit_price": 500.0,
                        "tds_category": "service_general",
                    },
                )
            ],
        }
    )
    with pytest.raises(UserError, match="deactivated"), m.env.cr.savepoint():
        bill.action_submit_approval()


# ----------------------------------------------------------------- portal P02 / P14
def test_portal_bill_takes_the_po_currency_and_a_replay_returns_it(m):
    """Mutations: no currency_id in the portal vals -> the bill is BDT and
    blocks; no replay lookup -> a second draft."""
    po = _send(_po(m, price=10.0, currency=m.usd))
    lines = [{"product_id": m.prod.id, "description": "Panel", "quantity": 1, "unit_price": 10.0}]
    out = m.ctl.invoices(invoice_ref="PH/INV/77", po_id=po.id, lines=lines)
    bill = m.env["fix.vendor.invoice"].browse(out["invoice"]["id"])
    assert bill.currency_id == m.usd
    again = m.ctl.invoices(invoice_ref="ph inv 77", po_id=po.id, lines=lines)
    assert again["invoice"]["id"] == bill.id and again["invoice"]["replayed"]
    assert m.env["fix.vendor.invoice"].search_count([("requisition_id", "=", po.id)]) == 1


# ----------------------------------------------------------------- P20 / P45 / P35 / P43
def test_p20_screening_is_not_cleared_by_who_recorded_it(m):
    s = (
        m.env["fix.supplier.screening"]
        .with_user(m.steward)
        .create({"supplier_id": m.sup.id, "screening_type": "sanctions", "result": "clear"})
    )
    with pytest.raises(UserError), m.env.cr.savepoint():
        s.with_user(m.steward).action_clear()
    s.with_user(m.steward2).action_clear()
    assert s.state == "cleared"


def test_p45_two_d_grades_must_be_consecutive_periods(m):
    """Mutation: drop the previous-period check -> a D in August and one in
    November open a CAR."""
    Card = m.env["fix.supplier.performance"]
    old = Card.create({"supplier_id": m.sup.id, "period": "2026-08"})
    old._guarded().write({"state": "published", "grade": "d"})
    now = Card.create({"supplier_id": m.sup.id, "period": "2026-11"})
    now._guarded().write({"grade": "d"})
    assert not now._a06_auto_car()
    prev = Card.create({"supplier_id": m.sup.id, "period": "2026-10"})
    prev._guarded().write({"state": "published", "grade": "d"})
    assert now._a06_auto_car()


def test_p43_bank_change_proposal_tells_the_supplier(m):
    change = (
        m.env["fix.supplier.bank.change"]
        .with_user(m.steward)
        .create(
            {
                "supplier_id": m.sup.id,
                "acc_number": "1234567890123",
                "verification_ref": "Called the supplier's MD on the number in its signed form",
                "evidence_ref": "dms://p2p42/bank",
            }
        )
    )
    change.with_user(m.steward).action_propose()
    assert any(m.vendor.commercial_partner_id in msg.partner_ids for msg in m.sup.message_ids)


# ----------------------------------------------------------------- P30
def test_p30_agreed_prices_are_not_read_by_every_employee(m):
    """Mutation: restore the base.group_user read rows -> the clerk reads them."""
    clerk = _user(m.env, "p2p42_clerk")
    for model in ("fix.supplier.price.list", "fix.procurement.approved.source"):
        with pytest.raises(AccessError):
            m.env[model].with_user(clerk).check_access("read")
    m.env["fix.supplier.price.list"].with_user(m.buyer).check_access("read")


# ----------------------------------------------------------------- P18 / P19
def test_p18_requalification_outcome_and_completion_by_two_people(m):
    """Mutation: drop the _not_by in action_complete -> one steward does both."""
    req = (
        m.env["fix.supplier.requalification"]
        .with_user(m.steward)
        .create({"supplier_id": m.sup.id, "due_on": m.today})
    )
    req.with_user(m.steward).write({"outcome": "pass"})
    with pytest.raises(UserError), m.env.cr.savepoint():
        req.with_user(m.steward).action_complete()
    req.with_user(m.steward2).action_complete()
    assert req.state == "done"


def test_p19_expired_brand_authorisation_stops_orders_and_class_is_fixed(m):
    """Mutations: no brand check in _a06_order_problems -> orders go out;
    no classification pin -> a steward re-labels it to escape the evidence."""
    m.sup.write({"classification": "authorised_distributor"})
    assert "its brand authorisation is missing or expired" in m.sup._a06_order_problems()
    with pytest.raises(UserError, match="classification"), m.env.cr.savepoint():
        m.sup.with_user(m.steward).write({"classification": "oem"})


def test_p42_no_draft_order_to_a_blocked_or_prospect_supplier(m):
    """Mutation: drop the create check -> the draft is raised."""
    m.sup._a06_set_status("deactivated", "Sanctions list hit")
    with pytest.raises(UserError, match="no purchase order is drafted"), m.env.cr.savepoint():
        _po(m)


# ----------------------------------------------------------------- P27 blanket
def test_p27_blanket_calls_off_under_the_agreement_in_force(m):
    """Mutation: no _a06_agreement_problems -> a second, competing contract."""
    env = m.env
    agreement = env["fix.supplier.agreement"].create(
        {
            "supplier_id": m.sup.id,
            "agreement_type": "framework",
            "reference": "P2P42-FA-B",
            "term_from": m.today - timedelta(days=10),
            "term_to": m.today + timedelta(days=200),
        }
    )
    agreement._guarded().write({"state": "active"})
    approver = _user(env, "p2p42_papprover", ["cd_requisition.group_fix_procurement_approver"])
    blanket = env["fix.procurement.blanket"].create(
        {
            "vendor_id": m.vendor.id,
            "valid_from": m.today,
            "valid_to": m.today + timedelta(days=60),
            "cap_amount": 100000.0,
        }
    )
    with pytest.raises(UserError, match="calls off under it"), env.cr.savepoint():
        blanket.with_user(approver).action_activate()
    blanket.write({"agreement_id": agreement.id})
    blanket.with_user(approver).action_activate()
    assert blanket.state == "active"


# ----------------------------------------------------------------- P36 / P44
def test_p36_register_is_per_company(m):
    """Mutation: UNIQUE (partner_id) -> the second company cannot register it."""
    env = m.env
    other = env["res.company"].create(
        {"name": "P2P42 Second Company", "currency_id": env.ref("base.BDT").id}
    )
    twin = env["fix.supplier"].create(
        {"name": m.vendor.name, "partner_id": m.vendor.id, "company_id": other.id}
    )
    assert env["fix.supplier"]._for_partner(m.vendor, other) == twin
    assert env["fix.supplier"]._for_partner(m.vendor) == m.sup
    from psycopg2 import IntegrityError

    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.supplier"].create(
            {"name": m.vendor.name, "partner_id": m.vendor.id, "company_id": other.id}
        )


def test_p44_risk_tier_sets_review_frequency_and_approval_tier(m):
    """Mutations: cadence by segment only -> no review for a critical
    transactional supplier; risk_tier not in the tier keys -> no authority."""
    env = m.env
    icp = env["ir.config_parameter"]
    icp.set_param("cd_vendor_portal.review_cadence_by_risk_months", "critical:3")
    icp.set_param("cd_vendor_portal.qualification_tier_by_risk", "critical:tier_4")
    m.sup.write(
        {
            "segment": "transactional",
            "risk_tier": "critical",
            "onboarded_on": m.today - timedelta(days=120),
        }
    )
    made = env["fix.supplier"]._cron_review_cadence()
    assert made.filtered(lambda r: r.supplier_id == m.sup)
    qual = env["fix.supplier.qualification"].create({"supplier_id": m.sup.id, "score": 90})
    assert qual._a06_required_tier() == "tier_4"
