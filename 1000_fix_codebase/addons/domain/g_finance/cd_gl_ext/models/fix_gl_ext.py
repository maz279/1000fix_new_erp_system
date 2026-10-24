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
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

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

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", required=True, index=True
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    cost_centre = fields.Char(
        string="Cost Centre",
        index=True,
        help="Free-form cost centre code from the MD-* finance set",
    )
    move_line_id = fields.Many2one(
        "account.move.line", string="Journal Item", required=True, ondelete="cascade", index=True
    )

    @api.constrains("branch_id", "operating_unit_id")
    def _check_branch_ou(self):
        for dim in self:
            if dim.branch_id and dim.branch_id.operating_unit_id != dim.operating_unit_id:
                raise ValidationError(
                    "Branch %s does not belong to operating unit %s"
                    % (dim.branch_id.name, dim.operating_unit_id.name)
                )


class FixPeriodClose(models.Model):
    """The 5-day month-end close process (T06 / CD-M19-05).

    A close checklist instance per company+period. Each line is a close step
    with an owner and a target day-offset; the close is DONE only when every
    blocking step is cleared. Day 0 = period end."""

    _name = "fix.period.close"
    _description = "Period Close Checklist"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_end desc, company_id"
    _company_period_unique = models.Constraint(
        "UNIQUE (company_id, period_end)", "One close checklist per company and period"
    )

    CLOSE_TARGET_DAYS = 5  # G3-04: month-end close within 5 days

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    period_end = fields.Date(string="Period End", required=True)
    started_at = fields.Datetime(string="Started At", default=fields.Datetime.now)
    target_completion_date = fields.Date(
        string="Target Completion Date",
        compute="_compute_target_completion",
        store=True,
    )
    state = fields.Selection(
        [
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("ready_to_close", "Ready to Close"),
            ("closed", "Closed"),
        ],
        default="open",
        required=True,
        tracking=True,
    )
    sla_status = fields.Selection(
        [("within_sla", "Within 5-Day SLA"), ("breached", "Breached Target")],
        string="SLA Performance",
        compute="_compute_duration",
        store=True,
    )
    line_ids = fields.One2many("fix.period.close.line", "close_id", string="Close Steps")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # AS-10: monetary, never float
    suspense_opening = fields.Monetary(
        string="Suspense Opening",
        currency_field="currency_id",
        help="Balance in the W2 inventory suspense account at period start",
    )
    suspense_closing = fields.Monetary(string="Suspense Closing", currency_field="currency_id")
    suspense_reconciled = fields.Boolean(string="Suspense Reconciled", default=False)
    cutover_voucher_ref = fields.Char(string="Suspense Cutover Voucher Ref", readonly=True)
    cutover_move_id = fields.Many2one(
        "account.move",
        string="Suspense Cutover Journal Entry",
        copy=False,
        help="The POSTED journal entry that brings the W2 inventory suspense into the "
        "general ledger. Required to reconcile the suspense.",
    )
    closed_at = fields.Datetime(readonly=True)
    close_duration_days = fields.Float(
        compute="_compute_duration", store=True, string="Close Duration (days)"
    )

    @api.depends("period_end")
    def _compute_target_completion(self):
        for close in self:
            target_days = getattr(close, "CLOSE_TARGET_DAYS", getattr(self, "CLOSE_TARGET_DAYS", 5))
            if close.period_end:
                close.target_completion_date = fields.Date.add(close.period_end, days=target_days)
            else:
                close.target_completion_date = False

    @api.depends("period_end", "closed_at")
    def _compute_duration(self):
        for close in self:
            target_days = getattr(close, "CLOSE_TARGET_DAYS", getattr(self, "CLOSE_TARGET_DAYS", 5))
            if close.closed_at:
                delta = fields.Datetime.from_string(close.closed_at).date() - close.period_end
                duration = max(delta.days, 0.0)
                close.close_duration_days = duration
                close.sla_status = "within_sla" if duration <= target_days else "breached"
            else:
                close.close_duration_days = 0.0
                close.sla_status = "within_sla"

    def action_generate_standard_steps(self):
        """Generate the 10 statutory close steps from SOP SP-020."""
        self.ensure_one()
        steps_data = [
            (10, "Subledger Cut-Off & Physical Inventory Counts", "Supply Chain Lead", 0, True),
            (
                20,
                "Bank Statement Feeds Import & Automated Reconciliation",
                "Treasury Lead",
                1,
                True,
            ),
            (30, "AR Billing & Auto-Invoice Clearance", "Billing Specialist", 2, True),
            (40, "AP Three-Way Match & Vendor Invoice Clearance", "AP Accountant", 3, True),
            (50, "VAT Sub-Ledger & Mushak 9.1 Return Preparation", "Tax Manager", 3, True),
            (
                60,
                "Inventory Suspense Account Zero-Balance Clearance",
                "Inventory Accountant",
                4,
                True,
            ),
            (70, "Fixed Asset Capitalisation Interface Review", "Asset Accountant", 4, False),
            (80, "Inter-Branch & Operating Unit Dimension Balancing", "GL Lead", 5, True),
            (90, "Accruals, Depreciation & Tax Withholding Postings", "Senior Accountant", 5, True),
            (
                100,
                "General Ledger Lock & Financial Statements Generation",
                "Chief Financial Officer",
                5,
                True,
            ),
        ]
        line_model = self.env["fix.period.close.line"]
        for seq, name, role, day, blocking in steps_data:
            line_model.create(
                {
                    "close_id": self.id,
                    "sequence": seq,
                    "name": name,
                    "owner_role": role,
                    "target_day": day,
                    "blocking": blocking,
                    "state": "pending",
                }
            )
        self.write({"state": "in_progress"})
        return True

    def action_reconcile_inventory_suspense(self) -> dict:
        """T04: Reconcile the W2 inventory suspense entries against a REAL,
        balancing cutover journal entry.

        The cutover entry (``cutover_move_id``) must be posted, belong to the
        company, and move the suspense account(s) the entries are booked
        against by exactly the pending suspense valuation. Only then are the
        entries marked reconciled, with the entry's number as voucher. The
        closing suspense is what is STILL pending afterwards — computed, not
        written as 0. (This action used to mark every entry reconciled
        against an invented voucher "GL-CUTOVER-W2-M15-<id>" and force the
        suspense balance to zero without any journal entry.)"""
        self.ensure_one()
        suspense_model = self.env["fix.inventory.valuation.suspense"]
        domain = [
            ("status", "=", "pending_gl_cutover"),
            ("company_id", "=", self.company_id.id),
        ]
        pending_entries = suspense_model.search(domain)
        total_suspense = round(sum(pending_entries.mapped("total_valuation")), 2)
        voucher_ref = False
        if pending_entries:
            move = self.cutover_move_id
            if not move:
                raise UserError(
                    "Post the suspense cutover journal entry (%.2f) and select it on the "
                    "close before reconciling the inventory suspense." % total_suspense
                )
            if move.state != "posted" or move.company_id != self.company_id:
                raise UserError(
                    "Cutover entry %s must be a POSTED entry of %s."
                    % (move.display_name, self.company_id.name)
                )
            codes = set(pending_entries.mapped("suspense_account_code"))
            Account = self.env["account.account"].with_company(self.company_id)
            accounts = Account.search(
                [*Account._check_company_domain(self.company_id), ("code", "in", list(codes))]
            )
            missing = codes - set(accounts.mapped("code"))
            if missing:
                raise UserError(
                    "Suspense account(s) %s are not in the chart of %s."
                    % (", ".join(sorted(missing)), self.company_id.name)
                )
            moved = round(
                sum(
                    move.line_ids.filtered(lambda line: line.account_id in accounts).mapped(
                        "balance"
                    )
                ),
                2,
            )
            if round(abs(moved) - abs(total_suspense), 2) != 0:
                raise UserError(
                    "Cutover entry %s moves the suspense account(s) %s by %.2f, but the "
                    "pending suspense valuation is %.2f — it does not clear the suspense."
                    % (move.name, ", ".join(sorted(codes)), abs(moved), total_suspense)
                )
            voucher_ref = move.name
            for entry in pending_entries:
                entry.action_reconcile_to_gl(voucher_ref)

        remaining = round(sum(suspense_model.search(domain).mapped("total_valuation")), 2)
        self.write(
            {
                "suspense_closing": remaining,
                "suspense_reconciled": remaining == 0,
                "cutover_voucher_ref": voucher_ref or self.cutover_voucher_ref,
            }
        )
        publish(
            self.env,
            "inventory.suspense.reconciled",
            "fix.period.close",
            self.id,
            {
                "company_id": self.company_id.id,
                "period_end": str(self.period_end),
                "reconciled_entries_count": len(pending_entries),
                "total_valuation_cleared": float(total_suspense),
                "voucher_ref": voucher_ref or "",
                "suspense_balance": float(remaining),
            },
        )
        return {
            "reconciled_entries": len(pending_entries),
            "total_valuation": float(total_suspense),
            "voucher_ref": voucher_ref or "",
            "status": "zero_cleared" if remaining == 0 else "residual_pending",
        }

    def action_ready(self):
        for close in self:
            blocking = close.line_ids.filtered(lambda line: line.blocking and line.state != "done")
            if blocking:
                raise UserError("Close steps still open: %s" % ", ".join(blocking.mapped("name")))
            if close.suspense_closing:
                raise UserError(
                    "Suspense account must be zero at close (AR-006 §5.4) — "
                    "balance: %.2f" % close.suspense_closing
                )
            close.state = "ready_to_close"

    def action_close(self):
        for close in self:
            if close.state != "ready_to_close":
                raise UserError("Run the ready check before closing")
            close.write({"state": "closed", "closed_at": fields.Datetime.now()})
            publish(
                close.env,
                "period.closed",
                "fix.period.close",
                close.id,
                {
                    "company_id": close.company_id.id,
                    "period_end": str(close.period_end),
                    "duration_days": close.close_duration_days,
                    "sla_status": close.sla_status,
                    "step_count": len(close.line_ids),
                },
            )
            target_days = getattr(close, "CLOSE_TARGET_DAYS", getattr(self, "CLOSE_TARGET_DAYS", 5))
            if close.close_duration_days > target_days:
                _logger.warning(
                    "P06 G3-04 breach: close took %.1f days (target %d)",
                    close.close_duration_days,
                    target_days,
                )

    def action_fail_close_target(self):
        """Report-only helper for the G3 gate: which closes exceeded 5 days."""
        return self.search_read(
            [("state", "=", "closed"), ("close_duration_days", ">", self.CLOSE_TARGET_DAYS)],
            ["period_end", "close_duration_days", "sla_status"],
        )


