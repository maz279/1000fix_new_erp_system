# fix.account.assignment + fix.account.plan — account management (M07,
# FR-CRM-026…030). BRU-CRM-08: every corporate/dealer/government account has
# a named owner at all times; the plan is institutional memory that survives
# the account manager's departure.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixAccountAssignment(models.Model):
    """Ownership of a party as a sales account."""

    _name = "fix.account.assignment"
    _description = "Account Assignment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "effective_from desc, id desc"
    # Odoo 19 constraint attribute form
    _partner_unique = models.Constraint(
        "UNIQUE (partner_id, effective_from)",
        "One assignment per party per effective date",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Account",
        required=True,
        index=True,
        ondelete="cascade",
        domain=["|", ("customer_rank", ">", 0), ("role_ids", "!=", False)],
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Account Manager",
        required=True,
        tracking=True,
        help="BRU-CRM-08: every corporate, dealer and government account has a "
        "named owner at all times",
    )
    assignment_type = fields.Selection(
        [
            ("territory", "Territory Coverage"),
            ("account", "Named Account"),
            ("dedicated", "Dedicated Manager (FR-CRM-027)"),
        ],
        string="Assignment Type",
        default="account",
        required=True,
        tracking=True,
    )
    dedicated = fields.Boolean(
        string="Dedicated Manager",
        compute="_compute_dedicated",
        store=True,
        help="Set when the account crosses the published eligibility criteria "
        "(Q-01 open with the CCO — the criteria threshold is configuration)",
    )
    effective_from = fields.Date(string="Effective From", default=fields.Date.today, required=True)
    effective_to = fields.Date(string="Effective To", help="Empty = current owner")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("assignment_type")
    def _compute_dedicated(self):
        for assignment in self:
            assignment.dedicated = assignment.assignment_type == "dedicated"

    @api.model
    def action_assign_unowned(self, default_owner_id=None):
        """BRU-CRM-08 safety net: give every active party-account an owner.
        Returns the number of coverage gaps closed.

        A03 P2: now a P03 button (G-M07-7). It assigns every unowned customer
        in the estate, so it is a sales manager's decision, not any user's."""
        if not self.env.su and not self.env.user.has_group("sales_team.group_sale_manager"):
            raise UserError(
                "Assigning every unowned account is a sales manager's decision. "
                "Ask a sales manager to run it."
            )
        owner = default_owner_id or self.env.user.id
        parties = self.env["res.partner"].search(
            ["|", ("customer_rank", ">", 0), ("role_ids.role_type", "=", "customer")]
        )
        current = self.search([("effective_to", "=", False)]).mapped("partner_id")
        unowned = parties - current
        for partner in unowned:
            self.create(
                {"partner_id": partner.id, "owner_id": owner, "assignment_type": "territory"}
            )
        return len(unowned)


class FixAccountPlan(models.Model):
    """The strategic plan for one account and period."""

    _name = "fix.account.plan"
    _description = "Account Plan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc, id desc"

    partner_id = fields.Many2one(
        "res.partner", string="Account", required=True, index=True, ondelete="cascade"
    )
    period = fields.Char(string="Period (YYYY or YYYY-Qn)", required=True)
    objectives = fields.Text(string="Objectives")
    whitespace_json = fields.Text(
        string="Whitespace (JSON)",
        help="Products/services the account does not buy but is a candidate for "
        "(FR-CRM-030) — peer comparison arrives with M17/M25 estate data",
    )
    risks = fields.Text(string="Risks")
    actions = fields.Text(string="Planned Actions")
    reviewed_at = fields.Datetime(string="Last Reviewed")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    def action_mark_reviewed(self):
        self.write({"reviewed_at": fields.Datetime.now()})
        from libs.py.fix_events import publish

        for plan in self:
            publish(
                self.env,
                "account_plan.updated",
                "fix.account.plan",
                plan.id,
                {"partner_id": plan.partner_id.id, "period": plan.period},
            )
        return True
