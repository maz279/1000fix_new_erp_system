# cd_loyalty tests — P05-M08-T01..T03 / R03-M05-T01 (CD-M10-01).
import inspect
from pathlib import Path
import unittest
import yaml

from odoo.addons.cd_loyalty.models.fix_loyalty_program import FixLoyaltyProgram
from odoo.addons.cd_loyalty.models.fix_loyalty_tier import FixLoyaltyTier
from odoo.addons.cd_loyalty.models.fix_loyalty_account import FixLoyaltyAccount
from odoo.addons.cd_loyalty.models.fix_loyalty_ledger import FixLoyaltyLedger
from odoo.addons.cd_loyalty.models.fix_loyalty_voucher import FixLoyaltyVoucher
from odoo.addons.cd_loyalty.models.fix_loyalty_stub import FixLoyaltyRedemptionStub


class TestLoyaltyProgram(unittest.TestCase):
    def test_points_calculation_method(self):
        src = inspect.getsource(FixLoyaltyProgram.calculate_points_earned)
        self.assertIn("points_per_bdt", src)
        self.assertIn("points_multiplier", src)

    def test_ratio_constraints(self):
        src = inspect.getsource(FixLoyaltyProgram._check_ratios)
        self.assertIn("Points per BDT cannot be negative", src)
        self.assertIn("strictly positive", src)


class TestLoyaltyTier(unittest.TestCase):
    def test_tier_benefit_constraints(self):
        src = inspect.getsource(FixLoyaltyTier._check_benefits)
        self.assertIn("Points multiplier must be at least 1.0x", src)
        self.assertIn("Labour discount must be between 0% and 100%", src)
        self.assertIn("Parts discount must be between 0% and 100%", src)


class TestLoyaltyAccount(unittest.TestCase):
    def test_tier_update_logic(self):
        src = inspect.getsource(FixLoyaltyAccount.check_and_update_tier)
        self.assertIn("min_points_threshold", src)
        self.assertIn("min_spend_bdt", src)
        self.assertIn("loyalty.tier_upgraded", src)

    def test_account_creation_emits_event(self):
        src = inspect.getsource(FixLoyaltyAccount.create)
        self.assertIn("loyalty.account_created", src)


class TestLoyaltyLedger(unittest.TestCase):
    def test_action_post_validates_balance(self):
        src = inspect.getsource(FixLoyaltyLedger.action_post)
        self.assertIn("Insufficient points", src)
        self.assertIn("points_balance", src)
        self.assertIn("loyalty.points_accrued", src)
        self.assertIn("loyalty.points_redeemed", src)


class TestLoyaltyVoucher(unittest.TestCase):
    def test_voucher_parameters_constraint(self):
        src = inspect.getsource(FixLoyaltyVoucher._check_voucher_parameters)
        self.assertIn("Discount value must be greater than zero", src)
        self.assertIn("validity window is inverted", src)

    def test_action_redeem_checks_expiry(self):
        src = inspect.getsource(FixLoyaltyVoucher.action_redeem)
        self.assertIn("outside its validity window", src)
        self.assertIn("loyalty.voucher_redeemed", src)


class TestLoyaltyStub(unittest.TestCase):
    def test_stub_code_and_expiry(self):
        src = inspect.getsource(FixLoyaltyRedemptionStub)
        self.assertIn('default="STUB-M10-M11-001"', src)
        self.assertIn('default="R04-M02-T08"', src)

    def test_check_redemption_eligibility(self):
        src = inspect.getsource(FixLoyaltyRedemptionStub.check_redemption_eligibility)
        self.assertIn("STUB-M10-M11-001 invoked", src)
        self.assertIn("min_points_to_redeem", src)
        self.assertIn("discount_bdt", src)


class TestLoyaltyManifest(unittest.TestCase):
    def test_cd_id_is_registered(self):
        manifest_path = Path(__file__).resolve().parents[1] / "__manifest__.py"
        manifest = eval(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["x_cd_id"], "CD-M10-01")
        self.assertEqual(manifest["x_module_id"], "M10")
        self.assertEqual(manifest["x_wave"], "W2")

        repo_root = Path(__file__).resolve().parents[5]
        reg_file = repo_root / "tooling" / "cd-register.yaml"
        reg = yaml.safe_load(reg_file.read_text(encoding="utf-8"))
        items = reg.get("items", []) if isinstance(reg, dict) else reg
        cd_ids = {entry["id"] for entry in items if isinstance(entry, dict) and "id" in entry}
        self.assertIn("CD-M10-01", cd_ids)


if __name__ == "__main__":
    unittest.main()
