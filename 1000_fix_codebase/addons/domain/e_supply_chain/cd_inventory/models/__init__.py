# Alphabetical order is also the load order Odoo needs: fix_inventory_approval
# (the mixin) loads before every model that inherits it.
from . import (
    fix_graded_stock,
    fix_inventory_approval,
    fix_inventory_ops,
    fix_reorder_rule,
    fix_spare_part,
    fix_stock_bridges,
    fix_stock_consumption,
    fix_stock_location,
    fix_valuation_suspense,
    fix_wms_ops,
    fix_wms_ops_floor,
)
