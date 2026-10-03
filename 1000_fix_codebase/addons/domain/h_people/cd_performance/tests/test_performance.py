# cd_performance tests — P08-M04 (CD-M57-01). DoD-03: incentive math.
import unittest

from odoo.addons.cd_performance.models.fix_performance import (
    composite_score, incentive_amount)


class TestCompositeScore(unittest.TestCase):
    def test_perfect_scores(self):
        self.assertEqual(composite_score(1, 1, 1, 0), 0.85)

    def test_rework_penalty_applies(self):
        clean = composite_score(1, 1, 1, 0)
        dirty = composite_score(1, 1, 1, 1)
        self.assertAlmostEqual(clean - dirty, 0.15, places=6)

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


if __name__ == "__main__":
    unittest.main()
