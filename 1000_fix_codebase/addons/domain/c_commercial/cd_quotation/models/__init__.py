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

# M36 capture pass 2 (19 Nov 2026): extends fix.quotation, fix.tender and
# fix.estimate after every file above defines them.
# isort: split
from . import fix_quote_capture2, fix_quote_capture3
