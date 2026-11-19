# Counters and queue priority rules (FR-FRD-004, -007, -027; BRU-FRD-07).
#
# M04 build, 13 Nov 2026: a token carried a free "Counter #" integer and a
# priority lane the agent picked by hand. Nothing said which counters a branch
# has or what each one serves, and Privilege / corporate / elderly customers
# were placed in priority only if the agent remembered to (BRU-FRD-07 says
# "automatically"). This file adds the branch's counters with their
# capabilities and the priority rules a token is placed by, and binds a token
# to a counter that can serve its service type.
#
# Loaded after fix_token_queue (it extends fix.token.queue): keep the name.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .fix_cash_shift import fill_operating_unit
from .fix_token_queue import LANE_RANK

# service type -> the counter capability that serves it
CAPABILITY_FOR = {
    "drop_off": "can_intake",
    "pick_up": "can_collect",
    "payment": "can_pay",
    "enquiry": "can_enquiry",
    "other": "can_enquiry",
}

# LANE_RANK: one lane order for the priority rules and for calling (fix_token_queue)


class FixQueueCounter(models.Model):
    """A service position at a branch and what it can serve."""

    _name = "fix.queue.counter"
    _description = "Branch Service Counter"
    _inherit = ["mail.thread"]
    _order = "branch_id, number"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True, index=True)
    number = fields.Integer(string="Counter No.", required=True)
    label = fields.Char(
        string="Counter Name", help="What the display calls it, e.g. 'Corporate Desk'."
    )
    can_intake = fields.Boolean(string="Device Drop-off / Intake", default=True)
    can_collect = fields.Boolean(string="Collection / Pick-up", default=True)
    can_pay = fields.Boolean(string="Payment", default=True)
    can_enquiry = fields.Boolean(string="Enquiry", default=True)
    can_corporate = fields.Boolean(string="Corporate Accounts")
    can_technical = fields.Boolean(string="Technical Desk")
    agent_id = fields.Many2one("res.users", string="Staffed By", tracking=True)
    active = fields.Boolean(default=True)

    @api.depends("branch_id", "number", "label")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s Counter %s%s" % (
                rec.branch_id.code or rec.branch_id.name or "",
                rec.number or "",
                " (%s)" % rec.label if rec.label else "",
            )

    @api.constrains("branch_id", "number")
    def _check_unique_number(self):
        for rec in self:
            if rec.number <= 0:
                raise ValidationError("A counter number is 1 or more.")
            twin = self.with_context(active_test=False).search(
                [
                    ("id", "!=", rec.id),
                    ("branch_id", "=", rec.branch_id.id),
                    ("number", "=", rec.number),
                ],
                limit=1,
            )
            if twin:
                raise ValidationError(
                    "%s already has a counter %s." % (rec.branch_id.display_name, rec.number)
                )

    @api.model_create_multi
    def create(self, vals_list):
        fill_operating_unit(self.env, vals_list)
        return super().create(vals_list)

    def _fd_serves(self, service_type) -> bool:
        self.ensure_one()
        return bool(self[CAPABILITY_FOR.get(service_type, "can_enquiry")])

    def action_call_next(self):
        """A02 ERP audit M04-F12 (BRU-FRD-07): the counter calls the next
        customer it can serve: today's waiting tokens of its branch, the
        highest priority lane first, then the earliest issued. A token routed
        to another counter is left to that counter."""
        self.ensure_one()
        Token = self.env["fix.token.queue"]
        Token._fd_require_queue_role("Calling the next token")
        if not self.active:
            raise ValidationError("Counter %s is closed." % self.name)
        token = Token._fd_next_waiting(self.branch_id, counter=self, company=self.company_id)
        if not token:
            raise ValidationError("No customer %s can serve is waiting." % self.name)
        token = token.with_env(self.env)
        if token.counter_id != self:
            token.write({"counter_id": self.id})
        token.action_call()
        return {"called": token.token_display, "token_id": token.id}


