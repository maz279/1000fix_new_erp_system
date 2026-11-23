# cd_quotation models.
from . import (
    fix_commercial_documents,
    fix_quotation,
    fix_quote_ops,
    fix_quote_scope,
    fix_quote_supply,
    fix_quote_template,
    fix_quote_with_customer,
    fix_tender,
    fix_tender_boq,
)

# M11 capture pass 2 (18 Nov 2026): extends fix.discount.approval, so it loads last.
# isort: split
from . import fix_discount_reason

# A04 ERP audit (20 Nov 2026, B2): quotation / tender money; extends the
# quotation, its lines and billing plan, the tender, its bonds and variations
# and the invoice. Capture passes 2 and 3 stay last (they extend all of these).
# isort: split
from . import fix_a04_quote_money

# M36 capture pass 2 (19 Nov 2026): extends fix.quotation, fix.tender and
# fix.estimate after every file above defines them.
# isort: split
from . import fix_quote_capture2, fix_quote_capture3

# A10 deep audit (2026-11-23, D-A10-4): the M24 envelope route for quote e-sign.
from . import fix_quote_m24_esign
