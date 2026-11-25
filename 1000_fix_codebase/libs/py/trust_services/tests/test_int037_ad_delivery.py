"""Behavioural tests for INT-037 ad delivery, budgeting and attribution."""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import libs.py.trust_services as trust_services
from libs.py.trust_services.int037_ads import (
    AdCampaign,
    AdDeliveryEngine,
    AdPlacement,
)

HERO = "home_hero_banner"
SEARCH = "search_sponsored"


@pytest.fixture
def engine() -> AdDeliveryEngine:
    return AdDeliveryEngine()


def _campaign(**overrides: object) -> AdCampaign:
    fields: dict = {
        "campaign_id": "CMP-X",
        "seller_id": 1,
        "title": "t",
        "target_categories": ["ALL"],
        "placement": HERO,
        "budget_bdt": 100.0,
        "cpc_rate_bdt": 5.0,
        "cpm_rate_bdt": 50.0,
    }
    fields.update(overrides)
    return AdCampaign(**fields)


def test_package_exports_the_int037_api() -> None:
    assert trust_services.AdDeliveryEngine is AdDeliveryEngine
    assert trust_services.AdCampaign is AdCampaign
    assert trust_services.AdPlacement is AdPlacement is str


# --------------------------------------------------------------------------
# AdCampaign
# --------------------------------------------------------------------------


def test_campaign_defaults() -> None:
    camp = _campaign()
    assert (camp.spent_bdt, camp.impressions, camp.clicks, camp.conversions) == (0.0, 0, 0, 0)
    assert camp.state == "active"
    assert datetime.fromisoformat(camp.created_at).tzinfo is not None


def test_remaining_budget_is_rounded_and_never_negative() -> None:
    assert _campaign(budget_bdt=10.0, spent_bdt=3.333).remaining_budget == 6.67
    assert _campaign(budget_bdt=10.0, spent_bdt=12.0).remaining_budget == 0.0


def test_ctr_is_zero_without_impressions_and_a_rounded_percentage_otherwise() -> None:
    assert _campaign(clicks=5).ctr == 0.0
    assert _campaign(impressions=3, clicks=1).ctr == 33.33


# --------------------------------------------------------------------------
# create / get
# --------------------------------------------------------------------------


def test_create_campaign_normalises_inputs(engine: AdDeliveryEngine) -> None:
    camp = engine.create_campaign(
        seller_id=42,
        title="Summer AC service",
        target_categories=["home_appliances", "Ac"],
        placement=SEARCH,
        budget_bdt=500,
        cpc_rate_bdt=4,
        cpm_rate_bdt=40,
    )
    assert re.match(r"^CMP-[0-9A-F]{10}$", camp.campaign_id)
    assert camp.target_categories == ["HOME_APPLIANCES", "AC"]
    assert (camp.budget_bdt, camp.cpc_rate_bdt, camp.cpm_rate_bdt) == (500.0, 4.0, 40.0)
    assert all(isinstance(v, float) for v in (camp.budget_bdt, camp.cpc_rate_bdt))
    assert camp.state == "active"
    assert engine.get_campaign(camp.campaign_id) is camp


def test_create_campaign_with_explicit_id_and_default_rates(engine: AdDeliveryEngine) -> None:
    camp = engine.create_campaign(1, "t", ["ALL"], HERO, 100.0, campaign_id="CMP-FIXED")
    assert camp.campaign_id == "CMP-FIXED"
    assert (camp.cpc_rate_bdt, camp.cpm_rate_bdt) == (5.0, 50.0)


@pytest.mark.parametrize("budget", [0, -1.0])
def test_non_positive_budget_is_rejected(engine: AdDeliveryEngine, budget: float) -> None:
    with pytest.raises(ValueError, match="budget must be positive"):
        engine.create_campaign(1, "t", ["ALL"], HERO, budget)
    assert engine._campaigns == {}


