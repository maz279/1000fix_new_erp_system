"""cd_marketplace behaviour (live ORM, rolled back): seller onboarding (KYC,
Z4 routing, CFO gate), Journey 7 order lifecycle, quotes, transparent
scoring/tiering and disputes with the BRU-BIL-03 payout lock."""

from __future__ import annotations

import json
from datetime import timedelta
from unittest.mock import patch

import pytest
from lxml import etree
from odoo import fields
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

from libs.py.fix_residency import ResidencyError

SELLER = "fix.marketplace.seller"
ORDER = "fix.marketplace.order"
QUOTE = "fix.seller.quote"
SCORE = "fix.seller.score"
DISPUTE = "fix.marketplace.dispute"


def _job_evidence(order):
    """BRU-MKP-02 (M12 capture audit, 19 Nov 2026): a marketplace job
    completes only with the owned-job evidence. Recorded as the trusted
    superuser, as a seller's app or an operator would."""
    import base64

    png = base64.b64encode(b"\x89PNG evidence")
    Evidence = order.env["fix.marketplace.job.evidence"].sudo()
    for kind, vals in (
        ("before_photo", {"evidence_file": png, "evidence_filename": "before.png"}),
        ("after_photo", {"evidence_file": png, "evidence_filename": "after.png"}),
        ("qc_checklist", {"qc_passed": True, "note": "All QC checks passed"}),
        ("parts_declaration", {"provenance": "none"}),
    ):
        Evidence.create({"order_id": order.id, "artefact_type": kind, **vals})


def _events(env, event_type, aggregate, res_id):
    rows = env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", res_id),
        ],
        order="id",
    )
    return [json.loads(r.payload) for r in rows]


@pytest.fixture(autouse=True)
def _commission_rate(odoo_env):
    """The platform commission rate is configuration (system parameter)."""
    # get_param is ormcached and a rolled-back test can leave a stale value:
    # removing then setting the key always writes, which invalidates the cache
    params = odoo_env["ir.config_parameter"].sudo()
    params.set_param("cd_marketplace.platform_commission_rate", False)
    params.set_param("cd_marketplace.platform_commission_rate", "0.10")


def _partner(env, name):
    return env["res.partner"].create({"name": name})


def _seller(env, name="Gadget Fixers BD", verified=True, approved=True, **vals):
    seller = env[SELLER].create({"name": name, "partner_id": _partner(env, name).id, **vals})
    seller.write({"kyc_status": "verified" if verified else "pending", "cfo_approved": approved})
    return seller


def _order(env, **vals):
    vals.setdefault("customer_id", _partner(env, "Marketplace Customer").id)
    vals.setdefault("description", "Cracked screen on Galaxy A54")
    vals.setdefault("customer_consent", True)  # BRU-MKP-07
    vals.setdefault("consent_method", "signed")
    return env[ORDER].create(vals)


def _quote(env, order, seller, price=2500.0, **vals):
    return env[QUOTE].create(
        {"marketplace_order_id": order.id, "seller_id": seller.id, "quoted_price": price, **vals}
    )


def _dispute(env, order, seller, **vals):
    vals.setdefault("description", "Screen flickers after repair")
    return env[DISPUTE].create(
        {"order_id": order.id, "seller_id": seller.id, "customer_id": order.customer_id.id, **vals}
    )


def _order_in(env, state, seller=None, price=2500.0):
    """An order awarded to `seller` and moved to `state`."""
    seller = seller or _seller(env)
    order = _order(env)
    quote = _quote(env, order, seller, price)
    order.action_select_quote(quote)
    order.write({"state": state})
    return order


# --------------------------------------------------------------------------
# Seller onboarding
# --------------------------------------------------------------------------


def test_submit_kyc_without_documents_issues_local_z4_token(odoo_env):
    seller = _seller(odoo_env, verified=False, approved=False)
    seller.action_submit_kyc(
        nid_number="1990123456789", trade_license_no="TL-77", tin_number="TIN-9"
    )
    assert seller.kyc_status == "in_review"
    assert seller.kyc_submission_date == fields.Date.context_today(seller)  # the local day
    assert seller.nid_number == "1990123456789"
    assert seller.trade_license_no == "TL-77"
    assert seller.tin_number == "TIN-9"
    assert seller.kyc_doc_z4_ref.startswith(f"z4-token-{seller.id}-")
    assert _events(odoo_env, "seller.kyc_submitted", SELLER, seller.id) == [
        {
            "seller": seller.name,
            "nid_masked": "******6789",
            "trade_license": "TL-77",
            "z4_ref": seller.kyc_doc_z4_ref,
        }
    ]


def test_submit_kyc_keeps_existing_identity_and_masks_missing_or_short_nid(odoo_env):
    blank = _seller(odoo_env, name="Blank Shop", verified=False)
    blank.action_submit_kyc()
    short = _seller(odoo_env, name="Short NID Shop", verified=False, nid_number="123")
    short.action_submit_kyc()
    assert short.nid_number == "123"
    for seller in (blank, short):
        (payload,) = _events(odoo_env, "seller.kyc_submitted", SELLER, seller.id)
        assert payload["nid_masked"] == "N/A"
        assert payload["trade_license"] == "N/A"
        assert seller.kyc_status == "in_review"


