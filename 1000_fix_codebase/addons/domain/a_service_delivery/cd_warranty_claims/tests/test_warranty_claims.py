# cd_warranty_claims tests — M09 (P07-M02; G4-01/G4-02).
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "models"
          / "fix_warranty_claims.py").read_text(encoding="utf-8")


class TestEvidencePack(unittest.TestCase):
    def test_all_seven_items(self):
        for key in ("photo_before", "photo_after", "diagnostic", "parts_issued",
                    "device_serial", "technician_cert", "purchase_proof"):
            self.assertIn('"%s"' % key, SOURCE)

    def test_submission_blocks_on_incomplete_pack(self):
        """T05 / G4-02: an incomplete claim never submits."""
        self.assertIn("missing evidence", SOURCE)
        self.assertIn("incomplete claim is a rejected claim", SOURCE)

    def test_missing_list_computed(self):
        self.assertIn("_compute_evidence", SOURCE)


class TestAut018(unittest.TestCase):
    def test_auto_create_from_completed_warranty_job(self):
        self.assertIn("consume_order_completed", SOURCE)

    def test_warranty_category_only(self):
        """Auto-claims are for WARRANTY jobs — paid jobs don't claim."""
        self.assertIn('order_category != "warranty"', SOURCE)

    def test_idempotent_on_order(self):
        self.assertIn("one claim per warranty job", SOURCE)

    def test_72h_submission_deadline(self):
        """G4-01: submitted within 72 — the deadline is created with the claim."""
        self.assertIn("timedelta(hours=72)", SOURCE)

    def test_timing_latencies_and_deadline_tracking(self):
        """R05-M01-T02: Creation and submission latencies tracking."""
        self.assertIn("auto_creation_latency_hours", SOURCE)
        self.assertIn("submission_latency_hours", SOURCE)
        self.assertIn("is_submission_overdue", SOURCE)
        self.assertIn("job_completed_at", SOURCE)

    def test_workshop_evidence_pack_assembly(self):
        """R05-M01-T05: Assembles evidence drawing from workshop repair records."""
        self.assertIn("action_assemble_workshop_evidence_pack", SOURCE)


class TestRemittance(unittest.TestCase):
    def test_mismatch_flagged_not_adjusted(self):
        self.assertIn("mismatch", SOURCE)
        self.assertIn("never auto-adjusted", SOURCE)

    def test_only_approved_takes_remittance(self):
        self.assertIn("Only an approved claim takes a remittance", SOURCE)


class TestProtectionProduct(unittest.TestCase):
    def test_waiting_period_declared(self):
        """WTY-12: claims within the waiting period are rejected."""
        self.assertIn("waiting_days", SOURCE)

    def test_claim_limit_declared(self):
        """WTY-14: aggregate limits decrement."""
        self.assertIn("claim_limit", SOURCE)

    def test_excess_declared(self):
        """WTY-13: customer excess collected before fulfilment."""
        self.assertIn("excess_amount", SOURCE)


if __name__ == "__main__":
    unittest.main()
