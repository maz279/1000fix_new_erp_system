# cd_cash_position — Treasury controls on M02's field cash reconciliation
# (A08 B13 · M50-F5 · FR-TRE-017).
#
# M02's `fix.field.cash.recon` (FR-FSM-056 / BRU-FSM-07) is the ONE
# per-technician per-business-day field-cash register: jobs cashed, cash
# handed to a branch shift, still outstanding, the counted amount, the
# variance + reason, and a second person's confirmation. The audit's
# "field-cash reconciliation entirely missing" was overstated; adding a
# second register would double the figures and give the estate two
# conflicting blocks. This module therefore EXTENDS that register with the
# treasury control FR-TRE-017:
#
#   * receipts_amount — the day's CONFIRMED cash M20 receipts for this
#     technician's field collections, plus the receipts / paper refs the
#     technician quotes. fix.ar.receipt has no technician field; the field
#     link is source_order_id -> fix.service.order.technician_id with
#     settlement_source = "field_collection" and method = "cash".
#   * receipts_variance = counted_amount - receipts_amount, evaluated at
#     Submit / Confirm against cd_cash_position.field_cash_tolerance (default
#     0). Above it the existing variance_reason is mandatory.
#   * Above cd_cash_position.field_cash_escalate_above a negative variance
#     books the shortfall receivable through the rider-COD settlement's
#     ledger pattern (fix.cod.settlement._fix_book_staff_cash_shortage:
#     Dr rider_shortage / Cr branch_cash) and variance_state becomes open;
#     action_clear_variance recovers it (cash / payroll) or closes an
#     investigated variance, setting variance_state = recovered.
#   * BRU-TRE-04 parity: submitting a new day refuses while a prior-day row
#     of the same technician has variance_state = open.
#
# M02 already refuses a self-confirm (BRU-FSM-07) and its write() freezes a
# row once it leaves draft; this extension does not duplicate those guards.
# M02 has no model-level unlink guard — its ACLs give no group unlink (only
# the superuser), and that remains the evidence gap. This extension only
# locks its own computed treasury fields against typing.
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .treasury_common import (
    GROUP_ADMIN,
    bank_account_of,
    float_param,
    require_other_person,
    require_role,
    treasury_account,
    treasury_alert,
)

# The two thresholds of FR-TRE-017. The spec gives no value (M50 Q-04), so
# with nothing configured every variance takes the strictest path. The same
# keys the B13 treasury reconciliation used; they are configuration only.
PARAM_TOLERANCE = "cd_cash_position.field_cash_tolerance"
PARAM_ESCALATE = "cd_cash_position.field_cash_escalate_above"
EPS = 0.005


