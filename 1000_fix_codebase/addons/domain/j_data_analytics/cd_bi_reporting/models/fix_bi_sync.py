# fix_bi_sync — M25: Power BI sync configuration + the aggregate snapshot
# engine. Snapshots are REAL read_group aggregates over the live service
# order / estimate / AR invoice tables; the external transport fails closed
# until operator credentials are provisioned (estate policy: never fake an
# outbound integration).
import json
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

OPEN_ORDER_STATES = (
    "draft",
    "intake",
    "diagnostic",
    "estimate_pending",
    "estimate_sent",
    "awaiting_approval",
    "approved",
    "in_repair",
    "qc_pending",
    "qc_failed",
    "ready",
)
ISSUED_INVOICE_STATES = ("issued", "paid")


class FixBiSyncConfig(models.Model):
    """M25: one outbound analytics-sync configuration."""

    _name = "fix.bi.sync.config"
    _description = "BI Sync Configuration"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    dataset_scope = fields.Selection(
        [
            ("exec_kpi", "Executive KPI Dataset"),
            ("service_ops", "Service Operations Dataset"),
            ("finance", "Finance & Revenue Dataset"),
            ("full", "Full Warehouse Dataset"),
        ],
        required=True,
        default="exec_kpi",
    )
    sync_frequency = fields.Selection(
        [("hourly", "Hourly"), ("daily", "Daily"), ("weekly", "Weekly")],
        required=True,
        default="daily",
    )
    target_workspace = fields.Char(
        string="Target Workspace",
        help="Descriptive name of the external workspace. The outbound "
        "transport stays DISABLED until operator credentials are provisioned.",
    )
    enabled = fields.Boolean(default=True)
    last_test_status = fields.Selection(
        [("never", "Not Tested"), ("ok", "Configuration Valid"), ("fail", "Configuration Invalid")],
        default="never",
        readonly=True,
    )
    last_test_note = fields.Char(readonly=True)
    notes = fields.Text()
    log_ids = fields.One2many("fix.bi.sync.log", "config_id", string="Sync Runs")
    last_sync_at = fields.Datetime(compute="_compute_last_sync", store=True)

    def _bi_company_domain(self, model):
        """Company-wide reads follow the A08 pattern: sudo + explicit company."""
        companies = self.env.companies.ids
        if "company_id" in self.env[model]._fields:
            return [("company_id", "in", companies)]
        return []

    def _compute_snapshot_metrics(self):
        """REAL aggregates for the snapshot — every number is measured."""
        self.ensure_one()
        orders = self.env["fix.service.order"]
        estimates = self.env["fix.estimate"]
        invoices = self.env["fix.ar.invoice"]
        today = fields.Date.today()
        month_start = today.replace(day=1)
        open_domain = [
            ("state", "in", list(OPEN_ORDER_STATES)),
            *self._bi_company_domain("fix.service.order"),
        ]
        approved_domain = [
            ("state", "=", "approved"),
            ("create_date", ">=", fields.Datetime.to_datetime(month_start)),
            *self._bi_company_domain("fix.estimate"),
        ]
        invoice_domain = [
            ("state", "in", list(ISSUED_INVOICE_STATES)),
            ("invoice_date", ">=", month_start),
            *self._bi_company_domain("fix.ar.invoice"),
        ]
        revenue_mtd = sum(estimates.search(approved_domain).mapped("grand_total"))
        invoice_records = invoices.search(invoice_domain)
        return {
            "orders_open": orders.search_count(open_domain),
            "orders_in_repair": orders.search_count(
                [("state", "=", "in_repair"), *self._bi_company_domain("fix.service.order")]
            ),
            "estimates_approved_mtd": estimates.search_count(approved_domain),
            "revenue_approved_mtd": revenue_mtd,
            "invoices_issued_mtd": len(invoice_records),
            "invoice_taxable_mtd": sum(invoice_records.mapped("taxable_amount")),
        }

    def action_test_connection(self):
        """Validate the configuration honestly: completeness of the local
        setup. External reachability is NOT claimed — transport stays closed
        until operator credentials exist (fail-closed by design)."""
        for rec in self:
            problems = []
            if not rec.enabled:
                problems.append("config is disabled")
            if not rec.sync_frequency:
                problems.append("no frequency set")
            if not rec.dataset_scope:
                problems.append("no dataset scope set")
            if problems:
                rec.last_test_status = "fail"
                rec.last_test_note = "Invalid: " + ", ".join(problems)
            else:
                rec.last_test_status = "ok"
                rec.last_test_note = (
                    "Configuration valid; external transport activates with "
                    "operator credentials (fail-closed)"
                )
        return True

    def action_run_sync(self):
        """Run a REAL aggregate snapshot now and log it. This is the internal
        warehouse refresh that feeds the BI Data Freshness KPI — not a
        simulated external push."""
        log_model = self.env["fix.bi.sync.log"].sudo()
        ran = 0
        for rec in self:
            if not rec.enabled:
                raise UserError("Sync '%s' is disabled — enable it before running." % rec.name)
            metrics = rec._compute_snapshot_metrics()
            log_model.create(
                {
                    "config_id": rec.id,
                    "dataset_scope": rec.dataset_scope,
                    "status": "success",
                    "snapshot_json": json.dumps(metrics, default=str, sort_keys=True),
                }
            )
            ran += 1
        _logger.info("M25 BI sync: %d snapshot(s) recorded", ran)
        return True


class FixBiSyncLog(models.Model):
    """M25: one measured snapshot per run — the freshness source of truth."""

    _name = "fix.bi.sync.log"
    _description = "BI Sync Run"
    _order = "ran_at desc, id desc"

    config_id = fields.Many2one("fix.bi.sync.config", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="config_id.company_id", store=True)
    dataset_scope = fields.Selection(related="config_id.dataset_scope")
    ran_at = fields.Datetime(default=fields.Datetime.now, required=True)
    status = fields.Selection(
        [("success", "Success"), ("failed", "Failed")], default="success", required=True
    )
    snapshot_json = fields.Text(string="Snapshot (JSON)")
    notes = fields.Char()

    @api.model
    def freshness_minutes(self):
        """Minutes since the newest successful snapshot — drives the M25 KPI.
        Returns None when no snapshot exists (rendered as an honest '—')."""
        newest = self.sudo().search([("status", "=", "success")], order="ran_at desc", limit=1)
        if not newest or not newest.ran_at:
            return None
        delta = fields.Datetime.now() - newest.ran_at
        return max(0, int(delta.total_seconds() // 60))
