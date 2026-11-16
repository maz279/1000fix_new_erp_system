# ruff: noqa: I001 - import order is Odoo load order: a file that _inherits a
# model must import after the file defining it. Do not alphabetise.
# cd_equipment_register models.
from . import (
    fix_equipment,
    fix_equipment_ops,
    fix_equipment_capture,
)
