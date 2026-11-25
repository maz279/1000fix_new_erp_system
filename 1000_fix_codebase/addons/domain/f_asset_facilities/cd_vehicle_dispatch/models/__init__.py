# cd_vehicle_dispatch models.
# ruff: noqa: I001
# Order matters: the vehicle link on the field order before the re-dispatch
# flags that read it (A07 P1 wiring round 2).
from . import fix_field_order_vehicle
from . import fix_field_order_redispatch
