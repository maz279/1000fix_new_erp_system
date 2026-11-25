# fix_fpa — M54: budgets and cost-allocation cycles (P09-M07, A08 rebuild).
#
# A08 remediation (B3, 4 Nov 2026; M54-4, -7):
#   - fix.budget: no budget without a version; its state follows the version and
#     is never typed; "Actual" is computed from the posted GL, never stored or
#     typed (BRU-FPA-02); the planned figure is the sum of its lines.
#   - fix.cost.allocation: state and the compute/post stamps are guarded, the
#     receiver lines are written only by the compute, the post RECOMPUTES the
#     split from the ledger and refuses a cycle that no longer agrees, and the
#     user who computed a cycle does not post it. The allocation is raised to
#     M19 through its posting API (source "allocation", BRU-FPA-01).
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

VERSION_STATES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("superseded", "Superseded"),
]
# fields a budget may still receive once its version left draft
_BUDGET_UNLOCKED = {
    "actuals_refreshed_at",
    "message_main_attachment_id",
}
ACCOUNT_USER = "account.group_account_user"
ACCOUNT_MANAGER = "account.group_account_manager"


class FixBudget(models.Model):
    """An operating or capital budget inside a budget version. Planned is the
    sum of its lines; actual is read from the POSTED GL. The M49<->M54
    break (AR-006 pair 14): M54 consumes depreciation EVENTS; M49 never
    reads budgets."""

    _name = "fix.budget"
    _description = "Budget"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
        readonly=True,
    )
    actual_amount = fields.Monetary(
        string="Actual",
        currency_field="currency_id",
        compute="_compute_actual",
        help="Read live from the posted GL on the budget's lines; never typed.",
    )
    actuals_refreshed_at = fields.Datetime(string="Actuals Refreshed", readonly=True)
    variance = fields.Monetary(
        compute="_compute_actual",
        string="Variance (Planned − Actual)",
        currency_field="currency_id",
    )
    state = fields.Selection(
        VERSION_STATES,
        compute="_compute_state",
        store=True,
        readonly=True,
        default="draft",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "actuals_refreshed_at"}

    @api.depends("line_ids.planned_amount")
    def _compute_planned(self) -> None:
        for rec in self:
            rec.planned_amount = sum(rec.line_ids.mapped("planned_amount"))

    def _compute_actual(self) -> None:
        engine = self.env["fix.fpa.engine"]
        lines = self.mapped("line_ids").filtered("id")
        actuals = engine.line_actuals(lines) if lines else {}
        for rec in self:
            rec.actual_amount = sum(actuals.get(line.id, 0.0) for line in rec.line_ids)
            rec.variance = rec.planned_amount - rec.actual_amount

    @api.depends("version_id.state")
    def _compute_state(self) -> None:
        for rec in self:
            rec.state = rec.version_id.state if rec.version_id else "draft"

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
            if not version:
                raise ValidationError(
                    "A budget belongs to a budget version: plan it inside a version so it is "
                    "submitted and approved (A08 M54-7)."
                )
            version._check_editable()
            # blank on the form means "as the version": the year and window are
            # the version's unless the planner narrows them
            for name, value in (
                ("fiscal_year", version.fiscal_year),
                ("date_from", version.date_from),
                ("date_to", version.date_to),
                ("company_id", version.company_id.id),
            ):
                if not vals.get(name):
                    vals[name] = value
        return super().create(vals_list)

    def write(self, vals):
        if "version_id" in vals and not vals["version_id"]:
            raise ValidationError("A budget belongs to a budget version.")
        if set(vals) - _BUDGET_UNLOCKED:
            self.version_id._check_editable()
            if "version_id" in vals:
                self.env["fix.budget.version"].browse(vals["version_id"])._check_editable()
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
        """Measure every line against the posted GL (the actual is always live;
        this stamps when it was last looked at)."""
        for rec in self:
            if not rec.line_ids:
                raise UserError(
                    "Budget %s has no lines (account, period) — nothing to measure against "
                    "the GL" % rec.name
                )
            rec._guarded().write({"actuals_refreshed_at": fields.Datetime.now()})
        return True


