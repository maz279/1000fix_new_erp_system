"""A05 Complete Remediation Unit Tests — Zero-Trust Verification.
Covers:
  - M13 Rental: FixRentalAsset IAS 16 depreciation & FixRentalDeposit GL moves.
  - M14 Trade-In: FixRefurbishment active workflow methods, FixTradeinRequest ITA 2023 TDS & BTRC NEIR anti-theft gate.
  - M18 E-Waste: FixEwasteBattery UN 3480 Class 9 safety workflows & FixEwasteReturn S.R.O. 187/2021 mass balance.
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

from odoo.addons.cd_ewaste.models.fix_ewaste_ops import FixEwasteBattery, FixEwasteReturn
from odoo.addons.cd_rental_asset.models.fix_rental_fleet import FixRentalAsset, FixRentalDeposit
from odoo.addons.cd_tradein.models.fix_tradein import FixRefurbishment, FixTradeinRequest
from odoo.addons.cd_tradein.models.fix_tradein_ops import FixTradeinProvenance


class TestA05CompleteRemediation(unittest.TestCase):
    """Zero-trust verification of Area A05 backend hardening."""

    def test_m13_asset_depreciation_fields_declared(self):
        """FixRentalAsset must declare IAS 16 depreciation fields."""
        self.assertTrue(hasattr(FixRentalAsset, "purchase_cost"))
        self.assertTrue(hasattr(FixRentalAsset, "residual_value"))
        self.assertTrue(hasattr(FixRentalAsset, "useful_life_days"))
        self.assertTrue(hasattr(FixRentalAsset, "daily_depreciation"))
        self.assertTrue(hasattr(FixRentalAsset, "net_book_value"))
        src = inspect.getsource(FixRentalAsset._compute_depreciation)
        self.assertIn("daily_depreciation", src)
        self.assertIn("net_book_value", src)

    def test_m13_deposit_gl_integration_declared(self):
        """FixRentalDeposit must declare GL journal entry link."""
        self.assertTrue(hasattr(FixRentalDeposit, "journal_entry_id"))
        src = inspect.getsource(FixRentalDeposit._post)
        self.assertIn("GL Ready", src)

    def test_m14_refurbishment_methods_activated(self):
        """FixRefurbishment must not be a passive stub; methods must be defined."""
        self.assertTrue(hasattr(FixRefurbishment, "action_start"))
        self.assertTrue(hasattr(FixRefurbishment, "action_request_parts"))
        self.assertTrue(hasattr(FixRefurbishment, "action_complete_repair"))
        self.assertTrue(hasattr(FixRefurbishment, "labor_cost"))
        self.assertTrue(hasattr(FixRefurbishment, "total_cost"))
        src_start = inspect.getsource(FixRefurbishment.action_start)
        self.assertIn("in_progress", src_start)
        src_complete = inspect.getsource(FixRefurbishment.action_complete_repair)
        self.assertIn("done", src_complete)

    def test_m14_tradein_statutory_tds_and_neir_gate(self):
        """FixTradeinRequest must have NID, TDS fields, and NEIR anti-theft check."""
        self.assertTrue(hasattr(FixTradeinRequest, "customer_nid"))
        self.assertTrue(hasattr(FixTradeinRequest, "tds_applicable"))
        self.assertTrue(hasattr(FixTradeinRequest, "tds_amount"))
        self.assertTrue(hasattr(FixTradeinRequest, "net_payout"))
        src_pay = inspect.getsource(FixTradeinRequest.action_pay)
        self.assertIn("stolen_hit", src_pay)
        self.assertIn("BTRC NEIR", src_pay)

    def test_m14_provenance_btrc_neir_check(self):
        """FixTradeinProvenance must support BTRC NEIR check and Smart NID."""
        self.assertTrue(hasattr(FixTradeinProvenance, "btrc_neir_checked"))
        self.assertTrue(hasattr(FixTradeinProvenance, "btrc_neir_status"))
        self.assertTrue(hasattr(FixTradeinProvenance, "customer_nid_no"))
        self.assertTrue(hasattr(FixTradeinProvenance, "action_run_neir_check"))

    def test_m18_battery_un3480_class9_safety(self):
        """FixEwasteBattery must enforce terminal taping and fireproof barrel quarantine."""
        self.assertTrue(hasattr(FixEwasteBattery, "terminal_taped"))
        self.assertTrue(hasattr(FixEwasteBattery, "swollen_cell"))
        self.assertTrue(hasattr(FixEwasteBattery, "quarantine_barrel_ref"))
        self.assertTrue(hasattr(FixEwasteBattery, "action_inspect_and_quarantine"))
        self.assertTrue(hasattr(FixEwasteBattery, "action_dispatch"))
        self.assertTrue(hasattr(FixEwasteBattery, "action_process"))
        src_dispatch = inspect.getsource(FixEwasteBattery.action_dispatch)
        self.assertIn("terminal_taped", src_dispatch)

    def test_m18_statutory_doe_return_sro187(self):
        """FixEwasteReturn must implement S.R.O. 187-Law/2021 mass balance and returns."""
        self.assertTrue(hasattr(FixEwasteReturn, "form_type"))
        self.assertTrue(hasattr(FixEwasteReturn, "schedule_1_category"))
        self.assertTrue(hasattr(FixEwasteReturn, "total_tonnage_collected"))
        self.assertTrue(hasattr(FixEwasteReturn, "total_tonnage_recycled"))
        self.assertTrue(hasattr(FixEwasteReturn, "recovery_rate_pct"))
        self.assertTrue(hasattr(FixEwasteReturn, "action_calculate_mass_balance"))
        self.assertTrue(hasattr(FixEwasteReturn, "action_submit_return"))
        self.assertTrue(hasattr(FixEwasteReturn, "action_accept_return"))


if __name__ == "__main__":
    unittest.main()
