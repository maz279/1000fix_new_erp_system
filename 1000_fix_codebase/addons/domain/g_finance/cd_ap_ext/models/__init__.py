# cd_ap_ext models.
# ruff: noqa: I001 - fix_ap_capture extends the bill and the payment run, so it
# is imported after them (an _inherit before its _name fails to load).
from . import (
    ap_gl,
    fix_ap_controls,
    fix_ap_expense,
    fix_ap_ext,
    fix_ap_notes,
    fix_ap_payee_bank,
    fix_ap_payment_events,
    fix_ap_payment_run,
    fix_ap_supplier_advance,
    fix_ap_tax_ext,
    fix_ap_tax_profile,
    fix_withholding_certificate_ext,
    fix_ap_capture,
)
