# cd_cash_position — Field technician cash reconciliation (A08 · M50, FR-TRE-017).
#
# Audit M50-F5 (P0): the treasury had no per-technician, per-day reconciliation
# of the cash a field technician declares against the M20 receipts issued for
# that technician's field collections, and no block on further collection.
# BRU-TRE-04 covered riders only; `cod_settlement.py` says service-order field
# cash is not a COD source. This model is the treasury half of the control.
#
# The technician is an hr.employee: the same link M02's fix.field.order and
# M01's fix.service.order use. M02 has its own fix.field.cash.recon
# (FR-FSM-056: cash jobs vs hand-overs); it neither compares the declared cash
# to the M20 receipts nor blocks, and it is not edited here. This model is the
# treasury control FR-TRE-017. fix.ar.receipt has no technician field; the
# field-collection link is the receipt's source_order_id ->
# fix.service.order.technician_id with settlement_source = "field_collection".
# A receipt that cannot be reached through that link is quoted by the
# technician as a manual evidence line (receipt id / paper reference + amount).
#
# variance = declared - receipts. The thresholds are configuration, never
# hardcoded: cd_cash_position.field_cash_tolerance (default 0) and
# cd_cash_position.field_cash_escalate_above (default 0, the strictest path).
# Within tolerance the day verifies itself; above it the day is variance_open
# with a mandatory reason; above the escalation threshold a shortage is booked
# as a receivable against the technician through the rider-COD settlement's
# ledger pattern (fix.cod.settlement._fix_book_staff_cash_shortage), and
# finance is alerted. A technician with a prior open variance cannot declare
# another day (BRU-TRE-04 parity).
#
# Two-person rule: the technician never verifies or clears their own day
# (BRU-TRE-05 / SOD-12). The record is evidence once it leaves draft and is
# never deleted (FR-TRE-017).
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError

from .treasury_common import (
    GROUP_ACCOUNTANT,
    GROUP_ADMIN,
    bank_account_of,
    float_param,
    has_role,
    require_other_person,
    require_role,
    treasury_account,
    treasury_alert,
)

# The two variance tiers of FR-TRE-017. Both are configuration (M50 Q-04 has
# no value in the spec); with nothing configured every variance takes the
# strictest path, as the rider COD settlement does for BRU-TRE-03.
PARAM_TOLERANCE = "cd_cash_position.field_cash_tolerance"
PARAM_ESCALATE = "cd_cash_position.field_cash_escalate_above"
EPS = 0.005


