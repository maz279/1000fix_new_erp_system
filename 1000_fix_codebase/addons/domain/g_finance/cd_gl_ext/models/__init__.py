# cd_gl_ext models — M19 core.
from . import (
    coa_logic,
    fix_ap_takeon,
    fix_bank_takeon,
    fix_chart_loader,
    fix_fiscal_year_ext,
    fix_fx_revaluation,
    fix_gl_dimension_pnl,
    fix_gl_engine,
    fix_gl_ext,
    fix_gl_posting_control,
    fix_ledger_takeon,
    fix_legacy_ledger,
)

# isort: split
# imported last: these extend models defined above. The registry resolves
# _inherit in load order (Odoo 19 raises "does not exist in registry" when an
# extension meets its base first), so fix_gl_chain (extends
# fix.journal.posting.log of fix_gl_engine), the M19 capture pass-2 registers
# and the A10 invoice auto-file (2026-11-23, D-A10-2) load after every base
# they extend.
from . import fix_gl_capture, fix_gl_chain, fix_gl_recon
from . import fix_gl_autofile