def test_submit_kyc_routes_documents_through_z4_vault(odoo_env):
    seller = _seller(odoo_env, verified=False)
    with patch("libs.py.fix_residency.ResidencyClient") as client_cls:
        client_cls.return_value.put.return_value = {"key": "z4://seller-kyc/abc"}
        seller.action_submit_kyc(doc_payload={"nid_front": "base64..."})
    client_cls.return_value.put.assert_called_once_with(
        f"seller_kyc_{seller.id}", str({"nid_front": "base64..."})
    )
    assert seller.kyc_doc_z4_ref == "z4://seller-kyc/abc"


def test_submit_kyc_vault_reply_without_key_falls_back_to_token(odoo_env):
    seller = _seller(odoo_env, verified=False)
    with patch("libs.py.fix_residency.ResidencyClient") as client_cls:
        client_cls.return_value.put.return_value = {}
        seller.action_submit_kyc(doc_payload="scan")
    assert seller.kyc_doc_z4_ref.startswith(f"z4-token-{seller.id}-")


def test_submit_kyc_vault_outage_falls_back_to_token(odoo_env, caplog):
    seller = _seller(odoo_env, verified=False)
    with patch("libs.py.fix_residency.ResidencyClient") as client_cls:
        client_cls.return_value.put.side_effect = ResidencyError("residency service unreachable")
        seller.action_submit_kyc(doc_payload="scan")
    assert seller.kyc_doc_z4_ref.startswith(f"z4-token-{seller.id}-")
    assert seller.kyc_status == "in_review"
    assert "fix_residency put fallback" in caplog.text


def test_cfo_approval_records_approver(odoo_env):
    """The trusted path (superuser); a user approves from the M63 inbox
    (test_a04_m12_controls.py). KYC comes first either way."""
    seller = _seller(odoo_env, verified=False, approved=False)
    with pytest.raises(UserError, match="CFO approval comes after KYC"):
        seller.action_cfo_approve()
    seller.write({"kyc_status": "verified"})
    seller.action_cfo_approve()
    assert seller.cfo_approved is True
    assert seller.cfo_approval_date == fields.Date.context_today(seller)  # the local day
    assert seller.cfo_approved_by == odoo_env.user
    assert _events(odoo_env, "seller.cfo_approved", SELLER, seller.id) == [
        {"seller": seller.name, "approver": odoo_env.user.name}
    ]
    assert _events(odoo_env, "seller.approved", SELLER, seller.id) == [
        {"seller": seller.name, "tier": "unrated"}  # no measured performance yet
    ]


def test_verify_kyc_never_grants_cfo_approval(odoo_env):
    """A04 M12-1: verifying KYC used to tick CFO approval for the same user."""
    seller = _seller(
        odoo_env, verified=False, approved=False, trade_license_no="TL-1", tin_number="TIN-1"
    )
    seller.action_verify_kyc()
    assert seller.kyc_status == "verified"
    assert seller.kyc_verified_date == fields.Date.context_today(seller)
    assert seller.compliance_reviewer_id == odoo_env.user
    assert seller.cfo_approved is False and not seller.cfo_approved_by
    assert _events(odoo_env, "seller.kyc_verified", SELLER, seller.id) == [
        {"seller": seller.name, "reviewer": odoo_env.user.name}
    ]
    assert _events(odoo_env, "seller.approved", SELLER, seller.id) == []


def test_verify_kyc_keeps_prior_cfo_approval(odoo_env):
    cfo = odoo_env["res.users"].create({"name": "CFO", "login": "cfo-marketplace-behaviour"})
    seller = _seller(odoo_env, verified=False, trade_license_no="TL-2", tin_number="TIN-2")
    seller.write({"cfo_approved_by": cfo.id, "cfo_approval_date": "2026-01-15"})
    seller.action_verify_kyc()
    assert seller.kyc_status == "verified"
    assert seller.cfo_approved_by == cfo
    assert str(seller.cfo_approval_date) == "2026-01-15"


def test_reject_kyc_records_reason(odoo_env):
    default = _seller(odoo_env, name="Default Reject", verified=False)
    custom = _seller(odoo_env, name="Custom Reject", verified=False)
    default.action_reject_kyc()
    custom.action_reject_kyc(reason="Trade license expired")
    assert default.kyc_status == custom.kyc_status == "rejected"
    assert default.rejection_reason.startswith("Document verification failed")
    assert _events(odoo_env, "seller.kyc_rejected", SELLER, custom.id) == [
        {"seller": "Custom Reject", "reason": "Trade license expired"}
    ]


# --------------------------------------------------------------------------
# Quotes
# --------------------------------------------------------------------------


def test_order_created_with_defaults_and_event(odoo_env):
    order = _order(odoo_env, budget=4000)
    assert order.name == "MKT/New"
    assert order.state == "open"
    assert order.order_type == "service_quote"
    assert order.currency_id == odoo_env.ref("base.BDT")
    assert _events(odoo_env, "marketplace_order.created", ORDER, order.id) == [
        {"order": "MKT/New", "budget": 4000.0, "type": "service_quote"}
    ]


def test_order_name_from_sequence(odoo_env):
    odoo_env["ir.sequence"].create({"name": "MKT test", "code": ORDER, "prefix": "MKT/T/"})
    assert _order(odoo_env).name.startswith("MKT/T/")


