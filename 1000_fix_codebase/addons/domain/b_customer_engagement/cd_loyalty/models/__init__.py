# The scheme engine EXTENDS fix.loyalty.program/.account, so it imports after
# the files that define them.
from . import (
    fix_loyalty_account,
    fix_loyalty_campaign,
    fix_loyalty_event_receipt,
    fix_loyalty_ledger,
    fix_loyalty_merge_transfer,
    fix_loyalty_program,
    fix_loyalty_referral,
    fix_loyalty_scheme,
    fix_loyalty_scheme_engine,
    fix_loyalty_stub,
    fix_loyalty_tier,
    fix_loyalty_voucher,
)

# The capture registers extend tier, programme and voucher, so they load last.
from . import fix_loyalty_capture  # isort: skip
