"""settlement-engine tests — P07-M03-T10 (DoD-03: 100% of calculation paths)."""

from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from settlement_engine import (
    EarningEvent,
    PayoutLine,
    SettlementError,
    SoDViolationError,
    approve_payout_batch,
    commission_for,
    confirm_payout_batch,
    create_payout_batch,
    execute_payout_batch,
    generate_seller_statement,
    parse_commission_earned_event,
    reconcile_payout_run,
    settle_period,
    validate_payout_sod,
)

D = Decimal


class TestCommission(unittest.TestCase):
    def test_service_labour_10_pct(self):
        line = commission_for(EarningEvent("S1", D("1000.00"), "service_labour", "2026-10-01"))
        self.assertEqual(line.commission, D("100.00"))
        self.assertEqual(line.rate, D("10"))

    def test_part_margin_8_pct(self):
        line = commission_for(EarningEvent("S1", D("500.00"), "part_margin", "2026-10-01"))
        self.assertEqual(line.commission, D("40.00"))

    def test_subscription_reseller_15_pct(self):
        line = commission_for(
            EarningEvent("S2", D("200.00"), "subscription_reseller", "2026-10-01")
        )
        self.assertEqual(line.commission, D("30.00"))

    def test_marketplace_kicker_below_threshold(self):
        line = commission_for(EarningEvent("S3", D("100000.00"), "marketplace_gmv", "2026-10-01"))
        self.assertEqual(line.commission, D("5000.00"))  # 5% only

    def test_marketplace_kicker_above_threshold(self):
        line = commission_for(EarningEvent("S3", D("100000.01"), "marketplace_gmv", "2026-10-01"))
        # 5% + 2% kicker
        self.assertEqual(line.rate, D("7"))
        self.assertEqual(line.commission, D("7000.00"))

    def test_unknown_scheme_refused(self):
        with self.assertRaises(SettlementError):
            commission_for(EarningEvent("S1", D("100"), "nope", "2026-10-01"))

    def test_negative_basis_refused(self):
        with self.assertRaises(SettlementError):
            commission_for(EarningEvent("S1", D("-1"), "service_labour", "2026-10-01"))

    def test_rounding_half_up(self):
        line = commission_for(EarningEvent("S1", D("0.05"), "service_labour", "2026-10-01"))
        self.assertEqual(line.commission, D("0.01"))


class TestPayout(unittest.TestCase):
    def test_deduction_order_tds_then_fee(self):
        """gross -> TDS 10% -> fee 3% of after-TDS -> net."""
        payouts = settle_period(
            [EarningEvent("S1", D("1000.00"), "service_labour", "2026-10-15")], "2026-10"
        )
        self.assertEqual(len(payouts), 1)
        p = payouts[0]
        self.assertEqual(p.gross_commission, D("100.00"))
        self.assertEqual(p.tds, D("10.00"))  # 10% of 100
        self.assertEqual(p.platform_fee, D("2.70"))  # 3% of 90
        self.assertEqual(p.net_payable, D("87.30"))

    def test_period_filtering(self):
        """Events outside the period are excluded from the payout."""
        payouts = settle_period(
            [
                EarningEvent("S1", D("1000.00"), "service_labour", "2026-09-30"),
                EarningEvent("S1", D("1000.00"), "service_labour", "2026-10-01"),
            ],
            "2026-10",
        )
        self.assertEqual(len(payouts), 1)
        self.assertEqual(payouts[0].gross_commission, D("100.00"))

    def test_multi_seller_aggregation(self):
        payouts = settle_period(
            [
                EarningEvent("A", D("1000.00"), "service_labour", "2026-10-01"),
                EarningEvent("A", D("1000.00"), "service_labour", "2026-10-02"),
                EarningEvent("B", D("500.00"), "part_margin", "2026-10-03"),
            ],
            "2026-10",
        )
        self.assertEqual(len(payouts), 2)
        a = next(p for p in payouts if p.seller_ref == "A")
        self.assertEqual(a.gross_commission, D("200.00"))
        self.assertEqual(a.tds, D("20.00"))

    def test_empty_period_empty_payouts(self):
        self.assertEqual(settle_period([], "2026-10"), [])

    def test_pure_no_odoo_imports(self):
        import inspect

        import settlement_engine

        source = inspect.getsource(settlement_engine)
        self.assertNotIn("from odoo", source)
        self.assertNotIn("import sqlite", source)


