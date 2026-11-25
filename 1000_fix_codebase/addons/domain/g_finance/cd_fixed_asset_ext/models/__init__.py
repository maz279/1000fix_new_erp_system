# fix_asset_approval first: the capex, revaluation and disposal models
# inherit its routed-approval mixin.
from . import fix_asset_approval  # noqa: I001
from . import (
    fix_asset_depreciation,
    fix_asset_lifecycle,
    fix_asset_master,
    fix_asset_takeon,
    fix_asset_verification,
    fix_capex,
    fix_capex_po,
    fix_fixed_asset,
    fix_lease,
)

# the capture-audit records (2026-11-17) extend the register, CWIP, the
# depreciation run and the capex request: loaded after them
from . import fix_asset_capture

# the two gaps left by that audit: components of a seam asset and insurance
# cover; they extend the register and the disposal: loaded after the above
from . import fix_asset_gaps

# the take-on provenance extends the register: loaded after fix_fixed_asset
from . import fix_fixed_asset_takeon_ext
