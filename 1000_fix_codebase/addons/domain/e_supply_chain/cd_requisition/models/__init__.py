# ruff: noqa: I001 - import order is Odoo load order: a file that _inherits a
# model must import after the file defining it. Do not alphabetise.
# cd_requisition models.
from . import fix_requisition, fix_purchase_receipt, fix_procurement_ops, fix_purchase_proforma
from . import fix_procurement_capture  # M16 capture pass 2 (19 Nov 2026): imported last
from . import fix_purchase_price_amendment  # A06 P11
