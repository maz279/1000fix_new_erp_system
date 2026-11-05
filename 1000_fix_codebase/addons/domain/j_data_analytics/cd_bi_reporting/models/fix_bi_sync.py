# fix_bi_sync — M25: the aggregate snapshot engine. Snapshots are REAL
# read_group aggregates over the live service order / estimate / AR invoice
# tables; the external transport fails closed until operator credentials
# are provisioned (estate policy: never fake an outbound integration).
#
# A11 audit E7 (M25-4/-5/-10): a snapshot run is an OPERATOR act — gated on
# the BI operator group, stamped with who ran it, computed under the
# configuration's own company scope (not the runner's OU rules), logged
# immutably, and refreshed by a cron so freshness never depends on a manual
# click.
import json
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

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

OPERATOR_GROUP = "cd_bi_reporting.group_bi_operator"


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
        "transport stays DISABLED until operator credentials are provisioned; "
        "this configuration today defines the INTERNAL snapshot dataset only.",
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

    def _require_operator(self):
        """E7: running a snapshot is an operator act, not a click for every
        internal user. The cron (superuser) and the engine may pass through."""
        if self.env.su:
            return
        if not self.env.user.has_group(OPERATOR_GROUP):
            raise UserError(
                _(
                    "Running a BI snapshot is reserved for BI Sync Operators "
                    "(M25) — your snapshot run was refused. Ask the BI team."
                )
            )

    def _snapshot_env(self):
        """E7: the snapshot is computed under the CONFIGURATION's company
        scope, explicitly — never under the runner's own OU record rules, so
        a clerk cannot publish an OU-sized picture as the company dataset."""
        return self.with_context(allowed_company_ids=self.company_id.ids).sudo().env

    def _compute_snapshot_metrics(self):
        """REAL aggregates for the snapshot — every number is measured."""
        self.ensure_one()
        env = self._snapshot_env()
        orders = env["fix.service.order"]
        estimates = env["fix.estimate"]
        invoices = env["fix.ar.invoice"]
        company = [("company_id", "=", self.company_id.id)]
        today = fields.Date.today()
        month_start = today.replace(day=1)
        open_domain = [("state", "in", list(OPEN_ORDER_STATES)), *company]
        approved_domain = [
            ("state", "=", "approved"),
            ("create_date", ">=", fields.Datetime.to_datetime(month_start)),
            *company,
        ]
        invoice_domain = [
            ("state", "in", list(ISSUED_INVOICE_STATES)),
            ("invoice_date", ">=", month_start),
            *company,
        ]
        delivered_domain = [
            ("state", "in", ("delivered", "closed")),
            "|",
            ("delivered_at", ">=", fields.Datetime.to_datetime(month_start)),
            ("closed_at", ">=", fields.Datetime.to_datetime(month_start)),
            *company,
        ]
        revenue_mtd = sum(estimates.search(approved_domain).mapped("grand_total"))
        invoice_records = invoices.search(invoice_domain)
        return {
            "orders_open": orders.search_count(open_domain),
            "orders_in_repair": orders.search_count([("state", "=", "in_repair"), *company]),
            "orders_delivered_mtd": orders.search_count(delivered_domain),
            "estimates_approved_mtd": estimates.search_count(approved_domain),
            "quotes_value_mtd": revenue_mtd,
            "invoices_issued_mtd": len(invoice_records),
            "invoice_taxable_mtd": sum(invoice_records.mapped("taxable_amount")),
        }

    @api.depends("log_ids.ran_at")
    def _compute_last_sync(self):
        for rec in self:
            newest = rec.log_ids.sorted("ran_at")[-1:] if rec.log_ids else rec.log_ids.browse()
            rec.last_sync_at = newest.ran_at if newest else False

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
        """Run a REAL aggregate snapshot now and log it. E7: operator-gated,
        company-scoped, and stamped with WHO ran it — the internal warehouse
        refresh that feeds the BI Data Freshness KPI, never a simulated
        external push."""
        self._require_operator()
        return self._run_snapshot()

    def _run_snapshot(self):
        """The measured core, shared by the operator button and the cron."""
        log_model = self.env["fix.bi.sync.log"].sudo()
        ran = 0
        for rec in self:
            if not rec.enabled:
                raise UserError(_("Sync '%s' is disabled — enable it before running.") % rec.name)
            metrics = rec._compute_snapshot_metrics()
            log_model.create(
                {
                    "config_id": rec.id,
                    "dataset_scope": rec.dataset_scope,
                    "status": "success",
                    "ran_by": self.env.user.id,
                    "snapshot_json": json.dumps(metrics, default=str, sort_keys=True),
                }
            )
            ran += 1
        _logger.info("M25 BI sync: %d snapshot(s) recorded (by %s)", ran, self.env.user.login)
        return True

    @api.model
    def _cron_run_enabled(self):
        """M25-5: freshness must not depend on a manual click — the cron
        refreshes every enabled configuration daily (as the system user)."""
        enabled = self.sudo().search([("enabled", "=", True)])
        ran = 0
        for rec in enabled:
            try:
                rec._run_snapshot()
                ran += 1
            except UserError as exc:
                _logger.warning("M25 BI sync cron skipped %s: %s", rec.display_name, exc)
        _logger.info("M25 BI sync cron: %d snapshot(s)", ran)
        return ran


class FixBiSyncLog(models.Model):
    """M25: one measured snapshot per run — the freshness source of truth.

    A11 audit M25-10: append-only. Nobody rewrites a measured snapshot — not
    the operator, not admin (the old log could be edited to 2030 and freeze
    freshness at '0 min' forever)."""

    _name = "fix.bi.sync.log"
    _description = "BI Sync Run"
    _order = "ran_at desc, id desc"

    config_id = fields.Many2one("fix.bi.sync.config", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="config_id.company_id", store=True)
    dataset_scope = fields.Selection(related="config_id.dataset_scope")
    ran_at = fields.Datetime(default=fields.Datetime.now, required=True)
    ran_by = fields.Many2one(
        "res.users",
        string="Run By",
        readonly=True,
        index=True,
        ondelete="restrict",
        help="E7: who ran the snapshot — the operator button stamps the "
        "clicker, the cron stamps the system user.",
    )
    status = fields.Selection(
        [("success", "Success"), ("failed", "Failed")], default="success", required=True
    )
    snapshot_json = fields.Text(string="Snapshot (JSON)")
    notes = fields.Char()

    def write(self, vals):
        raise UserError(
            _("A BI sync log row is append-only (M25-10) — a measured snapshot is never rewritten.")
        )

    def unlink(self):
        raise UserError(
            _("A BI sync log row is append-only (M25-10) — a measured snapshot is never deleted.")
        )

    @api.model
    def freshness_minutes(self, companies=None):
        """M25-5: minutes since the newest successful snapshot IN THE
        CALLER'S COMPANIES — one company's run no longer makes another
        company read 'fresh'. Returns None when none exists (rendered '—')."""
        domain = [("status", "=", "success")]
        company_ids = companies if companies is not None else self.env.companies.ids
        if company_ids:
            domain.append(("company_id", "in", list(company_ids)))
        newest = self.sudo().search(domain, order="ran_at desc", limit=1)
        if not newest or not newest.ran_at:
            return None
        delta = fields.Datetime.now() - newest.ran_at
        return max(0, int(delta.total_seconds() // 60))