class FixCostAllocation(models.Model):
    """An allocation cycle: one run of a cost pool for a period. Compute
    gathers the pool's posted cost and splits it on the pool's basis; Post
    (by someone other than the computer) recomputes the split and books it
    through the M19 API (Dr absorbed overhead per receiver with its dimension,
    Cr the pool clearing account); Reverse books the mirror entry."""

    _name = "fix.cost.allocation"
    _description = "Cost Allocation Cycle"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
        string="Pool Cost",
        currency_field="currency_id",
        readonly=True,
        help="Posted cost gathered by the pool",
    )
    allocated_overhead = fields.Monetary(
        string="Allocated Overhead", currency_field="currency_id", readonly=True
    )
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

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "direct_cost",
            "allocated_overhead",
            "move_id",
            "reversal_move_id",
            "computed_by",
            "posted_by",
        }

    def write(self, vals):
        cycle = {"pool_id", "date_from", "date_to", "company_id", "currency_id"} & set(vals)
        if cycle and not self._fix_guard_open():
            if any(rec.state in ("posted", "reversed") for rec in self):
                raise UserError("A posted allocation is frozen; reverse it instead.")
            result = super().write(vals)
            # the computed split belonged to the old cycle
            for rec in self.filtered(lambda r: r.state == "computed"):
                rec.line_ids.sudo()._guarded().unlink()
                rec._guarded().write(
                    {
                        "state": "draft",
                        "direct_cost": 0.0,
                        "allocated_overhead": 0.0,
                        "computed_by": False,
                    }
                )
            return result
        return super().write(vals)

    @api.depends("direct_cost", "allocated_overhead")
    def _compute_total(self) -> None:
        for rec in self:
            rec.total_cost = rec.direct_cost + rec.allocated_overhead

    @api.constrains("date_from", "date_to")
    def _check_dates(self) -> None:
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError("Allocation %s ends before it starts" % rec.name)

    def _require(self, xmlid, what):
        if not self.env.su and not self.env.user.has_group(xmlid):
            raise AccessError("%s needs the %s role." % (what, self.env.ref(xmlid).name))

    def _require_cycle(self):
        for rec in self:
            if not rec.pool_id or not rec.date_from or not rec.date_to:
                raise UserError(
                    "Allocation %s needs a cost pool and a period before it can run" % rec.name
                )

    def _fpa_split(self):
        """(pool amount, [receiver line vals]) computed from the posted ledger
        and the pool's basis — the same computation for compute and post."""
        self.ensure_one()
        engine = self.env["fix.fpa.engine"]
        pool = self.pool_id
        amount = round(engine.pool_amount(pool, self.date_from, self.date_to), 2)
        if amount <= 0:
            raise UserError(
                "Pool %s gathered no posted cost between %s and %s — nothing to allocate"
                % (pool.code, self.date_from, self.date_to)
            )
        drivers = self._drivers()
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
            running = round(running + part, 2)
            vals = {"driver_qty": qty, "share_pct": round(100 * share, 4), "amount": part}
            vals["branch_id" if pool.receiver_type == "branch" else "business_line_id"] = receiver
            lines.append(vals)
        return amount, lines

    def action_compute(self):
        self._require(ACCOUNT_USER, "Computing a cost allocation")
        self._require_cycle()
        for rec in self:
            if rec.state not in ("draft", "computed"):
                raise UserError("Allocation %s is already posted" % rec.name)
            amount, lines = rec._fpa_split()
            rec.line_ids.sudo()._guarded().unlink()
            self.env["fix.cost.allocation.line"].sudo()._guarded().create(
                [dict(vals, allocation_id=rec.id) for vals in lines]
            )
            rec._guarded().write(
                {
                    "direct_cost": amount,
                    "allocated_overhead": round(sum(v["amount"] for v in lines), 2),
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

        self._require(ACCOUNT_USER, "Posting a cost allocation")
        for rec in self:
            if rec.state != "computed" or not rec.line_ids:
                raise UserError("Compute allocation %s before posting it" % rec.name)
            if not self.env.su and self.env.user in (rec.computed_by | rec.create_uid):
                raise UserError(
                    "Segregation of duties: %s prepared or computed allocation %s and cannot "
                    "post it; another accountant reviews and posts it."
                    % (self.env.user.name, rec.name)
                )
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
            # BRU-FPA-04/07: the posted figures are the ledger's, recomputed now.
            amount, fresh = rec._fpa_split()
            key = "branch_id" if pool.receiver_type == "branch" else "business_line_id"
            stored = sorted((ln[key].id, round(ln.amount, 2)) for ln in rec.line_ids)
            recomputed = sorted((v[key], round(v["amount"], 2)) for v in fresh)
            if stored != recomputed or round(rec.direct_cost - amount, 2) != 0:
                raise UserError(
                    "Allocation %s no longer agrees with the ledger (pool cost %.2f, computed "
                    "%.2f); compute it again before posting." % (rec.name, amount, rec.direct_cost)
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
                        "credit": round(sum(v["amount"] for v in fresh), 2),
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
                source_ref=rec.name,
            )
            rec._guarded().write({"move_id": move.id, "state": "posted", "posted_by": self.env.uid})
            rec.message_post(body="Allocation posted: %s" % move.display_name)
        return True

    def action_reverse(self):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import m19_context

        self._require(ACCOUNT_USER, "Reversing a cost allocation")
        for rec in self:
            if rec.state != "posted" or not rec.move_id:
                raise UserError("Only a posted allocation can be reversed")
            reversal = rec.move_id._reverse_moves(
                [{"ref": "Reversal of %s" % rec.name, "date": rec.move_id.date}]
            )
            reversal.with_context(**m19_context("cost_allocation"))._post(soft=False)
            rec._guarded().write({"reversal_move_id": reversal.id, "state": "reversed"})
            rec.message_post(body="Allocation reversed: %s" % reversal.display_name)
        return True

    def action_reset_draft(self):
        self._require(ACCOUNT_USER, "Resetting a cost allocation")
        for rec in self:
            if rec.state not in ("computed", "reversed"):
                raise UserError("Only a computed or reversed allocation returns to draft")
            rec.line_ids.sudo()._guarded().unlink()
            rec._guarded().write(
                {
                    "state": "draft",
                    "move_id": False,
                    "reversal_move_id": False,
                    "direct_cost": 0.0,
                    "allocated_overhead": 0.0,
                    "computed_by": False,
                    "posted_by": False,
                }
            )
        return True


class FixCostAllocationLine(models.Model):
    """One receiver of a computed allocation. Written only by the compute."""

    _name = "fix.cost.allocation.line"
    _description = "Cost Allocation Receiver"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

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

    _LINE_FIELDS = {
        "allocation_id",
        "branch_id",
        "business_line_id",
        "driver_qty",
        "share_pct",
        "amount",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._LINE_FIELDS

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(
                "Allocation receivers are written by Compute, never typed (BRU-FPA-04)."
            )
        return super().create(vals_list)

    def unlink(self):
        if not self._fix_guard_open():
            raise UserError(
                "Allocation receivers are written by Compute, never typed (BRU-FPA-04)."
            )
        return super().unlink()

    @api.depends("branch_id", "business_line_id")
    def _compute_receiver_name(self) -> None:
        for line in self:
            line.receiver_name = (line.branch_id or line.business_line_id).display_name or ""
