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
        # the one resolver every delivery path uses (download, email, here)
        from ..controllers import report_delivery

        return report_delivery.pack_function(module_key, report_key)

    def _build_artifact(self):
        """The branded artefact, built by the SAME function the download
        buttons and the send-by-email route use (report_delivery.build)."""
        from ..controllers import report_delivery

        self.ensure_one()
        if not self._pack_function(self.module_key, self.report_key):
            raise ValidationError(
                "Pack %s:%s disappeared from the registry" % (self.module_key, self.report_key)
            )
        return report_delivery.build(self.env, self.module_key, self.report_key, self.format, {})

    def action_deliver_now(self):
        """Send this subscription's pack now (also the cron body). Records
        the outcome honestly — an SMTP failure is a state, not an error."""
        from ..controllers import report_delivery, report_pdf

        self.ensure_one()
        art = self._build_artifact()
        emails, _err = report_delivery.parse_recipients(self.recipients)
        result = report_delivery.send_mail(
            self.env,
            emails,
            art["data"],
            art["filename"],
            art["title"],
            art["count"],
            body="Scheduled %s delivery of this report." % self.period,
        )
        report_delivery.log_export(
            self.env,
            "%s:%s" % (self.module_key, self.report_key),
            "distribution",
            self.format,
            art["count"],
            {"subscription": self.name},
        )
        stamp = report_pdf.local_now(self.env).strftime("%Y-%m-%d %H:%M")
        self.write(
            {
                "last_run": fields.Datetime.now(),
                "last_state": "%s (Dhaka): %s (%d rows)" % (stamp, result["state"], art["count"]),
                "delivery_count": self.delivery_count + 1,
            }
        )
        return {
            "mail_id": result["mail_id"],
            "state": result["state"],
            "attachment": result["attachment"],
            "rows": art["count"],
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
