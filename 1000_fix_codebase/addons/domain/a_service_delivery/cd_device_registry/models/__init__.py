# cd_device_registry — M17 Device & Customer Asset Registry (P04-M01)
from . import (
    fix_device,
    fix_device_history,
    fix_device_ops,
    fix_device_ownership,
    fix_device_part_compatibility,
    fix_party_merge_consumer,
    fix_warranty,
)

# isort: split
# A02 audit B1/B4: extend fix.warranty, so they import after it.
from . import fix_warranty_approval, fix_warranty_expiry