class TestPayoutRunSoD(unittest.TestCase):
    """R05-M02-T04: Settlement payout-run readiness with two-person Segregation of Duties (SoD)."""

    def setUp(self):
        self.events = [
            EarningEvent("Seller-101", D("5000.00"), "service_labour", "2026-10-05"),
            EarningEvent("Seller-102", D("12000.00"), "part_margin", "2026-10-12"),
        ]

    def test_payout_batch_creation(self):
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        self.assertEqual(batch.period, "2026-10")
        self.assertEqual(batch.seller_count, 2)
        self.assertEqual(batch.prepared_by, "acc_clerk_01")
        self.assertIsNone(batch.approved_by)
        self.assertEqual(batch.state, "draft")
        self.assertTrue(batch.total_net_payable > D("0.00"))

    def test_payout_batch_missing_preparer(self):
        with self.assertRaises(SettlementError):
            create_payout_batch(self.events, "2026-10", prepared_by="")

    def test_sod_valid_approval(self):
        """Two-person rule: preparer 'acc_clerk_01' is distinct from approver 'cfo_01'."""
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        approved = approve_payout_batch(batch, approver_id="cfo_01", approver_role="cfo")
        self.assertEqual(approved.state, "approved")
        self.assertEqual(approved.approved_by, "cfo_01")

    def test_sod_negative_self_approval_blocked(self):
        """SoD negative test: preparer attempting to self-approve MUST raise SoDViolationError."""
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        with self.assertRaises(SoDViolationError) as ctx:
            approve_payout_batch(batch, approver_id="acc_clerk_01", approver_role="cfo")
        self.assertIn("Preparer cannot approve their own payout run", str(ctx.exception))

    def test_sod_negative_unauthorized_role_blocked(self):
        """SoD negative test: unauthorized role (e.g. junior clerk or technician) is blocked."""
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        with self.assertRaises(SoDViolationError) as ctx:
            approve_payout_batch(batch, approver_id="mgr_02", approver_role="junior_clerk")
        self.assertIn("does not possess payout approval authority", str(ctx.exception))

    def test_sod_negative_empty_approver_blocked(self):
        with self.assertRaises(SoDViolationError):
            validate_payout_sod("user_a", "", "finance_manager")

    def test_empty_payout_batch_approval_blocked(self):
        batch = create_payout_batch([], "2026-10", prepared_by="acc_clerk_01")
        with self.assertRaises(SettlementError) as ctx:
            approve_payout_batch(batch, approver_id="cfo_01", approver_role="cfo")
        self.assertIn("zero commission lines", str(ctx.exception))

    def test_execution_requires_prior_approval(self):
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        with self.assertRaises(SettlementError):
            execute_payout_batch(batch)  # in draft

        approved = approve_payout_batch(batch, approver_id="cfo_01", approver_role="cfo")
        released = execute_payout_batch(approved)
        # releasing to the rail is not paying: no bank evidence yet
        self.assertEqual(released.state, "pending_bank_confirmation")
        self.assertIsNone(released.bank_reference)

    def test_confirmation_requires_the_bank_reference(self):
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        approved = approve_payout_batch(batch, approver_id="cfo_01", approver_role="cfo")
        with self.assertRaises(SettlementError):
            confirm_payout_batch(approved, "BK-1")  # not released yet
        released = execute_payout_batch(approved)
        for missing in ("", "   ", None):
            with self.assertRaises(SettlementError) as ctx:
                confirm_payout_batch(released, missing)
            self.assertIn("bank settlement reference is required", str(ctx.exception))
        executed = confirm_payout_batch(released, " BEFTN-STL-0042 ")
        self.assertEqual(executed.state, "executed")
        self.assertEqual(executed.bank_reference, "BEFTN-STL-0042")
        self.assertEqual(executed.total_net_payable, approved.total_net_payable)

    def test_approve_non_draft_batch_raises(self):
        batch = create_payout_batch(self.events, "2026-10", prepared_by="acc_clerk_01")
        approved = approve_payout_batch(batch, approver_id="cfo_01", approver_role="cfo")
        with self.assertRaises(SettlementError) as ctx:
            approve_payout_batch(approved, approver_id="cfo_02", approver_role="cfo")
        self.assertIn("must be 'draft'", str(ctx.exception))

    def test_approve_zero_net_payable_raises(self):
        from settlement_engine import PayoutBatch, PayoutLine

        dummy_line = PayoutLine("S0", "2026-10", D("0.00"), D("0.00"), D("0.00"), D("0.00"))
        zero_batch = PayoutBatch(
            period="2026-10",
            payout_lines=(dummy_line,),
            total_gross=D("0.00"),
            total_tds=D("0.00"),
            total_platform_fee=D("0.00"),
            total_net_payable=D("0.00"),
            seller_count=1,
            prepared_by="acc_clerk_01",
        )
        with self.assertRaises(SettlementError) as ctx:
            approve_payout_batch(zero_batch, approver_id="cfo_01", approver_role="cfo")
        self.assertIn("zero or negative net payable", str(ctx.exception))