class FixFieldCashReconciliation(models.Model):
    _name = "fix.field.cash.reconciliation"
    _description = "Field Technician Cash Reconciliation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "reconciliation_date desc, technician_id, id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
        default=lambda self: self._fix_default_operating_unit(),
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True, ondelete="restrict")
    technician_id = fields.Many2one(
        "hr.employee",
        string="Technician",
        required=True,
        index=True,
        ondelete="restrict",
        default=lambda self: self.env["hr.employee"]
        .sudo()
        .search([("user_id", "=", self.env.uid)], limit=1),
    )
    reconciliation_date = fields.Date(
        string="Business Day",
        required=True,
        index=True,
        default=fields.Date.context_today,
        help="The Dhaka business day whose field cash is reconciled (one row per technician "
        "per day).",
    )
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", store=True, readonly=True
    )
    declared_amount = fields.Monetary(
        string="Declared Cash",
        currency_field="currency_id",
        required=True,
        default=0.0,
        help="The cash the technician declares / hands in for the day.",
    )
    receipts_amount = fields.Monetary(
        string="Field Receipts",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="Frozen at declaration: the confirmed cash M20 receipts issued for this "
        "technician's field collections that day, plus the receipt ids the technician "
        "quoted as evidence.",
    )
    variance = fields.Monetary(
        string="Variance",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="Declared cash minus field receipts. Negative is a shortage (the technician "
        "declares less than the receipts issued), positive an overage.",
    )
    receipt_ids = fields.Many2many(
        "fix.ar.receipt",
        "fix_field_cash_recon_receipt_rel",
        "reconciliation_id",
        "receipt_id",
        string="Receipts Issued",
        compute="_compute_receipts",
        help="Live view of the cash receipts this day reconciles: the field-collection "
        "receipts reached through source_order_id.technician_id, plus the receipt ids in "
        "the evidence lines. The frozen evidence is Receipt Refs.",
    )
    receipts_preview_amount = fields.Monetary(
        string="Receipts Found (live)",
        currency_field="currency_id",
        compute="_compute_preview",
        help="What the current receipts and evidence lines total — the figure Declare freezes.",
    )
    variance_preview = fields.Monetary(
        string="Variance Preview",
        currency_field="currency_id",
        compute="_compute_preview",
    )
    receipt_refs = fields.Text(
        string="Receipt Refs (frozen)",
        readonly=True,
        copy=False,
        help="The receipt names / quoted references and amounts compared at declaration.",
    )
    evidence_line_ids = fields.One2many(
        "fix.field.cash.reconciliation.line",
        "reconciliation_id",
        string="Quoted Receipts",
        help="Receipts the technician quotes that the M20 field link cannot reach (a paper "
        "receipt, or a receipt booked without source_order_id).",
    )
    tolerance_amount = fields.Monetary(
        string="Tolerance Applied",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="cd_cash_position.field_cash_tolerance at declaration (frozen for audit).",
    )
    escalation_amount = fields.Monetary(
        string="Escalation Above",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="cd_cash_position.field_cash_escalate_above at declaration (frozen for audit).",
    )
    variance_tier = fields.Selection(
        [
            ("none", "Within Tolerance / None"),
            ("open", "Variance Open"),
            ("escalated", "Escalated"),
        ],
        string="Variance Tier",
        readonly=True,
        copy=False,
        help="Where the absolute variance fell against the two configured thresholds.",
    )
    variance_reason = fields.Text(
        string="Variance Reason",
        copy=False,
        tracking=True,
        help="Mandatory when the absolute variance is above the tolerance; frozen once "
        "declared.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("declared", "Declared"),
            ("verified", "Verified"),
            ("variance_open", "Variance Open"),
            ("recovered", "Recovered / Closed"),
        ],
        string="Status",
        required=True,
        default="draft",
        readonly=True,
        copy=False,
        tracking=True,
    )
    declared_by_id = fields.Many2one("res.users", string="Declared By", readonly=True, copy=False)
    declared_at = fields.Datetime(readonly=True, copy=False)
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_at = fields.Datetime(string="Verified At", readonly=True, copy=False)
    auto_verified = fields.Boolean(
        string="Auto-Verified",
        readonly=True,
        copy=False,
        help="True when the declaration was within tolerance and closed itself; no person "
        "verified it.",
    )
    verification_note = fields.Char(string="Verification Note", readonly=True, copy=False)
    shortfall_amount = fields.Monetary(
        string="Shortfall Booked",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    shortfall_move_id = fields.Many2one(
        "account.move", string="Shortfall GL Entry", readonly=True, copy=False
    )
    shortfall_account_id = fields.Many2one(
        "account.account", string="Shortfall Receivable Account", readonly=True, copy=False
    )
    recovery_state = fields.Selection(
        [("none", "No Shortfall"), ("open", "Recovery Open"), ("recovered", "Recovered")],
        string="Recovery",
        default="none",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        help="A booked shortage stays open against the technician until it is recovered "
        "(BRU-TRE-04 / FR-TRE-017).",
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
        "account.move", string="Recovery GL Entry", readonly=True, copy=False
    )
    recovered_by_id = fields.Many2one(
        "res.users", string="Recovery Posted By", readonly=True, copy=False
    )
    recovered_at = fields.Datetime(string="Recovered At", readonly=True, copy=False)
    # Inputs the Clear Variance button reads. They are not workflow fields: the
    # action copies them into the guarded recovery stamps after its checks.
    proposed_recovery_ref = fields.Char(string="Recovery Reference (to clear)")
    proposed_recovery_method = fields.Selection(
        [("cash", "Cash Repayment"), ("payroll", "Payroll Deduction")],
        string="Recovery Method",
        default="cash",
    )
    proposed_recovery_journal_id = fields.Many2one(
        "account.journal",
        string="Repayment Journal",
        domain="[('type', 'in', ('bank', 'cash'))]",
    )

    _tech_day_uniq = models.Constraint(
        "UNIQUE (technician_id, reconciliation_date, company_id)",
        "This technician's field cash is already reconciled for that day.",
    )
    _declared_positive = models.Constraint(
        "CHECK (declared_amount >= 0)", "Declared field cash cannot be negative."
    )

    _FCR_GUARDED = frozenset(
        {
            "name",
            "state",
            "declared_by_id",
            "declared_at",
            "receipts_amount",
            "receipt_refs",
            "variance",
            "tolerance_amount",
            "escalation_amount",
            "variance_tier",
            "verified_by_id",
            "verified_at",
            "auto_verified",
            "verification_note",
            "shortfall_amount",
            "shortfall_move_id",
            "shortfall_account_id",
            "recovery_state",
            "recovery_ref",
            "recovery_method",
            "recovery_move_id",
            "recovered_by_id",
            "recovered_at",
        }
    )
    # Frozen once the day leaves draft: the declaration and its evidence.
    _FCR_FROZEN = frozenset(
        {
            "company_id",
            "operating_unit_id",
            "branch_id",
            "technician_id",
            "reconciliation_date",
            "declared_amount",
            "variance_reason",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._FCR_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked |= self._FCR_FROZEN
        return locked

    def _fix_default_operating_unit(self):
        user = self.env.user
        return user.default_operating_unit_id or user.assigned_operating_unit_ids[:1]

    def _fix_technician_partner(self):
        """The technician as a ledger party (the rider-COD shortage pattern:
        a shortage with no partner is nobody's balance)."""
        self.ensure_one()
        employee = self.technician_id.sudo()
        partner = employee.work_contact_id or employee.user_id.partner_id
        if not partner:
            raise UserError(
                "%s has no work contact: the shortfall is booked against the technician, so "
                "give the employee a work contact first." % employee.name
            )
        return partner

    # ------------------------------------------------------------ evidence
    def _fix_field_receipts(self):
        """The confirmed cash M20 receipts for this technician's field
        collections on this day: source_order_id ->
        fix.service.order.technician_id with settlement_source =
        field_collection. There is no technician field on fix.ar.receipt; this
        is the field link the estate records. A wallet / card field payment is
        not cash in the technician's hands and is not counted here."""
        self.ensure_one()
        if not self.technician_id or not self.reconciliation_date:
            return self.env["fix.ar.receipt"]
        return (
            self.env["fix.ar.receipt"]
            .sudo()
            .search(
                [
                    ("state", "=", "confirmed"),
                    ("method", "=", "cash"),
                    ("company_id", "=", self.company_id.id),
                    ("receipt_date", "=", self.reconciliation_date),
                    ("source_order_id", "!=", False),
                    ("source_order_id.company_id", "=", self.company_id.id),
                    ("source_order_id.technician_id", "=", self.technician_id.id),
                    ("source_order_id.settlement_source", "=", "field_collection"),
                ]
            )
        )

    def _fix_evidence_receipts(self):
        """Auto-linked field receipts plus the receipt ids the technician
        quoted; a quoted receipt already auto-linked is counted once."""
        self.ensure_one()
        return self._fix_field_receipts() | self.evidence_line_ids.mapped("receipt_id")

    def _fix_evidence_total(self) -> float:
        self.ensure_one()
        receipts = self._fix_evidence_receipts()
        quoted_without_receipt = self.evidence_line_ids.filtered(lambda line: not line.receipt_id)
        return round(
            sum(receipts.mapped("amount")) + sum(quoted_without_receipt.mapped("amount")), 2
        )

    def _fix_evidence_refs(self):
        self.ensure_one()
        receipts = self._fix_evidence_receipts()
        parts = [
            "%s BDT %.2f" % (receipt.name or receipt.id, receipt.amount)
            for receipt in receipts.sorted(lambda rec: (rec.name or "", rec.id))
        ]
        for line in self.evidence_line_ids.filtered(lambda ev: not ev.receipt_id):
            parts.append("%s BDT %.2f (quoted)" % (line.reference or "-", line.amount))
        return "; ".join(parts) or False

    @api.depends(
        "technician_id",
        "reconciliation_date",
        "company_id",
        "evidence_line_ids.receipt_id",
    )
    def _compute_receipts(self):
        for rec in self:
            rec.receipt_ids = rec._fix_evidence_receipts()

    @api.depends(
        "technician_id",
        "reconciliation_date",
        "declared_amount",
        "evidence_line_ids.receipt_id",
        "evidence_line_ids.amount",
    )
    def _compute_preview(self):
        for rec in self:
            total = rec._fix_evidence_total()
            rec.receipts_preview_amount = total
            rec.variance_preview = round((rec.declared_amount or 0.0) - total, 2)

    # ------------------------------------------------------------ lifecycle
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            tech = self.env["hr.employee"].sudo().browse(vals.get("technician_id")).exists()
            if not tech:
                raise UserError("Choose the technician whose field cash is reconciled.")
            company = (
                self.env["res.company"].browse(vals.get("company_id")).exists() or self.env.company
            )
            if tech.company_id and tech.company_id != company:
                raise UserError(
                    "Technician %s belongs to %s; the reconciliation is %s's money."
                    % (tech.name, tech.company_id.name, company.name)
                )
            vals["company_id"] = company.id
            if not vals.get("operating_unit_id"):
                unit = (
                    tech.sudo().user_id.default_operating_unit_id
                    or self.env.user.default_operating_unit_id
                    or self.env.user.assigned_operating_unit_ids[:1]
                )
                if unit:
                    vals["operating_unit_id"] = unit.id
            day = fields.Date.to_date(vals.get("reconciliation_date")) or fields.Date.context_today(
                self
            )
            if day > fields.Date.context_today(self):
                raise UserError("A field cash day is reconciled once it has happened.")
            vals["reconciliation_date"] = day
            if self.sudo().search_count(
                [
                    ("technician_id", "=", tech.id),
                    ("reconciliation_date", "=", day),
                    ("company_id", "=", company.id),
                ]
            ):
                raise UserError("%s's field cash for %s is already reconciled." % (tech.name, day))
            if vals.get("name") in (None, False, "", "New", "/"):
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.field.cash.reconciliation")
                    or "/"
                )
        if self.env.su or self._fix_guard_has_token():
            return super().create(vals_list)
        # The reference is assigned above; every other workflow field is
        # refused unless a transition obtained the token (same idiom as the
        # rider COD settlement).
        guarded = self._fix_guarded_fields() - {"name"}
        for vals in vals_list:
            bad = [key for key in guarded & set(vals) if vals[key] not in (False, None, "", 0, [])]
            if vals.get("state", "draft") != "draft":
                bad.append("state")
            if bad:
                self._fix_guard_refuse(set(bad))
        return super()._guarded().create(vals_list).with_env(self.env)

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = self._FCR_FROZEN & set(vals)
            if frozen and any(rec.state != "draft" for rec in self):
                raise UserError(
                    "FR-TRE-017: a declared field cash reconciliation is evidence; %s cannot "
                    "change after declaration." % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def unlink(self):
        # T-14 immutable audit: a day that left draft carries the technician's
        # declaration, the receipts compared and the recovery decision.
        if not (self.env.su or self._fix_guard_has_token()):
            locked = self.filtered(lambda rec: rec.state != "draft")
            if locked:
                raise UserError(
                    "FR-TRE-017: field cash reconciliations that left draft are evidence and "
                    "are never deleted."
                )
        return super().unlink()

    @api.model
    def _fix_technician_has_open_variance(self, technician, before_day=None, company=None):
        """BRU-TRE-04 parity: a technician with an unresolved field cash
        variance (a day still variance_open) is blocked from further field
        collection. M02 / M20 call this before accepting a new declaration;
        ``action_declare`` also refuses a new day itself."""
        if not technician:
            return False
        domain = [
            ("technician_id", "=", technician.id),
            ("state", "=", "variance_open"),
        ]
        if company:
            domain.append(("company_id", "=", company.id))
        if before_day:
            domain.append(("reconciliation_date", "<", before_day))
        return bool(self.sudo().search_count(domain))

    def _fix_prior_open_variance(self, day):
        self.ensure_one()
        return self.sudo().search(
            [
                ("id", "!=", self.id),
                ("technician_id", "=", self.technician_id.id),
                ("company_id", "=", self.company_id.id),
                ("state", "=", "variance_open"),
                ("reconciliation_date", "<", day),
            ],
            order="reconciliation_date desc, id desc",
            limit=1,
        )

    def action_declare(self, reason=None):
        """Declare the day's cash and resolve it against the receipts.

        Within tolerance: declared -> verified automatically. Above it:
        declared -> variance_open with a mandatory reason; above the
        escalation threshold a negative variance is also booked as a
        receivable against the technician. A prior open variance blocks the
        declaration (FR-TRE-017 / BRU-TRE-04)."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError(
                "%s is %s; only a draft day is declared."
                % (self.name, dict(self._fields["state"].selection).get(self.state, self.state))
            )
        if not self.technician_id:
            raise UserError("Choose the technician whose field cash is declared.")
        if not (
            self.env.su
            or self.env.user == self.technician_id.user_id
            or has_role(self.env, GROUP_ACCOUNTANT)
        ):
            raise UserError(
                "FR-TRE-017: the field cash day is declared by the technician or by finance."
            )
        day = self.reconciliation_date or fields.Date.context_today(self)
        prior = self._fix_prior_open_variance(day)
        if prior:
            raise UserError(
                "FR-TRE-017 / BRU-TRE-04: %s has an unresolved field cash variance from %s "
                "(%s, BDT %.2f). Clear it before declaring another day's collection."
                % (
                    self.technician_id.name,
                    prior.reconciliation_date,
                    prior.name,
                    prior.variance,
                )
            )
        declared = round(self.declared_amount or 0.0, 2)
        if declared < 0:
            raise UserError("Declared field cash cannot be negative.")
        receipts_total = self._fix_evidence_total()
        refs = self._fix_evidence_refs()
        tolerance = max(round(float_param(self.env, PARAM_TOLERANCE, 0.0), 2), 0.0)
        escalation = max(round(float_param(self.env, PARAM_ESCALATE, 0.0), 2), tolerance)
        variance = round(declared - receipts_total, 2)
        why = (reason or self.variance_reason or "").strip()
        if abs(variance) > tolerance + EPS and not why:
            raise UserError(
                "FR-TRE-017: the declared cash differs from the field receipts by BDT %.2f "
                "(tolerance BDT %.2f, set by %s). Record the reason for the variance."
                % (variance, tolerance, PARAM_TOLERANCE)
            )
        if abs(variance) <= tolerance + EPS:
            tier = "none"
        elif abs(variance) > escalation + EPS:
            tier = "escalated"
        else:
            tier = "open"
        now = fields.Datetime.now()
        self._guarded().write(
            {
                # The declared state is written first, as the flow's second
                # step; the same transaction then resolves it.
                "state": "declared",
                "declared_by_id": self.env.uid,
                "declared_at": now,
                "receipts_amount": receipts_total,
                "receipt_refs": refs,
                "variance": variance,
                "variance_tier": tier,
                "variance_reason": why or False,
                "tolerance_amount": tolerance,
                "escalation_amount": escalation,
            }
        )
        if tier == "none":
            self._guarded().write(
                {
                    "state": "verified",
                    "auto_verified": True,
                    "verified_at": now,
                }
            )
            self.message_post(
                body="Declared BDT %.2f against field receipts BDT %.2f (variance BDT %.2f, "
                "within tolerance BDT %.2f): auto-verified."
                % (declared, receipts_total, variance, tolerance)
            )
            return True
        self._guarded().write({"state": "variance_open"})
        if tier == "escalated":
            treasury_alert(
                self,
                "Field cash variance escalated",
                "%s's field cash for %s is BDT %.2f declared against BDT %.2f receipts "
                "(variance BDT %.2f, above %s = BDT %.2f). %s"
                % (
                    self.technician_id.name,
                    day,
                    declared,
                    receipts_total,
                    variance,
                    PARAM_ESCALATE,
                    escalation,
                    why,
                ),
            )
            if variance < -EPS:
                self._fix_book_shortfall()
        self.message_post(
            body="Declared BDT %.2f against field receipts BDT %.2f (variance BDT %.2f, "
            "tier %s, rule FR-TRE-017). Reason: %s"
            % (declared, receipts_total, variance, tier, why)
        )
        return True

    def _fix_book_shortfall(self):
        """Book a negative variance above the escalation threshold as a
        receivable against the technician, through the rider-COD settlement's
        ledger pattern (A02 pass 2 M03-F8): Dr shortage receivable (technician
        as partner) / Cr the drawer cash the field receipts debited. The
        recovery then mirrors action_mark_recovered."""
        self.ensure_one()
        amount = round(max(-(self.variance or 0.0), 0.0), 2)
        if amount <= EPS:
            return self.env["account.move"]
        shortage_account = treasury_account(self.env, self.company_id, "rider_shortage")
        cash_account = treasury_account(self.env, self.company_id, "branch_cash")
        move = (
            self.env["fix.cod.settlement"]
            .sudo()
            ._fix_book_staff_cash_shortage(
                self.technician_id,
                amount,
                self.company_id,
                self.reconciliation_date,
                self.name,
                shortage_account,
                cash_account,
                branch=self.branch_id,
            )
        )
        self._guarded().write(
            {
                "shortfall_amount": amount,
                "shortfall_move_id": move.id,
                "shortfall_account_id": shortage_account.id,
                "recovery_state": "open",
            }
        )
        return move

    def action_verify(self, note=None):
        """Finance verifies the declaration; never the technician and never
        whoever declared it (BRU-TRE-05 / SOD-12). A variance stays open until
        it is cleared, so verifying only countersigns the figures."""
        require_role(self.env, GROUP_ADMIN, "Verifying a field cash reconciliation")
        for rec in self:
            if rec.state not in ("declared", "variance_open"):
                raise UserError(
                    "%s is %s; only a declared or variance-open day is verified."
                    % (
                        rec.name,
                        dict(rec._fields["state"].selection).get(rec.state, rec.state),
                    )
                )
            if rec.verified_by_id:
                raise UserError(
                    "%s is already verified by %s." % (rec.name, rec.verified_by_id.name)
                )
            require_other_person(
                self.env,
                rec.technician_id.user_id | rec.declared_by_id,
                "Verifying field cash reconciliation %s (BRU-TRE-05 / SOD-12)" % rec.name,
            )
            vals = {
                "verified_by_id": self.env.uid,
                "verified_at": fields.Datetime.now(),
            }
            if note:
                vals["verification_note"] = note
            if rec.state == "declared":
                vals["state"] = "verified"
            rec._guarded().write(vals)
            rec.message_post(
                body="Field cash declaration verified by %s%s."
                % (self.env.user.name, " — %s" % note if note else "")
            )
        return True

    def action_clear_variance(self, reference=None, method=None, journal_id=None):
        """Clear an open variance: a booked shortfall is recovered by cash
        repayment or payroll deduction (the rider-COD pattern); an
        investigated variance below the escalation threshold closes on its
        reference. Finance, other than the technician and the declarer."""
        require_role(self.env, GROUP_ADMIN, "Clearing a field cash variance")
        for rec in self:
            if rec.state != "variance_open":
                raise UserError("%s has no open variance." % rec.name)
            if not rec.verified_by_id:
                raise UserError(
                    "Finance verifies %s before its variance is cleared (BRU-TRE-05)." % rec.name
                )
            require_other_person(
                self.env,
                rec.technician_id.user_id | rec.declared_by_id,
                "Clearing field cash reconciliation %s (BRU-TRE-05)" % rec.name,
            )
            ref = (reference or rec.proposed_recovery_ref or rec.recovery_ref or "").strip()
            if not ref:
                raise UserError(
                    "Record the recovery reference (cash receipt / payroll deduction) first."
                )
            how = (method or rec.proposed_recovery_method or "cash").strip()
            if how not in ("cash", "payroll", "none"):
                raise UserError(
                    "Clear a field cash variance by cash repayment, payroll deduction, or as "
                    "investigated with no recovery."
                )
            booked = rec.recovery_state == "open" and rec.shortfall_amount > EPS
            if not booked:
                # No receivable was booked (below the escalation threshold, or
                # an overage): clearing is an investigation closure, never a
                # cash/payroll stamp with no ledger effect behind it.
                how = "none"
            vals = {
                "state": "recovered",
                "recovery_ref": ref,
                "recovery_method": how,
                "recovered_by_id": self.env.uid,
                "recovered_at": fields.Datetime.now(),
            }
            if booked:
                if how == "none":
                    raise UserError(
                        "A booked shortfall of BDT %.2f is recovered by cash or payroll, not "
                        "written off here." % rec.shortfall_amount
                    )
                amount = round(rec.shortfall_amount, 2)
                if how == "cash":
                    journal = (
                        self.env["account.journal"]
                        .browse(int(journal_id or rec.proposed_recovery_journal_id.id or 0))
                        .exists()
                    )
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
                        rec.technician_id,
                        amount,
                        rec.company_id,
                        fields.Date.context_today(rec),
                        ref,
                        debit_account,
                        credit_account,
                        branch=rec.branch_id,
                        partner_on_debit=partner_on_debit,
                    )
                )
                vals.update(
                    {
                        "recovery_state": "recovered",
                        "recovery_move_id": move.id,
                    }
                )
            rec._guarded().write(vals)
            rec.message_post(body="Field cash variance cleared (%s): %s." % (how, ref))
        return True


class FixFieldCashReconciliationLine(models.Model):
    """A receipt the technician quotes as evidence when the M20 field link
    cannot reach it. It counts in the day's receipts total: the quoted
    receipt's amount when receipt_id is set, the line amount otherwise."""

    _name = "fix.field.cash.reconciliation.line"
    _description = "Field Cash Reconciliation Evidence"
    _order = "id"

    reconciliation_id = fields.Many2one(
        "fix.field.cash.reconciliation",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        "res.company", related="reconciliation_id.company_id", store=True, index=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="reconciliation_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(
        "res.currency", related="reconciliation_id.currency_id", store=True
    )
    receipt_id = fields.Many2one(
        "fix.ar.receipt",
        string="M20 Receipt",
        ondelete="restrict",
        help="The cash receipt the technician quotes; its booked amount is counted.",
    )
    reference = fields.Char(
        string="Receipt / Paper Ref",
        help="The cash receipt id or paper receipt number the technician quotes when the "
        "receipt is not in M20 (or not reachable through source_order_id).",
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        required=True,
        help="Counted when no M20 receipt is linked; otherwise the receipt's amount is used.",
    )
    note = fields.Char(string="Note")

    _amount_positive = models.Constraint(
        "CHECK (amount > 0)", "An evidence line carries a positive amount."
    )
    _evidence_present = models.Constraint(
        "CHECK (receipt_id IS NOT NULL OR (reference IS NOT NULL AND reference <> ''))",
        "Quote an M20 receipt or a paper receipt reference.",
    )

    def _check_open(self):
        for line in self:
            if line.reconciliation_id.state != "draft":
                raise UserError(
                    "FR-TRE-017: the evidence of a declared field cash reconciliation is "
                    "frozen; it cannot be added to, changed or deleted."
                )

    def _check_cash_receipt(self, vals):
        receipt = self.env["fix.ar.receipt"].browse(vals.get("receipt_id")).exists()
        if receipt and receipt.state != "confirmed":
            raise UserError(
                "FR-TRE-017: only a confirmed M20 receipt is evidence; receipt %s is %s."
                % (receipt.name, receipt.state)
            )
        if receipt and receipt.method != "cash":
            raise UserError(
                "FR-TRE-017: a field cash reconciliation quotes cash receipts; receipt %s is "
                "%s. Quote the cash receipt or record the paper reference."
                % (
                    receipt.name,
                    dict(receipt._fields["method"].selection).get(receipt.method, receipt.method),
                )
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            rec = self.env["fix.field.cash.reconciliation"].browse(vals.get("reconciliation_id"))
            if not self.env.su and rec.state != "draft":
                raise UserError(
                    "FR-TRE-017: the evidence of a declared field cash reconciliation is "
                    "frozen; it cannot be added to, changed or deleted."
                )
            self._check_cash_receipt(vals)
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            self._check_open()
        if vals.get("receipt_id"):
            self._check_cash_receipt(vals)
        return super().write(vals)

    def unlink(self):
        if not (self.env.su or self.env.context.get("fix_guarded_transition")):
            self._check_open()
        return super().unlink()
