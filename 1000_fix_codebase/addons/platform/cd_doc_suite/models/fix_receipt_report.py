"""The 80 mm thermal receipt (owner request 18 Nov 2026: "build the 80 mm
thermal receipt too, beside the A4 print").

A thermal roll has no page length: the receipt's page height is computed from
its content and handed to wkhtmltopdf through `data-report-page-height` on
the <html> tag (web.report_layout extended in report_receipt_80mm.xml), so a
two-line cash memo prints short and a twenty-line invoice prints long, with
no blank paper and no page break in the middle of a receipt.
"""

from datetime import datetime

import pytz
from odoo import models

DHAKA = pytz.timezone("Asia/Dhaka")

# Millimetres of 80 mm roll, measured on rendered receipts (18 Nov 2026:
# a 2-line memo ends at 77 mm, a 5-line repair at 92 mm), plus a tear-off
# margin. Generous by ~15 mm rather than ever cutting a receipt short.
BASE_MM = 44  # letterhead, title, customer block, totals box, words, footer
LINE_MM = 5  # one priced line: description row + qty x price / VAT row
WRAP_MM = 3  # a description that wraps to a second row
SERIAL_MM = 2
META_MM = 3.5
SECTION_MM = 4
NOTE_MM = 5
POLICY_MM = 8
TEAR_MM = 6
MIN_MM = 80
MAX_MM = 2000


class IrActionsReportReceipt(models.Model):
    _inherit = "ir.actions.report"

    def _build_wkhtmltopdf_args(
        self,
        paperformat_id,
        landscape,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        args = super()._build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
        height = (specific_paperformat_args or {}).get("data-report-page-height")
        if height and "--page-height" in args:
            try:
                mm = min(max(int(float(height)), MIN_MM), MAX_MM)
            except (TypeError, ValueError):
                return args
            args[args.index("--page-height") + 1] = "%smm" % mm
        return args


class FixDocPrintReceipt(models.AbstractModel):
    _inherit = "fix.doc.print.mixin"

    def _fix_receipt_payload(self):
        """The A4 payload, plus what only a receipt prints."""
        self.ensure_one()
        p = dict(self._fix_print_payload())
        p["printed_at"] = datetime.now(pytz.utc).astimezone(DHAKA).strftime("%d-%b-%Y %I:%M %p")
        p["printed_by"] = self.env.user.name
        return p

    def _fix_receipt_height_mm(self):
        self.ensure_one()
        p = self._fix_print_payload()
        lines = p.get("lines") or []
        priced = [ln for ln in lines if "sl" in ln]
        mm = BASE_MM + TEAR_MM + LINE_MM * len(priced)
        mm += WRAP_MM * sum(1 for ln in priced if len(ln.get("description") or "") > 34)
        mm += SERIAL_MM * sum(1 for ln in priced if ln.get("serial"))
        mm += SECTION_MM * (len(lines) - len(priced))
        mm += NOTE_MM * min(len(p.get("notes") or []), 3)
        mm += META_MM * len(p.get("meta") or [])
        if p.get("policy"):
            mm += POLICY_MM
        if p.get("service_item"):
            mm += META_MM
        address = (p.get("company") or {}).get("address") or ""
        if address:  # the seller address line under the name: ~44 characters a row
            mm += WRAP_MM * (1 + len(address) // 44)
        return int(round(mm))

    def _fix_receipt_page_height(self):
        """One height for the whole print job (several receipts print as
        several pages of the tallest one)."""
        return max([rec._fix_receipt_height_mm() for rec in self] or [MIN_MM])
