# ruff: noqa: I001 - import order is Odoo load order: a file that _inherits a
# model must import after the file defining it. Do not alphabetise.
# cd_import_order models.
from . import (
    fix_import_common,
    fix_import_order,
    fix_import_ops,
    fix_import_compliance,
    fix_import_advance,
    fix_import_gl,
)