@pytest.mark.parametrize(("cpc", "cpm"), [(0, 50.0), (5.0, 0), (-1.0, 50.0), (5.0, -2.0)])
def test_non_positive_rates_are_rejected(engine: AdDeliveryEngine, cpc: float, cpm: float) -> None:
    with pytest.raises(ValueError, match="CPC and CPM rates must be positive"):
        engine.create_campaign(1, "t", ["ALL"], HERO, 100.0, cpc_rate_bdt=cpc, cpm_rate_bdt=cpm)


def test_get_unknown_campaign_returns_none(engine: AdDeliveryEngine) -> None:
    assert engine.get_campaign("CMP-NOPE") is None


# --------------------------------------------------------------------------
# serve_ads
# --------------------------------------------------------------------------


@pytest.fixture
def stocked(engine: AdDeliveryEngine) -> AdDeliveryEngine:
    engine.create_campaign(1, "Laptops", ["it_equipment"], HERO, 100, campaign_id="C-IT")
    engine.create_campaign(2, "Everything", ["ALL"], HERO, 100, campaign_id="C-ALL")
    engine.create_campaign(3, "Phones", ["mobile"], HERO, 100, campaign_id="C-MOB")
    engine.create_campaign(4, "Search IT", ["it_equipment"], SEARCH, 100, campaign_id="C-SRCH")
    paused = engine.create_campaign(5, "Paused IT", ["it_equipment"], HERO, 100, campaign_id="C-P")
    paused.state = "paused"
    return engine


def test_serve_ads_filters_by_state_placement_and_category(stocked: AdDeliveryEngine) -> None:
    ads = stocked.serve_ads(HERO, category="It_Equipment", limit=10)
    assert [a["campaign_id"] for a in ads] == ["C-IT", "C-ALL"]
    assert ads[0] == {
        "campaign_id": "C-IT",
        "seller_id": 1,
        "title": "Laptops",
        "placement": HERO,
        "target_categories": ["IT_EQUIPMENT"],
    }


def test_serve_ads_without_category_returns_every_active_ad_for_placement(
    stocked: AdDeliveryEngine,
) -> None:
    ids = [a["campaign_id"] for a in stocked.serve_ads(HERO, limit=10)]
    assert ids == ["C-IT", "C-ALL", "C-MOB"]
    assert [a["campaign_id"] for a in stocked.serve_ads(SEARCH)] == ["C-SRCH"]


def test_serve_ads_respects_limit(stocked: AdDeliveryEngine) -> None:
    assert [a["campaign_id"] for a in stocked.serve_ads(HERO, limit=2)] == ["C-IT", "C-ALL"]
    assert len(stocked.serve_ads(HERO)) == 3  # default limit


def test_serve_ads_unknown_category_only_matches_wildcard(stocked: AdDeliveryEngine) -> None:
    assert [a["campaign_id"] for a in stocked.serve_ads(HERO, "tv")] == ["C-ALL"]
    assert stocked.serve_ads("category_banner") == []


# --------------------------------------------------------------------------
# Impressions, clicks, conversions, analytics
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "record", ["record_impression", "record_click", "record_conversion", "get_analytics"]
)
def test_unknown_campaign_is_reported(engine: AdDeliveryEngine, record: str) -> None:
    assert getattr(engine, record)("CMP-NOPE") == {"error": "campaign_not_found"}


@pytest.mark.parametrize("record", ["record_impression", "record_click"])
def test_billing_events_on_inactive_campaign_are_refused(
    engine: AdDeliveryEngine, record: str
) -> None:
    camp = engine.create_campaign(1, "t", ["ALL"], HERO, 100, campaign_id="C1")
    camp.state = "paused"
    assert getattr(engine, record)("C1") == {"error": "campaign_not_active", "state": "paused"}
    assert (camp.impressions, camp.clicks, camp.spent_bdt) == (0, 0, 0.0)


