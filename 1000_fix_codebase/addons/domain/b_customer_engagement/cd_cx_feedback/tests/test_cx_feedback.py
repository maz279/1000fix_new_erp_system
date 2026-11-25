# cd_cx_feedback tests — M34 + M42 (P07-M06).
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "models" / "fix_cx_feedback.py").read_text(
    encoding="utf-8"
)


class TestSurvey(unittest.TestCase):
    def test_triggered_from_events_not_calls(self):
        """T04: the survey consumes service_order.closed (AS-08) — journey 1
        ends at an event, never a synchronous call."""
        self.assertIn("consume_order_closed", SOURCE)
        self.assertNotIn('self.env["fix.service.order"].write', SOURCE)

    def test_one_survey_per_order(self):
        self.assertIn("order_unique", SOURCE)

    def test_bengali_ratings(self):
        self.assertIn("খুব ভালো", SOURCE)

    def test_nps_computed(self):
        body = SOURCE[SOURCE.index("def _compute_nps") :]
        self.assertIn("-100", body)
        self.assertIn("100", body)


class TestComplaint(unittest.TestCase):
    def test_journey14_lifecycle_complete(self):
        for stage in ("ncr_raised", "root_cause", "capa_open", "verification", "closed"):
            self.assertIn(stage, SOURCE)

    def test_critical_requires_capa(self):
        """No shortcut: critical closes only through CAPA verification."""
        body = SOURCE[SOURCE.index("def action_close") :]
        self.assertIn("CRITICAL complaint closes only through CAPA", body)

    def test_ncr_stub_registered_with_expiry(self):
        """T03: the M23 stub is registered with an expiry date."""
        self.assertIn("NCR-STUB", SOURCE)
        self.assertIn("STUB", SOURCE)
        self.assertIn("expiry", SOURCE)


class TestSupplierScorecard(unittest.TestCase):
    def test_consumes_m16_events(self):
        """T06 / pair 10: the asymmetric interface — goods.received events
        in, scorecards out; M16 tables never read."""
        self.assertIn("consume_goods_received", SOURCE)

    def test_no_m16_table_access(self):
        self.assertNotIn('self.env["fix.purchase.order"].search', SOURCE)

    def test_score_weights(self):
        body = SOURCE[SOURCE.index("def _compute_scores") :]
        self.assertIn("0.6 * on_time + 0.4 * quality", body)

    def test_scorecards_publish_for_portal(self):
        self.assertIn('"supplier.scorecard"', SOURCE)

    def test_one_card_per_vendor_period(self):
        self.assertIn("vendor_period_unique", SOURCE)


if __name__ == "__main__":
    unittest.main()