class FixFieldCashReconTreasury(models.Model):
    _inherit = "fix.field.cash.recon"

    receipts_amount = fields.Monetary(
        string="Field Receipts",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="Recomputed from the receipts at Create / Submit / Confirm: the day's confirmed "
        "cash M20 receipts for this technician's field collections, plus the M20 receipts and "
        "paper amounts the technician quotes.",
    )
    receipts_variance = fields.Monetary(
        string="Receipts Variance",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="Counted cash minus Field Receipts, evaluated at Submit / Confirm against "
        "cd_cash_position.field_cash_tolerance.",
    )
    variance_state = fields.Selection(
        [
            ("clear", "Clear"),
            ("open", "Open"),
            ("recovered", "Recovered"),
        ],
        string="Receipts Variance State",
        default="clear",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        help="clear: the counted cash ties to the receipts within tolerance. open: a variance "
        "above tolerance is unresolved (and, above the escalation threshold, booked as a "
        "receivable). recovered: action_clear_variance closed it.",
    )
    quoted_receipt_ids = fields.Many2many(
        "fix.ar.receipt",
        "fix_field_cash_recon_quoted_receipt_rel",
        "recon_id",
        "receipt_id",
        string="Quoted Receipts",
        domain="[('state', '=', 'confirmed'), ('method', '=', 'cash')]",
        help="Confirmed cash M20 receipts the technician quotes because the field link "
        "(source_order_id -> technician) cannot reach them.",
    )
    quoted_receipt_refs = fields.Text(
        string="Quoted Paper Receipts",
        help="Paper / other cash receipt references not in M20. Their total goes in Quoted "
        "Amount; the reference is the evidence.",
    )
    quoted_receipt_amount = fields.Monetary(
        string="Quoted Amount",
        currency_field="currency_id",
        default=0.0,
        help="The total of the paper receipt refs above; counted in Field Receipts.",
    )
    shortfall_amount = fields.Monetary(
        string="Shortfall Booked",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    shortfall_move_id = fields.Many2one(
        "account.move",
        string="Shortfall GL Entry",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )
    shortfall_account_id = fields.Many2one(
        "account.account",
        string="Shortfall Receivable Account",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )
    recovery_ref = fields.Char(string="Recovery Reference", readonly=True, copy=False)
    recovery_method = fields.Selection(
        [
            ("cash", "Cash Repayment"),
            ("payroll", "Payroll Deduction"),
            ("none", "No Recovery (Investigated)"),
        ],
        string="Recovered By",
        readonly=True,
        copy=False,
    )
    recovery_move_id = fields.Many2one(
        "account.move",
        string="Recovery GL Entry",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )
    recovered_by_id = fields.Many2one(
        "res.users", string="Recovery Posted By", readonly=True, copy=False
    )
    recovered_at = fields.Datetime(string="Recovered At", readonly=True, copy=False)

    _quoted_amount_nonnegative = models.Constraint(
        "CHECK (quoted_receipt_amount >= 0)",
        "A quoted receipt amount cannot be negative.",
    )

    # Computed / workflow stamps. Only the transitions (with sudo) write them;
    # the technicians' inputs are counted_amount, variance_reason and the
    # quoted receipts, which M02 already freezes once the row leaves draft.
    _FIX_TREASURY_LOCKED = frozenset(
        {
            "receipts_amount",
            "receipts_variance",
            "variance_state",
            "shortfall_amount",
            "shortfall_move_id",
            "shortfall_account_id",
            "recovery_ref",
            "recovery_method",
            "recovery_move_id",
            "recovered_by_id",
            "recovered_at",
        }
    )

    # ------------------------------------------------------------ evidence
    def _fix_field_receipts(self):
        """The day's confirmed cash M20 receipts for this technician's field
        collections. fix.ar.receipt has no technician field; the field link is
        its source_order_id -> fix.service.order.technician_id with
        settlement_source = field_collection. Wallet / card field payments are
        not cash in the technician's hands and are not counted."""
        self.ensure_one()
        if not self.employee_id or not self.recon_date:
            return self.env["fix.ar.receipt"]
        return (
            self.env["fix.ar.receipt"]
            .sudo()
            .search(
                [
                    ("state", "=", "confirmed"),
                    ("method", "=", "cash"),
                    ("company_id", "=", self.company_id.id),
                    ("receipt_date", "=", self.recon_date),
                    ("source_order_id", "!=", False),
                    ("source_order_id.company_id", "=", self.company_id.id),
                    ("source_order_id.technician_id", "=", self.employee_id.id),
                    ("source_order_id.settlement_source", "=", "field_collection"),
                ]
            )
        )

    @api.constrains("quoted_receipt_ids")
    def _check_quoted_receipts(self):
        for rec in self:
            bad = rec.sudo().quoted_receipt_ids.filtered(
                lambda receipt: receipt.state != "confirmed" or receipt.method != "cash"
            )
            if bad:
                raise ValidationError(
                    "FR-TRE-017: a quoted receipt is a confirmed cash M20 receipt; %s is not."
                    % ", ".join(bad.mapped("name"))
                )

    def _fix_receipts_total(self):
        """The day's receipts total, fresh from M20 and the quoted evidence.
        A quoted receipt already reached by the field link is counted once."""
        self.ensure_one()
        receipts = self._fix_field_receipts() | self.sudo().quoted_receipt_ids
        return round(sum(receipts.mapped("amount")) + (self.quoted_receipt_amount or 0.0), 2)

    def _fix_treasury_values(self, evaluated=False):
        """The receipts total and variance, fresh from the receipts, and the
        state they put the row in. The receipts tie-out engages when the day
        has receipts or quoted refs; with none, M02's job variance governs
        (there is nothing to reconcile the cash against). Create shows the
        figure but stays clear; Submit and Confirm evaluate it."""
        self.ensure_one()
        receipts = self._fix_receipts_total()
        tolerance = max(round(float_param(self.env, PARAM_TOLERANCE, 0.0), 2), 0.0)
        variance = round((self.counted_amount or 0.0) - receipts, 2)
        state = "clear"
        if receipts > EPS and evaluated and abs(variance) > tolerance + EPS:
            state = "open"
        return {
            "receipts_amount": receipts,
            "receipts_variance": variance,
            "variance_state": state,
        }

    # ------------------------------------------------------------ block
    def _fix_prior_open_variance(self):
        """BRU-TRE-04 parity: the most recent prior-day row of this technician
        that is submitted/confirmed with an open receipts variance."""
        self.ensure_one()
        if not self.employee_id or not self.recon_date:
            return self.browse()
        return self.sudo().search(
            [
                ("id", "!=", self.id),
                ("employee_id", "=", self.employee_id.id),
                ("company_id", "=", self.company_id.id),
                ("state", "in", ("submitted", "confirmed")),
                ("variance_state", "=", "open"),
                ("recon_date", "<", self.recon_date),
            ],
            order="recon_date desc, id desc",
            limit=1,
        )

    @api.model
    def _fix_technician_has_open_variance(self, employee, before_day=None, company=None):
        """The block M02 / M20 ask before accepting another collection day."""
        if not employee:
            return False
        domain = [
            ("employee_id", "=", employee.id),
            ("state", "in", ("submitted", "confirmed")),
            ("variance_state", "=", "open"),
        ]
        if company:
            domain.append(("company_id", "=", company.id))
        if before_day:
            domain.append(("recon_date", "<", before_day))
        return bool(self.sudo().search_count(domain))

    def _fix_branch(self):
        self.ensure_one()
        if not self.operating_unit_id:
            return False
        return (
            self.env["fix.branch"]
            .sudo()
            .search([("operating_unit_id", "=", self.operating_unit_id.id)], limit=1)
        )

    # ------------------------------------------------------------ lifecycle
    @api.model_create_multi
    def create(self, vals_list):
        # The treasury stamps are computed, never typed. M02's own create
        # strips its figures; this strips the treasury ones before the row is
        # written (a caller cannot forge a shortfall / recovered state).
        for vals in vals_list:
            for key in self._FIX_TREASURY_LOCKED:
                vals.pop(key, None)
        records = super().create(vals_list)
        for rec in records:
            rec.sudo().write(rec._fix_treasury_values())
        return records

    def write(self, vals):
        if not self.env.su:
            touched = self._FIX_TREASURY_LOCKED & set(vals)
            if touched:
                raise UserError(
                    "The treasury figures of %s are computed by Submit / Confirm / Clear and "
                    "cannot be typed (%s)." % (self._description, ", ".join(sorted(touched)))
                )
        return super().write(vals)

    def action_submit(self):
        """M02's submit, preceded by the FR-TRE-017 checks: no prior-day open
        variance, and a reason above the configured tolerance."""
        for rec in self:
            if rec.state != "draft":
                continue  # M02 raises its own "already submitted" error
            prior = rec._fix_prior_open_variance()
            if prior:
                raise UserError(
                    "FR-TRE-017 / BRU-TRE-04: %s has an unresolved field cash receipts variance "
                    "from %s (%s, BDT %.2f). Clear it before submitting another day's collection."
                    % (
                        rec.employee_id.name,
                        prior.recon_date,
                        prior.name,
                        prior.receipts_variance,
                    )
                )
            tolerance = max(round(float_param(self.env, PARAM_TOLERANCE, 0.0), 2), 0.0)
            receipts = rec._fix_receipts_total()
            variance = round((rec.counted_amount or 0.0) - receipts, 2)
            if (
                receipts > EPS
                and abs(variance) > tolerance + EPS
                and not (rec.variance_reason or "").strip()
            ):
                raise UserError(
                    "FR-TRE-017: the counted cash differs from the day's field receipts by "
                    "BDT %.2f (tolerance BDT %.2f, set by %s). Record the variance reason "
                    "before submitting." % (variance, tolerance, PARAM_TOLERANCE)
                )
        result = super().action_submit()
        for rec in self:
            rec.sudo().write(rec._fix_treasury_values(evaluated=True))
        return result

    def _fix_book_shortage(self):
        """M02 calls this on Confirm. Evaluate the receipts variance; above the
        escalation threshold a negative variance is booked through the
        rider-COD shortage receivable. Booking here (and setting
        shortage_booked) replaces M02's own shortage booking for the same cash
        so the missing money is posted once."""
        self.ensure_one()
        if self.shortage_booked:
            return False
        tolerance = max(round(float_param(self.env, PARAM_TOLERANCE, 0.0), 2), 0.0)
        escalation = max(round(float_param(self.env, PARAM_ESCALATE, 0.0), 2), tolerance)
        values = self._fix_treasury_values(evaluated=True)
        self.sudo().write(values)
        if values["receipts_amount"] <= EPS:
            # No receipts to tie the count to: M02's job variance remains the
            # control, exactly as before the treasury extension.
            self.sudo().write({"variance_state": "clear"})
            return super()._fix_book_shortage()
        variance = values["receipts_variance"]
        if abs(variance) > escalation + EPS:
            note = (
                "%s's field cash for %s is BDT %.2f counted against BDT %.2f receipts "
                "(receipts variance BDT %.2f, above %s = BDT %.2f). %s"
                % (
                    self.employee_id.name,
                    self.recon_date,
                    self.counted_amount,
                    self.receipts_amount,
                    variance,
                    PARAM_ESCALATE,
                    escalation,
                    self.variance_reason or "",
                )
            )
            if variance < -EPS:
                self._fix_book_treasury_shortfall(-variance)
                self.sudo().write({"variance_state": "open"})
                treasury_alert(self, "Field cash receipts variance escalated", note)
                return True  # the shortfall is booked once; skip M02's booking
            self.sudo().write({"variance_state": "open"})
            treasury_alert(self, "Field cash receipts variance escalated", note)
            return super()._fix_book_shortage()
        if abs(variance) > tolerance + EPS:
            self.sudo().write({"variance_state": "open"})
        else:
            self.sudo().write({"variance_state": "clear"})
        return super()._fix_book_shortage()

    def _fix_book_treasury_shortfall(self, amount):
        self.ensure_one()
        amount = round(amount or 0.0, 2)
        if amount <= EPS:
            return self.env["account.move"]
        shortage_account = treasury_account(self.env, self.company_id, "rider_shortage")
        cash_account = treasury_account(self.env, self.company_id, "branch_cash")
        move = (
            self.env["fix.cod.settlement"]
            .sudo()
            ._fix_book_staff_cash_shortage(
                self.employee_id,
                amount,
                self.company_id,
                self.recon_date,
                self.name,
                shortage_account,
                cash_account,
                branch=self._fix_branch(),
            )
        )
        self.sudo().write(
            {
                "shortfall_amount": amount,
                "shortfall_move_id": move.id,
                "shortfall_account_id": shortage_account.id,
                "variance_state": "open",
                "shortage_booked": True,
            }
        )
        return move

    def action_clear_variance(self, reference=None, method=None, journal_id=None):
        """Clear an open receipts variance. A booked shortfall is recovered by
        cash repayment or payroll deduction (the rider-COD recovery pattern);
        an unbooked variance closes as investigated. Finance, and not the
        technician or whoever submitted the day (BRU-TRE-05 / SOD-12)."""
        require_role(self.env, GROUP_ADMIN, "Clearing a field cash receipts variance")
        for rec in self:
            if rec.variance_state != "open":
                raise UserError("%s has no open receipts variance." % rec.name)
            if rec.state != "confirmed":
                raise UserError(
                    "BRU-FSM-07: %s is confirmed before its receipts variance is cleared."
                    % rec.name
                )
            if not rec.confirmed_by_id:
                raise UserError("BRU-FSM-07: %s has no confirming user." % rec.name)
            require_other_person(
                self.env,
                rec.employee_id.user_id | rec.submitted_by_id,
                "Clearing the field cash receipts variance of %s" % rec.name,
            )
            ref = (reference or "").strip()
            if not ref:
                raise UserError(
                    "Record the recovery reference (cash receipt / payroll deduction / "
                    "investigation) first."
                )
            how = (method or "none").strip()
            if how not in ("cash", "payroll", "none"):
                raise UserError(
                    "Clear the receipts variance by cash repayment, payroll deduction, or as "
                    "investigated with no recovery."
                )
            booked = bool(rec.shortfall_move_id) and rec.shortfall_amount > EPS
            if not booked:
                # No receivable was booked (below the escalation threshold, or
                # an overage): this is an investigation closure, never a
                # cash/payroll stamp with no ledger effect behind it.
                how = "none"
            elif how == "none":
                raise UserError(
                    "A booked shortfall of BDT %.2f is recovered by cash or payroll."
                    % rec.shortfall_amount
                )
            vals = {
                "variance_state": "recovered",
                "recovery_ref": ref,
                "recovery_method": how,
                "recovered_by_id": self.env.uid,
                "recovered_at": fields.Datetime.now(),
            }
            if booked:
                amount = round(rec.shortfall_amount, 2)
                if how == "cash":
                    journal = self.env["account.journal"].browse(int(journal_id or 0)).exists()
                    if not journal:
                        raise UserError(
                            "Select the bank / cash journal the technician repaid into."
                        )
                    if journal.company_id != rec.company_id:
                        raise UserError(
                            "Journal %s belongs to %s; %s is %s's money."
                            % (
                                journal.display_name,
                                journal.company_id.name,
                                rec.name,
                                rec.company_id.name,
                            )
                        )
                    debit_account = bank_account_of(journal)
                    partner_on_debit = False
                else:
                    debit_account = treasury_account(
                        self.env, rec.company_id, "rider_shortage_payroll"
                    )
                    partner_on_debit = True
                credit_account = rec.shortfall_account_id or treasury_account(
                    self.env, rec.company_id, "rider_shortage"
                )
                move = (
                    self.env["fix.cod.settlement"]
                    .sudo()
                    ._fix_recover_staff_cash_shortage(
                        rec.employee_id,
                        amount,
                        rec.company_id,
                        fields.Date.context_today(rec),
                        ref,
                        debit_account,
                        credit_account,
                        branch=rec._fix_branch(),
                        partner_on_debit=partner_on_debit,
                    )
                )
                vals["recovery_move_id"] = move.id
            rec.sudo().write(vals)
            rec.message_post(body="Field cash receipts variance cleared (%s): %s." % (how, ref))
        return True
