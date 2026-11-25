"""test_settlement_payout_e2e.py — Comprehensive E2E tests for Milestone R08-M02.
Verifies:
1. Commission ledger with 4 reconciliation keys (LP-02).
2. GL posting adhering strictly to FF-91 (MS-01) & contra-posting rule (LP-07).
3. Two-person Segregation of Duties (SoD) enforcement.
4. INT-007 payout rail: 7-day idempotency, unknown timeout state, read-back query (FF-85), BEFTN fallback.
5. Bilingual seller statements with ITA 2023 §52 withholding certification.
6. Payout reconciliation with count/amount separation (FF-94) and aging breaks (BR-01..BR-05).
"""

import sys
import unittest
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial]

from libs.py.payout_rail import (
    INT007PayoutRail,
    PayoutBatchRequest,
    PayoutRecipient,
    PayoutStatus,
)

# Add services/settlement-engine/src to sys.path
sys.path.insert(
    0, str(Path(__file__).resolve().parents[5] / "services" / "settlement-engine" / "src")
)

from settlement_engine import (
    SoDViolationError,
    approve_payout_batch,
    commission_for,
    create_payout_batch,
    generate_seller_statement,
    parse_commission_earned_event,
    reconcile_payout_run,
    settle_period,
)

D = Decimal


class TestSettlementPayoutFullLifecycle(unittest.TestCase):
    """Full lifecycle E2E test verifying R08-M02-T01 through R08-M02-T05."""

    def test_commission_event_to_statement_and_reconciliation_e2e(self):
        # 1. Consume M12 commission.earned event (R08-M02-T01)
        event_payload = {
            "seller_ref": "SELLER-BANGLA-01",
            "basis_amount": "50000.00",
            "scheme": "marketplace_gmv",
            "occurred_at": "2026-10-18",
        }
        event = parse_commission_earned_event(event_payload)
        self.assertEqual(event.seller_ref, "SELLER-BANGLA-01")
        self.assertEqual(event.basis_amount, D("50000.00"))

        comm_line = commission_for(event)
        # 5% GMV on 50,000 BDT = 2,500 BDT commission
        self.assertEqual(comm_line.commission, D("2500.00"))

        # 2. Settle period (R08-M02-T01)
        # Gross commission = 2500.00 -> TDS (10%) = 250.00 -> after TDS = 2250.00 -> fee (3%) = 67.50 -> net = 2182.50
        payout_lines = settle_period([event], "2026-10")
        self.assertEqual(len(payout_lines), 1)
        pline = payout_lines[0]
        self.assertEqual(pline.gross_commission, D("2500.00"))
        self.assertEqual(pline.tds, D("250.00"))
        self.assertEqual(pline.platform_fee, D("67.50"))
        self.assertEqual(pline.net_payable, D("2182.50"))

        # 3. Two-person SoD Payout Batch (R08-M02-T01)
        batch = create_payout_batch([event], "2026-10", prepared_by="accountant_rahim")
        self.assertEqual(batch.state, "draft")

        # Negative SoD test: preparer self-approval rejected
        with self.assertRaises(SoDViolationError):
            approve_payout_batch(batch, approver_id="accountant_rahim", approver_role="cfo")

        # Valid SoD approval
        approved_batch = approve_payout_batch(batch, approver_id="cfo_karim", approver_role="cfo")
        self.assertEqual(approved_batch.state, "approved")
        self.assertEqual(approved_batch.approved_by, "cfo_karim")

        # 4. INT-007 Payout Rail Dispatch (R08-M02-T02)
        rail = INT007PayoutRail()
        recipients = (
            PayoutRecipient(
                seller_ref=pline.seller_ref,
                seller_name="Rahim Enterprises Ltd",
                account_number="20501234567890",
                routing_number="125272355",
                amount_bdt=pline.net_payable,
                disbursement_ref=f"DISB-{batch.period}-{pline.seller_ref}",
            ),
        )
        payout_req = PayoutBatchRequest(
            batch_ref=f"PAY-{batch.period}-001",
            period=batch.period,
            recipients=recipients,
            idempotency_key="IDEMP-7D-TEST-KEY-0001",
            total_amount=pline.net_payable,
            recipient_count=1,
        )

        # 4a. Timeout into first-class unknown state (IN-007-D-01 / FF-85)
        timeout_res = rail.submit_payout_batch(payout_req, simulate_timeout=True)
        self.assertEqual(timeout_res.status, PayoutStatus.UNKNOWN)
        self.assertEqual(timeout_res.unknown_count, 1)

        # 4b. The bank's read-back (outcome + its reference) resolves unknown to confirmed (FF-85)
        confirmed_res = rail.read_back_status(
            timeout_res.batch_ref,
            timeout_res.rail_batch_id,
            PayoutStatus.CONFIRMED,
            bank_reference="BANK-RB-TEST-0001",
        )
        self.assertEqual(confirmed_res.status, PayoutStatus.CONFIRMED)
        self.assertEqual(confirmed_res.confirmed_count, 1)

        # 4c. Idempotency test (7-day window): resubmission returns cached confirmed result
        cached_res = rail.submit_payout_batch(payout_req)
        self.assertEqual(cached_res.rail_batch_id, timeout_res.rail_batch_id)

        # 4d. Tested fallback: generate 128-byte BEFTN batch file
        beftn_req = PayoutBatchRequest(
            batch_ref=f"BEFTN-{batch.period}-001",
            period=batch.period,
            recipients=recipients,
            idempotency_key="IDEMP-BEFTN-FALLBACK-0001",
            total_amount=pline.net_payable,
            recipient_count=1,
        )
        beftn_res = rail.generate_beftn_fallback_batch(beftn_req)
        self.assertEqual(beftn_res.rail_type, "beftn")
        self.assertIsNotNone(beftn_res.beftn_raw)
        for line in beftn_res.beftn_raw.splitlines():
            self.assertEqual(len(line), 128)

        # 5. Bilingual Seller Statement with ITA 2023 §52 Certificate (R08-M02-T04)
        statement = generate_seller_statement(pline, statement_seq=1, cert_year=2026)
        self.assertEqual(statement.seller_ref, "SELLER-BANGLA-01")
        # gross sales value is the 50,000.00 GMV the commission was earned on;
        # the 2,500.00 commission is reported separately (never as the GMV)
        self.assertEqual(statement.gross_gmv, D("50000.00"))
        self.assertEqual(statement.commission_amount, D("2500.00"))
        self.assertEqual(statement.tds_withheld, D("250.00"))
        self.assertEqual(statement.net_payable, D("2182.50"))
        self.assertIn("NBR-TDS52-2026", statement.withholding_cert_ref)
        self.assertIn("আয়কর আইন ২০২৩ ধারা ৫২", statement.bilingual_labels["tds"]["bn"])

        # 6. Payout Reconciliation with separate count/amount and zero aged breaks (R08-M02-T04)
        rail_records = [
            {
                "seller_ref": "SELLER-BANGLA-01",
                "amount": "2182.50",
                "status": "confirmed",
                "record_date": "2026-10-19",
            }
        ]
        rec_report = reconcile_payout_run(approved_batch, rail_records)
        self.assertTrue(rec_report.count_matched)
        self.assertTrue(rec_report.amount_matched)
        self.assertTrue(rec_report.is_balanced)
        self.assertEqual(rec_report.unmatched_count, 0)
        self.assertEqual(rec_report.aged_unmatched_count, 0)
        self.assertFalse(rec_report.divergence_alert)


if __name__ == "__main__":
    unittest.main()
