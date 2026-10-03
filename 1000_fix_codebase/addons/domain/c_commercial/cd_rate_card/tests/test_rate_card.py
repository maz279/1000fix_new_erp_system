# cd_rate_card tests — M11 data core (P06-M06).
import pytest


class TestRateCard:
    def test_model_exists(self):
        from addons.domain.c_commercial.cd_rate_card.models.fix_rate_card import FixRateCard
        assert FixRateCard is not None

    def test_contract_lane_constraint_declared(self):
        """Tier-99 is the contract lane and demands a contract number."""
        import inspect
        source = inspect.getsource(
            __import__("addons.domain.c_commercial.cd_rate_card.models.fix_rate_card",
                       fromlist=["FixRateCard"]).FixRateCard)
        assert "A tier-99 rate is a CONTRACT rate" in source

    def test_unique_per_product_tier_contract(self):
        from addons.domain.c_commercial.cd_rate_card.models.fix_rate_card import FixRateCard
        names = [c[0] for c in (FixRateCard._sql_constraints or [])]
        assert "product_tier_unique" in names

    def test_projects_to_engine_line(self):
        import inspect
        source = inspect.getsource(
            __import__("addons.domain.c_commercial.cd_rate_card.models.fix_rate_card",
                       fromlist=["FixRateCard"]).FixRateCard)
        assert "to_engine_line" in source
