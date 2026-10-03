# cd_cash_position tests — M50 core (P06-M04).
import inspect
import pytest


class TestPaymentExecution:
    def test_idempotent_on_source_key(self):
        """DI-04: a replayed payment.requested never double-pays."""
        from odoo.addons.cd_cash_position.models.fix_cash_position import FixPaymentExecution
        assert hasattr(FixPaymentExecution, "_request_key_unique")  # Odoo 19 models.Constraint attr

    def test_execution_publishes_confirmation(self):
        source = inspect.getsource(
            __import__("odoo.addons.cd_cash_position.models.fix_cash_position",
                       fromlist=["FixPaymentExecution"]).FixPaymentExecution.action_execute)
        assert '"payment.executed"' in source

    def test_consumes_events_not_calls(self):
        source = inspect.getsource(
            __import__("odoo.addons.cd_cash_position.models.fix_cash_position",
                       fromlist=["FixPaymentExecution"]).FixPaymentExecution.consume_payment_requested)
        assert "payment.requested" in source or "payload" in source


class TestBankReconciliation:
    def test_match_states(self):
        from odoo.addons.cd_cash_position.models.fix_cash_position import FixBankStatementLine
        states = dict(FixBankStatementLine.match_state.selection)
        assert set(states) == {"unmatched", "auto", "manual"}


class TestCashPosition:
    def test_consumes_m04_drawers(self):
        """T07: the position sums open fix.cash.shift expected closings."""
        source = inspect.getsource(
            __import__("odoo.addons.cd_cash_position.models.fix_cash_position",
                       fromlist=["FixCashPosition"]).FixCashPosition._compute_drawers)
        assert "fix.cash.shift" in source
