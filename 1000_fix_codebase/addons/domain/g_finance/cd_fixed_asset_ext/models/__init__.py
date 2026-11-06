# fix_asset_approval first: the capex, revaluation and disposal models
# inherit its routed-approval mixin.
from . import fix_asset_approval  # noqa: I001
from . import (
    fix_asset_depreciation,
    fix_asset_lifecycle,
    fix_asset_master,
    fix_asset_verification,
    fix_capex,
    fix_capex_po,
    fix_fixed_asset,
    fix_lease,
)