@pytest.mark.parametrize(("verified", "approved"), [(False, True), (True, False), (False, False)])
def test_only_verified_and_approved_sellers_quote(odoo_env, verified, approved):
    order = _order(odoo_env)
    seller = _seller(odoo_env, verified=verified, approved=approved)
    with pytest.raises(UserError, match="BRU-ECM-01"), odoo_env.cr.savepoint():
        _quote(odoo_env, order, seller)
    assert not order.quote_ids
    assert order.state == "open"


@pytest.mark.parametrize("price", [0.0, -10.0])
def test_quote_price_must_be_positive(odoo_env, price):
    order = _order(odoo_env)
    with pytest.raises(UserError, match="Quoted price must be positive"), odoo_env.cr.savepoint():
        _quote(odoo_env, order, _seller(odoo_env), price)


def test_first_quote_moves_order_to_quoted_and_publishes(odoo_env):
    order = _order(odoo_env)
    first = _quote(odoo_env, order, _seller(odoo_env, name="Seller One"), 3000)
    assert order.state == "quoted"
    second = _quote(odoo_env, order, _seller(odoo_env, name="Seller Two"), 2800, eta_days=1)
    assert order.state == "quoted"
    assert order.quote_ids == first | second
    assert first.state == second.state == "submitted"
    assert _events(odoo_env, "seller.quoted", QUOTE, second.id) == [
        {"seller": "Seller Two", "order": order.name, "price": 2800.0}
    ]


def test_no_quote_on_an_in_flight_order(odoo_env):
    order = _order(odoo_env)
    order.write({"state": "in_progress"})
    with pytest.raises(UserError, match="only accepted on open jobs"), odoo_env.cr.savepoint():
        _quote(odoo_env, order, _seller(odoo_env))
    assert order.state == "in_progress" and not order.quote_ids


# --------------------------------------------------------------------------
# Selection (BRU-ECM-05 / BRU-ECM-07)
# --------------------------------------------------------------------------


def test_select_quote_awards_order_and_reveals_contact(odoo_env):
    order = _order(odoo_env)
    winner_seller = _seller(odoo_env, name="Winner")
    winner = _quote(odoo_env, order, winner_seller, 2000)
    loser = _quote(odoo_env, order, _seller(odoo_env, name="Loser"), 2600)
    order.action_select_quote(winner)
    assert order.state == "selected"
    assert order.selected_quote_id == winner
    assert order.customer_contact_revealed is True
    assert order.revealed_seller_id == winner_seller
    assert winner.state == "selected"
    assert loser.state == "not_selected"
    assert _events(odoo_env, "order.selected", ORDER, order.id) == [
        {"seller": "Winner", "seller_id": winner_seller.id, "price": 2000.0}
    ]
    assert _events(odoo_env, "marketplace.contact_revealed", ORDER, order.id) == [
        {"seller_id": winner_seller.id, "order": order.name}
    ]


def test_select_quote_refused_once_awarded(odoo_env):
    order = _order(odoo_env)
    quote = _quote(odoo_env, order, _seller(odoo_env))
    order.action_select_quote(quote)
    with pytest.raises(UserError, match="Open or Quoted"):
        order.action_select_quote(quote)


def test_select_quote_of_another_order_refused(odoo_env):
    seller = _seller(odoo_env)
    order, other = _order(odoo_env), _order(odoo_env)
    foreign = _quote(odoo_env, other, seller)
    _quote(odoo_env, order, seller)
    with pytest.raises(UserError, match="does not belong"):
        order.action_select_quote(foreign)
    assert order.state == "quoted"


@pytest.mark.parametrize("change", [{"kyc_status": "rejected"}, {"cfo_approved": False}])
def test_select_quote_refused_when_seller_lost_standing(odoo_env, change):
    order = _order(odoo_env)
    seller = _seller(odoo_env)
    quote = _quote(odoo_env, order, seller)
    seller.write(change)
    with pytest.raises(UserError, match="unverified or unapproved"):
        order.action_select_quote(quote)


def test_select_quote_enforces_category_qualification(odoo_env):
    phones = odoo_env["product.category"].create({"name": "Phones (behaviour)"})
    laptops = odoo_env["product.category"].create({"name": "Laptops (behaviour)"})
    order = _order(odoo_env, category_id=laptops.id)
    seller = _seller(odoo_env, name="Phone Specialist", category_ids=[(6, 0, phones.ids)])
    quote = _quote(odoo_env, order, seller)
    with pytest.raises(UserError, match="not certified for category Laptops"):
        order.action_select_quote(quote)
    assert order.state == "quoted"


def test_select_quote_accepts_qualified_or_unrestricted_sellers(odoo_env):
    phones = odoo_env["product.category"].create({"name": "Phones (behaviour)"})
    qualified_order = _order(odoo_env, category_id=phones.id)
    qualified = _seller(odoo_env, name="Qualified", category_ids=[(6, 0, phones.ids)])
    qualified_order.action_select_quote(_quote(odoo_env, qualified_order, qualified))
    assert qualified_order.state == "selected"

    # A04 M12-11: a seller with NO approved categories is not qualified for
    # a category-restricted job (the gate used to skip him)
    unrestricted_order = _order(odoo_env, category_id=phones.id)
    generalist = _seller(odoo_env, name="Generalist")
    with pytest.raises(UserError, match="BRU-ECM-07"), odoo_env.cr.savepoint():
        unrestricted_order.action_select_quote(_quote(odoo_env, unrestricted_order, generalist))
    uncategorised = _order(odoo_env)
    uncategorised.action_select_quote(_quote(odoo_env, uncategorised, generalist))
    assert uncategorised.state == "selected"


