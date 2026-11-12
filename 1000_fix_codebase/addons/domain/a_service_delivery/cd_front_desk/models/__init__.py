# cd_front_desk — M04 Front Desk (P04-M02).
# fix_workstation_ext extends fix.cash.shift / fix.token.queue /
# fix.walkin.intake and MUST import after them. Its name sorts last
# alphabetically, so the formatter-safe single import below is also the
# correct load order — do not rename it to anything sorting before
# fix_walkin_intake (the pre-rename name fix_front_desk_ext did exactly
# that and 500-crash-looped the whole server, 2026-10-26).
from . import (
    fix_branch_announcement,
    fix_branch_checklist,
    fix_cash_movement,
    fix_cash_shift,
    fix_service_order_drawer,
    fix_token_queue,
    fix_token_routing,
    fix_walkin_intake,
    fix_walkin_storage,
    fix_workstation_ext,
)