class TestEventConsumption(unittest.TestCase):
    """Test consuming M12 commission.earned events without direct coupling."""

    def test_parse_valid_event(self):
        payload = {
            "seller_ref": "SELLER-99",
            "basis_amount": "50000.00",
            "scheme": "marketplace_gmv",
            "occurred_at": "2026-10-18",
        }
        event = parse_commission_earned_event(payload)
        self.assertEqual(event.seller_ref, "SELLER-99")
        self.assertEqual(event.basis_amount, D("50000.00"))
        self.assertEqual(event.scheme, "marketplace_gmv")

    def test_parse_event_missing_seller(self):
        with self.assertRaises(SettlementError):
            parse_commission_earned_event({"basis_amount": "100.00"})

    def test_parse_event_missing_basis(self):
        with self.assertRaises(SettlementError):
            parse_commission_earned_event({"seller_ref": "S1"})

    def test_parse_event_invalid_basis(self):
        with self.assertRaises(SettlementError):
            parse_commission_earned_event({"seller_ref": "S1", "basis_amount": "not_a_number"})

    def test_parse_event_invalid_payload_type(self):
        with self.assertRaises(SettlementError):
            parse_commission_earned_event("not_a_dict")  # type: ignore


class TestSellerStatement(unittest.TestCase):
    """Test bilingual seller statements and ITA 2023 §52 withholding certification."""

    def test_statement_generation(self):
        payout_line = PayoutLine(
            seller_ref="SELLER-BD-01",
            period="2026-10",
            gross_commission=D("10000.00"),
            tds=D("1000.00"),
            platform_fee=D("270.00"),
            net_payable=D("8730.00"),
            gross_basis=D("100000.00"),
        )
        stmt = generate_seller_statement(payout_line, statement_seq=42, cert_year=2026)
        self.assertEqual(stmt.statement_id, "STM-2026-10-SELLER-BD-01-0042")
        self.assertEqual(stmt.gross_gmv, D("100000.00"))
        self.assertEqual(stmt.commission_amount, D("10000.00"))
        self.assertEqual(stmt.tds_withheld, D("1000.00"))
        self.assertEqual(stmt.net_payable, D("8730.00"))
        self.assertIn("NBR-TDS52-2026-SELLER-B-0042", stmt.withholding_cert_ref)
        # Check bilingual presence
        self.assertIn("bn", stmt.bilingual_labels["tds"])
        self.assertIn("আয়কর আইন ২০২৩ ধারা ৫২", stmt.bilingual_labels["tds"]["bn"])
        self.assertIn("মোট বিক্রয় মূল্য", stmt.bilingual_labels["gross_gmv"]["bn"])


