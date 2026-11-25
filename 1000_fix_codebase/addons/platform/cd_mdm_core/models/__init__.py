# cd_mdm_core — M64-core MDM governance (P03-M07)
# The attribute register and payload mixin load first: the others inherit it.
# fix_mdm_capture (M64 capture audit) needs only the payload mixin, so the
# alphabetical order ruff enforces is also a valid load order.
from . import (
    fix_mdm_attribute_governance,
    fix_mdm_capture,
    fix_mdm_change_request,
    fix_mdm_golden_rule,
    fix_mdm_match_rule,
    fix_mdm_steward_approval,
    fix_mdm_stewardship,
)
