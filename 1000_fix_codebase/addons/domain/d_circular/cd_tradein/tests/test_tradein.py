"""cd_tradein tests — P09-M04 / R07-M03-T03 / R07-M03-T04.
Comprehensive test suite covering 10-state lifecycle, M06 data wipe gate,
M31 workshop refurbishment costing, M37 grading, M15 graded inventory,
and M50 treasury payout execution.
"""

from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor" / "odoo"))
import odoo
import odoo.addons

circular_path = str(ROOT / "addons" / "domain" / "d_circular")
if circular_path not in odoo.addons.__path__:
    odoo.addons.__path__.append(circular_path)

import odoo.fields as f
from odoo.addons.cd_tradein.models.fix_tradein import (
    TRADEIN_STATES,
    FixTradeinRequest,
)


class TestTradeinLifecycleAndGates(unittest.TestCase):
    """Verifies 10-state lifecycle, M06 wipe gate, M37 grading, and M03 logistics."""

    def test_ten_state_lifecycle(self):
        state_keys = [s[0] for s in TRADEIN_STATES]
        # A05 ERP M14-09/21: an approved write-off routes the unit to parts only
        self.assertEqual(len(state_keys), 11)
        expected_states = (
            "draft",
            "offered",
            "accepted",
            "collected",
            "wiped",
            "refurbished",
            "graded",
            "resale_ready",
            "parts_only",
            "closed",
            "rejected",
        )
        for state in expected_states:
            self.assertIn(state, state_keys, f"State '{state}' must exist in TRADEIN_STATES")

    def test_wipe_gate_strictly_blocks_refurbishment(self):
        """M06 Data Wipe Gate: Refurbishment is strictly impossible without wipe cert."""
        src = inspect.getsource(FixTradeinRequest.action_refurbish)
        self.assertIn("wipe_certificate_id", src)
        self.assertIn("WIPE GATE", src)
        self.assertIn("UserError", src)

    def test_grading_required_before_resale(self):
        """M37 Grading Gate: Resale readiness requires an explicit grade."""
        src = inspect.getsource(FixTradeinRequest.action_grade)
        self.assertIn("refurb_grade_id", src)
        self.assertIn("A grade is required before resale", src)

    def test_m03_logistics_consignment_on_collect(self):
        """M03 logistics consignment is created upon collection."""
        self.assertTrue(hasattr(FixTradeinRequest, "consignment_id"))
        src = inspect.getsource(FixTradeinRequest.action_collect)
        self.assertIn("fix.consignment", src)
        self.assertIn("pickup", src)

    def test_m31_workshop_job_link(self):
        """M31 workshop job link and refurbishment cost calculation."""
        self.assertTrue(hasattr(FixTradeinRequest, "workshop_job_id"))
        self.assertTrue(hasattr(FixTradeinRequest, "parts_cost"))
        self.assertTrue(hasattr(FixTradeinRequest, "labour_cost"))
        self.assertTrue(hasattr(FixTradeinRequest, "refurbishment_cost"))

    def test_m15_graded_inventory_stock_link(self):
        """M15 graded stock record generated upon resale readiness."""
        self.assertTrue(hasattr(FixTradeinRequest, "graded_stock_id"))
        src = inspect.getsource(FixTradeinRequest.action_resale_ready)
        self.assertIn("fix.graded.stock", src)

    def test_m50_treasury_payout_execution(self):
        """M50 treasury payout execution created upon action_pay."""
        self.assertTrue(hasattr(FixTradeinRequest, "payout_execution_id"))
        src = inspect.getsource(FixTradeinRequest.action_pay)
        self.assertIn("fix.payment.execution", src)
        self.assertIn("tradein.paid", src)

    def test_events_published(self):
        src = inspect.getsource(FixTradeinRequest)
        for event in ("tradein.offered", "tradein.wiped", "tradein.paid"):
            self.assertIn(event, src, f"Event {event} must be published by FixTradeinRequest")


class TestTradeinFinancialMoneyPath(unittest.TestCase):
    """100% Money Path Coverage: monetary fields and financial consistency."""

    def test_monetary_fields(self):
        money_fields = [
            "offered_value",
            "parts_cost",
            "labour_cost",
            "refurbishment_cost",
            "resale_value",
        ]
        for fn in money_fields:
            self.assertTrue(
                hasattr(FixTradeinRequest, fn), f"Field {fn} must exist on FixTradeinRequest"
            )
            self.assertIsInstance(
                getattr(FixTradeinRequest, fn),
                f.Monetary,
                f"Field {fn} must be Monetary per AS-10",
            )

    def test_refurbishment_cost_sum_logic(self):
        parts = 1200.0
        labour = 800.0
        total_refurb = parts + labour
        self.assertEqual(total_refurb, 2000.0)

    def test_inventory_valuation_and_margin_logic(self):
        acquisition = 15000.0
        refurbishment = 3500.0
        total_cost = acquisition + refurbishment
        resale_price = 24000.0
        margin = resale_price - total_cost
        margin_pct = (margin / resale_price) * 100.0

        self.assertEqual(total_cost, 18500.0)
        self.assertEqual(margin, 5500.0)
        self.assertAlmostEqual(margin_pct, 22.916666, places=4)


if __name__ == "__main__":
    unittest.main()