class TestPayoutReconciliation(unittest.TestCase):
    """Test reconciliation comparing count and amount separately (FF-94) and checking aged breaks."""

    def setUp(self):
        self.events = [
            EarningEvent("S1", D("1000.00"), "service_labour", "2026-10-01"),
            EarningEvent("S2", D("2000.00"), "service_labour", "2026-10-02"),
        ]
        self.batch = create_payout_batch(self.events, "2026-10", prepared_by="clerk_01")

    def test_reconciliation_perfect_match(self):
        rail_records = [
            {
                "seller_ref": "S1",
                "amount": "87.30",
                "status": "confirmed",
                "record_date": "2026-10-15",
            },
            {
                "seller_ref": "S2",
                "amount": "174.60",
                "status": "confirmed",
                "record_date": "2026-10-15",
            },
        ]
        report = reconcile_payout_run(self.batch, rail_records)
        self.assertTrue(report.count_matched)
        self.assertTrue(report.amount_matched)
        self.assertEqual(report.unmatched_count, 0)
        self.assertEqual(report.aged_unmatched_count, 0)
        self.assertTrue(report.is_balanced)
        self.assertFalse(report.divergence_alert)

    def test_reconciliation_count_mismatch(self):
        """Amount may match or mismatch, but count difference flags divergence."""
        rail_records = [
            {
                "seller_ref": "S1",
                "amount": "261.90",
                "status": "confirmed",
                "record_date": "2026-10-15",
            },
        ]
        report = reconcile_payout_run(self.batch, rail_records)
        self.assertFalse(report.count_matched)
        self.assertTrue(report.divergence_alert)
        self.assertFalse(report.is_balanced)

    def test_reconciliation_aged_unmatched_flagged(self):
        """Unmatched records older than 30 days are tracked in aged_unmatched_count."""
        from datetime import date

        today = date(2026, 11, 20)
        rail_records = [
            {
                "seller_ref": "S1",
                "amount": "87.30",
                "status": "confirmed",
                "record_date": "2026-10-15",
            },
            # S2 has discrepancy and record date is 2026-10-01 (50 days old)
            {
                "seller_ref": "S2",
                "amount": "100.00",
                "status": "failed",
                "record_date": "2026-10-01",
            },
        ]
        report = reconcile_payout_run(self.batch, rail_records, as_of_date=today)
        self.assertFalse(report.is_balanced)
        self.assertEqual(report.unmatched_count, 1)
        self.assertEqual(report.aged_unmatched_count, 1)
        self.assertTrue(report.aged_unmatched_amount > D("0.00"))

    def test_reconciliation_unparseable_and_missing_record_dates(self):
        rail_records = [
            {
                "seller_ref": "S1",
                "amount": "80.00",
                "status": "confirmed",
                "record_date": "invalid-date-string",
            },
            {"seller_ref": "S2", "amount": "170.00", "status": "confirmed"},  # no record_date
        ]
        report = reconcile_payout_run(self.batch, rail_records)
        self.assertFalse(report.is_balanced)
        self.assertEqual(report.unmatched_count, 2)
        # S1 had unparseable date, S2 had no date -> age_days defaults to 0 -> not aged
        self.assertEqual(report.aged_unmatched_count, 0)


