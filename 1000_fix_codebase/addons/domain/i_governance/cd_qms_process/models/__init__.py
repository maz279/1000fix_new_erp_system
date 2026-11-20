# cd_qms_process models.
# fix_supplier_car_consumer must load after fix_qms (it extends fix.ncr), and
# fix_qms_capture after both fix_qms and fix_qms_ops (it extends their
# models): the import order below is load order.
# ruff: noqa: I001
from . import fix_qms, fix_qms_ops, fix_supplier_car_consumer
from . import fix_qms_capture

# A02 ERP pass 2 X5-14: M01 qc_failed / rework.detected -> NCR (extends fix.ncr).
from . import fix_a02r2_quality_consumers
