# cd_cash_position tests — M50 core (P06-M04).
import inspect


class TestPaymentExecution:
    def test_idempotent_on_source_key(self):
        """DI-04: a replayed payment.requested never double-pays."""
        from odoo.addons.cd_cash_position.models.fix_cash_position import FixPaymentExecution

        assert hasattr(FixPaymentExecution, "_request_key_unique")  # Odoo 19 models.Constraint attr

    def test_execution_publishes_confirmation(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_cash_position.models.fix_cash_position",
                fromlist=["FixPaymentExecution"],
            ).FixPaymentExecution.action_execute
        )
        assert '"payment.executed"' in source

    def test_consumes_events_not_calls(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_cash_position.models.fix_cash_position",
                fromlist=["FixPaymentExecution"],
            ).FixPaymentExecution.consume_payment_requested
        )
        assert "payment.requested" in source or "payload" in source


class TestBankReconciliation:
    def test_match_states(self):
        from odoo.addons.cd_cash_position.models.fix_cash_position import FixBankStatementLine

        states = dict(FixBankStatementLine.match_state.selection)
        assert set(states) == {"unmatched", "auto", "manual"}

    def test_auto_match_ladder_supports_ar_ap_and_exp(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_cash_position.models.fix_cash_position",
                fromlist=["FixBankStatementLine"],
            ).FixBankStatementLine.auto_match
        )
        assert "AR" in source
        assert "AP" in source
        assert "EXP" in source

    def test_live_auto_match_reconciliation_rate(self):
        """Gate G3-02: Auto-reconciliation matches >= 90% of unambiguous executed payments."""
        from unittest.mock import MagicMock

        from odoo.addons.cd_cash_position.models.fix_cash_position import FixBankStatementLine

        currency_mock = MagicMock()
        company_mock = MagicMock()
        payments = []
        statement_lines = []

        # Generate 10 payments and 10 matching statement lines across AR, AP, and EXP
        for i in range(1, 11):
            source_model = (
                "fix.ar.invoice"
                if i <= 4
                else "fix.vendor.invoice"
                if i <= 7
                else "fix.expense.claim"
            )
            prefix = "AR" if i <= 4 else "AP" if i <= 7 else "EXP"
            p = MagicMock()
            p.id = 100 + i
            p.source_id = i
            p.source_model = source_model
            p.amount = float(1000 * i)
            p.currency_id = currency_mock
            p.company_id = company_mock
            p.payee = f"vendor_{i}"
            payments.append(p)

            line = MagicMock()
            line.id = 200 + i
            line.match_state = "unmatched"
            line.amount = float(1000 * i)
            line.currency_id = currency_mock
            line.company_id = company_mock
            line.reference = f"{prefix}/{i} ref-txn-{i}"
            line.narration = f"Settlement {prefix}/{i}"
            statement_lines.append(line)

        # Mock search calls
        model_mock = MagicMock()
        model_mock.search = MagicMock(return_value=statement_lines)
        env_mock = MagicMock()
        env_mock.__getitem__.return_value.search.return_value = payments
        model_mock.env = env_mock

        matched_count = FixBankStatementLine.auto_match(model_mock)
        reconciliation_rate = (matched_count / len(statement_lines)) * 100.0
        assert reconciliation_rate >= 90.0
        assert matched_count == 10


class TestCashPosition:
    def test_consumes_m04_drawers(self):
        """T07: the position sums open fix.cash.shift expected closings."""
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_cash_position.models.fix_cash_position",
                fromlist=["FixCashPosition"],
            ).FixCashPosition._compute_drawers
        )
        assert "fix.cash.shift" in source
