# cd_ap_ext tests — M52 core (P06-M04).
#
# A08 build (2026-11-04): the three source-grep tests that lived here
# (inspect.getsource of action_request_payment and _compute_tds, asserting
# words such as "match_state" and "payment.requested" appear in the code)
# certified nothing about behaviour. They are replaced by executed tests:
#   - payment refused unless matched: test_a06_m16_match.py
#     (test_m16_qty_variance_blocks_and_refuses_payment, ..._price_variance_...)
#     and test_a08_m52_controls.py::test_m52_15_blocked_bill_not_payable;
#   - TDS from M51's effective-dated rate master: test_ap_a08_orm.py
#     (TestVendorTaxProfile) and test_a08_m52_controls.py::test_m52_12_...;
#   - payment requests are events: test_a08_m52_controls.py
#     (test_bill_payment_requested_payload, test_m52_60_...).
import pytest

pytestmark = [pytest.mark.financial, pytest.mark.tax]


class TestThreeWayMatch:
    def test_unmatched_po_bill_is_refused_payment(self, odoo_env):
        """G3-06, as behaviour: a purchase-order bill with no order behind it is
        unmatched, and the payment request refuses it and publishes nothing."""
        from odoo.exceptions import UserError

        env = odoo_env
        ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
        bill = env["fix.vendor.invoice"].create(
            {
                "operating_unit_id": ou.id,
                "vendor_id": env["res.partner"].create({"name": "G3-06 vendor"}).id,
                "invoice_ref": "G3-06-1",
                "bill_type": "po",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": env["product.product"].create({"name": "G3-06"}).id,
                            "description": "G3-06",
                            "quantity": 1.0,
                            "unit_price": 100.0,
                        },
                    )
                ],
            }
        )
        assert bill.match_state == "unmatched"
        with pytest.raises(UserError, match="G3-06"):
            bill.action_request_payment()
        assert bill.payment_state == "not_paid"
        assert not env["fix.ap.bill.payment"].sudo().search([("bill_id", "=", bill.id)])

    def test_match_states_block_not_warn(self):
        """G3-06: the match outcome set includes 'blocked' — an unmatched
        invoice is BLOCKED, never warned about."""
        from odoo.addons.cd_ap_ext.models.fix_ap_ext import FixVendorInvoice

        states = dict(FixVendorInvoice.match_state.selection)
        assert "blocked" in states

    def test_match_lives_in_m52_not_m16(self):
        """AR-006 section 4.1 pair 11: the seam belongs in M52, consuming
        M16 (fix.purchase.order) events — verified by the model location
        and the PO reference."""
        from odoo.addons.cd_ap_ext.models.fix_ap_ext import FixVendorInvoice

        assert "fix.purchase.order" in FixVendorInvoice.requisition_id.comodel_name


class TestExpenseClaim:
    def test_threshold_and_employee_master(self):
        from odoo.addons.cd_ap_ext.models.fix_ap_controls import DEFAULT_CLAIM_MANAGER_THRESHOLD
        from odoo.addons.cd_ap_ext.models.fix_ap_expense import FixExpenseClaim

        assert FixExpenseClaim.APPROVAL_THRESHOLD == DEFAULT_CLAIM_MANAGER_THRESHOLD == 25000
        assert FixExpenseClaim.employee_id.comodel_name == "hr.employee"
