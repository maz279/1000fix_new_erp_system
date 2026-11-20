"""cd_demand_plan — planning engine unit tests (CD-M43-01, T-04).

The engine is pure Python; these tests pin its maths to known values so the
deterministic local method stays deterministic."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))
import planning_engine as E  # noqa: E402


class TestClassification(unittest.TestCase):
    def test_syntetos_boylan_quadrants(self):
        self.assertEqual(E.classify_intermittency(1.0, 0.2), "smooth")
        self.assertEqual(E.classify_intermittency(1.0, 0.8), "erratic")
        self.assertEqual(E.classify_intermittency(2.0, 0.2), "intermittent")
        self.assertEqual(E.classify_intermittency(2.0, 0.8), "lumpy")

    def test_cutoffs_are_exclusive_lower_bounds(self):
        self.assertEqual(E.classify_intermittency(1.32, 0.49), "lumpy")

    def test_bad_inputs_raise(self):
        with self.assertRaises(E.PlanningError):
            E.classify_intermittency(0, 0.1)

    def test_no_ses_for_intermittent_bru_dpl_04(self):
        self.assertEqual(E.method_for("intermittent"), "croston_sba")
        self.assertEqual(E.method_for("lumpy"), "croston_sba")
        self.assertEqual(E.method_for("lumpy", critical=True), "bootstrap")
        self.assertEqual(E.method_for("smooth"), "ets")

    def test_nine_box(self):
        self.assertEqual(E.nine_box("a", "x"), "AX")
        with self.assertRaises(E.PlanningError):
            E.nine_box("d", "x")

    def test_cz_defaults_to_order_on_demand_bru_dpl_17(self):
        self.assertEqual(E.default_policy("c", "z", "deferrable"), "order_on_demand")
        self.assertEqual(E.default_policy("c", "z", "job_stopping"), "continuous_rop")
        self.assertEqual(E.default_policy("a", "z", "deferrable"), "continuous_rop")

    def test_readiness_gate_bru_dpl_01(self):
        self.assertEqual(E.readiness_verdict(24, 0.5, 0.95, False), "ready")
        self.assertEqual(E.readiness_verdict(6, 0.5, 0.95, False), "provisional")
        self.assertEqual(E.readiness_verdict(24, 0.5, 0.95, True), "provisional")
        self.assertEqual(E.readiness_verdict(24, 0.1, 0.95, False), "provisional")


class TestPolicyMaths(unittest.TestCase):
    def test_z_scores(self):
        self.assertAlmostEqual(E.z_for_service_level(95.0), 1.6449, places=3)
        self.assertAlmostEqual(E.z_for_service_level(98.0), 2.0537, places=3)
        with self.assertRaises(E.PlanningError):
            E.z_for_service_level(100.0)

    def test_safety_stock_uses_both_variabilities_bru_dpl_07(self):
        # z(95%)·sqrt(10·2² + 5²·3²) = 1.6449·sqrt(265)
        expected = round(E.z_for_service_level(95.0) * math.sqrt(10 * 4 + 25 * 9), 2)
        self.assertEqual(E.safety_stock(95.0, 5.0, 2.0, 10.0, 3.0), expected)
        # zero lead-time variability still leaves demand variability
        self.assertGreater(E.safety_stock(95.0, 5.0, 2.0, 10.0, 0.0), 0)

    def test_reorder_point(self):
        self.assertEqual(E.reorder_point(5.0, 10.0, 12.5), 62.5)

    def test_eoq(self):
        self.assertEqual(E.economic_order_quantity(1000, 50, 10), 100.0)
        self.assertEqual(E.economic_order_quantity(0, 50, 10), 0.0)

    def test_constraints_recorded_bru_dpl_10(self):
        qty, notes = E.apply_order_constraints(7, moq=10, pack_size=4)
        self.assertEqual(qty, 12)
        self.assertEqual(len(notes), 2)
        qty, notes = E.apply_order_constraints(12, moq=10, pack_size=4)
        self.assertEqual((qty, notes), (12, []))

    def test_guard_rails_bru_dpl_08(self):
        self.assertTrue(E.requires_planner_review("a", "deferrable", 10, 10))
        self.assertTrue(E.requires_planner_review("c", "job_stopping", 10, 10))
        self.assertFalse(E.requires_planner_review("b", "deferrable", 10, 12))
        self.assertTrue(E.requires_planner_review("b", "deferrable", 10, 20))
        self.assertFalse(E.requires_planner_review("c", "cosmetic", 0, 50))


class TestNetworkAndMeasurement(unittest.TestCase):
    def test_rebalance_net_benefit_bru_dpl_13(self):
        self.assertEqual(E.rebalance_net_benefit(5000, 1200), 3800)
        self.assertLessEqual(E.rebalance_net_benefit(500, 1200), 0)

    def test_lead_time_statistics_from_actuals(self):
        stats = E.lead_time_statistics([10, 12, 14, 30])
        self.assertEqual(stats["sample_count"], 4)
        self.assertEqual(stats["mean_days"], 16.5)
        self.assertEqual(stats["p95_days"], 30)
        self.assertEqual(E.lead_time_statistics([])["sample_count"], 0)

    def test_mape_and_bias(self):
        pairs = [(110, 100), (90, 100), (100, 0)]
        self.assertEqual(E.mape(pairs), 10.0)  # zero actual skipped
        self.assertEqual(E.bias([(120, 100), (100, 100)]), 10.0)

    def test_simulation_is_pure_and_monotone(self):
        base = E.simulate_tradeoff(95, 95, 1000, 4000)
        self.assertEqual(base["resulting_investment"], 5000)
        higher = E.simulate_tradeoff(95, 98, 1000, 4000)
        self.assertGreater(higher["resulting_investment"], base["resulting_investment"])
        self.assertEqual(higher["resulting_stockout_risk"], 2.0)


if __name__ == "__main__":
    unittest.main()