def test_impression_charges_cpm_share(engine: AdDeliveryEngine) -> None:
    engine.create_campaign(1, "t", ["ALL"], HERO, 100, cpm_rate_bdt=50, campaign_id="C1")
    res = engine.record_impression("C1")
    assert res == {
        "status": "recorded",
        "campaign_id": "C1",
        "impressions": 1,
        "spent_bdt": 0.05,
        "remaining_budget": 99.95,
        "state": "active",
    }


def test_impressions_exhaust_the_budget(engine: AdDeliveryEngine) -> None:
    engine.create_campaign(1, "t", ["ALL"], HERO, 0.1, cpm_rate_bdt=50, campaign_id="C1")
    assert engine.record_impression("C1")["state"] == "active"  # 0.05 spent
    last = engine.record_impression("C1")  # 0.10 spent == budget
    assert (last["state"], last["remaining_budget"]) == ("exhausted", 0.0)
    assert engine.record_impression("C1") == {"error": "campaign_not_active", "state": "exhausted"}
    assert engine.serve_ads(HERO) == []


def test_click_charges_cpc_and_reports_ctr(engine: AdDeliveryEngine) -> None:
    engine.create_campaign(1, "t", ["ALL"], HERO, 100, cpc_rate_bdt=4.5, campaign_id="C1")
    for _ in range(4):
        engine.record_impression("C1")
    res = engine.record_click("C1")
    assert res == {
        "status": "recorded",
        "campaign_id": "C1",
        "clicks": 1,
        "ctr": 25.0,
        "spent_bdt": 4.7,  # 4 x 0.05 impressions + 4.50 click
        "remaining_budget": 95.3,
        "state": "active",
    }


def test_click_exhausts_the_budget(engine: AdDeliveryEngine) -> None:
    engine.create_campaign(1, "t", ["ALL"], HERO, 10, cpc_rate_bdt=10, campaign_id="C1")
    res = engine.record_click("C1")
    assert (res["state"], res["spent_bdt"], res["remaining_budget"]) == ("exhausted", 10.0, 0.0)
    assert engine.record_click("C1")["error"] == "campaign_not_active"


def test_regression_click_keeps_sub_paisa_impression_spend(engine: AdDeliveryEngine) -> None:
    """Regression: record_click rounded the running spend to 2 dp, silently
    dropping (or inventing) the 4-dp impression charges accrued before it."""
    engine.create_campaign(
        1, "t", ["ALL"], HERO, 100, cpc_rate_bdt=5, cpm_rate_bdt=12.3, campaign_id="C1"
    )
    assert engine.record_impression("C1")["spent_bdt"] == 0.0123
    assert engine.record_click("C1")["spent_bdt"] == 5.0123  # was 5.01
    assert engine.record_impression("C1")["spent_bdt"] == 5.0246
    assert engine.get_analytics("C1")["spent_bdt"] == 5.0246


def test_conversion_is_attributed_even_after_budget_exhaustion(engine: AdDeliveryEngine) -> None:
    camp = engine.create_campaign(1, "t", ["ALL"], HERO, 5, cpc_rate_bdt=5, campaign_id="C1")
    engine.record_click("C1")
    assert camp.state == "exhausted"
    assert engine.record_conversion("C1") == {
        "status": "recorded",
        "campaign_id": "C1",
        "conversions": 1,
    }
    assert engine.record_conversion("C1")["conversions"] == 2


def test_analytics_reports_full_performance(engine: AdDeliveryEngine) -> None:
    engine.create_campaign(9, "Boost", ["ALL"], SEARCH, 50, campaign_id="C1")
    for _ in range(10):
        engine.record_impression("C1")
    engine.record_click("C1")
    engine.record_conversion("C1")

    assert engine.get_analytics("C1") == {
        "campaign_id": "C1",
        "seller_id": 9,
        "title": "Boost",
        "placement": SEARCH,
        "budget_bdt": 50.0,
        "spent_bdt": 5.5,
        "remaining_budget": 44.5,
        "impressions": 10,
        "clicks": 1,
        "ctr": 10.0,
        "conversions": 1,
        "state": "active",
    }
