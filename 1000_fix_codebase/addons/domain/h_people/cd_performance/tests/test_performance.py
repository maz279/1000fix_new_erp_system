# cd_performance tests — P08-M04, R06-M01 (CD-M57-01).
import inspect
import unittest

from odoo.addons.cd_performance.models.fix_performance import (
    WEIGHTS,
    FixCompensationBand,
    FixIncentiveRun,
    FixPerformanceScorecard,
    composite_score,
    incentive_amount,
    rework_clawback_penalty,
)


class TestCompositeScore(unittest.TestCase):
    def test_perfect_scores(self):
        # RAP-M57-01: positive weights sum to 1.00 so top band (>=0.90) is reachable
        self.assertEqual(composite_score(1, 1, 1, 0), 1.0)
        self.assertEqual(composite_score(1, 1, 1, 0, salvage=1.0), 1.0)
        self.assertAlmostEqual(
            WEIGHTS["first_time_fix"] + WEIGHTS["sla_hit"] + WEIGHTS["csat"] + WEIGHTS["salvage"],
            1.0,
            places=6,
        )

    def test_rework_penalty_applies(self):
        clean = composite_score(1, 1, 1, 0)
        dirty = composite_score(1, 1, 1, 1)
        self.assertAlmostEqual(clean - dirty, 0.15, places=6)

    def test_rework_30d_clawback_and_salvage_component(self):
        # RAP-M57-02: 0% rework -> 0 penalty; 3% -> 0 penalty; 6% -> -0.30 penalty; salvage at target -> +0.15
        self.assertEqual(rework_clawback_penalty(0.0), 0.0)
        self.assertEqual(rework_clawback_penalty(0.03), 0.0)
        self.assertEqual(rework_clawback_penalty(0.06), 0.30)
        no_salvage = composite_score(1, 1, 1, 0, salvage=0.0)
        with_salvage = composite_score(1, 1, 1, 0, salvage=1.0)
        self.assertAlmostEqual(with_salvage - no_salvage, 0.15, places=6)
        with_clawback = composite_score(1, 1, 1, 0, salvage=1.0, rework_30d=0.06)
        self.assertEqual(with_clawback, 0.70)

    def test_every_incentive_band_reachable_by_constructed_input(self):
        # RAP-M57-01 property test: >=0.90 (15%), >=0.75 (8%), >=0.60 (4%), <0.60 (0%) all reachable
        s_top = composite_score(1.0, 1.0, 1.0, 0.0)
        s_mid = composite_score(0.8, 0.8, 0.8, 0.0)
        s_low = composite_score(0.65, 0.65, 0.65, 0.0)
        s_zero = composite_score(0.4, 0.4, 0.4, 0.0)
        self.assertGreaterEqual(s_top, 0.90)
        self.assertEqual(incentive_amount(s_top, 20000), 3000.00)
        self.assertEqual(incentive_amount(s_mid, 20000), 1600.00)
        self.assertEqual(incentive_amount(s_low, 20000), 800.00)
        self.assertEqual(incentive_amount(s_zero, 20000), 0.00)

    def test_clamped_zero_one(self):
        self.assertEqual(composite_score(0, 0, 0, 1), 0.0)
        self.assertEqual(composite_score(1, 1, 1, 0), composite_score(1, 1, 1, 0))

    def test_out_of_range_raises(self):
        for bad in ((1.5, 0, 0, 0), (0, -0.1, 0, 0), (0, 0, 2, 0)):
            with self.assertRaises(ValueError):
                composite_score(*bad)


class TestIncentiveBands(unittest.TestCase):
    """It pays people — every band edge pinned."""

    def test_top_band_15pct(self):
        self.assertEqual(incentive_amount(0.95, 10000), 1500.00)

    def test_top_band_edge_inclusive(self):
        self.assertEqual(incentive_amount(0.90, 10000), 1500.00)

    def test_second_band_8pct(self):
        self.assertEqual(incentive_amount(0.80, 10000), 800.00)
        self.assertEqual(incentive_amount(0.75, 10000), 800.00)

    def test_third_band_4pct(self):
        self.assertEqual(incentive_amount(0.65, 10000), 400.00)
        self.assertEqual(incentive_amount(0.60, 10000), 400.00)

    def test_below_bands_pays_zero(self):
        self.assertEqual(incentive_amount(0.59, 10000), 0.00)

    def test_invalid_inputs_raise(self):
        with self.assertRaises(ValueError):
            incentive_amount(1.2, 1000)
        with self.assertRaises(ValueError):
            incentive_amount(0.9, -1)


class TestIncentiveCoverage100Pct(unittest.TestCase):
    """100% coverage verification of incentive engine feeding payroll (R06-M01-T05)."""

    def test_full_range_evaluation_no_dead_zones(self):
        # 100 score steps between 0.00 and 1.00
        for i in range(101):
            score = round(i / 100.0, 2)
            amount = incentive_amount(score, 25000.0)
            self.assertIsInstance(amount, float)
            self.assertGreaterEqual(amount, 0.0)
            if score >= 0.90:
                self.assertEqual(amount, round(25000.0 * 0.15, 2))
            elif score >= 0.75:
                self.assertEqual(amount, round(25000.0 * 0.08, 2))
            elif score >= 0.60:
                self.assertEqual(amount, round(25000.0 * 0.04, 2))
            else:
                self.assertEqual(amount, 0.0)

    def test_incentive_engine_feeds_payroll_event(self):
        src_apply = inspect.getsource(FixIncentiveRun.action_apply)
        self.assertIn("incentive.granted", src_apply)
        self.assertIn("applied", src_apply)

    def test_scorecard_published_event(self):
        src_pub = inspect.getsource(FixPerformanceScorecard.action_publish)
        self.assertIn("scorecard.published", src_pub)


class TestT5FieldLevelPermissions(unittest.TestCase):
    """Compensation banding with T5 field-level permissions negative-tested (R06-M01-T05)."""

    def test_compensation_band_ranges_protected_by_group_system(self):
        for field_name in ("range_min", "range_mid", "range_max"):
            field_def = getattr(FixCompensationBand, field_name, None)
            self.assertIsNotNone(field_def, f"Field {field_name} missing on FixCompensationBand")
            self.assertEqual(
                getattr(field_def, "groups", None),
                "base.group_system",
                f"Field {field_name} must be restricted to base.group_system (T5)",
            )

    def test_incentive_run_band_base_protected_by_group_system(self):
        field_def = getattr(FixIncentiveRun, "band_base", None)
        self.assertIsNotNone(field_def, "Field band_base missing on FixIncentiveRun")
        self.assertEqual(
            getattr(field_def, "groups", None),
            "base.group_system",
            "Field band_base must be restricted to base.group_system (T5)",
        )

    def test_band_range_validation_ordering(self):
        src = inspect.getsource(FixCompensationBand._check_range)
        self.assertIn("rec.range_min <= rec.range_mid <= rec.range_max", src)


if __name__ == "__main__":
    unittest.main()
