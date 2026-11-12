# ruff: noqa: I001 - import order is Odoo load order: a file that _inherits a
# model must import after the file defining it. Do not alphabetise.
# cd_requisition models.
from . import fix_requisition, fix_purchase_receipt, fix_procurement_ops, fix_purchase_proforma
