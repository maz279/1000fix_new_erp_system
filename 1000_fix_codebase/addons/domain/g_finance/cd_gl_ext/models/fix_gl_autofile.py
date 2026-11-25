# fix_gl_autofile — M24 finance auto-file (A10 deep audit 2026-11-23, D-A10-2).
#
# "Every transaction auto-files" was the registry's claim; the operational
# modules honoured it (8 producers through fix.document.attach) but MONEY
# MOVEMENT did not: a posted customer or vendor invoice left no governed
# document behind, so retention classes, legal holds, integrity seals and the
# access log (the whole M24 control set) never applied to VAT evidence.
#
# This bridge files the posted invoice's own PDF into the repository, once
# per move. It hooks account.move._post (the single posting method every
# engine path funnels through) rather than each caller; the idempotency guard
# makes a repeat call a no-op. Rendering failures never block posting: the
# move gets a chatter note and the nightly backfill retries.
import base64
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

INVOICE_MOVE_TYPES = ("out_invoice", "out_refund", "in_invoice", "in_refund")
RETENTION_CODE = "FIN-7Y"
REPORT_REF = "account.account_invoices"
AUTFILE_MARK = ("res_model", "=", "account.move")


class AccountMoveAutoFile(models.Model):
    _inherit = "account.move"

    def _fix_document_exists(self) -> bool:
        self.ensure_one()
        return bool(
            self.env["fix.document"]
            .sudo()
            .search_count(
                [
                    ("res_model", "=", "account.move"),
                    ("res_id", "=", self.id),
                    ("document_type", "=", "invoice"),
                ]
            )
        )

    def _fix_render_invoice_bytes(self) -> tuple[bytes, str]:
        """The invoice's own bytes: PDF when wkhtmltopdf answers, HTML as the
        honest fallback (a snapshot that still carries the whole document)."""
        report = self.env["ir.actions.report"].sudo()
        try:
            pdf, _kind = report._render_qweb_pdf(REPORT_REF, self.ids)
            if pdf:
                return pdf, "pdf"
        except Exception as exc:  # rendering must never block the posting
            _logger.warning("M24 auto-file: PDF render failed for %s: %s", self.name, exc)
        html, _kind = report._render_qweb_html(REPORT_REF, self.ids)
        return html, "html"

    def _fix_autofile_invoice_document(self):
        """File the posted invoice once. Returns the document or False."""
        self.ensure_one()
        if self.move_type not in INVOICE_MOVE_TYPES or self.state != "posted":
            return False
        if self._fix_document_exists():
            return False
        payload, kind = self._fix_render_invoice_bytes()
        retention = (
            self.env["fix.retention.class"].sudo().search([("code", "=", RETENTION_CODE)], limit=1)
        )
        partner = self.partner_id.display_name or ""
        name = "%s — %s.%s" % (self.name, partner, kind)
        doc = (
            self.env["fix.document"]
            .with_company(self.company_id)
            .sudo()
            .attach(
                name=name[:200],
                datas=base64.b64encode(payload),
                document_type="invoice",
                res_model="account.move",
                res_id=self.id,
                retention_class_id=retention.id if retention else None,
            )
        )
        if kind != "pdf":
            doc.message_post(
                body="Filed as HTML: the PDF renderer was unavailable at posting time. "
                "Re-post cannot regenerate it; print the invoice and replace the document "
                "if a PDF original is required."
            )
        self.message_post(
            body="Filed in the document repository (M24): %s, retention %s."
            % (doc.name, retention.code if retention else "unclassified")
        )
        return doc

    def _fix_missing_invoice_documents(self) -> int:
        """Backfill: every posted invoice without its governed document."""
        moves = self.sudo().search(
            [
                ("move_type", "in", INVOICE_MOVE_TYPES),
                ("state", "=", "posted"),
            ]
        )
        filed = 0
        for move in moves:
            if move._fix_autofile_invoice_document():
                filed += 1
        return filed

    @api.model
    def cron_autofile_invoices(self):
        """Nightly convergence: an invoice posted while the renderer was down
        (or before this bridge shipped) is filed on the next run."""
        filed = self.sudo()._fix_missing_invoice_documents()
        if filed:
            _logger.info("M24 auto-file: filed %d missing invoice document(s)", filed)
        return True

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        for move in posted:
            try:
                with self.env.cr.savepoint():
                    move._fix_autofile_invoice_document()
            except Exception as exc:  # never let the archive block the ledger
                _logger.warning("M24 auto-file skipped for %s: %s", move.name, exc)
                move.message_post(
                    body="M24 auto-file skipped: %s. The nightly backfill retries." % exc
                )
        return posted
