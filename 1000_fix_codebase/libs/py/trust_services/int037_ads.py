"""INT-037 — Ad Delivery & Marketplace Boost Engine.

Provides ad serving, targeted product boost, impression tracking, and click
attribution for the 1000FiX marketplace and storefront ecosystem.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

AdPlacement = (
    str  # "home_hero_banner", "search_sponsored", "category_banner", "product_detail_boost"
)


@dataclass
class AdCampaign:
    campaign_id: str
    seller_id: int
    title: str
    target_categories: list[str]
    placement: AdPlacement
    budget_bdt: float
    cpc_rate_bdt: float
    cpm_rate_bdt: float
    spent_bdt: float = 0.0
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    state: str = "active"  # active, paused, exhausted, completed
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def remaining_budget(self) -> float:
        return max(0.0, round(self.budget_bdt - self.spent_bdt, 2))

    @property
    def ctr(self) -> float:
        if self.impressions == 0:
            return 0.0
        return round((self.clicks / self.impressions) * 100.0, 2)


class AdDeliveryEngine:
    """Manages marketplace ad campaigns, serving, and attribution."""

    def __init__(self):
        self._campaigns: dict[str, AdCampaign] = {}

    def create_campaign(
        self,
        seller_id: int,
        title: str,
        target_categories: list[str],
        placement: AdPlacement,
        budget_bdt: float,
        cpc_rate_bdt: float = 5.0,
        cpm_rate_bdt: float = 50.0,
        campaign_id: str | None = None,
    ) -> AdCampaign:
        """Create and activate a new ad campaign."""
        if budget_bdt <= 0:
            raise ValueError("Campaign budget must be positive")
        if cpc_rate_bdt <= 0 or cpm_rate_bdt <= 0:
            raise ValueError("CPC and CPM rates must be positive")

        cid = campaign_id or f"CMP-{uuid.uuid4().hex[:10].upper()}"
        camp = AdCampaign(
            campaign_id=cid,
            seller_id=seller_id,
            title=title,
            target_categories=[c.upper() for c in target_categories],
            placement=placement,
            budget_bdt=float(budget_bdt),
            cpc_rate_bdt=float(cpc_rate_bdt),
            cpm_rate_bdt=float(cpm_rate_bdt),
        )
        self._campaigns[cid] = camp
        return camp

    def get_campaign(self, campaign_id: str) -> AdCampaign | None:
        return self._campaigns.get(campaign_id)

    def serve_ads(
        self,
        placement: AdPlacement,
        category: str | None = None,
        limit: int = 3,
    ) -> list[dict]:
        """Serve active ads matching placement and optional category."""
        results = []
        cat_upper = category.upper() if category else None
        for camp in self._campaigns.values():
            if camp.state != "active":
                continue
            if camp.placement != placement:
                continue
            if (
                cat_upper
                and cat_upper not in camp.target_categories
                and "ALL" not in camp.target_categories
            ):
                continue

            results.append(
                {
                    "campaign_id": camp.campaign_id,
                    "seller_id": camp.seller_id,
                    "title": camp.title,
                    "placement": camp.placement,
                    "target_categories": camp.target_categories,
                }
            )
            if len(results) >= limit:
                break
        return results

    def record_impression(self, campaign_id: str) -> dict:
        """Record an impression and deduct CPM share (cpm / 1000)."""
        camp = self._campaigns.get(campaign_id)
        if not camp:
            return {"error": "campaign_not_found"}
        if camp.state != "active":
            return {"error": "campaign_not_active", "state": camp.state}

        cost = round(camp.cpm_rate_bdt / 1000.0, 4)
        camp.impressions += 1
        camp.spent_bdt = round(camp.spent_bdt + cost, 4)

        if camp.spent_bdt >= camp.budget_bdt:
            camp.state = "exhausted"

        return {
            "status": "recorded",
            "campaign_id": camp.campaign_id,
            "impressions": camp.impressions,
            "spent_bdt": camp.spent_bdt,
            "remaining_budget": camp.remaining_budget,
            "state": camp.state,
        }

    def record_click(self, campaign_id: str) -> dict:
        """Record a click and deduct CPC rate."""
        camp = self._campaigns.get(campaign_id)
        if not camp:
            return {"error": "campaign_not_found"}
        if camp.state != "active":
            return {"error": "campaign_not_active", "state": camp.state}

        cost = round(camp.cpc_rate_bdt, 2)
        camp.clicks += 1
        # Same 4-dp precision as record_impression: rounding the running total
        # to 2 dp here silently dropped/added sub-paisa impression spend.
        camp.spent_bdt = round(camp.spent_bdt + cost, 4)

        if camp.spent_bdt >= camp.budget_bdt:
            camp.state = "exhausted"

        return {
            "status": "recorded",
            "campaign_id": camp.campaign_id,
            "clicks": camp.clicks,
            "ctr": camp.ctr,
            "spent_bdt": camp.spent_bdt,
            "remaining_budget": camp.remaining_budget,
            "state": camp.state,
        }

    def record_conversion(self, campaign_id: str) -> dict:
        """Record a confirmed marketplace or storefront sale attributed to ad."""
        camp = self._campaigns.get(campaign_id)
        if not camp:
            return {"error": "campaign_not_found"}
        camp.conversions += 1
        return {
            "status": "recorded",
            "campaign_id": camp.campaign_id,
            "conversions": camp.conversions,
        }

    def get_analytics(self, campaign_id: str) -> dict:
        """Retrieve full performance analytics for a campaign."""
        camp = self._campaigns.get(campaign_id)
        if not camp:
            return {"error": "campaign_not_found"}
        return {
            "campaign_id": camp.campaign_id,
            "seller_id": camp.seller_id,
            "title": camp.title,
            "placement": camp.placement,
            "budget_bdt": camp.budget_bdt,
            "spent_bdt": camp.spent_bdt,
            "remaining_budget": camp.remaining_budget,
            "impressions": camp.impressions,
            "clicks": camp.clicks,
            "ctr": camp.ctr,
            "conversions": camp.conversions,
            "state": camp.state,
        }
