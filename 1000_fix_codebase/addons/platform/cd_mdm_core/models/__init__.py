# cd_mdm_core — M64-core MDM governance (P03-M07)
# The attribute register and payload mixin load first: the others inherit it.
from . import (
    fix_mdm_attribute_governance,
    fix_mdm_change_request,
    fix_mdm_golden_rule,
    fix_mdm_match_rule,
    fix_mdm_steward_approval,
    fix_mdm_stewardship,
)
