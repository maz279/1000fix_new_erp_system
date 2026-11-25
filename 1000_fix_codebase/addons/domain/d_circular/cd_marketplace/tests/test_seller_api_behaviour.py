"""cd_marketplace seller API behaviour (live ORM, rolled back).

The controller module's `request` is replaced by a fake exposing env /
session / httprequest and the endpoints are called directly, so the tests
exercise the real routing wrappers and the real ORM behind them."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from odoo.addons.cd_marketplace.controllers import seller_api
from odoo.addons.cd_marketplace.controllers.seller_api import SellerApiController, _fmt_bdt


@pytest.fixture
def api(odoo_env, monkeypatch):
    """Bind the controller to a fake request on `odoo_env`; returns a setter
    to switch the acting environment (e.g. to a portal user)."""
    fake = SimpleNamespace(
        env=odoo_env,
        session={},
        httprequest=SimpleNamespace(remote_addr="127.0.0.1", headers={}),
    )
    monkeypatch.setattr(seller_api, "request", fake)

    def act_as(env):
        fake.env = env

    controller = SellerApiController()
    controller.act_as = act_as
    return controller


def _partner(env, name):
    return env["res.partner"].create({"name": name})


def _seller(env, name="API Seller", partner=None, verified=True, approved=True):
    seller = env["fix.marketplace.seller"].create(
        {"name": name, "partner_id": (partner or _partner(env, name)).id}
    )
    seller.write({"kyc_status": "verified" if verified else "pending", "cfo_approved": approved})
    return seller


def _order(env, budget=1500.0, **vals):
    return env["fix.marketplace.order"].create(
        {
            "customer_id": _partner(env, "API Customer").id,
            "description": "Battery swap",
            "budget": budget,
            "customer_consent": True,
            "consent_method": "signed",  # BRU-MKP-07
            **vals,
        }
    )


def _portal_env(odoo_env, partner):
    user = odoo_env["res.users"].create(
        {
            "name": partner.name,
            "login": f"portal-seller-{partner.id}",
            "partner_id": partner.id,
            "group_ids": [(6, 0, [odoo_env.ref("base.group_portal").id])],
        }
    )
    # su keeps record rules out of the way: the controller's own scoping is under test
    return odoo_env(user=user.id, su=True)


# --------------------------------------------------------------------------
# _fmt_bdt — BN-007 money strings
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("amount", "text"),
    [
        (0, "0.00"),
        (5, "5.00"),
        (999.5, "999.50"),
        (1000, "1,000.00"),
        (123456.78, "1,23,456.78"),
        (12345678.9, "1,23,45,678.90"),
        ("2500", "2,500.00"),
        (None, "0.00"),
        ("not-a-number", "0.00"),
        (float("nan"), "0.00"),
        (float("inf"), "0.00"),
        (1e30, "0.00"),
    ],
)
def test_fmt_bdt_groups_south_asian_style(amount, text):
    assert _fmt_bdt(amount) == text


@pytest.mark.parametrize(
    ("amount", "text"),
    [
        (999.999, "1,000.00"),  # was "999.00": the paisa carry was dropped
        (1.995, "2.00"),
        (1234.995, "1,235.00"),
        (-1234.5, "-1,234.50"),  # was "-1,2340.50"
        (-0.5, "-0.50"),  # was "00.50"
        (-0.001, "0.00"),
    ],
)
def test_fmt_bdt_rounds_before_splitting_and_keeps_sign(amount, text):
    """Regression: the fraction was formatted separately from the whole part,
    losing the rounding carry and mangling negative amounts."""
    assert _fmt_bdt(amount) == text


# --------------------------------------------------------------------------
# Seller resolution (EA-05 / anti-IDOR)
# --------------------------------------------------------------------------


def test_dashboard_without_seller_profile(api):
    result = api.dashboard()
    assert result["error"]["code"] == "no_seller"


@pytest.mark.parametrize("seller_id", ["abc", "999999999"])
def test_dashboard_unknown_or_malformed_seller_id(api, seller_id):
    assert api.dashboard(seller_id=seller_id)["error"]["code"] == "no_seller"


def test_dashboard_for_internal_user_by_seller_id(odoo_env, api):
    """Regression: the dashboard read `seller.kyc_ref`, a field the model
    does not have, so every seller dashboard call raised AttributeError."""
    seller = _seller(odoo_env, name="Dash Seller", verified=False)
    seller.write({"rating": 4.6, "total_jobs": 12})
    odoo_env["ir.attachment"].create(
        {"name": "kyc.pdf", "datas": "UERG", "res_model": seller._name, "res_id": seller.id}
    )  # A04 ERP M12-F8: KYC is submitted with its documents
    seller.action_submit_kyc()
    result = api.dashboard(seller_id=str(seller.id))
    assert result == {
        "seller": {
            "id": seller.id,
            "name": "Dash Seller",
            "kyc_status": "in_review",
            "kyc_ref": seller.kyc_doc_z4_ref,
            "rating": 4.6,
            "total_jobs": 12,
        }
    }
    # A04 ERP M12-F8: the reference of real documents, never a made-up token
    assert result["seller"]["kyc_ref"].startswith("attachment:")


def test_dashboard_kyc_ref_empty_before_submission(odoo_env, api):
    seller = _seller(odoo_env)
    assert api.dashboard(seller_id=seller.id)["seller"]["kyc_ref"] == ""


def test_portal_user_resolves_own_seller_from_session_partner(odoo_env, api):
    partner = _partner(odoo_env, "Portal Seller Co")
    seller = _seller(odoo_env, partner=partner)
    api.act_as(_portal_env(odoo_env, partner))
    assert api.dashboard()["seller"]["id"] == seller.id
    assert api.dashboard(seller_id=seller.id)["seller"]["id"] == seller.id


def test_portal_user_cannot_act_for_another_seller(odoo_env, api):
    mine = _partner(odoo_env, "Portal Mine")
    _seller(odoo_env, partner=mine)
    other = _seller(odoo_env, name="Someone Else")
    api.act_as(_portal_env(odoo_env, mine))
    assert api.dashboard(seller_id=other.id)["error"]["code"] == "no_seller"
    assert api.orders(seller_id=other.id)["error"]["code"] == "no_seller"
    assert api.quotes(seller_id=other.id)["error"]["code"] == "no_seller"
    assert api.scorecard(seller_id=other.id)["error"]["code"] == "no_seller"
    assert api.disputes(seller_id=other.id)["error"]["code"] == "no_seller"


# --------------------------------------------------------------------------
# Jobs board
# --------------------------------------------------------------------------


def test_orders_requires_seller(api):
    assert api.orders()["error"]["code"] == "no_seller"


def test_orders_board_shows_biddable_jobs_with_own_quote_only(odoo_env, api):
    """Regression: the board listed only `open` jobs, but the first quote moves
    a job to `quoted` — so a quoted job vanished for every other seller and a
    seller never saw their own `my_quote`."""
    me = _seller(odoo_env, name="Board Me")
    rival = _seller(odoo_env, name="Board Rival")
    fresh = _order(odoo_env, budget=123456.78)
    contested = _order(odoo_env)
    awarded = _order(odoo_env)
    rival_quote = odoo_env["fix.seller.quote"].create(
        {"marketplace_order_id": contested.id, "seller_id": rival.id, "quoted_price": 900}
    )
    my_quote = odoo_env["fix.seller.quote"].create(
        {
            "marketplace_order_id": contested.id,
            "seller_id": me.id,
            "quoted_price": 1100.5,
            "eta_days": 2,
        }
    )
    awarded_quote = odoo_env["fix.seller.quote"].create(
        {"marketplace_order_id": awarded.id, "seller_id": rival.id, "quoted_price": 700}
    )
    awarded.action_select_quote(awarded_quote)

    result = api.orders(seller_id=me.id)
    by_id = {row["id"]: row for row in result["orders"]}
    assert fresh.id in by_id and contested.id in by_id
    assert awarded.id not in by_id
    assert result["total"] == len(result["orders"])
    assert by_id[fresh.id]["budget_bdt"] == "1,23,456.78"
    assert by_id[fresh.id]["state"] == "open"
    assert by_id[fresh.id]["my_quote"] is None
    assert by_id[contested.id]["state"] == "quoted"
    assert by_id[contested.id]["my_quote"] == {
        "id": my_quote.id,
        "price_bdt": "1,100.50",
        "eta_days": 2,
        "state": "submitted",
    }
    assert rival_quote.id not in {(row["my_quote"] or {}).get("id") for row in result["orders"]}


# --------------------------------------------------------------------------
# Quotes: listing and submission
# --------------------------------------------------------------------------


def test_quotes_listing_requires_seller(api):
    assert api.quotes()["error"]["code"] == "no_seller"


def test_quotes_listing_returns_only_own_quotes(odoo_env, api):
    me = _seller(odoo_env, name="Lister")
    rival = _seller(odoo_env, name="Other Lister")
    order = _order(odoo_env)
    mine = odoo_env["fix.seller.quote"].create(
        {"marketplace_order_id": order.id, "seller_id": me.id, "quoted_price": 2500, "eta_days": 4}
    )
    odoo_env["fix.seller.quote"].create(
        {"marketplace_order_id": order.id, "seller_id": rival.id, "quoted_price": 2400}
    )
    assert api.quotes(seller_id=me.id) == {
        "quotes": [
            {
                "id": mine.id,
                "order_name": order.name,
                "price_bdt": "2,500.00",
                "eta_days": 4,
                "state": "submitted",
            }
        ],
        "total": 1,
    }


def test_submit_quote_requires_seller(odoo_env, api):
    order = _order(odoo_env)
    assert api.quotes(order_id=order.id, quoted_price=100)["error"]["code"] == "no_seller"


def test_submit_quote_requires_verified_kyc(odoo_env, api):
    seller = _seller(odoo_env, verified=False)
    order = _order(odoo_env)
    result = api.quotes(seller_id=seller.id, order_id=order.id, quoted_price=100)
    assert result["error"]["code"] == "kyc_not_verified"
    assert not order.quote_ids


@pytest.mark.parametrize("price", [None, 0, -5, "abc", "nan", "inf"])
def test_submit_quote_rejects_invalid_price(odoo_env, api, price):
    """Regression (non-numeric input): `float("abc")` used to escape as a 500."""
    seller = _seller(odoo_env)
    order = _order(odoo_env)
    kwargs = {"seller_id": seller.id, "order_id": order.id}
    if price is not None:
        kwargs["quoted_price"] = price
    assert api.quotes(**kwargs)["error"]["code"] == "invalid_price"
    assert not order.quote_ids


@pytest.mark.parametrize("eta", ["soon", "2.5", None])
def test_submit_quote_rejects_invalid_eta(odoo_env, api, eta):
    seller = _seller(odoo_env)
    order = _order(odoo_env)
    result = api.quotes(seller_id=seller.id, order_id=order.id, quoted_price=100, eta_days=eta)
    assert result["error"]["code"] == "invalid_eta"
    assert not order.quote_ids


@pytest.mark.parametrize("order_ref", ["missing", "abc"])
def test_submit_quote_requires_existing_order(odoo_env, api, order_ref):
    seller = _seller(odoo_env)
    order_id = 999999999 if order_ref == "missing" else "abc"
    result = api.quotes(seller_id=seller.id, order_id=order_id, quoted_price=100)
    assert result["error"]["code"] == "order_not_open"


def test_submit_quote_refused_on_awarded_job(odoo_env, api):
    seller = _seller(odoo_env)
    order = _order(odoo_env)
    order.action_select_quote(
        odoo_env["fix.seller.quote"].create(
            {"marketplace_order_id": order.id, "seller_id": seller.id, "quoted_price": 500}
        )
    )
    result = api.quotes(seller_id=seller.id, order_id=order.id, quoted_price=450)
    assert result["error"]["code"] == "order_not_open"
    assert len(order.quote_ids) == 1


def test_submit_quote_creates_quote(odoo_env, api):
    seller = _seller(odoo_env)
    order = _order(odoo_env)
    result = api.quotes(
        seller_id=seller.id,
        order_id=str(order.id),
        quoted_price="1750.25",
        eta_days="5",
        notes="OEM part",
    )
    quote = order.quote_ids
    assert result == {"quote": {"id": quote.id, "state": "submitted"}}
    assert quote.seller_id == seller
    assert quote.quoted_price == 1750.25
    assert quote.eta_days == 5
    assert quote.notes == "OEM part"
    assert order.state == "quoted"


def test_second_seller_can_still_quote_a_quoted_job(odoo_env, api):
    """Regression: the first quote moved the job to `quoted` and every later
    seller got `order_not_open` — competing quotes were impossible."""
    first = _seller(odoo_env, name="First Bidder")
    second = _seller(odoo_env, name="Second Bidder")
    order = _order(odoo_env)
    assert "quote" in api.quotes(seller_id=first.id, order_id=order.id, quoted_price=1000)
    result = api.quotes(seller_id=second.id, order_id=order.id, quoted_price=950)
    assert "quote" in result
    assert order.quote_ids.mapped("seller_id") == first | second
    assert next(q for q in order.quote_ids if q.seller_id == second).eta_days == 3


def test_submit_quote_model_rejection_is_structured(odoo_env, api):
    # KYC verified but no CFO approval: the model's BRU-ECM-01 gate refuses
    seller = _seller(odoo_env, approved=False)
    order = _order(odoo_env)
    with odoo_env.cr.savepoint():
        result = api.quotes(seller_id=seller.id, order_id=order.id, quoted_price=100)
    assert result["error"]["code"] == "quote_rejected"
    assert "BRU-ECM-01" in result["error"]["message"]


# --------------------------------------------------------------------------
# Scorecard and disputes
# --------------------------------------------------------------------------


def test_scorecard_requires_seller(api):
    assert api.scorecard()["error"]["code"] == "no_seller"


def test_scorecard_lists_periods_newest_first(odoo_env, api):
    seller = _seller(odoo_env)
    odoo_env["fix.seller.score"].create(
        [
            {"seller_id": seller.id, "period": "2026-08", "dispute_rate": 0.05},
            {"seller_id": seller.id, "period": "2026-09"},
        ]
    )
    result = api.scorecard(seller_id=seller.id)
    assert result["total"] == 2
    assert [row["period"] for row in result["scorecard"]] == ["2026-09", "2026-08"]
    assert result["scorecard"][1]["dispute_rate"] == 0.05
    assert set(result["scorecard"][0]) == {
        "period",
        "acceptance_rate",
        "on_time_rate",
        "review_rating",
        "dispute_rate",
        "composite",
    }


def test_disputes_requires_seller(api):
    assert api.disputes()["error"]["code"] == "no_seller"


def test_disputes_lists_own_disputes_with_sla(odoo_env, api):
    seller = _seller(odoo_env)
    other = _seller(odoo_env, name="Other Disputed")
    order = _order(odoo_env)
    dispute = odoo_env["fix.marketplace.dispute"].create(
        {
            "order_id": order.id,
            "seller_id": seller.id,
            "customer_id": order.customer_id.id,
            "description": "Late delivery",
            "dispute_reason": "delay",
            "disputed_amount": 1234.5,
        }
    )
    odoo_env["fix.marketplace.dispute"].create(
        {
            "order_id": order.id,
            "seller_id": other.id,
            "customer_id": order.customer_id.id,
            "description": "Not mine",
        }
    )
    assert api.disputes(seller_id=seller.id) == {
        "disputes": [
            {
                "id": dispute.name,
                "order_ref": order.name,
                "dispute_reason": "delay",
                "disputed_amount_bdt": "1,234.50",
                "state": "raised",
                "sla_breached": False,
                "description": "Late delivery",
            }
        ],
        "total": 1,
    }


def test_the_openapi_contract_lists_the_seller_operations():
    """Moved from the retired source-inspection suite (test_seller_api.py)."""
    import json
    from pathlib import Path

    repo = Path(__file__).resolve().parents[5]
    spec = json.loads((repo / "contracts" / "openapi" / "w4-portals.json").read_text("utf-8"))
    for path in ("/seller/dashboard", "/seller/orders", "/seller/quotes", "/seller/scorecard"):
        assert path in spec["paths"]
