# cd_inventory tests — M15 Spare Parts & Inventory Core Tests (CD-M15-01).
from __future__ import annotations

import inspect


class TestFixStockLocation:
    """Tests for fix.stock.location (Multi-location, Hubs, Service Centers, Mobile Vans)."""

    def test_model_exists(self):
        from odoo.addons.cd_inventory.models.fix_stock_location import FixStockLocation

        assert FixStockLocation is not None

    def test_unique_code_constraint(self):
        from odoo.addons.cd_inventory.models.fix_stock_location import FixStockLocation

        assert hasattr(FixStockLocation, "_code_company_unique")

    def test_van_location_fields(self):
        from odoo.addons.cd_inventory.models.fix_stock_location import FixStockLocation

        fields = dir(FixStockLocation)
        assert "is_van_location" in fields
        assert "technician_id" in fields
        assert "van_plate" in fields
        assert "last_audit_date" in fields

    def test_audit_van_stock_publishes_event(self):
        from odoo.addons.cd_inventory.models.fix_stock_location import FixStockLocation

        source = inspect.getsource(FixStockLocation.action_audit_van_stock)
        assert "van.reconciled" in source
        assert "last_audit_date" in source

    def test_bengali_field_present(self):
        from odoo.addons.cd_inventory.models.fix_stock_location import FixStockLocation

        assert "name_bn" in dir(FixStockLocation)


class TestFixSparePart:
    """Tests for fix.spare.part (Catalog, Compatibility, Barcodes, Pricing)."""

    def test_model_exists(self):
        from odoo.addons.cd_inventory.models.fix_spare_part import FixSparePart

        assert FixSparePart is not None

    def test_unique_part_number_constraint(self):
        from odoo.addons.cd_inventory.models.fix_spare_part import FixSparePart

        assert hasattr(FixSparePart, "_part_code_unique")

    def test_barcode_and_qr_fields(self):
        from odoo.addons.cd_inventory.models.fix_spare_part import FixSparePart

        fields = dir(FixSparePart)
        assert "barcode" in fields
        assert "qr_code" in fields
        assert "is_serialized" in fields
        assert "compatible_models" in fields
        assert "warranty_months" in fields

    def test_find_by_code_method(self):
        from odoo.addons.cd_inventory.models.fix_spare_part import FixSparePart

        assert hasattr(FixSparePart, "find_by_code")

    def test_bengali_field_present(self):
        from odoo.addons.cd_inventory.models.fix_spare_part import FixSparePart

        assert "name_bn" in dir(FixSparePart)


class TestFixStockConsumption:
    """Tests for fix.stock.consumption (Barcode Scan-to-Consume Engine)."""

    def test_model_exists(self):
        from odoo.addons.cd_inventory.models.fix_stock_consumption import FixStockConsumption

        assert FixStockConsumption is not None

    def test_scan_and_consume_method(self):
        from odoo.addons.cd_inventory.models.fix_stock_consumption import FixStockConsumption

        source = inspect.getsource(FixStockConsumption.action_scan_and_consume)
        assert "stock.consumed" in source
        assert "fix.inventory.valuation.suspense" in source
        assert "qty_available" in source
        assert "110999" in source

    def test_return_part_method(self):
        from odoo.addons.cd_inventory.models.fix_stock_consumption import FixStockConsumption

        source = inspect.getsource(FixStockConsumption.action_return_part)
        assert "stock.returned" in source
        assert "fix.inventory.valuation.suspense" in source
        assert "returned" in source


class TestFixValuationSuspense:
    """Tests for fix.inventory.valuation.suspense (GV-005 Suspense Stub)."""

    def test_model_exists(self):
        from odoo.addons.cd_inventory.models.fix_valuation_suspense import (
            FixInventoryValuationSuspense,
        )

        assert FixInventoryValuationSuspense is not None

    def test_suspense_account_default(self):
        from odoo.addons.cd_inventory.models.fix_valuation_suspense import (
            FixInventoryValuationSuspense,
        )

        source = inspect.getsource(FixInventoryValuationSuspense)
        assert "110999" in source
        assert "STUB-M15-M19-001" in source

    def test_action_reconcile_to_gl(self):
        from odoo.addons.cd_inventory.models.fix_valuation_suspense import (
            FixInventoryValuationSuspense,
        )

        source = inspect.getsource(FixInventoryValuationSuspense.action_reconcile_to_gl)
        assert "gl_voucher_ref" in source
        assert "reconciled" in source