class TestINT007PayoutRail(unittest.TestCase):
    """Test INT-007 seller payout rail: idempotency, unknown state, and BEFTN fallback."""

    def setUp(self):
        from libs.py.payout_rail import (
            BankEndpointNotConfiguredError,
            IdempotencyConflictError,
            INT007PayoutRail,
            PayoutBatchRequest,
            PayoutRailError,
            PayoutRecipient,
            PayoutStatus,
        )

        self.INT007PayoutRail = INT007PayoutRail
        self.PayoutRecipient = PayoutRecipient
        self.PayoutBatchRequest = PayoutBatchRequest
        self.PayoutStatus = PayoutStatus
        self.IdempotencyConflictError = IdempotencyConflictError
        self.PayoutRailError = PayoutRailError
        self.BankEndpointNotConfiguredError = BankEndpointNotConfiguredError

        self.rail = INT007PayoutRail()
        self.recipients = (
            PayoutRecipient(
                seller_ref="S1",
                seller_name="Seller One",
                account_number="1234567890",
                routing_number="125272355",
                amount_bdt=D("5000.00"),
                disbursement_ref="DISB-001",
            ),
            PayoutRecipient(
                seller_ref="S2",
                seller_name="Seller Two",
                account_number="9876543210",
                routing_number="125272355",
                amount_bdt=D("7500.00"),
                disbursement_ref="DISB-002",
            ),
        )
        self.request = PayoutBatchRequest(
            batch_ref="BATCH-2026-10-01",
            period="2026-10",
            recipients=self.recipients,
            idempotency_key="IDEMP-KEY-TEST-001",
            total_amount=D("12500.00"),
            recipient_count=2,
        )

    def test_payout_submission_success(self):
        # Fail-closed (R01 re-audit): with no bank endpoint configured the
        # rail refuses - it must never fabricate CONFIRMED lines.
        with self.assertRaises(self.BankEndpointNotConfiguredError):
            self.rail.submit_payout_batch(self.request)

        # Over a (faked) wire, a real response produces real outcomes.
        from unittest.mock import patch

        class _Resp:
            def __init__(self, payload):
                self._payload = payload

            def read(self):
                import json

                return json.dumps(self._payload).encode()

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        # Wire contract per libs/py/payout_rail/tests: status + recipients
        # keyed by seller_ref (the rail maps them to disbursement lines).
        wire_payload = {
            "status": "confirmed",
            "recipients": [
                {"seller_ref": "S1", "status": "confirmed", "failure_reason": None},
                {"seller_ref": "S2", "status": "confirmed", "failure_reason": None},
            ],
        }
        import os
        import urllib.request

        with patch.dict(os.environ, {"FIX_INT007_BANK_API_URL": "http://rail.test/api"}):
            wire_rail = self.INT007PayoutRail()
            with patch.object(urllib.request, "urlopen", return_value=_Resp(wire_payload)):
                result = wire_rail.submit_payout_batch(self.request)
        self.assertEqual(result.status, self.PayoutStatus.CONFIRMED)
        self.assertEqual(result.confirmed_count, 2)
        self.assertEqual(result.confirmed_amount, D("12500.00"))
        self.assertEqual(result.failed_count, 0)
        self.assertEqual(result.unknown_count, 0)

    def test_idempotent_double_submission(self):
        import json
        import os
        import urllib.request
        from unittest.mock import patch

        class _Resp:
            def __init__(self, payload):
                self._payload = payload

            def read(self):
                return json.dumps(self._payload).encode()

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        def _wire():
            return _Resp(
                {
                    "status": "confirmed",
                    "recipients": [
                        {"seller_ref": "S1", "status": "confirmed", "failure_reason": None},
                        {"seller_ref": "S2", "status": "confirmed", "failure_reason": None},
                    ],
                }
            )

        with patch.dict(os.environ, {"FIX_INT007_BANK_API_URL": "http://rail.test/api"}):
            wire_rail = self.INT007PayoutRail()
            with patch.object(urllib.request, "urlopen", return_value=_wire()):
                result1 = wire_rail.submit_payout_batch(self.request)
            with patch.object(urllib.request, "urlopen", return_value=_wire()):
                result2 = wire_rail.submit_payout_batch(self.request)
        self.assertEqual(result1.rail_batch_id, result2.rail_batch_id)
        self.assertEqual(result1.idempotency_key, result2.idempotency_key)

    def test_idempotent_conflict_raises(self):
        import json
        import os
        import urllib.request
        from unittest.mock import patch

        class _Resp:
            def __init__(self, payload):
                self._payload = payload

            def read(self):
                return json.dumps(self._payload).encode()

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        def _wire():
            return _Resp(
                {
                    "status": "confirmed",
                    "recipients": [
                        {"seller_ref": "S1", "status": "confirmed", "failure_reason": None},
                        {"seller_ref": "S2", "status": "confirmed", "failure_reason": None},
                    ],
                }
            )

        with patch.dict(os.environ, {"FIX_INT007_BANK_API_URL": "http://rail.test/api"}):
            wire_rail = self.INT007PayoutRail()
            with patch.object(urllib.request, "urlopen", return_value=_wire()):
                wire_rail.submit_payout_batch(self.request)
        # Same control totals (FF-94 stays happy) but a DIFFERENT payload
        # under the SAME idempotency key -> the store must raise the conflict.
        from libs.py.payout_rail import PayoutRecipient as _Rec

        conflicting_request = self.PayoutBatchRequest(
            batch_ref="BATCH-2026-10-01",
            period="2026-10",
            recipients=(
                _Rec(
                    seller_ref="S1",
                    seller_name="Seller One",
                    account_number="1234567890",
                    routing_number="125272355",
                    amount_bdt=D("4000.00"),
                    disbursement_ref="DISB-001",
                ),
                _Rec(
                    seller_ref="S2",
                    seller_name="Seller Two",
                    account_number="9876543210",
                    routing_number="125272355",
                    amount_bdt=D("8500.00"),
                    disbursement_ref="DISB-002",
                ),
            ),
            idempotency_key="IDEMP-KEY-TEST-001",
            total_amount=D("12500.00"),
            recipient_count=2,
        )
        with (
            patch.dict(os.environ, {"FIX_INT007_BANK_API_URL": "http://rail.test/api"}),
            self.assertRaises(self.IdempotencyConflictError),
        ):
            wire_rail.submit_payout_batch(conflicting_request)

    def test_timeout_enters_unknown_state_and_resolves_via_readback(self):
        """IN-007-D-01 & FF-85: Timeout MUST enter unknown state, resolved only via read-back."""
        timeout_result = self.rail.submit_payout_batch(self.request, simulate_timeout=True)
        self.assertEqual(timeout_result.status, self.PayoutStatus.UNKNOWN)
        self.assertEqual(timeout_result.unknown_count, 2)
        self.assertEqual(timeout_result.confirmed_count, 0)

        # Read-back query resolves UNKNOWN to CONFIRMED
        resolved = self.rail.read_back_status(
            timeout_result.batch_ref,
            timeout_result.rail_batch_id,
            self.PayoutStatus.CONFIRMED,
            bank_reference="BANK-RB-TEST-0001",
        )
        self.assertEqual(resolved.status, self.PayoutStatus.CONFIRMED)
        self.assertEqual(resolved.confirmed_count, 2)
        self.assertEqual(resolved.unknown_count, 0)

    def test_beftn_fallback_generation(self):
        """BEFTN fallback produces valid 128-byte line output."""
        result = self.rail.generate_beftn_fallback_batch(self.request)
        # a generated file is not a settled transfer: it awaits the bank read-back
        self.assertEqual(result.status, self.PayoutStatus.UNKNOWN)
        self.assertEqual(result.rail_type, "beftn")
        self.assertIsNotNone(result.beftn_raw)
        lines = result.beftn_raw.splitlines()
        self.assertTrue(len(lines) >= 3)
        for line in lines:
            self.assertEqual(len(line), 128)


if __name__ == "__main__":
    unittest.main()