# --------------------------------------------------------------------------
# Job execution, review, commission, payout
# --------------------------------------------------------------------------


def test_start_job_requires_selection(odoo_env):
    order = _order(odoo_env)
    with pytest.raises(UserError, match="must be selected"):
        order.action_start_job()
    awarded = _order_in(odoo_env, "selected")
    awarded.action_start_job()
    assert awarded.state == "in_progress"


def test_complete_requires_selected_seller(odoo_env):
    order = _order(odoo_env)
    order.write({"state": "in_progress"})
    with pytest.raises(UserError, match="No seller selected"):
        order.action_complete()


def test_complete_closes_contact_window(odoo_env):
    order = _order_in(odoo_env, "in_progress")
    seller = order.selected_quote_id.seller_id
    _job_evidence(order)
    order.action_complete()
    assert order.state == "completed"
    assert order.customer_contact_revealed is False
    assert _events(odoo_env, "marketplace_order.completed", ORDER, order.id) == [
        {"order": order.name, "seller_id": seller.id}
    ]


@pytest.mark.parametrize("state", ["selected", "completed", "reviewed", "commissioned", "paid"])
def test_complete_only_from_in_progress(odoo_env, state):
    """Regression: completion only checked for a selected quote, so a
    commissioned order could be completed, reviewed and commissioned AGAIN
    (commission.earned published twice for one job)."""
    order = _order_in(odoo_env, state)
    with pytest.raises(UserError, match="Only a job in progress"):
        order.action_complete()
    assert order.state == state


def test_commission_cannot_be_earned_twice(odoo_env):
    order = _order_in(odoo_env, "in_progress", price=3000)
    _job_evidence(order)
    order.action_complete()
    order.action_review()
    order.action_earn_commission()
    with pytest.raises(UserError):
        order.action_complete()
    with pytest.raises(UserError):
        order.action_earn_commission()
    assert len(_events(odoo_env, "commission.earned", ORDER, order.id)) == 1


def test_review_requires_completion(odoo_env):
    order = _order_in(odoo_env, "in_progress")
    with pytest.raises(UserError, match="requires completed job"):
        order.action_review()
    order.write({"state": "completed"})
    order.action_review()
    assert order.state == "reviewed"


def test_commission_requires_review(odoo_env):
    order = _order_in(odoo_env, "completed")
    with pytest.raises(UserError, match="Review required"):
        order.action_earn_commission()


def test_commission_uses_the_configured_rate_on_the_selected_quote(odoo_env):
    seller = _seller(odoo_env, name="Commission Seller")
    order = _order_in(odoo_env, "reviewed", seller=seller, price=4321.5)
    assert order.commission_rate == 0.10  # copied from the system parameter
    order.action_earn_commission()
    assert order.state == "commissioned"
    assert order.commission_amount == pytest.approx(432.15)
    assert _events(odoo_env, "commission.earned", ORDER, order.id) == [
        {
            "order_id": order.id,
            "seller_id": seller.id,
            "seller_partner_id": seller.partner_id.id,
            "seller_tier": "unrated",
            "order": order.name,
            "gross": 4321.5,
            "rate": 0.1,
            "commission": 432.15,
            "currency": "BDT",
            "payout_available_date": "",
        }
    ]


def test_commission_needs_an_awarded_seller(odoo_env):
    """A04 M12-5: a forged 'reviewed' order with no seller earned commission
    on its budget and was paid."""
    order = _order(odoo_env, budget=5000)
    order.write({"state": "reviewed"})
    with pytest.raises(UserError, match="no awarded seller"):
        order.action_earn_commission()
    assert not _events(odoo_env, "commission.earned", ORDER, order.id)


def test_commission_rate_is_configurable_and_fails_closed(odoo_env):
    params = odoo_env["ir.config_parameter"].sudo()
    order = _order_in(odoo_env, "reviewed", price=2000)
    order.commission_rate = 0.125  # a negotiated rate on this order
    order.action_earn_commission()
    assert order.commission_amount == 250.0
    params.set_param("cd_marketplace.platform_commission_rate", "0.08")
    assert _order(odoo_env).commission_rate == 0.08
    params.set_param("cd_marketplace.platform_commission_rate", "junk")
    unset = _order_in(odoo_env, "reviewed", price=2000)
    assert unset.commission_rate == 0.0
    with pytest.raises(UserError, match="No platform commission rate"):
        unset.action_earn_commission()
    assert unset.state == "reviewed"
    with pytest.raises(UserError, match="between 0 and 1"):
        unset.commission_rate = 1.5


def test_commission_blocked_by_open_dispute(odoo_env):
    order = _order_in(odoo_env, "reviewed")
    _dispute(odoo_env, order, order.selected_quote_id.seller_id)
    assert order.has_open_dispute is True
    with pytest.raises(UserError, match="BRU-BIL-03"):
        order.action_earn_commission()
    assert order.state == "reviewed"