class FixQueuePriorityRule(models.Model):
    """BRU-FRD-07: who is placed in which priority lane, automatically."""

    _name = "fix.queue.priority.rule"
    _description = "Queue Priority Rule"
    _inherit = ["mail.thread"]
    _order = "sequence, id"

    name = fields.Char(string="Rule", required=True, tracking=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    branch_id = fields.Many2one(
        "fix.branch", string="Branch", help="Leave empty to apply at every branch."
    )
    corporate_only = fields.Boolean(
        string="Corporate Customer", help="Matches a customer that is a company or belongs to one."
    )
    partner_category_id = fields.Many2one(
        "res.partner.category",
        string="Customer Tag",
        help="Matches a customer with this tag (e.g. Senior Citizen, Accessibility Need).",
    )
    loyalty_tier_name = fields.Char(
        string="Loyalty Tier",
        help="Matches a customer whose active loyalty account is in this tier (e.g. Gold, "
        "Diamond). Exact tier name.",
    )
    service_type = fields.Selection(
        [
            ("drop_off", "Device Drop-off"),
            ("pick_up", "Device Pick-up"),
            ("enquiry", "Enquiry"),
            ("payment", "Payment"),
            ("other", "Other"),
        ],
        string="Service Type",
        help="Leave empty to match every service type.",
    )
    priority_level = fields.Selection(
        [
            ("vip_corporate", "VIP / Corporate SLA"),
            ("warranty_express", "Express Warranty Lane"),
            ("senior_citizen", "Senior Citizen / Accessibility Priority"),
        ],
        string="Place In Lane",
        required=True,
        tracking=True,
    )
    active = fields.Boolean(default=True)

    # name and lane are always written, so the check also runs on a create
    # that sets no condition at all
    @api.constrains(
        "name",
        "priority_level",
        "corporate_only",
        "partner_category_id",
        "loyalty_tier_name",
        "service_type",
    )
    def _check_has_condition(self):
        for rec in self:
            if not (
                rec.corporate_only
                or rec.partner_category_id
                or (rec.loyalty_tier_name or "").strip()
                or rec.service_type
            ):
                raise ValidationError(
                    "Rule '%s' has no condition: it would put every customer in priority. "
                    "Choose a customer tag, a loyalty tier, corporate customers or a service type."
                    % rec.name
                )

    def _fd_matches(self, branch, partner, service_type) -> bool:
        self.ensure_one()
        if self.branch_id and self.branch_id != branch:
            return False
        if self.service_type and self.service_type != service_type:
            return False
        customer_conditions = (
            self.corporate_only
            or self.partner_category_id
            or (self.loyalty_tier_name or "").strip()
        )
        if customer_conditions and not partner:
            return False
        if self.corporate_only and not (partner.is_company or partner.parent_id.is_company):
            return False
        if self.partner_category_id and self.partner_category_id not in (
            partner.category_id | partner.parent_id.category_id
        ):
            return False
        tier = (self.loyalty_tier_name or "").strip()
        if tier:
            Account = self.env.get("fix.loyalty.account")
            if Account is None:
                return False
            accounts = Account.sudo().search([("partner_id", "=", partner.id)])
            if "state" in Account._fields:
                accounts = accounts.filtered(lambda a: a.state == "active")
            names = {(a.tier_id.name or "").strip().lower() for a in accounts if a.tier_id}
            if tier.lower() not in names:
                return False
        return True

    @api.model
    def _fd_lane_for(self, branch, partner, service_type):
        """The first matching rule (by sequence) for a token, or an empty set."""
        domain = [("company_id", "in", self.env.companies.ids)]
        for rule in self.sudo().search(domain):
            if rule._fd_matches(branch, partner, service_type):
                return rule
        return self.browse()


class FixTokenRouting(models.Model):
    _inherit = "fix.token.queue"

    counter_id = fields.Many2one(
        "fix.queue.counter",
        string="Service Counter",
        domain="[('branch_id', '=', branch_id)]",
        tracking=True,
    )
    priority_rule_id = fields.Many2one(
        "fix.queue.priority.rule",
        string="Placed By Rule",
        readonly=True,
        help="The priority rule that placed this token in its lane (BRU-FRD-07).",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"priority_rule_id"}

    @api.model_create_multi
    def create(self, vals_list):
        Rule = self.env["fix.queue.priority.rule"]
        Branch = self.env["fix.branch"]
        Partner = self.env["res.partner"]
        placed = []
        for vals in vals_list:
            rule = Rule.browse()
            lane = vals.get("priority_level") or "normal"
            if vals.get("branch_id"):
                rule = Rule._fd_lane_for(
                    Branch.browse(vals["branch_id"]),
                    Partner.browse(vals["customer_id"]) if vals.get("customer_id") else Partner,
                    vals.get("service_type") or "drop_off",
                )
            # a rule raises the lane; it never lowers one the agent chose
            if rule and LANE_RANK[rule.priority_level] > LANE_RANK.get(lane, 0):
                vals["priority_level"] = rule.priority_level
                placed.append(rule)
            else:
                placed.append(Rule.browse())
            if vals.get("counter_id"):
                vals["counter_number"] = (
                    self.env["fix.queue.counter"].browse(vals["counter_id"]).number
                )
        records = super().create(vals_list)
        for rec, rule in zip(records, placed, strict=True):
            if rule:
                rec._guarded().write({"priority_rule_id": rule.id})
        return records

    def write(self, vals):
        if vals.get("counter_id"):
            vals = dict(
                vals, counter_number=self.env["fix.queue.counter"].browse(vals["counter_id"]).number
            )
        return super().write(vals)

    @api.constrains("counter_id", "branch_id", "service_type")
    def _check_counter_serves_token(self):
        for rec in self.filtered("counter_id"):
            counter = rec.counter_id
            if counter.branch_id != rec.branch_id:
                raise ValidationError(
                    "Counter %s is at %s, not at the token's branch %s."
                    % (counter.name, counter.branch_id.display_name, rec.branch_id.display_name)
                )
            if not counter.active:
                raise ValidationError("Counter %s is closed." % counter.name)
            if not counter._fd_serves(rec.service_type):
                raise ValidationError(
                    "Counter %s does not serve %s (FR-FRD-007): route the token to a counter "
                    "that does."
                    % (counter.name, dict(rec._fields["service_type"].selection)[rec.service_type])
                )
