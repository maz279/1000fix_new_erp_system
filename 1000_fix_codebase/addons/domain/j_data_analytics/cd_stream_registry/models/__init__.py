# ruff: noqa: I001 - import order is Odoo load order: a file that _inherits a
# model must import after the file defining it. Do not alphabetise.
# cd_stream_registry models.
from . import (
    fix_iot_ops,
    fix_stream_registry,
    fix_iot_capture,
    fix_iot_a07erp,
)
