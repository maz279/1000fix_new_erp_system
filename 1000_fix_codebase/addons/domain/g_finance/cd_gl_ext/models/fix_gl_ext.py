# cd_gl_ext — M19 Financial Accounting & General Ledger core (P06-M01).
#
# Built on Odoo `account` (vendor) + OCA account-financial-tools (T01), this
# module carries the 1000FiX-specific structure:
#   - branch/OU dimensions on every posting (AS-03: cost centre + branch)
#   - the 5-day period-close process (CD-M19-05 close checklist)
#   - the fixed-asset seam M49 extends in Phase 8
#   - the W2 inventory suspense reconciliation stub (AR-006 §5.4)
#   - journal.posted / period.closed events through the outbox (AS-08)
#
# AS-10: every amount below is fields.Monetary with an explicit currency_id.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging

from libs.py.fix_events import publish  # FF-28: the only event client

_logger = logging.getLogger(__name__)


class FixJournalDimension(models.Model):
    """Branch/cost-centre dimension attached to account.move lines.

    Every posting carries its branch and operating unit — the multi-entity,
    multi-branch ledger requirement (T03). Implementing as a mixin-style
    model linked to move lines keeps Odoo's account.move untouched at the
    column level while the dimension rides every entry."""

    _name = "fix.journal.dimension"
    _description = "Journal Posting Dimension"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit",
                                        required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    cost_centre = fields.Char(string="Cost Centre", index=True,
                              help="Free-form cost centre code from the MD-* finance set")
    move_line_id = fields.Many2one("account.move.line", string="Journal Item",
                                   required=True, ondelete="cascade", index=True)

    @api.constrains("branch_id", "operating_unit_id")
    def _check_branch_ou(self):
        for dim in self:
            if dim.branch_id and dim.branch_id.operating_unit_id != dim.operating_unit_id:
                raise ValidationError(
                    "Branch %s does not belong to operating unit %s"
                    % (dim.branch_id.name, dim.operating_unit_id.name))


class FixPeriodClose(models.Model):
    """The 5-day month-end close process (T06 / CD-M19-05).

    A close checklist instance per company+period. Each line is a close step
    with an owner and a target day-offset; the close is DONE only when every
    blocking step is cleared. Day 0 = period end."""

    _name = "fix.period.close"
    _description = "Period Close Checklist"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_end desc, company_id"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _company_period_unique = models.Constraint('UNIQUE (company_id, period_end)', 'One close checklist per company and period')

    CLOSE_TARGET_DAYS = 5  # G3-04: month-end close within 5 days

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    period_end = fields.Date(string="Period End", required=True)
    state = fields.Selection(
        [("open", "Open"), ("in_progress", "In Progress"),
         ("ready_to_close", "Ready to Close"), ("closed", "Closed")],
        default="open", required=True, tracking=True)
    line_ids = fields.One2many("fix.period.close.line", "close_id", string="Close Steps")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    # AS-10: monetary, never float
    suspense_opening = fields.Monetary(string="Suspense Opening", currency_field="currency_id",
                                       help="Balance in the W2 inventory suspense account at period start")
    suspense_closing = fields.Monetary(string="Suspense Closing", currency_field="currency_id")
    closed_at = fields.Datetime(readonly=True)
    close_duration_days = fields.Float(compute="_compute_duration", store=True,
                                       string="Close Duration (days)")

    @api.depends("period_end", "closed_at")
    def _compute_duration(self):
        for close in self:
            if close.closed_at:
                delta = fields.Datetime.from_string(close.closed_at).date() - close.period_end
                close.close_duration_days = max(delta.days, 0.0)
            else:
                close.close_duration_days = 0.0

    def action_ready(self):
        for close in self:
            blocking = close.line_ids.filtered(lambda l: l.blocking and l.state != "done")
            if blocking:
                raise UserError(
                    "Close steps still open: %s"
                    % ", ".join(blocking.mapped("name")))
            if close.suspense_closing:
                raise UserError(
                    "Suspense account must be zero at close (AR-006 §5.4) — "
                    "balance: %.2f" % close.suspense_closing)
            close.state = "ready_to_close"

    def action_close(self):
        for close in self:
            if close.state != "ready_to_close":
                raise UserError("Run the ready check before closing")
            close.write({"state": "closed", "closed_at": fields.Datetime.now()})
            publish(self.env, "period.closed", "fix.period.close", close.id, {
                "company_id": close.company_id.id,
                "period_end": str(close.period_end),
                "duration_days": close.close_duration_days,
            })
            if close.close_duration_days > self.CLOSE_TARGET_DAYS:
                _logger.warning(
                    "P06 G3-04 breach: close took %.1f days (target %d)",
                    close.close_duration_days, self.CLOSE_TARGET_DAYS)

    def action_fail_close_target(self):
        """Report-only helper for the G3 gate: which closes exceeded 5 days."""
        return self.search_read(
            [("state", "=", "closed"), ("close_duration_days", ">", self.CLOSE_TARGET_DAYS)],
            ["period_end", "close_duration_days"])


