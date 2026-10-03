# cd_ap_ext tests — M52 core (P06-M04).
import inspect
import pytest


class TestThreeWayMatch:
    def test_model_exists(self):
        from addons.domain.g_finance.cd_ap_ext.models.fix_ap_ext import FixVendorInvoice
        assert FixVendorInvoice is not None

    def test_match_states_block_not_warn(self):
        """G3-06: the match outcome set includes 'blocked' — an unmatched
        invoice is BLOCKED, never warned about."""
        from addons.domain.g_finance.cd_ap_ext.models.fix_ap_ext import FixVendorInvoice
        states = dict(FixVendorInvoice._fields["match_state"].selection)
        assert "blocked" in states

    def test_payment_refused_unless_matched(self):
        source = inspect.getsource(
            __import__("addons.domain.g_finance.cd_ap_ext.models.fix_ap_ext",
                       fromlist=["FixVendorInvoice"]).FixVendorInvoice.action_request_payment)
        assert "match_state" in source and "raise UserError" in source

    def test_match_lives_in_m52_not_m16(self):
        """AR-006 section 4.1 pair 11: the seam belongs in M52, consuming
        M16 (fix.purchase.order) events — verified by the model location
        and the PO reference."""
        from addons.domain.g_finance.cd_ap_ext.models.fix_ap_ext import FixVendorInvoice
        assert "fix.purchase.order" in FixVendorInvoice._fields["requisition_id"].comodel_name

    def test_tds_is_synchronous_import(self):
        """AR-006 pair 8: M52 calls M51 synchronously."""
        source = inspect.getsource(
            __import__("addons.domain.g_finance.cd_ap_ext.models.fix_ap_ext",
                       fromlist=["FixVendorInvoice"]))
        assert "from cd_tax_engine_bd.models import tax_logic" in source

    def test_payment_requests_are_events(self):
        """AR-006 pair 9: M52 -> M50 is an event, never a synchronous call."""
        source = inspect.getsource(
            __import__("addons.domain.g_finance.cd_ap_ext.models.fix_ap_ext",
                       fromlist=["FixVendorInvoice"]).FixVendorInvoice.action_request_payment)
        assert '"payment.requested"' in source
        assert "call" not in source.replace("events", "")


class TestExpenseClaim:
    def test_threshold_and_employee_master(self):
        from addons.domain.g_finance.cd_ap_ext.models.fix_ap_ext import FixExpenseClaim
        assert FixExpenseClaim.APPROVAL_THRESHOLD == 25000
        assert FixExpenseClaim._fields["employee_id"].comodel_name == "hr.employee"
