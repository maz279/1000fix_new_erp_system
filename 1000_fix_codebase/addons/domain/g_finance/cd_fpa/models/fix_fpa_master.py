# fix_fpa_master — M54 cost model master data: business lines (MD-036),
# cost pools, their cost elements and fixed allocation shares.
import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError

BL_CODE = re.compile(r"^BL-\d{2}$")

POOL_TYPES = [
    ("overhead", "Branch Overhead"),
    ("support", "Support Function"),
    ("facility", "Facility & Occupancy"),
    ("labour", "Labour On-Cost"),
]
RECEIVER_TYPES = [("branch", "Branch"), ("business_line", "Business Line")]
ALLOCATION_BASES = [
    ("service_orders", "Service Orders Received"),
    ("labour_hours", "Work-Order Labour Hours"),
    ("revenue", "Posted Revenue"),
    ("fixed", "Fixed Shares"),
]


class FixBusinessLine(models.Model):
    """One of the revenue-stream business lines (MD-036 `BL-nn`). The GL
    dimension `fix.journal.dimension.business_line` carries the CODE; every
    report takes the line's NAME from here, never from code."""

    _name = "fix.business.line"
    _description = "Business Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, code"
    _code_unique = models.Constraint("UNIQUE (code)", "A business-line code is used once only")

    company_id = fields.Many2one("res.company", string="Company", index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    code = fields.Char(required=True, tracking=True, help="Permanent MD-036 code, e.g. BL-01")
    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)", help="Bengali business-line name — DE-17")
    sequence = fields.Integer(default=10)
    revenue_stream_no = fields.Integer(string="Revenue Stream No.")
    is_profit_centre = fields.Boolean(string="Profit Centre", default=True)
    active = fields.Boolean(default=True, tracking=True)

    @api.constrains("code")
    def _check_code(self) -> None:
        for line in self:
            if not BL_CODE.match(line.code or ""):
                raise ValidationError(
                    "Business-line code %s must have the form BL-nn (MD-036)" % line.code
                )

    @api.depends("code", "name")
    def _compute_display_name(self) -> None:
        for line in self:
            line.display_name = f"{line.code} {line.name}" if line.code else line.name


class FixCostPool(models.Model):
    """A cost pool: the GL accounts (through its elements) whose posted
    balances are gathered and allocated to branches or business lines.
    The pool IS the allocation rule: basis, receivers and the two posting
    accounts (absorbed overhead debit / pool clearing credit)."""

    _name = "fix.cost.pool"
    _description = "Cost Pool"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"
    _code_company_unique = models.Constraint(
        "UNIQUE (company_id, code)", "A cost-pool code is used once per company"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    code = fields.Char(required=True, tracking=True)
    name = fields.Char(required=True, tracking=True)
    pool_type = fields.Selection(POOL_TYPES, required=True, default="overhead", tracking=True)
    receiver_type = fields.Selection(
        RECEIVER_TYPES, string="Allocate To", required=True, default="branch", tracking=True
    )
    allocation_basis = fields.Selection(
        ALLOCATION_BASES, string="Allocation Basis", required=True, default="service_orders"
    )
    include_in_labour_rate = fields.Boolean(
        string="Load Into Technician Rate",
        help="The pool's posted cost is spread over productive hours in the "
        "technician loaded-cost rate.",
    )
    element_ids = fields.One2many("fix.cost.element", "pool_id", string="Cost Elements")
    element_count = fields.Integer(compute="_compute_element_count", string="Elements")
    share_ids = fields.One2many("fix.cost.pool.share", "pool_id", string="Fixed Shares")
    target_account_id = fields.Many2one(
        "account.account",
        string="Absorbed Overhead Account (Dr)",
        help="Debited per receiver, with the receiver's branch / business-line dimension.",
    )
    clearing_account_id = fields.Many2one(
        "account.account",
        string="Pool Clearing Account (Cr)",
        help="Credited with the allocated total — the pool's contra account.",
    )
    journal_id = fields.Many2one("account.journal", string="Allocation Journal")
    active = fields.Boolean(default=True)

    @api.depends("element_ids")
    def _compute_element_count(self) -> None:
        for pool in self:
            pool.element_count = len(pool.element_ids)

    @api.constrains("receiver_type", "allocation_basis")
    def _check_basis(self) -> None:
        for pool in self:
            if pool.receiver_type == "business_line" and pool.allocation_basis not in (
                "revenue",
                "fixed",
            ):
                raise ValidationError(
                    "Pool %s: business-line receivers allocate on posted revenue or "
                    "fixed shares only" % pool.code
                )

    @api.constrains("target_account_id", "clearing_account_id", "element_ids")
    def _check_posting_accounts(self) -> None:
        for pool in self:
            if pool.target_account_id and pool.target_account_id == pool.clearing_account_id:
                raise ValidationError(
                    "Pool %s: the absorbed-overhead and clearing accounts must differ" % pool.code
                )
            own = pool.target_account_id | pool.clearing_account_id
            if own & pool.element_ids.account_ids:
                raise ValidationError(
                    "Pool %s: a posting account cannot also be a cost element of the pool — "
                    "the allocation would feed itself" % pool.code
                )


class FixCostPoolShare(models.Model):
    """A fixed allocation share of a pool (basis = Fixed Shares)."""

    _name = "fix.cost.pool.share"
    _description = "Cost Pool Fixed Share"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    pool_id = fields.Many2one("fix.cost.pool", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="pool_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    business_line_id = fields.Many2one("fix.business.line", string="Business Line")
    percent = fields.Float(string="Share %", required=True)

    @api.constrains("percent", "branch_id", "business_line_id")
    def _check_share(self) -> None:
        for share in self:
            if share.percent <= 0 or share.percent > 100:
                raise ValidationError("A fixed share must be between 0 and 100 percent")
            receiver = (
                share.branch_id
                if share.pool_id.receiver_type == "branch"
                else share.business_line_id
            )
            if not receiver:
                raise ValidationError(
                    "Pool %s: each fixed share names a %s"
                    % (share.pool_id.code, share.pool_id.receiver_type.replace("_", " "))
                )


class FixCostElement(models.Model):
    """A cost element: a named group of GL accounts inside a pool. An
    account may sit in one element of one active pool only, so no cost is
    gathered twice."""

    _name = "fix.cost.element"
    _description = "Cost Element"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "pool_id, code"

    pool_id = fields.Many2one("fix.cost.pool", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="pool_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    element_type = fields.Selection(
        [("primary", "Primary (from the GL)"), ("secondary", "Secondary (allocated)")],
        string="Element Type",
        required=True,
        default="primary",
    )
    account_ids = fields.Many2many(
        "account.account",
        "fix_cost_element_account_rel",
        "element_id",
        "account_id",
        string="GL Accounts",
    )

    @api.constrains("account_ids", "pool_id")
    def _check_unique_accounts(self) -> None:
        for element in self:
            if not element.account_ids:
                continue
            clash = self.search(
                [
                    ("id", "!=", element.id),
                    ("pool_id.active", "=", True),
                    ("company_id", "=", element.company_id.id),
                    ("account_ids", "in", element.account_ids.ids),
                ],
                limit=1,
            )
            if clash:
                raise ValidationError(
                    "An account of element %s already belongs to element %s (pool %s): "
                    "a cost may be gathered once only"
                    % (element.code, clash.code, clash.pool_id.code)
                )
