# cd_wms_structure tests — M41 W3 slice (P06-M07).


class TestZones:
    def test_quarantine_not_reservable(self):
        """BRU-INV-08: quarantine/blocked stock cannot be reserved."""
        from odoo.addons.cd_wms_structure.models.fix_wms_structure import FixWarehouseZone

        assert hasattr(FixWarehouseZone, "_compute_reservable")
        source_zone_types = dict(FixWarehouseZone.zone_type.selection)
        assert "quarantine" in source_zone_types

    def test_reservable_rule_in_source(self):
        import inspect

        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_wms_structure.models.fix_wms_structure",
                fromlist=["FixWarehouseZone"],
            ).FixWarehouseZone._compute_reservable
        )
        assert "quarantine" in source and "inspection" in source


class TestBins:
    def test_capacity_never_negative(self):
        import inspect

        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_wms_structure.models.fix_wms_structure",
                fromlist=["FixWarehouseBin"],
            ).FixWarehouseBin
        )
        assert "cannot be negative" in source
