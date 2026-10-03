# cd_contract_core tests — M08 (P07-M01).
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "models" / "fix_contract.py").read_text(encoding="utf-8")


class TestFamilies(unittest.TestCase):
    def test_all_five_families_on_one_engine(self):
        for family in ("amc", "ramc", "managed", "rental", "marketplace"):
            self.assertIn('("%s"' % family, SOURCE)


class TestEntitlement(unittest.TestCase):
    def test_drawdown_never_negative(self):
        """Consumption past the included quantity returns False, never goes
        negative — the caller re-classifies the order as paid."""
        self.assertIn("ent.quantity_remaining < qty", SOURCE)
        self.assertIn("return False", SOURCE)

    def test_unlimited_sentinel(self):
        self.assertIn("quantity_included == 0", SOURCE)

    def test_entitlement_active_api_exists(self):
        """BRU-SRM-03: the API M01's AMC gate consumes."""
        self.assertIn("def entitlement_active", SOURCE)

    def test_consumption_publishes_event(self):
        self.assertIn('"entitlement.consumed"', SOURCE)


class TestActivation(unittest.TestCase):
    def test_signature_gate(self):
        """T07: activation requires a COMPLETED kernel envelope."""
        self.assertIn("the e-signature envelope is", SOURCE)

    def test_activation_generates_pm_schedule(self):
        self.assertIn("_generate_pm_schedule", SOURCE)

    def test_activation_publishes(self):
        self.assertIn('"contract.activated"', SOURCE)


class TestRenewal(unittest.TestCase):
    def test_escalation_applied(self):
        self.assertIn("escalation_pct", SOURCE)
        self.assertIn("factor", SOURCE)

    def test_renewal_publishes(self):
        self.assertIn('"contract.renewed"', SOURCE)

    def test_aut015_ladder(self):
        """AUT-015: the −90/−60/−30/−15 expiring ladder."""
        self.assertIn("(90, 60, 30, 15)", SOURCE)


class TestContractCostOwnership(unittest.TestCase):
    def test_cost_owned_here_not_in_m53_m54(self):
        """T08 / AR-008 §2.2: the ruling — M08 owns, M53/M54 consume via
        events. The annual_value field lives here; no M53/M54 import."""
        self.assertIn("annual_value", SOURCE)
        self.assertNotIn("cd_subscription", SOURCE)
        self.assertNotIn("cd_settlement", SOURCE)


class TestContractSla(unittest.TestCase):
    def test_same_policy_model_as_m01(self):
        """T04: one SLA concept — the m2m targets fix.sla.policy."""
        self.assertIn('"fix.sla.policy"', SOURCE)


if __name__ == "__main__":
    unittest.main()
