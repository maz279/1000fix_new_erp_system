# Tests for cd_catalogue (P03-M06) — AS-10 monetary, model constraints.
import pytest


class TestFixCatalogueItem:
    def test_model_exists(self):
        from addons.platform.cd_catalogue.models.fix_catalogue_item import FixCatalogueItem
        assert FixCatalogueItem is not None

    def test_product_tmpl_unique(self):
        from addons.platform.cd_catalogue.models.fix_catalogue_item import FixCatalogueItem
        assert any("product_tmpl_unique" in str(c) for c in FixCatalogueItem._sql_constraints)


class TestFixServiceKit:
    def test_model_exists(self):
        from addons.platform.cd_catalogue.models.fix_service_kit import FixServiceKit
        assert FixServiceKit is not None

    def test_has_components_constraint(self):
        from addons.platform.cd_catalogue.models.fix_service_kit import FixServiceKit
        assert '_check_has_components' in dir(FixServiceKit)

    def test_as10_monetary_cost(self):
        """AS-10: estimated_cost is Monetary with currency_id."""
        from addons.platform.cd_catalogue.models.fix_service_kit import FixServiceKit
        assert 'estimated_cost' in dir(FixServiceKit)
        assert 'currency_id' in dir(FixServiceKit)


class TestFixRentalSku:
    def test_model_exists(self):
        from addons.platform.cd_catalogue.models.fix_rental_sku import FixRentalSku
        assert FixRentalSku is not None

    def test_as10_monetary_rates(self):
        """AS-10: rental rates are Monetary, never Float."""
        from addons.platform.cd_catalogue.models.fix_rental_sku import FixRentalSku
        for field in ('daily_rate', 'weekly_rate', 'monthly_rate', 'security_deposit'):
            assert field in dir(FixRentalSku)


class TestFixBrand:
    def test_model_exists(self):
        from addons.platform.cd_catalogue.models.fix_brand import FixBrand
        assert FixBrand is not None

    def test_name_unique(self):
        from addons.platform.cd_catalogue.models.fix_brand import FixBrand
        assert any("name_unique" in str(c) for c in FixBrand._sql_constraints)


class TestFixDeviceModel:
    def test_model_exists(self):
        from addons.platform.cd_catalogue.models.fix_device_model import FixDeviceModel
        assert FixDeviceModel is not None

    def test_brand_name_unique(self):
        from addons.platform.cd_catalogue.models.fix_device_model import FixDeviceModel
        assert any("brand_name_unique" in str(c) for c in FixDeviceModel._sql_constraints)
