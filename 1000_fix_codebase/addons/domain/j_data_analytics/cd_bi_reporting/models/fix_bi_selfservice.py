# M25 self-service BI configuration: saved dashboards, scheduled
# distribution and threshold alerts. These are CONFIGURATION records — the
# dashboards themselves render live from /p03/bi/*; distribution transport
# and alert dispatch are porting phase and are never simulated here.
from odoo import fields, models

DASHBOARD_ROLES = [
    ("all", "All Roles"),
    ("ceo", "CEO"),
    ("coo", "COO / Operations"),
    ("cfo", "CFO / Finance"),
    ("cco", "CCO / Commercial"),
    ("service", "Service"),
    ("finance", "Finance Analytics"),
    ("people", "People"),
    ("quality", "Quality"),
]


class FixBiDashboard(models.Model):
    """A saved dashboard definition (name, target role, layout contract)."""

    _name = "fix.bi.dashboard"
    _description = "Saved BI Dashboard"
    _order = "role, name"

    name = fields.Char(required=True)
    role = fields.Selection(DASHBOARD_ROLES, required=True, default="all", index=True)
    description = fields.Text()
    is_shared = fields.Boolean(
        help="Shared dashboards are visible to every internal user of the company."
    )
    owner_id = fields.Many2one(
        "res.users", required=True, default=lambda self: self.env.user, index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    sections_json = fields.Text(
        string="Layout (JSON)",
        help="Self-service layout contract: ordered KPI/report sections. "
        "An empty value means the dashboard uses its role's standard pack.",
    )
    last_viewed_at = fields.Datetime(readonly=True)


class FixBiDistributionSchedule(models.Model):
    """A scheduled distribution of one report pack (cadence + recipients)."""

    _name = "fix.bi.distribution.schedule"
    _description = "BI Distribution Schedule"
    _order = "name"

    name = fields.Char(required=True)
    report_key = fields.Char(
        required=True,
        help="The report to distribute, as module:report (e.g. M25:branch_league).",
    )
    cadence = fields.Selection(
        [("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly")],
        required=True,
        default="weekly",
    )
    recipients = fields.Char(
        required=True, help="Comma-separated e-mail addresses of the recipients."
    )
    format = fields.Selection(
        [("csv", "CSV"), ("pdf", "PDF"), ("xlsx", "XLSX")],
        required=True,
        default="csv",
    )
    active = fields.Boolean(default=True)
    last_sent_at = fields.Datetime(readonly=True)
    last_status = fields.Selection(
        [("never", "Never Sent"), ("sent", "Sent"), ("failed", "Failed")],
        required=True,
        default="never",
        readonly=True,
    )
    note = fields.Char(
        help="Scheduler transport is porting phase — a schedule is configuration "
        "until the distribution worker is provisioned."
    )


class FixBiAlertSubscription(models.Model):
    """A threshold alert on any KPI metric key."""

    _name = "fix.bi.alert.subscription"
    _description = "BI Threshold Alert"
    _order = "name"

    name = fields.Char(required=True)
    metric_key = fields.Char(
        required=True, help="KPI key to watch, e.g. overdue_gt_60d or ar_invoices_mtd."
    )
    comparator = fields.Selection(
        [("gt", "Greater than"), ("lt", "Less than")], required=True, default="gt"
    )
    threshold = fields.Float(required=True)
    recipients = fields.Char(required=True, help="Comma-separated e-mail addresses.")
    active = fields.Boolean(default=True)
    last_value = fields.Float(readonly=True)
    last_checked_at = fields.Datetime(readonly=True)
    last_fired_at = fields.Datetime(readonly=True)
    note = fields.Char(
        help="The watched metric is visible live on the role dashboards; outbound "
        "notification transport is porting phase and is never simulated."
    )
