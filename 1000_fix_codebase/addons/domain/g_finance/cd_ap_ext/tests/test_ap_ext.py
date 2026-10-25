# cd_ap_ext tests — M52 core (P06-M04).
import inspect

import pytest

pytestmark = [pytest.mark.financial, pytest.mark.tax]


class TestThreeWayMatch:
    def test_model_exists(self):
        from odoo.addons.cd_ap_ext.models.fix_ap_ext import FixVendorInvoice

        assert FixVendorInvoice is not None

    def test_match_states_block_not_warn(self):
        """G3-06: the match outcome set includes 'blocked' — an unmatched
        invoice is BLOCKED, never warned about."""
        from odoo.addons.cd_ap_ext.models.fix_ap_ext import FixVendorInvoice

        states = dict(FixVendorInvoice.match_state.selection)
        assert "blocked" in states

    def test_payment_refused_unless_matched(self):
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_ap_ext.models.fix_ap_ext", fromlist=["FixVendorInvoice"]
            ).FixVendorInvoice.action_request_payment
        )
        assert "match_state" in source and "raise UserError" in source

    def test_match_lives_in_m52_not_m16(self):
        """AR-006 section 4.1 pair 11: the seam belongs in M52, consuming
        M16 (fix.purchase.order) events — verified by the model location
        and the PO reference."""
        from odoo.addons.cd_ap_ext.models.fix_ap_ext import FixVendorInvoice

        assert "fix.purchase.order" in FixVendorInvoice.requisition_id.comodel_name

    def test_tds_is_synchronous_import(self):
        """AR-006 pair 8: M52 calls M51 synchronously — since A08 through
        M51's effective-dated Tax Rate Master (fix.tax.rate.find_rate)."""
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_ap_ext.models.fix_ap_ext", fromlist=["FixVendorInvoiceLine"]
            ).FixVendorInvoiceLine._compute_tds
        )
        assert 'self.env["fix.tax.rate"]' in source and "Rate.find_rate(" in source

    def test_payment_requests_are_events(self):
        """AR-006 pair 9: M52 -> M50 is an event, never a synchronous call."""
        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_ap_ext.models.fix_ap_ext", fromlist=["FixVendorInvoice"]
            ).FixVendorInvoice.action_request_payment
        )
        assert '"payment.requested"' in source
        # The docstring disclaims the synchronous call by naming it; mask the
        # disclaimers before scanning for an actual call.
        masked = (
            source.replace("events", "")
            .replace("No synchronous call into M50", "")
            .replace("never a synchronous call", "")
        )
        assert "call" not in masked

    def test_live_negative_match_qty_variance_blocks_and_refuses_payment(self):
        """G3-06b: Live negative test — quantity invoiced > quantity received strictly blocks."""
        from unittest.mock import MagicMock

        from odoo.addons.cd_ap_ext.models.fix_ap_ext import FixVendorInvoice
        from odoo.exceptions import UserError

        class MockRecordset(list):
            def filtered(self, predicate):
                return MockRecordset([x for x in self if predicate(x)])

            def __getitem__(self, item):
                res = super().__getitem__(item)
                return MockRecordset(res) if isinstance(res, list) else res

            def __getattr__(self, name):
                if len(self) == 1:
                    return getattr(self[0], name)
                raise AttributeError(name)

        inv = MagicMock()
        line = MagicMock()
        line.product_id.id = 101
        line.description = "Spare Battery Pack"
        line.quantity = 10.0
        line.unit_price = 500.0

        po_line = MagicMock()
        po_line.product_id.id = 101
        po_line.qty_ordered = 10.0
        po_line.qty_received = 4.0
        po_line.unit_price = 500.0

        po = MagicMock()
        po.line_ids = MockRecordset([po_line])

        inv.requisition_id = po
        inv.line_ids = [line]

        FixVendorInvoice._compute_match([inv])
        assert inv.match_state == "blocked"
        assert "received 4.00 < invoiced 10.00" in inv.match_detail

        with pytest.raises(UserError, match="G3-06: an unmatched vendor invoice cannot be paid"):
            FixVendorInvoice.action_request_payment([inv])

    def test_live_negative_match_price_variance_blocks_and_refuses_payment(self):
        """G3-06b: Live negative test — unit price invoiced > PO price strictly blocks."""
        from unittest.mock import MagicMock

        from odoo.addons.cd_ap_ext.models.fix_ap_ext import FixVendorInvoice
        from odoo.exceptions import UserError

        class MockRecordset(list):
            def filtered(self, predicate):
                return MockRecordset([x for x in self if predicate(x)])

            def __getitem__(self, item):
                res = super().__getitem__(item)
                return MockRecordset(res) if isinstance(res, list) else res

            def __getattr__(self, name):
                if len(self) == 1:
                    return getattr(self[0], name)
                raise AttributeError(name)

        inv = MagicMock()
        line = MagicMock()
        line.product_id.id = 202
        line.description = "Display Panel"
        line.quantity = 1.0
        line.unit_price = 3500.0  # above PO price

        po_line = MagicMock()
        po_line.product_id.id = 202
        po_line.qty_ordered = 1.0
        po_line.qty_received = 1.0
        po_line.unit_price = 3000.0

        po = MagicMock()
        po.line_ids = MockRecordset([po_line])

        inv.requisition_id = po
        inv.line_ids = [line]

        FixVendorInvoice._compute_match([inv])
        assert inv.match_state == "blocked"
        assert "price above PO" in inv.match_detail

        with pytest.raises(UserError, match="G3-06: an unmatched vendor invoice cannot be paid"):
            FixVendorInvoice.action_request_payment([inv])


class TestExpenseClaim:
    def test_threshold_and_employee_master(self):
        from odoo.addons.cd_ap_ext.models.fix_ap_expense import FixExpenseClaim

        assert FixExpenseClaim.APPROVAL_THRESHOLD == 25000
        assert FixExpenseClaim.employee_id.comodel_name == "hr.employee"