def test_paid_after_commission_once_the_escrow_has_run(odoo_env):
    order = _order_in(odoo_env, "commissioned")
    with pytest.raises(UserError, match="no completed, customer-confirmed job"):
        order.action_paid()
    order.write(
        {
            "completed_at": fields.Datetime.now() - timedelta(days=9),
            "delivery_confirmed_at": fields.Datetime.now() - timedelta(days=8),
        }
    )
    order.action_paid()
    assert order.state == "paid"


@pytest.mark.parametrize("state", ["open", "selected", "reviewed", "cancelled", "paid"])
def test_paid_only_after_commission(odoo_env, state):
    """Regression: payout could be marked on an order that never earned a
    commission (even a cancelled one)."""
    order = _order_in(odoo_env, state)
    with pytest.raises(UserError, match="commission to be earned"):
        order.action_paid()
    assert order.state == state


def test_paid_blocked_by_open_dispute(odoo_env):
    order = _order_in(odoo_env, "commissioned")
    order.write({"completed_at": fields.Datetime.now() - timedelta(days=9)})
    _dispute(odoo_env, order, order.selected_quote_id.seller_id)
    with pytest.raises(UserError, match="open disputes"):
        order.action_paid()


def test_refurb_resale_listing_with_disclosures(odoo_env):
    stock = odoo_env["fix.graded.stock"].browse()
    unlinked = _order(odoo_env)
    unlinked.action_list_refurb_resale(stock, 18000)
    assert unlinked.order_type == "refurb_resale"
    assert unlinked.state == "open"
    assert unlinked.budget == 18000
    assert unlinked.battery_health_percent == 92.0
    assert unlinked.disclosed_defects == "Grade-A minor chassis scuff"
    assert _events(odoo_env, "marketplace.refurb_listed", ORDER, unlinked.id) == [
        {
            "order": unlinked.name,
            "stock_id": False,
            "battery_health": 92.0,
            "defects": "Grade-A minor chassis scuff",
            "price": 18000.0,
        }
    ]


@pytest.mark.parametrize("state", ["quoted", "selected", "completed", "commissioned", "cancelled"])
def test_refurb_listing_only_for_an_open_order(odoo_env, state):
    """Regression: listing reset an order in ANY state back to `open`, e.g.
    re-opening an awarded or already-commissioned job for new quotes."""
    order = _order_in(odoo_env, state)
    with pytest.raises(UserError, match="only an open order can be listed"):
        order.action_list_refurb_resale(odoo_env["fix.graded.stock"].browse(), 9000)
    assert order.state == state
    assert order.order_type == "service_quote"
    assert _events(odoo_env, "marketplace.refurb_listed", ORDER, order.id) == []


def _graded_stock(env, **vals):
    brand = env["fix.brand"].create({"name": "Behaviour Brand MKT", "code": "BBMKT"})
    model = env["fix.device.model"].create({"name": "Phone X", "brand_id": brand.id})
    device = env["fix.device"].create({"device_model_id": model.id})
    grade = env["fix.refurb.grade"].search([("code", "=", "B")], limit=1)
    return env["fix.graded.stock"].create(
        {"device_id": device.id, "grade_id": grade.id, "resale_price": 15000, **vals}
    )


@pytest.mark.parametrize("stock_state", ["reserved", "sold", "scrapped", "draft"])
def test_refurb_listing_requires_refurbished_unit_in_stock(odoo_env, stock_state):
    stock = _graded_stock(odoo_env, state=stock_state)
    order = _order(odoo_env)
    with pytest.raises(UserError, match="is not in stock"):
        order.action_list_refurb_resale(stock, 15000)
    assert order.order_type == "service_quote"
    assert not order.graded_stock_id


def test_refurb_resale_listing_links_graded_stock(odoo_env):
    brand = odoo_env["fix.brand"].create({"name": "Behaviour Brand MKT", "code": "BBMKT"})
    model = odoo_env["fix.device.model"].create({"name": "Phone X", "brand_id": brand.id})
    device = odoo_env["fix.device"].create({"device_model_id": model.id})
    grade = odoo_env["fix.refurb.grade"].search([("code", "=", "B")], limit=1)
    stock = odoo_env["fix.graded.stock"].create(
        {"device_id": device.id, "grade_id": grade.id, "resale_price": 15000}
    )
    order = _order(odoo_env)
    order.action_list_refurb_resale(stock, 15000, battery_health=81.0, defects="Back glass chip")
    assert order.graded_stock_id == stock
    assert order.battery_health_percent == 81.0
    (payload,) = _events(odoo_env, "marketplace.refurb_listed", ORDER, order.id)
    assert payload["stock_id"] == stock.id
    assert payload["defects"] == "Back glass chip"


# --------------------------------------------------------------------------
# Scoring & tiers
# --------------------------------------------------------------------------


def _score(env, seller, measured=True, **rates):
    """A score whose KPIs are taken as measured (formula/threshold tests)."""
    return env[SCORE].create(
        {"seller_id": seller.id, "period": "2026-09", "metrics_measured": measured, **rates}
    )


def test_composite_score_formula(odoo_env):
    score = _score(
        odoo_env,
        _seller(odoo_env),
        acceptance_rate=0.9,
        on_time_rate=0.8,
        review_rating=4.0,
        dispute_rate=0.1,
    )
    assert score.composite == pytest.approx(0.9 * 0.3 + 0.8 * 0.3 + 0.8 * 0.25 - 0.1 * 0.15)
    score.write({"dispute_rate": 0.0})
    assert score.composite == pytest.approx(0.71)


