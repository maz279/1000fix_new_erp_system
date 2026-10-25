# fix_fpa — M54: budgets and cost-allocation cycles (P09-M07, A08 rebuild).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

VERSION_STATES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("superseded", "Superseded"),
]
# fields a budget may still receive once its version left draft
_BUDGET_UNLOCKED = {
    "actual_amount",
    "actuals_refreshed_at",
    "state",
    "message_main_attachment_id",
}


class FixBudget(models.Model):
    """An operating or capital budget inside a budget version. Planned is the
    sum of its lines; actual is refreshed from the POSTED GL. The M49<->M54
    break (AR-006 pair 14): M54 consumes depreciation EVENTS; M49 never
    reads budgets."""

    _name = "fix.budget"
    _description = "Budget"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "fiscal_year desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    version_id = fields.Many2one(
        "fix.budget.version", string="Budget Version", index=True, ondelete="cascade"
    )
    budget_type = fields.Selection(
        [("operating", "Operating"), ("capital", "Capital")],
        string="Budget Type",
        required=True,
        default="operating",
    )
    fiscal_year = fields.Char(required=True)
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    line_ids = fields.One2many("fix.budget.line", "budget_id", string="Budget Lines")
    planned_amount = fields.Monetary(
        string="Planned",
        currency_field="currency_id",
        compute="_compute_planned",
        store=True,
        readonly=False,
    )
    actual_amount = fields.Monetary(
        string="Actual", currency_field="currency_id", help="Refreshed from the posted GL"
    )
    actuals_refreshed_at = fields.Datetime(string="Actuals Refreshed", readonly=True)
    variance = fields.Monetary(
        compute="_compute_variance",
        string="Variance (Planned − Actual)",
        currency_field="currency_id",
        store=True,
    )
    state = fields.Selection(
        VERSION_STATES,
        compute="_compute_state",
        store=True,
        readonly=False,
        default="draft",
        required=True,
        tracking=True,
    )

    @api.depends("line_ids.planned_amount")
    def _compute_planned(self) -> None:
        for rec in self:
            if rec.line_ids:
                rec.planned_amount = sum(rec.line_ids.mapped("planned_amount"))
            else:
                rec.planned_amount = rec.planned_amount or 0.0

    @api.depends("planned_amount", "actual_amount")
    def _compute_variance(self) -> None:
        for rec in self:
            rec.variance = rec.planned_amount - rec.actual_amount

    @api.depends("version_id.state")
    def _compute_state(self) -> None:
        for rec in self:
            rec.state = rec.version_id.state if rec.version_id else (rec.state or "draft")

    @api.onchange("version_id")
    def _onchange_version(self) -> None:
        if self.version_id:
            self.fiscal_year = self.version_id.fiscal_year
            self.date_from = self.version_id.date_from
            self.date_to = self.version_id.date_to

    @api.model_create_multi
    def create(self, vals_list):
        versions = self.env["fix.budget.version"]
        for vals in vals_list:
            version = versions.browse(vals.get("version_id"))
            if version:
                version._check_editable()
                vals.setdefault("fiscal_year", version.fiscal_year)
                vals.setdefault("date_from", version.date_from)
                vals.setdefault("date_to", version.date_to)
                vals.setdefault("company_id", version.company_id.id)
        return super().create(vals_list)

    def write(self, vals):
        if set(vals) - _BUDGET_UNLOCKED:
            self.version_id._check_editable()
        return super().write(vals)

    def unlink(self):
        self.version_id._check_editable()
        return super().unlink()

    @api.constrains("date_from", "date_to", "version_id")
    def _check_window(self) -> None:
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError("Budget %s: the window ends before it starts" % rec.name)
            ver = rec.version_id
            if (
                ver
                and rec.date_from
                and (rec.date_from < ver.date_from or rec.date_to > ver.date_to)
            ):
                raise ValidationError(
                    "Budget %s lies outside its version window %s - %s"
                    % (rec.name, ver.date_from, ver.date_to)
                )

    def action_refresh_actuals(self):
        """Measure every line against the posted GL and store the total."""
        engine = self.env["fix.fpa.engine"]
        for rec in self:
            if not rec.line_ids:
                raise UserError(
                    "Budget %s has no lines (account, period) — nothing to measure against "
                    "the GL" % rec.name
                )
            actuals = engine.line_actuals(rec.line_ids)
            rec.write(
                {
                    "actual_amount": sum(actuals.values()),
                    "actuals_refreshed_at": fields.Datetime.now(),
                }
            )
        return True


