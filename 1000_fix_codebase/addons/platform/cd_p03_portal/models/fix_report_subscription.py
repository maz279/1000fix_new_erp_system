# cd_p03_portal — scheduled branded report delivery (CoA report R5,
# NetSuite-style: a pack emailed as a PDF/Excel attachment on a schedule).
#
# Architectural note: this module holds "no models of its own" (AS-09) for
# DOMAIN data — this model is platform infrastructure that schedules the
# module's own report packs, not domain data, and lives here so it can
# never drift from the pack registry it delivers.
from __future__ import annotations

import datetime
import logging
import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PERIODS = {"daily": 1, "weekly": 7, "monthly": 30}


def _pack_registry():
    """The module REPORTS registry (imported lazily: controllers import
    odoo.http and must not load at module-import time of the model)."""
    from ..controllers import a02, a03, a04, a05, a06, a07, a08, a09, a10, a11, a12

    yield from (a08, a02, a03, a04, a05, a06, a07, a09, a10, a12, a11)


class FixReportSubscription(models.Model):
    _name = "fix.report.subscription"
    _description = "Scheduled Report Delivery (branded pack by email)"
    _inherit = ["mail.thread"]
    _order = "next_run"

    name = fields.Char(required=True, tracking=True)
    module_key = fields.Char(string="Module", required=True, help="Registry module code, e.g. M19")
    report_key = fields.Char(
        string="Report Pack", required=True, help="REPORTS key, e.g. close_sla"
    )
    format = fields.Selection(
        [("xlsx", "Excel workbook"), ("pdf", "PDF")], required=True, default="pdf"
    )
    recipients = fields.Char(
        required=True, tracking=True, help="Comma-separated email addresses (max 10)"
    )
    period = fields.Selection(
        [("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly")],
        required=True,
        default="weekly",
    )
    next_run = fields.Datetime(
        required=True,
        default=lambda self: fields.Datetime.now() + datetime.timedelta(hours=1),
    )
    last_run = fields.Datetime(readonly=True)
    last_state = fields.Char(readonly=True, tracking=True)
    delivery_count = fields.Integer(readonly=True)
    active = fields.Boolean(default=True)

    @api.constrains("module_key", "report_key")
    def _check_pack_exists(self):
        for sub in self:
            if not self._pack_function(sub.module_key, sub.report_key):
                raise ValidationError(
                    "No report pack %s:%s in the registry — the delivery would "
                    "always fail." % (sub.module_key, sub.report_key)
                )

    @api.constrains("recipients")
    def _check_recipients(self):
        for sub in self:
            emails = [e.strip() for e in re.split(r"[;,\s]+", sub.recipients or "") if e.strip()]
            bad = [e for e in emails if not _EMAIL.fullmatch(e)]
            if bad or not emails or len(emails) > 10:
                raise ValidationError(
                    "Recipients must be 1-10 valid email addresses (bad: %s)" % ", ".join(bad[:3])
                )

    @staticmethod
    def _pack_function(module_key, report_key):
        # MODULES maps the module code (e.g. 'M19') to its FRAGMENT; the
        # REPORTS registry lives on the fragment (a08.m19.REPORTS), not on
        # the area package itself.
        for mod in _pack_registry():
            inner = getattr(mod, "MODULES", {}).get(module_key)
            if inner is not None:
                fn = getattr(inner, "REPORTS", {}).get(report_key)
                if fn:
                    return fn
        return None

    def _build_attachment(self):
        """The branded artefact, built by the SAME shared byte-builder the
        download buttons and the send-by-email route use (report_bytes)."""
        import base64

        from ..controllers import report_bytes

        self.ensure_one()
        fn = self._pack_function(self.module_key, self.report_key)
        if not fn:
            raise ValidationError(
                "Pack %s:%s disappeared from the registry" % (self.module_key, self.report_key)
            )
        out = fn(self.env)
        cols = out.get("cols") or []
        labels = out.get("labels") or {}
        base_name = "%s_%s" % (self.module_key, self.report_key.replace("/", "_"))
        if self.format == "xlsx":
            data = report_bytes.xlsx_bytes(self.env, out, cols, labels, base_name, {})
        else:
            rows = list(out.get("rows") or [])
            totals = out.get("totals")
            if totals:
                rows.append({c: totals.get(c, "") for c in cols})
            payload = {"rows": rows, "cols": cols, "labels": labels, "count": len(rows)}
            data = report_bytes.pdf_bytes(self.env, payload, base_name, title=out.get("title"))
        attachment = self.env["ir.attachment"].create(
            {
                "name": "%s.%s" % (base_name, self.format),
                "datas": base64.b64encode(data).decode(),
                "public": False,
            }
        )
        return attachment, len(out.get("rows") or []), out.get("title") or base_name

    def action_deliver_now(self):
        """Send this subscription's pack now (also the cron body). Records
        the outcome honestly — an SMTP failure is a state, not an error."""
        import base64 as _b64  # noqa: F401  (kept for parity with the route)

        from ..controllers import brand as _brand

        self.ensure_one()
        attachment, row_count, title = self._build_attachment()
        emails = [e.strip() for e in re.split(r"[;,\s]+", self.recipients or "") if e.strip()]
        lh = _brand.letterhead(self.env)
        mail = self.env["mail.mail"].create(
            {
                "subject": "%s — %s (%s)"
                % (lh["name"], title, fields.Datetime.now().strftime("%Y-%m-%d")),
                "body_html": (
                    "<p>Scheduled delivery of the <b>%s</b> pack — %d rows, generated %s.</p>"
                    "<p style='color:#888;font-size:12px'>%s · %s</p>"
                    % (
                        title,
                        row_count,
                        fields.Datetime.now().strftime("%Y-%m-%d %H:%M"),
                        lh["name"] + " · " + _brand.ISO_BADGE,
                        lh["contact_line"],
                    )
                ),
                "email_to": ", ".join(emails),
                "auto_delete": False,
                "attachment_ids": [(6, 0, [attachment.id])],
            }
        )
        try:
            mail.send(raise_exception=False)
        except Exception:
            _logger.exception("scheduled delivery %s send failed", self.name)
        self.write(
            {
                "last_run": fields.Datetime.now(),
                "last_state": "%s: %s (%d rows)"
                % (fields.Datetime.now().strftime("%Y-%m-%d %H:%M"), mail.state, row_count),
                "delivery_count": self.delivery_count + 1,
            }
        )
        return {
            "mail_id": mail.id,
            "state": mail.state,
            "attachment": attachment.name,
            "rows": row_count,
        }

    @api.model
    def action_deliver_due(self):
        """Cron entry: deliver every due subscription and reschedule."""
        now = fields.Datetime.now()
        due = self.search([("active", "=", True), ("next_run", "<=", now)])
        delivered = 0
        for sub in due:
            try:
                sub.action_deliver_now()
                delivered += 1
            except Exception:
                _logger.exception("scheduled delivery failed for %s", sub.name)
            delta = datetime.timedelta(days=_PERIODS[sub.period])
            sub.write({"next_run": sub.next_run + delta if sub.next_run > now else now + delta})
        _logger.info("scheduled report delivery: %d of %d due sent", delivered, len(due))
        return delivered
