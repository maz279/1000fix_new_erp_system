# cd_device_registry — M17 Device & Customer Asset Registry (P04-M01)
from . import (
    fix_device,
    fix_device_history,
    fix_device_lineage,  # A07 P2 (2026-11-04): identifier history, merge lineage
    fix_device_ops,
    fix_device_ownership,
    fix_device_part_compatibility,
    fix_party_merge_consumer,
    fix_warranty,
)

# isort: split
# A02 audit B1/B4: extend fix.warranty, so they import after it.
from . import fix_warranty_approval, fix_warranty_expiry

# isort: split
# M17 capture audit (2026-11-13): bulk estate registration (FR-AST-039).
from . import fix_device_bulk

# isort: split
# M17 capture pass 2 (2026-11-19): labels, identifiers, accessories,
# configuration, population, estate nodes and placements, end-of-life
# decisions, stewardship worklist. Extends the models above, so it is last.
from . import fix_device_capture