@pytest.mark.parametrize(
    ("rates", "tier"),
    [
        (
            {
                "acceptance_rate": 1.0,
                "on_time_rate": 1.0,
                "review_rating": 5.0,
                "dispute_rate": 0.0,
            },
            "platinum",
        ),
        (
            {
                "acceptance_rate": 0.9,
                "on_time_rate": 0.9,
                "review_rating": 4.5,
                "dispute_rate": 0.02,
            },
            "gold",
        ),
        (
            {
                "acceptance_rate": 0.7,
                "on_time_rate": 0.7,
                "review_rating": 3.0,
                "dispute_rate": 0.1,
            },
            "silver",
        ),
        (
            {
                "acceptance_rate": 0.5,
                "on_time_rate": 0.5,
                "review_rating": 2.5,
                "dispute_rate": 0.25,
            },
            "at_risk",
        ),
    ],
)
def test_ranking_tier_thresholds(odoo_env, rates, tier):
    seller = _seller(odoo_env)
    score = _score(odoo_env, seller, **rates)
    assert score.compute_ranking_tier() == tier
    assert seller.tier == tier
    assert _events(odoo_env, "seller.tier_updated", SELLER, seller.id) == [
        {"seller": seller.name, "tier": tier, "composite": score.composite}
    ]


def test_ranking_ranks_every_score_in_the_recordset(odoo_env):
    """Regression: compute_ranking_tier returned inside its loop, so only the
    first score of a batch was ranked."""
    top = _seller(odoo_env, name="Top")
    weak = _seller(odoo_env, name="Weak")
    scores = _score(
        odoo_env, top, acceptance_rate=1.0, on_time_rate=1.0, review_rating=5.0, dispute_rate=0.0
    ) | _score(
        odoo_env, weak, acceptance_rate=0.4, on_time_rate=0.4, review_rating=2.0, dispute_rate=0.5
    )
    assert scores.compute_ranking_tier() == "at_risk"
    assert top.tier == "platinum"
    assert weak.tier == "at_risk"


def test_ranking_empty_recordset(odoo_env):
    assert odoo_env[SCORE].compute_ranking_tier() is False


def test_new_score_has_no_invented_kpis(odoo_env):
    score = odoo_env[SCORE].create({"seller_id": _seller(odoo_env).id, "period": "2026-09"})
    assert (score.acceptance_rate, score.on_time_rate, score.review_rating) == (0.0, 0.0, 0.0)
    assert (score.dispute_rate, score.composite, score.metrics_measured) == (0.0, 0.0, False)
    assert score.compute_ranking_tier() == "unrated"


def test_publish_without_evidence_ranks_unrated(odoo_env):
    seller = _seller(odoo_env, name="Published")
    score = _score(odoo_env, seller, measured=False)
    score.action_publish()
    assert (score.composite, score.metrics_measured, seller.tier) == (0.0, False, "unrated")
    assert _events(odoo_env, "seller.scored", SCORE, score.id) == [
        {
            "seller": "Published",
            "period": "2026-09",
            "composite": 0.0,
            "tier": "unrated",
            "measured": False,
        }
    ]


def test_kpis_are_measured_from_real_quotes_orders_ratings_and_disputes(odoo_env):
    seller = _seller(odoo_env, name="Measured Seller")
    rival = _seller(odoo_env, name="Rival Seller")
    on_time = _order(odoo_env)
    on_time.action_select_quote(_quote(odoo_env, on_time, seller, eta_days=3))
    on_time.action_start_job()
    _job_evidence(on_time)
    on_time.action_complete()
    on_time.action_review(rating=4)
    late = _order(odoo_env)
    late.action_select_quote(_quote(odoo_env, late, seller, eta_days=1))
    late.action_start_job()
    _job_evidence(late)
    late.action_complete()
    late.write({"completed_at": late.started_at + timedelta(days=2)})
    late.action_review(rating=2)
    _dispute(odoo_env, late, seller)
    lost = _order(odoo_env)
    _quote(odoo_env, lost, seller)
    lost.action_select_quote(_quote(odoo_env, lost, rival))
    with pytest.raises(UserError, match="1 to 5"), odoo_env.cr.savepoint():
        on_time.review_rating = 9
    period = fields.Datetime.now().strftime("%Y-%m")
    score = odoo_env[SCORE].create({"seller_id": seller.id, "period": period})
    score.action_publish()
    assert (score.quotes_decided, score.orders_awarded) == (3, 2)
    assert (score.orders_timed, score.orders_rated) == (2, 2)
    assert score.acceptance_rate == pytest.approx(2 / 3)
    assert score.on_time_rate == 0.5
    assert score.review_rating == 3.0
    assert score.dispute_rate == 0.5
    assert score.metrics_measured is True
    assert score.composite == pytest.approx(
        round((2 / 3) * 0.3 + 0.5 * 0.3 + (3.0 / 5.0) * 0.25 - 0.5 * 0.15, 4)
    )
    assert seller.tier == "at_risk"  # 0.4 composite
    empty = odoo_env[SCORE].create({"seller_id": seller.id, "period": "2001-12"})
    empty.action_measure()
    assert (empty.orders_awarded, empty.metrics_measured) == (0, False)
    with pytest.raises(UserError, match="YYYY-MM"):
        odoo_env[SCORE].create({"seller_id": seller.id, "period": "Sept"}).action_measure()