class FixPeriodCloseLine(models.Model):
    """One step of the close checklist with its owner and day-offset target."""

    _name = "fix.period.close.line"
    _description = "Period Close Step"

    close_id = fields.Many2one("fix.period.close", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Step", required=True)
    owner_role = fields.Char(string="Owning Role", help="R-nn role accountable for this step")
    target_day = fields.Integer(string="Target Day", help="Day offset from period end (0..5)")
    blocking = fields.Boolean(default=True,
                              help="A blocking step must clear before the period can close")
    state = fields.Selection(
        [("pending", "Pending"), ("in_progress", "In Progress"), ("done", "Done")],
        default="pending", required=True)
    evidence_ref = fields.Char(string="Evidence Reference",
                               help="Report ID or reconciliation record proving the step")


class FixFixedAssetSeam(models.Model):
    """The fixed-asset seam M49 extends in Phase 8 (T07).

    Deliberately minimal: the capitalisation interface the asset register
    will plug into. Finance posts capitalisation events; M49 consumes and
    owns depreciation. No depreciation logic here — the seam, not the asset
    module."""

    _name = "fix.fixed.asset.seam"
    _description = "Fixed Asset Seam (M49 interface)"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(string="Capitalisation Reference", required=True)
    move_line_id = fields.Many2one("account.move.line", string="Journal Item",
                                   required=True, ondelete="restrict")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    amount = fields.Monetary(string="Capitalised Amount", currency_field="currency_id",
                             required=True)
    asset_category = fields.Char(string="Asset Category",
                                 help="From the MD-* finance master data")
    consumed = fields.Boolean(default=False, readonly=True,
                              help="True once M49 has created the asset register entry")

    def action_mark_consumed(self):
        """Called by M49 (Phase 8) when the asset record exists. Idempotent."""
        self.write({"consumed": True})


def post_with_dimensions(env, move_vals, dimension_by_line):
    """T03/T09 helper: post an account.move and attach branch/OU dimensions
    to every line in the SAME transaction, then emit journal.posted.

    dimension_by_line: {line_index: {"branch_id": int, "cost_centre": str}}
    Returns (move, dimensions)."""
    move = env["account.move"].create(move_vals)
    move.action_post()
    dimension_model = env["fix.journal.dimension"]
    dimensions = dimension_model
    for idx, line in enumerate(move.line_ids):
        dim_vals = dimension_by_line.get(idx, {})
        if dim_vals:
            dimensions |= dimension_model.create({
                "move_line_id": line.id,
                "company_id": move.company_id.id,
                "operating_unit_id": dim_vals.get(
                    "operating_unit_id", move.company_id.id and
                    env["operating.unit"].search([], limit=1).id),
                "branch_id": dim_vals.get("branch_id", False),
                "cost_centre": dim_vals.get("cost_centre", False),
            })
    publish(env, "journal.posted", "account.move", move.id, {
        "company_id": move.company_id.id,
        "amount": float(move.amount_total),
        "currency": move.currency_id.name,
        "line_count": len(move.line_ids),
    })
    return move, dimensions