class FixCostAllocation(models.Model):
    """An allocation cycle: one run of a cost pool for a period. Compute
    gathers the pool's posted cost and splits it on the pool's basis; Post
    books it (Dr absorbed overhead per receiver with its dimension, Cr the
    pool clearing account); Reverse books the mirror entry."""

    _name = "fix.cost.allocation"
    _description = "Cost Allocation Cycle"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_to desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    pool_id = fields.Many2one("fix.cost.pool", string="Cost Pool", index=True, tracking=True)
    receiver_type = fields.Selection(related="pool_id.receiver_type")
    allocation_basis = fields.Selection(related="pool_id.allocation_basis")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    direct_cost = fields.Monetary(
        string="Pool Cost", currency_field="currency_id", help="Posted cost gathered by the pool"
    )
    allocated_overhead = fields.Monetary(string="Allocated Overhead", currency_field="currency_id")
    total_cost = fields.Monetary(
        compute="_compute_total", string="Total", currency_field="currency_id", store=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("computed", "Computed"),
            ("posted", "Posted"),
            ("reversed", "Reversed"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.cost.allocation.line", "allocation_id", string="Receivers")
    move_id = fields.Many2one("account.move", string="Allocation Entry", readonly=True, copy=False)
    reversal_move_id = fields.Many2one(
        "account.move", string="Reversal Entry", readonly=True, copy=False
    )
    computed_by = fields.Many2one("res.users", readonly=True, copy=False)
    posted_by = fields.Many2one("res.users", readonly=True, copy=False)

    @api.depends("direct_cost", "allocated_overhead")
    def _compute_total(self) -> None:
        for rec in self:
            rec.total_cost = rec.direct_cost + rec.allocated_overhead

    @api.constrains("date_from", "date_to")
    def _check_dates(self) -> None:
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError("Allocation %s ends before it starts" % rec.name)

    def _require_cycle(self):
        for rec in self:
            if not rec.pool_id or not rec.date_from or not rec.date_to:
                raise UserError(
                    "Allocation %s needs a cost pool and a period before it can run" % rec.name
                )

    def action_compute(self):
        self._require_cycle()
        engine = self.env["fix.fpa.engine"]
        for rec in self:
            if rec.state not in ("draft", "computed"):
                raise UserError("Allocation %s is already posted" % rec.name)
            pool = rec.pool_id
            amount = round(engine.pool_amount(pool, rec.date_from, rec.date_to), 2)
            if amount <= 0:
                raise UserError(
                    "Pool %s gathered no posted cost between %s and %s — nothing to allocate"
                    % (pool.code, rec.date_from, rec.date_to)
                )
            drivers = rec._drivers()
            total_driver = sum(drivers.values())
            if total_driver <= 0:
                raise UserError(
                    "Pool %s: the allocation basis (%s) measured zero for every receiver "
                    "in the period" % (pool.code, pool.allocation_basis)
                )
            lines, running = [], 0.0
            receivers = sorted(drivers.items(), key=lambda kv: kv[0])
            for idx, (receiver, qty) in enumerate(receivers):
                share = qty / total_driver
                part = (
                    round(amount - running, 2)
                    if idx == len(receivers) - 1
                    else round(amount * share, 2)
                )
                running += part
                vals = {"driver_qty": qty, "share_pct": round(100 * share, 4), "amount": part}
                vals["branch_id" if pool.receiver_type == "branch" else "business_line_id"] = (
                    receiver
                )
                lines.append((0, 0, vals))
            rec.line_ids.unlink()
            rec.write(
                {
                    "line_ids": lines,
                    "direct_cost": amount,
                    "allocated_overhead": round(running, 2),
                    "state": "computed",
                    "computed_by": self.env.uid,
                }
            )
        return True

    def _drivers(self):
        self.ensure_one()
        pool = self.pool_id
        engine = self.env["fix.fpa.engine"]
        if pool.allocation_basis == "fixed":
            total = sum(pool.share_ids.mapped("percent"))
            if round(total, 4) != 100.0:
                raise UserError(
                    "Pool %s: fixed shares add up to %.2f%%, not 100%%" % (pool.code, total)
                )
            key = "branch_id" if pool.receiver_type == "branch" else "business_line_id"
            return {s[key].id: s.percent for s in pool.share_ids}
        if pool.receiver_type == "business_line":
            return engine.business_line_driver(self.date_from, self.date_to)
        drivers = engine.branch_driver(self.date_from, self.date_to, pool.allocation_basis)
        drivers.pop(False, None)
        return drivers

    def action_post(self):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        for rec in self:
            if rec.state != "computed" or not rec.line_ids:
                raise UserError("Compute allocation %s before posting it" % rec.name)
            pool = rec.pool_id
            missing = [
                label
                for label, value in (
                    ("absorbed-overhead account", pool.target_account_id),
                    ("clearing account", pool.clearing_account_id),
                    ("allocation journal", pool.journal_id),
                )
                if not value
            ]
            if missing:
                raise UserError(
                    "Pool %s is not configured for posting — set its %s"
                    % (pool.code, ", ".join(missing))
                )
            clash = self.search(
                [
                    ("id", "!=", rec.id),
                    ("pool_id", "=", pool.id),
                    ("state", "=", "posted"),
                    ("date_from", "<=", rec.date_to),
                    ("date_to", ">=", rec.date_from),
                ],
                limit=1,
            )
            if clash:
                raise UserError(
                    "Pool %s is already allocated for an overlapping period (%s)"
                    % (pool.code, clash.name)
                )
            line_vals, dims = [], {}
            for idx, line in enumerate(rec.line_ids):
                line_vals.append(
                    (
                        0,
                        0,
                        {
                            "name": "%s → %s" % (rec.name, line.receiver_name),
                            "account_id": pool.target_account_id.id,
                            "debit": line.amount,
                            "credit": 0.0,
                        },
                    )
                )
                dims[idx] = (
                    {
                        "branch_id": line.branch_id.id,
                        "operating_unit_id": line.branch_id.operating_unit_id.id,
                    }
                    if line.branch_id
                    else {"business_line": line.business_line_id.code}
                )
            line_vals.append(
                (
                    0,
                    0,
                    {
                        "name": "%s — pool %s cleared" % (rec.name, pool.code),
                        "account_id": pool.clearing_account_id.id,
                        "debit": 0.0,
                        "credit": rec.allocated_overhead,
                    },
                )
            )
            move, _dims = post_with_dimensions(
                self.env,
                {
                    "journal_id": pool.journal_id.id,
                    "company_id": rec.company_id.id,
                    "date": rec.date_to,
                    "ref": rec.name,
                    "line_ids": line_vals,
                },
                dims,
                source="allocation",
            )
            rec.write({"move_id": move.id, "state": "posted", "posted_by": self.env.uid})
            rec.message_post(body="Allocation posted: %s" % move.display_name)
        return True

    def action_reverse(self):
        for rec in self:
            if rec.state != "posted" or not rec.move_id:
                raise UserError("Only a posted allocation can be reversed")
            reversal = rec.move_id._reverse_moves(
                [{"ref": "Reversal of %s" % rec.name, "date": rec.move_id.date}]
            )
            reversal.action_post()
            rec.write({"reversal_move_id": reversal.id, "state": "reversed"})
            rec.message_post(body="Allocation reversed: %s" % reversal.display_name)
        return True

    def action_reset_draft(self):
        for rec in self:
            if rec.state not in ("computed", "reversed"):
                raise UserError("Only a computed or reversed allocation returns to draft")
            rec.line_ids.unlink()
            rec.write({"state": "draft", "move_id": False, "reversal_move_id": False})
        return True


class FixCostAllocationLine(models.Model):
    _name = "fix.cost.allocation.line"
    _description = "Cost Allocation Receiver"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    allocation_id = fields.Many2one(
        "fix.cost.allocation", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="allocation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="branch_id.operating_unit_id", store=True, string="Operating Unit"
    )
    currency_id = fields.Many2one(related="allocation_id.currency_id")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    business_line_id = fields.Many2one("fix.business.line", string="Business Line")
    receiver_name = fields.Char(compute="_compute_receiver_name", string="Receiver")
    driver_qty = fields.Float(string="Driver Quantity")
    share_pct = fields.Float(string="Share %", digits=(16, 4))
    amount = fields.Monetary(currency_field="currency_id")

    @api.depends("branch_id", "business_line_id")
    def _compute_receiver_name(self) -> None:
        for line in self:
            line.receiver_name = (line.branch_id or line.business_line_id).display_name or ""
