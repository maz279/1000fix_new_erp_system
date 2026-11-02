# fix.account + fix.account.stakeholder — the B2B Key Account master (M07).
#
# The A03 zero-trust audit (2026-10-31) found the whole KAM deliverable —
# account overview, tier, health, ACV, stakeholder matrix, QBR cadence and
# profitability grade — specified but never built. fix_account.py defined only
# fix.account.assignment and fix.account.plan, so M07-form-account had no
# model behind it and the workspace listed assignments where operators
# expected accounts.
#
# Ownership is NOT duplicated here: BRU-CRM-08 keeps it on the assignment, and
# this model follows the current one.
from odoo import api, fields, models


class FixAccount(models.Model):
    """The firmographic and commercial record for one corporate party."""

    _name = "fix.account"
    _description = "B2B Key Account"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "acv_bdt desc, id desc"
    _partner_unique = models.Constraint(
        "UNIQUE (partner_id)", "One key-account record per corporate party"
    )

    QBR_DUE_DAYS = 90
    QBR_AT_RISK_DAYS = 105

    partner_id = fields.Many2one(
        "res.partner", string="Corporate Party", required=True, index=True, ondelete="cascade"
    )
    name = fields.Char(related="partner_id.name", store=True, string="Account Name")
    account_code = fields.Char(string="Account Code", index=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )

    industry_vertical = fields.Selection(
        [
            ("banking", "Banking & NBFI"),
            ("telecom", "Telecom"),
            ("healthcare", "Healthcare"),
            ("education", "Education"),
            ("government", "Government & Ministry"),
            ("retail", "Retail & FMCG"),
            ("garments", "RMG & Textiles"),
            ("it_services", "IT & Software Services"),
            ("other", "Other"),
        ],
        string="Industry Vertical",
        default="other",
        required=True,
        tracking=True,
    )
    tier = fields.Selection(
        [
            ("strategic", "Strategic"),
            ("enterprise", "Enterprise"),
            ("growth", "Growth"),
        ],
        string="Account Tier",
        default="growth",
        required=True,
        tracking=True,
    )
    health_rating = fields.Selection(
        [
            ("healthy", "Healthy"),
            ("neutral", "Neutral"),
            ("at_risk", "At Risk"),
            ("critical", "Critical"),
        ],
        string="Account Health",
        default="neutral",
        required=True,
        tracking=True,
    )
    acv_bdt = fields.Monetary(
        string="Annual Contract Value", currency_field="currency_id", tracking=True
    )
    office_address = fields.Char(string="Head Office Address")

    assignment_id = fields.Many2one(
        "fix.account.assignment",
        string="Current Assignment",
        compute="_compute_assignment",
        help="BRU-CRM-08 keeps ownership on the assignment; this follows the latest.",
    )
    user_id = fields.Many2one(
        "res.users", string="Key Account Manager", compute="_compute_assignment"
    )
    stakeholder_ids = fields.One2many(
        "fix.account.stakeholder", "account_id", string="Decision Makers"
    )

    last_qbr_date = fields.Date(string="Last QBR", compute="_compute_qbr", store=True)
    days_since_qbr = fields.Integer(string="Days Since QBR", compute="_compute_qbr", store=True)
    qbr_overdue = fields.Boolean(string="QBR Overdue", compute="_compute_qbr", store=True)

    gross_margin_pct = fields.Float(string="Gross Margin (%)", tracking=True)
    account_grade = fields.Selection(
        [("a_plus", "A+"), ("a", "A"), ("b", "B"), ("c", "C")],
        string="Profitability Grade",
        compute="_compute_grade",
        store=True,
    )

    def _compute_assignment(self):
        Assignment = self.env["fix.account.assignment"]
        for rec in self:
            latest = Assignment.search(
                [("partner_id", "=", rec.partner_id.id)],
                order="effective_from desc, id desc",
                limit=1,
            )
            rec.assignment_id = latest
            rec.user_id = latest.owner_id

    @api.depends("partner_id", "tier")
    def _compute_qbr(self):
        """REQ-07.4: Strategic and Enterprise accounts need a QBR every 90 days."""
        Qbr = self.env["fix.qbr"]
        today = fields.Date.today()
        for rec in self:
            # A QBR counts only once it has actually been HELD; a scheduled
            # one that never happened is exactly the churn signal REQ-07.4 is
            # written to catch.
            last = Qbr.search(
                [
                    ("partner_id", "=", rec.partner_id.id),
                    ("state", "=", "held"),
                    ("held_on", "!=", False),
                ],
                order="held_on desc, id desc",
                limit=1,
            )
            meeting_on = last.held_on if last else False
            rec.last_qbr_date = meeting_on
            rec.days_since_qbr = (today - meeting_on).days if meeting_on else 0
            rec.qbr_overdue = bool(
                rec.tier in ("strategic", "enterprise")
                and (not meeting_on or rec.days_since_qbr > rec.QBR_DUE_DAYS)
            )

    @api.depends("gross_margin_pct")
    def _compute_grade(self):
        for rec in self:
            margin = rec.gross_margin_pct or 0.0
            if margin >= 35.0:
                rec.account_grade = "a_plus"
            elif margin >= 25.0:
                rec.account_grade = "a"
            elif margin >= 15.0:
                rec.account_grade = "b"
            else:
                rec.account_grade = "c"

    @api.model
    def cron_flag_qbr_at_risk(self):
        """REQ-07.4: no QBR inside 105 days flags the account and alerts the CCO."""
        flagged = 0
        for rec in self.search([("tier", "in", ("strategic", "enterprise"))]):
            overdue = rec.days_since_qbr if rec.last_qbr_date else self.QBR_AT_RISK_DAYS + 1
            if overdue <= self.QBR_AT_RISK_DAYS:
                continue
            if rec.health_rating != "at_risk":
                rec.health_rating = "at_risk"
                rec.message_post(
                    body="No Quarterly Business Review in %d days — flagged At Risk "
                    "and escalated to the Chief Commercial Officer (REQ-07.4)." % overdue
                )
            flagged += 1
        return flagged


class FixAccountStakeholder(models.Model):
    """REQ-07.x Tab 2: who actually decides inside a corporate account."""

    _name = "fix.account.stakeholder"
    _description = "Key Account Stakeholder"
    _order = "buying_role, name"

    account_id = fields.Many2one(
        "fix.account", string="Key Account", required=True, index=True, ondelete="cascade"
    )
    partner_id = fields.Many2one("res.partner", string="Contact Record", ondelete="set null")
    name = fields.Char(required=True)
    designation = fields.Char(string="Corporate Designation")
    buying_role = fields.Selection(
        [
            ("economic_buyer", "Economic Buyer"),
            ("technical_evaluator", "Technical Evaluator"),
            ("user_buyer", "User Buyer"),
            ("coach", "Coach"),
            ("gatekeeper", "Gatekeeper"),
        ],
        required=True,
        default="user_buyer",
    )
    phone = fields.Char()
    email = fields.Char()
    sentiment = fields.Selection(
        [
            ("champion", "Champion"),
            ("supportive", "Supportive"),
            ("neutral", "Neutral"),
            ("detractor", "Detractor"),
        ],
        default="neutral",
        string="Engagement Sentiment",
    )
    notes = fields.Text()