class FixPeriodCloseLine(models.Model):
    """One step of the close checklist with its owner and day-offset target."""

    _name = "fix.period.close.line"
    _description = "Period Close Step"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    close_id = fields.Many2one("fix.period.close", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Step", required=True)
    owner_role = fields.Char(string="Owning Role", help="R-nn role accountable for this step")
    target_day = fields.Integer(string="Target Day", help="Day offset from period end (0..5)")
    blocking = fields.Boolean(
        default=True, help="A blocking step must clear before the period can close"
    )
    state = fields.Selection(
        [("pending", "Pending"), ("in_progress", "In Progress"), ("done", "Done")],
        default="pending",
        required=True,
    )
    evidence_ref = fields.Char(
        string="Evidence Reference", help="Report ID or reconciliation record proving the step"
    )

    @api.constrains("state", "evidence_ref")
    def _check_done_has_evidence(self):
        for line in self:
            if line.state == "done" and not (line.evidence_ref or "").strip():
                raise ValidationError(
                    "Close step '%s' cannot be done without an evidence reference "
                    "(report ID or reconciliation record)." % line.name
                )

    def action_mark_done(self, evidence: str = ""):
        """Complete a close step on real evidence. There is no default: the
        step used to be marked done with the evidence "VERIFIED" whenever
        none was given. Without evidence the step stays as it is."""
        evidence = (evidence or "").strip()
        if not evidence:
            raise UserError(
                "Provide the evidence reference (report ID / reconciliation record) "
                "proving the close step before marking it done."
            )
        for line in self:
            line.write({"state": "done", "evidence_ref": evidence})
        return True

    def action_set_state(self, new_state: str):
        if new_state not in ("pending", "in_progress", "done"):
            raise UserError(f"Invalid state: {new_state}")
        self.write({"state": new_state})
        return True


class FixFixedAssetSeam(models.Model):
    """The fixed-asset seam M49 extends in Phase 8 (T07).

    Deliberately minimal: the capitalisation interface the asset register
    will plug into. Finance posts capitalisation events; M49 consumes and
    owns depreciation. No depreciation logic here — the seam, not the asset
    module."""

    _name = "fix.fixed.asset.seam"
    _description = "Fixed Asset Seam (M49 interface)"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(string="Capitalisation Reference", required=True)
    move_line_id = fields.Many2one(
        "account.move.line", string="Journal Item", required=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(
        string="Capitalised Amount", currency_field="currency_id", required=True
    )
    asset_category = fields.Char(string="Asset Category", help="From the MD-* finance master data")
    consumed = fields.Boolean(
        default=False, readonly=True, help="True once M49 has created the asset register entry"
    )

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
            # A missing/empty OU falls back to the MOVE's company OU — never
            # another company's (the dimension is the multi-entity ledger key).
            operating_unit_id = (
                dim_vals.get("operating_unit_id")
                or env["operating.unit"]
                .search([("company_id", "=", move.company_id.id)], limit=1)
                .id
            )
            if not operating_unit_id:
                raise UserError(
                    "Company %s has no operating unit — every posting carries one (AS-03)"
                    % move.company_id.name
                )
            dimensions |= dimension_model.create(
                {
                    "move_line_id": line.id,
                    "company_id": move.company_id.id,
                    "operating_unit_id": operating_unit_id,
                    "branch_id": dim_vals.get("branch_id", False),
                    "cost_centre": dim_vals.get("cost_centre", False),
                }
            )
    publish(
        env,
        "journal.posted",
        "account.move",
        move.id,
        {
            "company_id": move.company_id.id,
            "amount": float(move.amount_total),
            "currency": move.currency_id.name,
            "line_count": len(move.line_ids),
        },
    )
    return move, dimensions
