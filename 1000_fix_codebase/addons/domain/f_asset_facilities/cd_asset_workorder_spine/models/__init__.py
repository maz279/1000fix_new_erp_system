# ruff: noqa: I001
# Order matters: the demand ledger is defined before the work-order spine
# that links to it, and both before the wiring that extends them.
from . import fix_maintenance_demand
from . import fix_spine_work_order
from . import fix_exit_asset_clearance
from . import fix_identity_gate
from . import fix_spine_wiring
from . import fix_quality_recheck
from . import fix_ml_outcome

# A07 P1 wiring round 2 (2026-11-04): M46 defect / telematics demands, and
# the M17 lost/stolen hold on M01 orders
from . import fix_spine_vehicle_wiring
from . import fix_device_flag_hold
