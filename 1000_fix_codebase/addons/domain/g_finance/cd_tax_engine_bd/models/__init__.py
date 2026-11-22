# cd_tax_engine_bd models. Order matters: fix_tax_returns_a08 extends the
# models defined in fix_tax_returns; fix_tax_capture (2026-11-17 capture audit)
# extends fix.vat.return, so it is imported after both.
# fix_tax_master first: fix_tax_engine's VAT treatment inherits its
# statutory-master approval mixin.
# fix_tax_event_consumers (M51-F10) extends fix.vat.return AND fix.tax.notice
# (fix_tax_capture), so it is imported after both.
from . import fix_tax_master  # noqa: I001
from . import fix_tax_engine
from . import fix_tax_returns
from . import fix_tax_compliance
from . import fix_tax_returns_a08
from . import fix_salary_tds
from . import fix_withholding_report
from . import fix_tax_capture
from . import fix_tax_event_consumers
from . import return_logic
from . import statutory_format
from . import tax_logic
