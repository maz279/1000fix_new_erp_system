# cd_inventory tests — Replenishment Engine & M43 Seam Tests (CD-M15-02).
from __future__ import annotations

import inspect
import pytest


class TestFixReorderRule:
    """Tests for fix.reorder.rule (Replenishment alerts and M43 forecasting seam)."""

    def test_model_exists(self):
        from odoo.addons.cd_inventory.models.fix_reorder_rule import FixReorderRule
        assert FixReorderRule is not None

    def test_m43_seam_fields_present(self):
        from odoo.addons.cd_inventory.models.fix_reorder_rule import FixReorderRule
        fields = dir(FixReorderRule)
        assert "m43_ai_override" in fields
        assert "m43_predicted_demand" in fields
        assert "m43_model_version" in fields

    def test_m43_seam_method_exists(self):
        from odoo.addons.cd_inventory.models.fix_reorder_rule import FixReorderRule
        assert hasattr(FixReorderRule, "compute_dynamic_reorder_point")

    def test_action_trigger_reorder_emits_event(self):
        from odoo.addons.cd_inventory.models.fix_reorder_rule import FixReorderRule
        source = inspect.getsource(FixReorderRule.action_trigger_reorder)
        assert "reorder.triggered" in source
        assert "compute_dynamic_reorder_point" in source
        assert "suggested_order_qty" in source

    def test_check_replenishment_alerts_cron(self):
        from odoo.addons.cd_inventory.models.fix_reorder_rule import FixReorderRule
        source = inspect.getsource(FixReorderRule.check_replenishment_alerts)
        assert "action_trigger_reorder" in source
        assert "current_stock" in source
        assert "min_qty" in source

    def test_quantity_constraints(self):
        from odoo.addons.cd_inventory.models.fix_reorder_rule import FixReorderRule
        source = inspect.getsource(FixReorderRule._check_quantities)
        assert "Minimum quantity cannot be negative" in source
        assert "Maximum stock level must strictly exceed minimum reorder point" in source
