# cd_partner models.
# isort: skip_file
# fix_partner_capture extends fix.partner, fix.partner.rebate and
# fix.partner.franchise, so it loads last (M40 capture audit 2026-11-19).
from . import (
    fix_comarketing,
    fix_partner,
    fix_partner_ops,
    fix_party_merge_consumer,
    fix_partner_capture,
    # A04 ERP audit (20 Nov 2026), stream B5: standing, rate governance, brand link
    fix_partner_a04erp,
    # A04 ERP audit round 2 (21 Nov 2026): M07 hand-off, M11 alliance benefit
    fix_partner_r2,
)
