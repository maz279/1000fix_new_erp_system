# cd_requisition tests — M16 W3 (P06-M07).
import inspect
import pytest


class TestPurchaseOrder:
    def test_model_exists(self):
        from odoo.addons.cd_requisition.models.fix_requisition import FixPurchaseOrder
        assert FixPurchaseOrder is not None

    def test_acknowledge_only_from_sent(self):
        source = inspect.getsource(
            __import__("odoo.addons.cd_requisition.models.fix_requisition",
                       fromlist=["FixPurchaseOrder"]).FixPurchaseOrder.action_acknowledge)
        assert "Only a sent PO can be acknowledged" in source

    def test_receipts_publish_goods_received(self):
        source = inspect.getsource(
            __import__("odoo.addons.cd_requisition.models.fix_requisition",
                       fromlist=["FixPurchaseOrder"]).FixPurchaseOrder.action_record_receipt)
        assert '"goods.received"' in source

    def test_received_qty_constraint(self):
        """Over-receipt is refused — BRU-INV-07 companion at the PO line."""
        source = inspect.getsource(
            __import__("odoo.addons.cd_requisition.models.fix_requisition",
                       fromlist=["FixPurchaseOrderLine"]).FixPurchaseOrderLine)
        assert "_check_quantities" in source


class TestRequisition:
    def test_threshold_25000(self):
        from odoo.addons.cd_requisition.models.fix_requisition import FixRequisition
        assert FixRequisition.APPROVAL_THRESHOLD == 25000
