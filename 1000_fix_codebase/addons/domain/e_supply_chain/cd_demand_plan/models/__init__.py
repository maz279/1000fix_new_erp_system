# ruff: noqa: I001 - import order is Odoo load order: a file that _inherits a
# model must import after the file defining it. Do not alphabetise.
# cd_demand_plan models.
from . import fix_demand_plan, fix_demand_ops, fix_demand_capture
