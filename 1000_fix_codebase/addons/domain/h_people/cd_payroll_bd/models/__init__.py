# ruff: noqa: I001
# cd_payroll_bd models. Load order: the statutory settings and the exit
# settlement hook first, then the payroll documents that use them, then the
# A09 round-2 documents that build on those (statutory pack, reviews, bank
# returns and MFS files, the gratuity provision), and last the M56 capture
# records (2026-11-17), which extend the off-cycle payment and recovery.
from . import (
    res_users_payroll,
    fix_payroll_statutory,
    fix_payroll_settlement,
    fix_payroll,
    fix_payroll_ops,
    fix_statutory_pack,
    fix_payroll_review,
    fix_payroll_bank_return,
    fix_payroll_gratuity,
    fix_payroll_recovery,
    fix_payroll_capture,
)
