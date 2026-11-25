# fix_incentive_adjustments — M57: incentive disputes (BRU-PIC-12) and
# clawbacks (BRU-PIC-11).
#
# A09 workflow audit M57 §1.2 rows 5 and 9: there was no dispute model or
# state, and no clawback model; the 30-day rework "clawback" was only a score
# penalty. Now:
#   * an employee disputes their own computed line, with a reason, inside a
#     window set by `cd_performance.incentive_dispute_days` (0 = no window).
#     The run's approval waits for the window and for every dispute to be
#     answered by an Incentive Officer who is not the employee;
#   * a rework or credit of an order paid in an approved run, raised within
#     `cd_performance.incentive_clawback_days` of the order's completion
#     (0 = no clawback), opens a clawback of that order's share of the
#     incentive. The next runs recover it from the employee's incentive,
#     never more than they earn in the run.
# Both are produced only by their transitions: every field is guarded.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_performance import OFFICER, require_group


class FixIncentiveDispute(models.Model):
    _name = "fix.incentive.dispute"
    _description = "Incentive Dispute"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "raised_at desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    run_id = fields.Many2one("fix.incentive.run", required=True, ondelete="cascade", index=True)
    line_id = fields.Many2one("fix.incentive.line", string="Disputed Line", ondelete="set null")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    disputed_amount = fields.Monetary(
        related="line_id.amount", string="Disputed Amount", currency_field="currency_id"
    )
    currency_id = fields.Many2one(related="line_id.currency_id")
    reason = fields.Text(required=True)
    state = fields.Selection(
        [("open", "Open"), ("upheld", "Upheld"), ("rejected", "Rejected")],
        default="open",
        required=True,
        tracking=True,
        index=True,
    )
    raised_by_id = fields.Many2one("res.users", string="Raised By", readonly=True)
    raised_at = fields.Datetime(string="Raised At", readonly=True)
    resolved_by_id = fields.Many2one("res.users", string="Answered By", readonly=True)
    resolved_at = fields.Datetime(string="Answered At", readonly=True)
    resolution = fields.Text(readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "company_id",
            "run_id",
            "line_id",
            "employee_id",
            "reason",
            "state",
            "raised_by_id",
            "raised_at",
            "resolved_by_id",
            "resolved_at",
            "resolution",
        }

    @api.depends("run_id.period", "employee_id.name")
    def _compute_name(self):
        for rec in self:
            rec.name = "Dispute %s / %s" % (rec.run_id.period or "?", rec.employee_id.name or "?")

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError("A dispute is raised from the employee's incentive line.")
        return super().create(vals_list)

    def unlink(self):
        if not self.env.su:
            raise UserError("A dispute is evidence; it is not deleted.")
        return super().unlink()

    def _fix_answer(self, state, resolution):
        require_group(self.env, OFFICER, "Answering an incentive dispute")
        resolution = (resolution or "").strip()
        if not resolution:
            raise UserError("Give the answer and its basis.")
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is already answered." % rec.name)
            if not self.env.su and self.env.user in (
                rec.raised_by_id | rec.employee_id.sudo().user_id
            ):
                raise UserError("You cannot answer your own dispute.")
            rec._guarded().write(
                {
                    "state": state,
                    "resolved_by_id": self.env.user.id,
                    "resolved_at": fields.Datetime.now(),
                    "resolution": resolution,
                }
            )
            rec.message_post(
                body="%s: %s" % (dict(self._fields["state"].selection)[state], resolution)
            )
        return True

    def action_uphold(self, resolution=None):
        """The figure is wrong: the run is reset and recomputed before approval."""
        return self._fix_answer("upheld", resolution)

    def action_reject(self, resolution=None):
        return self._fix_answer("rejected", resolution)


class FixIncentiveClawback(models.Model):
    _name = "fix.incentive.clawback"
    _description = "Incentive Clawback"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    source_line_id = fields.Many2one(
        "fix.incentive.line", string="Paid Line", required=True, ondelete="restrict", index=True
    )
    source_run_id = fields.Many2one(
        related="source_line_id.run_id", string="Paid In Run", store=True
    )
    # A09 ERP audit M57-F11: the run whose computation raised this clawback, so
    # the approver sees it on that run's approval statement and approves it with
    # the run (automatic clawbacks no longer deduct without approval/notice).
    raised_run_id = fields.Many2one(
        "fix.incentive.run",
        string="Raised By Run",
        readonly=True,
        index=True,
        ondelete="set null",
    )
    service_order_id = fields.Many2one(
        "fix.service.order", string="Service Order", required=True, ondelete="restrict"
    )
    trigger = fields.Selection([("rework", "Rework"), ("credit", "Credit Note")], required=True)
    trigger_ref = fields.Char(string="Rework / Credit")
    trigger_at = fields.Datetime(string="Raised At")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="To Recover", currency_field="currency_id")
    recovery_line_ids = fields.One2many("fix.incentive.line", "clawback_id", string="Recovered In")
    recovered_amount = fields.Monetary(
        string="Recovered", currency_field="currency_id", compute="_compute_recovered", store=True
    )
    remaining_amount = fields.Monetary(
        string="Remaining", currency_field="currency_id", compute="_compute_recovered", store=True
    )
    state = fields.Selection(
        [("open", "Open"), ("recovered", "Recovered")],
        compute="_compute_recovered",
        store=True,
        index=True,
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _one_per_order = models.Constraint(
        "UNIQUE (source_line_id, service_order_id)",
        "An order's share of a paid incentive is clawed back once",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "company_id",
            "employee_id",
            "source_line_id",
            "service_order_id",
            "trigger",
            "trigger_ref",
            "trigger_at",
            "currency_id",
            "amount",
        }

    @api.depends("employee_id.name", "service_order_id")
    def _compute_name(self):
        for rec in self:
            rec.name = "Clawback %s / %s" % (
                rec.employee_id.name or "?",
                rec.service_order_id.display_name or "?",
            )

    @api.depends("amount", "recovery_line_ids.amount")
    def _compute_recovered(self):
        for rec in self:
            recovered = round(-sum(rec.recovery_line_ids.mapped("amount")), 2)
            rec.recovered_amount = recovered
            rec.remaining_amount = round(max((rec.amount or 0.0) - recovered, 0.0), 2)
            rec.state = "recovered" if rec.remaining_amount <= 0.005 else "open"

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError("A clawback is raised by the incentive computation, not by hand.")
        return super().create(vals_list)

    def unlink(self):
        if not self.env.su:
            raise UserError("A clawback is evidence; it is not deleted.")
        return super().unlink()