# --------------------------------------------------------------------------
# Disputes, SLA and payout lock
# --------------------------------------------------------------------------


def test_dispute_sets_48h_sla_and_locks_payout(odoo_env):
    order = _order_in(odoo_env, "completed")
    seller = order.selected_quote_id.seller_id
    before = fields.Datetime.now()
    dispute = _dispute(odoo_env, order, seller, disputed_amount=1200, dispute_reason="delay")
    assert dispute.name == "DSP/New"
    assert dispute.state == "raised"
    assert before + timedelta(hours=48) <= dispute.sla_deadline
    assert dispute.sla_deadline <= fields.Datetime.now() + timedelta(hours=48)
    assert dispute.sla_breached is False
    assert seller.payout_hold is True
    assert order.has_open_dispute is True
    assert _events(odoo_env, "marketplace.dispute_raised", DISPUTE, dispute.id) == [
        {
            "dispute": "DSP/New",
            "order": order.name,
            "seller": seller.name,
            "amount": 1200.0,
            "sla_deadline": str(dispute.sla_deadline),
        }
    ]


def test_dispute_explicit_deadline_and_sequence(odoo_env):
    odoo_env["ir.sequence"].create({"name": "DSP test", "code": DISPUTE, "prefix": "DSP/T/"})
    order = _order_in(odoo_env, "completed")
    past = fields.Datetime.now() - timedelta(hours=1)
    dispute = _dispute(odoo_env, order, order.selected_quote_id.seller_id, sla_deadline=past)
    assert dispute.name.startswith("DSP/T/")
    assert dispute.sla_deadline == past.replace(microsecond=0)
    assert dispute.sla_breached is True


def test_sla_breach_after_resolution_compares_resolution_time(odoo_env):
    order = _order_in(odoo_env, "completed")
    seller = order.selected_quote_id.seller_id
    now = fields.Datetime.now()
    on_time = _dispute(odoo_env, order, seller)
    late = _dispute(odoo_env, order, seller, sla_deadline=now - timedelta(days=1))
    on_time.write({"state": "resolved", "resolved_date": now})
    late.write({"state": "resolved", "resolved_date": now})
    assert on_time.sla_breached is False
    assert late.sla_breached is True
    # without a deadline nothing can be breached, resolved or not
    late.write({"sla_deadline": False})
    assert late.sla_breached is False
    open_one = _dispute(odoo_env, order, seller)
    open_one.write({"sla_deadline": False})
    assert open_one.sla_breached is False


def test_sla_breach_is_live_for_untouched_disputes(odoo_env):
    """Regression: sla_breached was STORED, computed at the last write, so a
    dispute whose 48h deadline simply elapsed (nobody touched it) kept
    reporting "not breached" forever."""
    order = _order_in(odoo_env, "completed")
    dispute = _dispute(odoo_env, order, order.selected_quote_id.seller_id)
    assert dispute.sla_breached is False
    # time passes: the deadline is now behind us, with no ORM write at all
    elapsed = fields.Datetime.now() - timedelta(minutes=5)
    odoo_env.cr.execute(
        "UPDATE fix_marketplace_dispute SET sla_deadline = %s WHERE id = %s",
        (elapsed, dispute.id),
    )
    odoo_env.invalidate_all()
    assert dispute.sla_breached is True
    assert odoo_env[DISPUTE].search([("id", "=", dispute.id), ("sla_breached", "=", True)])


def _sla_matrix(env):
    order = _order_in(env, "completed")
    seller = order.selected_quote_id.seller_id
    now = fields.Datetime.now()
    rows = {
        "open_late": _dispute(env, order, seller, sla_deadline=now - timedelta(hours=1)),
        "open_on_time": _dispute(env, order, seller),
        "open_no_deadline": _dispute(env, order, seller),
        "resolved_late": _dispute(env, order, seller, sla_deadline=now - timedelta(days=1)),
        "resolved_on_time": _dispute(env, order, seller),
        "resolved_no_dates": _dispute(env, order, seller),
        "escalated_late": _dispute(env, order, seller, sla_deadline=now - timedelta(hours=2)),
    }
    rows["open_no_deadline"].write({"sla_deadline": False})
    rows["resolved_late"].write({"state": "resolved", "resolved_date": now})
    rows["resolved_on_time"].write({"state": "resolved", "resolved_date": now})
    rows["resolved_no_dates"].write({"state": "resolved", "sla_deadline": False})
    rows["escalated_late"].write({"state": "escalated"})
    breached = {"open_late", "resolved_late", "escalated_late"}
    return rows, breached


@pytest.mark.parametrize(
    ("condition", "expect_breached"),
    [
        (("=", True), True),
        (("!=", False), True),
        (("=", False), False),
        (("!=", True), False),
    ],
)
def test_sla_breached_is_searchable(odoo_env, condition, expect_breached):
    rows, breached = _sla_matrix(odoo_env)
    ids = [rec.id for rec in rows.values()]
    found = odoo_env[DISPUTE].search([("id", "in", ids), ("sla_breached", *condition)])
    expected = {k for k in rows if (k in breached) == expect_breached}
    assert {k for k, rec in rows.items() if rec in found} == expected
    # the search method agrees with the computed value on every record
    assert all(rec.sla_breached is expect_breached for rec in found)


def test_sla_breached_search_accepts_both_values(odoo_env):
    rows, _breached = _sla_matrix(odoo_env)
    ids = [rec.id for rec in rows.values()]
    found = odoo_env[DISPUTE].search([("id", "in", ids), ("sla_breached", "in", [True, False])])
    assert len(found) == len(rows)


def test_sla_breached_filters_in_memory(odoo_env):
    rows, breached = _sla_matrix(odoo_env)
    records = odoo_env[DISPUTE].browse([rec.id for rec in rows.values()])
    kept = records.filtered_domain([("sla_breached", "=", True)])
    assert {k for k, rec in rows.items() if rec in kept} == breached


def test_dispute_search_view_filters_breached_disputes(odoo_env):
    rows, breached = _sla_matrix(odoo_env)
    view = odoo_env.ref("cd_marketplace.view_fix_marketplace_dispute_search")
    arch = etree.fromstring(view.arch)  # noqa: S320 - the module's own view arch
    domain = safe_eval(arch.find(".//filter[@name='filter_sla_breached']").get("domain"))
    ids = [rec.id for rec in rows.values()]
    found = odoo_env[DISPUTE].search([("id", "in", ids), *domain])
    assert {k for k, rec in rows.items() if rec in found} == breached
    # it is the model's default search view, i.e. what the Disputes menu shows
    default_search = odoo_env[DISPUTE].get_views([(False, "search")])["views"]["search"]
    assert "filter_sla_breached" in default_search["arch"]


def test_investigate_and_arbitrate(odoo_env):
    order = _order_in(odoo_env, "completed")
    dispute = _dispute(odoo_env, order, order.selected_quote_id.seller_id)
    dispute.action_investigate()
    assert dispute.state == "investigating"
    with pytest.raises(UserError, match="Propose the ruling"):
        dispute.action_arbitrate()
    dispute.write({"proposed_resolution": "payout_seller", "resolution_notes": "No fault"})
    dispute.action_arbitrate()
    assert (dispute.state, dispute.approval_state) == ("arbitration", "pending")
    assert order.has_open_dispute is True


def test_resolving_last_dispute_releases_payout(odoo_env):
    order = _order_in(odoo_env, "completed")
    seller = order.selected_quote_id.seller_id
    dispute = _dispute(odoo_env, order, seller)
    dispute.action_resolve(resolution_type="split_settlement", notes="50/50")
    assert dispute.state == "resolved"
    assert dispute.resolution_type == "split_settlement"
    assert dispute.resolution_notes == "50/50"
    assert dispute.resolved_by == odoo_env.user
    assert dispute.resolved_date
    assert seller.payout_hold is False
    assert order.has_open_dispute is False
    assert _events(odoo_env, "marketplace.dispute_resolved", DISPUTE, dispute.id) == [
        {
            "dispute": dispute.name,
            "order": order.name,
            "order_id": order.id,
            "seller": seller.name,
            "seller_id": seller.id,
            "seller_partner_id": seller.partner_id.id,
            "customer_id": order.customer_id.id,
            "resolution": "split_settlement",
            "disputed_amount": 0.0,
            "refund_amount": 0.0,
            "currency": "BDT",
            "payout_unlocked": True,
        }
    ]


def test_resolving_one_of_two_disputes_keeps_payout_lock(odoo_env):
    order = _order_in(odoo_env, "completed")
    seller = order.selected_quote_id.seller_id
    first = _dispute(odoo_env, order, seller)
    _dispute(odoo_env, order, seller).action_investigate()
    first.action_resolve()
    assert first.resolution_type == "payout_seller"
    assert seller.payout_hold is True
    assert order.has_open_dispute is True
    (payload,) = _events(odoo_env, "marketplace.dispute_resolved", DISPUTE, first.id)
    assert payload["payout_unlocked"] is False


def test_escalation_marks_seller_at_risk(odoo_env):
    order = _order_in(odoo_env, "completed")
    seller = order.selected_quote_id.seller_id
    dispute = _dispute(odoo_env, order, seller)
    dispute.action_escalate()
    assert dispute.state == "escalated"
    assert seller.tier == "at_risk"
    assert _events(odoo_env, "marketplace.dispute_escalated", DISPUTE, dispute.id) == [
        {"dispute": dispute.name, "order": order.name, "seller": seller.name}
    ]


def test_escalated_dispute_keeps_the_payout_lock(odoo_env):
    """Regression: an escalated (still unresolved) dispute was not counted as
    open, so escalating LIFTED the BRU-BIL-03 lock — commission and payout
    could proceed, and resolving a sibling dispute released the seller hold."""
    order = _order_in(odoo_env, "reviewed")
    seller = order.selected_quote_id.seller_id
    escalated = _dispute(odoo_env, order, seller)
    sibling = _dispute(odoo_env, order, seller)
    escalated.action_escalate()
    assert order.has_open_dispute is True
    with pytest.raises(UserError, match="BRU-BIL-03"):
        order.action_earn_commission()
    sibling.action_resolve()
    assert seller.payout_hold is True
    # resolving the escalated dispute finally releases everything
    escalated.action_resolve(resolution_type="refund_customer")
    assert seller.payout_hold is False
    assert order.has_open_dispute is False
    order.action_earn_commission()
    assert order.state == "commissioned"
