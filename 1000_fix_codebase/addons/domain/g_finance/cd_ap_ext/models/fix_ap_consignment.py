# cd_ap_ext — brand consignment settlements (FR-APE-030 P0, AUT-APE-10/11,
# BRU-APE-21 H; spec M52 §5.4 / §10.1 entity `fix.ap.consignment.settlement`).
#
# M15 (cd_inventory) owns the consignment stock and records every issue of it
# on a warranty job as a `fix.stock.consumption` with ownership_class
# 'consignment' and state 'consumed'. When a period closes, the brand that
# owns the consumed parts must be settled: this document gathers the brand's
# consumed quantities in a period at the agreed partner rate, computes the
# payable (plus VAT where the brand's M51 tax profile is VAT-registered),
# goes through a two-person approval over the AP approval matrix, and posts
# Dr the AP expense/consumption account (+ input VAT) / Cr AP control with the
# operating-unit, branch and brand dimensions.
#
# M15 is read, never written (the task's boundary; cd_inventory also has no
# dependency on cd_ap_ext, so the reference is soft — the gather refuses when
# M15 is not installed). A consumption already on a live settlement of another
# brand/period is never gathered twice; a cancelled settlement releases its
# lines for reuse.
from datetime import timedelta

from odoo import api, fields, models
from odoo.addons.cd_cash_position.models.treasury_common import require_other_person
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_controls import require_finance
from .fix_ap_ext import _q

CONSUMPTION_MODEL = "fix.stock.consumption"


class FixApConsignmentSettlement(models.Model):
    """A brand's consignment-consumption obligation for one period."""

    _name = "fix.ap.consignment.settlement"
    _description = "Brand Consignment Settlement"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "period_end desc, id desc"

    _one_per_brand_period = models.UniqueIndex(
        "(company_id, brand_id, period_start, period_end) WHERE state != 'cancelled'",
        "A settlement for this brand and period already exists.",
    )

    name = fields.Char(readonly=True, copy=False, default="New", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", required=True, index=True, help="The unit the settlement posts in."
    )
    branch_id = fields.Many2one(
        "fix.branch",
        string="Branch",
        index=True,
        help="Optional branch dimension on every settlement posting line.",
    )
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True, index=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Brand Partner",
        required=True,
        index=True,
        ondelete="restrict",
        help="The brand party settled. Its M51 tax profile decides VAT.",
    )
    tax_profile_id = fields.Many2one(
        "fix.vendor.tax.profile",
        string="Tax Profile",
        compute="_compute_tax_profile",
        compute_sudo=True,
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id", string="Currency", store=True, readonly=True
    )
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    settlement_date = fields.Date(
        string="Settlement Date", default=fields.Date.context_today, required=True
    )
    line_ids = fields.One2many(
        "fix.ap.consignment.settlement.line",
        "settlement_id",
        string="Consumed Parts",
        copy=False,
    )
    line_count = fields.Integer(compute="_compute_amounts", compute_sudo=True, store=True)
    quantity_total = fields.Float(
        string="Quantity Consumed",
        compute="_compute_amounts",
        compute_sudo=True,
        store=True,
        digits=(16, 4),
    )
    value_untaxed = fields.Monetary(
        string="Value (excl. VAT)",
        currency_field="currency_id",
        compute="_compute_amounts",
        compute_sudo=True,
        store=True,
    )
    vat_registered = fields.Boolean(
        string="Brand VAT-Registered", compute="_compute_amounts", compute_sudo=True, store=True
    )
    vat_rate = fields.Float(
        string="VAT Rate (%)",
        digits=(6, 3),
        compute="_compute_amounts",
        compute_sudo=True,
        store=True,
    )
    vat_amount = fields.Monetary(
        string="Input VAT",
        currency_field="currency_id",
        compute="_compute_amounts",
        compute_sudo=True,
        store=True,
    )
    total_payable = fields.Monetary(
        string="Total Payable",
        currency_field="currency_id",
        compute="_compute_amounts",
        compute_sudo=True,
        store=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    statement_ref = fields.Char(
        string="Brand Statement Ref",
        help="The brand's own statement reference, when the settlement is sent to it (P08).",
    )
    note = fields.Text()
    gathered_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    gathered_at = fields.Datetime(readonly=True, copy=False)
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)
    submitted_at = fields.Datetime(readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    rejected_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    rejected_at = fields.Datetime(readonly=True, copy=False)
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)

    STAMPS = (
        "name",
        "state",
        "line_ids",
        "line_count",
        "quantity_total",
        "value_untaxed",
        "vat_registered",
        "vat_rate",
        "vat_amount",
        "total_payable",
        "gathered_by_id",
        "gathered_at",
        "submitted_by",
        "submitted_at",
        "approved_by_id",
        "approved_at",
        "rejected_by_id",
        "rejected_at",
        "move_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self.STAMPS)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in (False, "draft"):
            locked |= {
                "company_id",
                "operating_unit_id",
                "branch_id",
                "brand_id",
                "partner_id",
                "period_start",
                "period_end",
                "settlement_date",
            }
        if len(self) == 1 and self.state == "approved":
            locked |= {"statement_ref", "note"}
        return locked

    @api.constrains("period_start", "period_end")
    def _check_period(self):
        for rec in self:
            if rec.period_start and rec.period_end and rec.period_end < rec.period_start:
                raise ValidationError(
                    "Settlement %s ends before it starts." % (rec.name or rec.brand_id.name)
                )

    @api.depends("partner_id", "company_id")
    def _compute_tax_profile(self):
        for rec in self:
            profile = (
                self.env["fix.vendor.tax.profile"].for_partner(rec.partner_id, rec.company_id)
                if rec.partner_id
                else self.env["fix.vendor.tax.profile"]
            )
            rec.tax_profile_id = profile.id or False

    @api.depends(
        "line_ids.quantity",
        "line_ids.value",
        "partner_id",
        "company_id",
        "settlement_date",
        "period_end",
    )
    def _compute_amounts(self):
        Rate = self.env["fix.tax.rate"]
        for rec in self:
            rec.line_count = len(rec.line_ids)
            rec.quantity_total = round(sum(rec.line_ids.mapped("quantity")), 4)
            rec.value_untaxed = _q(sum(rec.line_ids.mapped("value")))
            profile = (
                self.env["fix.vendor.tax.profile"].for_partner(rec.partner_id, rec.company_id)
                if rec.partner_id
                else self.env["fix.vendor.tax.profile"]
            )
            # VAT follows the partner's M51 profile: a VAT-registered brand
            # (BIN on file, not merely turnover-enlisted) is charged the
            # standard VAT rate; no profile, no BIN or turnover-enlisted = no
            # VAT. A missing standard rate is refused at submission.
            registered = bool(profile and profile.bin and not profile.turnover_enlisted)
            rec.vat_registered = registered
            rate = 0.0
            if registered:
                on_date = rec.settlement_date or rec.period_end or fields.Date.context_today(rec)
                try:
                    rate = Rate.find_rate("vat", "standard", on_date, rec.company_id).rate
                except UserError:
                    rate = 0.0
            rec.vat_rate = rate
            rec.vat_amount = _q(rec.value_untaxed * rate / 100.0)
            rec.total_payable = _q(rec.value_untaxed + rec.vat_amount)

    @api.model_create_multi
    def create(self, vals_list):
        require_finance(self.env, "Raising a consignment settlement")
        recs = super().create(vals_list)
        for rec in recs:
            if rec.name in (False, "New"):
                rec._guarded().write(
                    {
                        "name": self.env["ir.sequence"]
                        .sudo()
                        .next_by_code("fix.ap.consignment.settlement")
                        or "CSET/New"
                    }
                )
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state not in ("draft", "rejected") and any(
                    rec._fix_guard_differs(k, vals[k], rec[k])
                    for k in (
                        "company_id",
                        "operating_unit_id",
                        "branch_id",
                        "brand_id",
                        "partner_id",
                        "period_start",
                        "period_end",
                        "settlement_date",
                    )
                    if k in vals
                ):
                    raise UserError(
                        "Settlement %s is %s: its brand, partner and period are fixed."
                        % (rec.name, rec.state)
                    )
        return super().write(vals)

    def unlink(self):
        if any(rec.state != "draft" for rec in self):
            raise UserError("Only a draft consignment settlement is deleted.")
        return super().unlink()

    # ------------------------------------------------------------ gathering --
    def _fix_brand_parts(self):
        """The brand's parts, as M15's own statement identifies them: the
        governed brand link, or the legacy device-brand text where the link
        is empty (fix.consignment.reconciliation._brand_parts)."""
        self.ensure_one()
        name = (self.brand_id.name or "").strip()
        domain = [("company_id", "in", [self.company_id.id, False])]
        if name:
            domain = [
                *domain,
                "|",
                ("brand_id", "=", self.brand_id.id),
                "&",
                ("brand_id", "=", False),
                ("device_brand", "=ilike", name),
            ]
        else:
            domain = [*domain, ("brand_id", "=", self.brand_id.id)]
        return self.env["fix.spare.part"].sudo().search(domain)

    def _fix_consumptions(self):
        """The brand's UN-settled consignment consumptions in this period.
        Read-only on M15: the issue ledger is the evidence."""
        self.ensure_one()
        if CONSUMPTION_MODEL not in self.env:
            raise UserError(
                "FR-APE-030: consignment settlement reads M15's consumption ledger, but the "
                "inventory module (cd_inventory) is not installed. Nothing was gathered."
            )
        parts = self._fix_brand_parts()
        if not parts:
            raise UserError(
                "FR-APE-030: brand %s has no spare parts in %s, so it has no consignment "
                "consumption to settle." % (self.brand_id.name, self.company_id.name)
            )
        start = fields.Datetime.to_datetime(self.period_start)
        end = fields.Datetime.to_datetime(self.period_end) + timedelta(days=1)
        consumptions = (
            self.env[CONSUMPTION_MODEL]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("state", "=", "consumed"),
                    ("ownership_class", "=", "consignment"),
                    ("product_id", "in", parts.ids),
                    ("consumed_at", ">=", start),
                    ("consumed_at", "<", end),
                ],
                order="consumed_at, id",
            )
        )
        if not consumptions:
            return consumptions
        settled = (
            self.env["fix.ap.consignment.settlement.line"]
            .sudo()
            .search(
                [
                    ("consumption_id", "in", consumptions.ids),
                    ("settlement_id", "!=", self.id),
                    ("settlement_id.state", "!=", "cancelled"),
                ]
            )
            .mapped("consumption_id")
        )
        return consumptions - settled

    def _fix_agreed_rate(self, part):
        """(rate, source, reference) for `part` from the partner's active
        consignment agreement's approved price list, or (0, 'manual', '').
        The rate is never guessed: with no agreed price the line stays at
        zero and submission refuses until finance enters the agreed rate."""
        self.ensure_one()
        if "fix.supplier" not in self.env or "fix.supplier.price.list" not in self.env:
            return 0.0, "manual", ""
        if not part.product_id:
            return 0.0, "manual", ""
        on_date = self.settlement_date or self.period_end
        supplier = self.env["fix.supplier"]._for_partner(self.partner_id, self.company_id)
        if not supplier:
            return 0.0, "manual", ""
        agreements = (
            self.env["fix.supplier.agreement"]
            .sudo()
            .search(
                [
                    ("supplier_id", "=", supplier.id),
                    ("agreement_type", "=", "consignment"),
                    ("state", "=", "active"),
                    ("term_from", "<=", on_date),
                    "|",
                    ("term_to", "=", False),
                    ("term_to", ">=", on_date),
                ],
                order="term_from desc, id desc",
            )
        )
        if not agreements:
            return 0.0, "manual", ""
        price = (
            self.env["fix.supplier.price.list"]
            .sudo()
            .search(
                [
                    ("agreement_id", "in", agreements.ids),
                    ("product_id", "=", part.product_id.id),
                    ("state", "=", "approved"),
                    ("valid_from", "<=", on_date),
                    "|",
                    ("valid_to", "=", False),
                    ("valid_to", ">=", on_date),
                ],
                order="valid_from desc, id desc",
                limit=1,
            )
        )
        if price:
            return price.price, "agreement", agreements[0].name
        return 0.0, "manual", ""

    def action_gather(self):
        """Gather the period's consumed consignment quantities at the agreed
        partner rate. Draft only."""
        require_finance(self.env, "Gathering a consignment settlement")
        for rec in self:
            if rec.state not in ("draft", "rejected"):
                raise UserError(
                    "Settlement %s is %s: reset it to draft to gather again."
                    % (rec.name, rec.state)
                )
            if not rec.brand_id or not rec.partner_id:
                raise UserError("A consignment settlement names its brand and brand partner.")
            if rec.period_end < rec.period_start:
                raise UserError("The settlement period ends before it starts.")
            consumptions = rec._fix_consumptions()
            if not consumptions:
                raise UserError(
                    "FR-APE-030: no unsettled consignment consumption of %s falls in %s - %s "
                    "(the parts were not issued on warranty jobs, or an earlier live "
                    "settlement already gathered them)."
                    % (rec.brand_id.name, rec.period_start, rec.period_end)
                )
            vals = []
            for consumption in consumptions:
                part = consumption.product_id.sudo()
                rate, source, reference = rec._fix_agreed_rate(part)
                vals.append(
                    (
                        0,
                        0,
                        {
                            "consumption_id": consumption.id,
                            "part_id": part.id,
                            "quantity": consumption.quantity,
                            "rate": rate,
                            "rate_source": source,
                            "rate_reference": reference,
                            "note": ""
                            if source == "agreement"
                            else "No agreed price list: enter the agreed partner rate.",
                        },
                    )
                )
            rec.line_ids.sudo().unlink()
            rec._guarded().write(
                {
                    "line_ids": vals,
                    "state": "draft",
                    "gathered_by_id": self.env.uid,
                    "gathered_at": fields.Datetime.now(),
                    "rejected_by_id": False,
                    "rejected_at": False,
                }
            )
            rec.message_post(
                body="Gathered %d consumed part line(s) of %s for %s - %s."
                % (len(vals), rec.brand_id.name, rec.period_start, rec.period_end)
            )
        return True

    # ------------------------------------------------------------- workflow --
    def _fix_duplicate_consumptions(self):
        """Lines whose consumption is already on another live settlement."""
        self.ensure_one()
        lines = self.line_ids
        if not lines:
            return lines
        other = (
            self.env["fix.ap.consignment.settlement.line"]
            .sudo()
            .search(
                [
                    ("consumption_id", "in", lines.mapped("consumption_id").ids),
                    ("settlement_id", "!=", self.id),
                    ("settlement_id.state", "!=", "cancelled"),
                ]
            )
        )
        return lines.filtered(lambda line: line.consumption_id in other.mapped("consumption_id"))

    def _fix_approval_levels(self):
        self.ensure_one()
        return (
            self.env["fix.ap.approval.rule"].sudo().levels_for(self.total_payable, self.company_id)
        )

    def action_submit(self):
        """Check the gathering and send it for a second person's approval.
        Every line needs a positive agreed rate; a consumption is settled
        once; the AP approval matrix must cover the amount."""
        require_finance(self.env, "Submitting a consignment settlement")
        for rec in self:
            if rec.state not in ("draft", "rejected"):
                raise UserError("Settlement %s is %s." % (rec.name, rec.state))
            if not rec.line_ids:
                raise UserError("Settlement %s has no gathered lines." % rec.name)
            if not rec.brand_id or not rec.partner_id:
                raise UserError("Settlement %s names no brand partner." % rec.name)
            duplicates = rec._fix_duplicate_consumptions()
            if duplicates:
                raise UserError(
                    "BRU-APE-21: settlement %s would settle %s twice: another live settlement "
                    "already includes %s."
                    % (
                        rec.name,
                        rec.brand_id.name,
                        ", ".join(duplicates.mapped("part_id.part_number")),
                    )
                )
            stale = rec.line_ids.filtered(
                lambda line: line.consumption_id.state != "consumed"
                or line.consumption_id.ownership_class != "consignment"
            )
            if stale:
                raise UserError(
                    "FR-APE-030: settlement %s includes consumption that is no longer a "
                    "consumed consignment issue (returned or cancelled): %s. Gather again."
                    % (
                        rec.name,
                        ", ".join(
                            "%s (%s)" % (line.part_id.part_number, line.consumption_id.name)
                            for line in stale
                        ),
                    )
                )
            missing = rec.line_ids.filtered(
                lambda line: (line.rate or 0.0) <= 0
                or abs((line.quantity or 0.0) - (line.consumption_id.quantity or 0.0)) > 1e-6
            )
            if missing:
                raise UserError(
                    "FR-APE-030: settlement %s needs a positive agreed rate on every line and "
                    "each line must carry exactly the consumed quantity: %s."
                    % (
                        rec.name,
                        ", ".join(
                            "%s (%s)" % (line.part_id.part_number, line.consumption_id.name)
                            for line in missing
                        ),
                    )
                )
            if rec.vat_registered and rec.vat_rate <= 0:
                raise UserError(
                    "BRU-APE-21: brand %s is VAT-registered but no standard VAT rate is in "
                    "force on %s: maintain the M51 Tax Rate Master (tax kind vat, code "
                    "standard)." % (rec.brand_id.name, rec.settlement_date or rec.period_end)
                )
            levels = rec._fix_approval_levels()
            if not levels:
                raise UserError(
                    "No AP approval-matrix level covers BDT %.2f in %s - maintain the AP "
                    "approval matrix first." % (rec.total_payable, rec.company_id.name)
                )
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by": self.env.uid,
                    "submitted_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Submitted for approval by %s (BDT %.2f)."
                % (self.env.user.name, rec.total_payable)
            )
        return True

    def action_approve(self):
        """A member of the highest AP-matrix level this amount reaches, who is
        not the submitter or creator, approves; the approval posts the
        settlement (Dr expense/consumption + input VAT / Cr AP control)."""
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Settlement %s is not awaiting approval." % rec.name)
            require_other_person(
                self.env,
                rec.submitted_by | rec.sudo().create_uid,
                "Approving settlement %s" % rec.name,
            )
            levels = rec._fix_approval_levels()
            if not levels:
                raise UserError(
                    "No AP approval-matrix level covers BDT %.2f in %s."
                    % (rec.total_payable, rec.company_id.name)
                )
            rule = levels[-1]
            if not self.env.su and rule.group_id not in self.env.user.all_group_ids:
                raise UserError(
                    "Settlement %s needs approval by a member of %s (level %d)."
                    % (rec.name, rule.group_id.display_name, rule.level)
                )
            rec._fix_post()
        return True

    def _fix_post(self):
        """Dr the module's purchase/consumption expense account for the
        gathered value, Dr input VAT where the partner's profile charges it,
        Cr AP control for the total — through the AP posting funnel, with the
        operating-unit, branch and brand dimensions."""
        self.ensure_one()
        env, company = self.env, self.company_id
        partner = self.partner_id.commercial_partner_id
        label = "Consignment settlement %s %s" % (self.brand_id.name, self.name)
        lines = [(ap_account(env, company, "expense"), label, self.value_untaxed, 0.0, partner)]
        if self.vat_amount:
            lines.append(
                (
                    ap_account(env, company, "vat_input"),
                    "Input VAT " + label,
                    self.vat_amount,
                    0.0,
                    partner,
                )
            )
        lines.append((ap_account(env, company, "ap"), label, 0.0, self.total_payable, partner))
        dims = {
            index: {
                "operating_unit_id": self.operating_unit_id.id,
                "branch_id": self.branch_id.id,
                "brand": self.brand_id.name,
            }
            for index in range(len(lines))
        }
        move = post_ap_move(
            env,
            company,
            ap_journal(env, company, "purchase"),
            self.settlement_date or self.period_end,
            label,
            lines,
            self.operating_unit_id,
            dims,
        )
        self._guarded().write(
            {
                "state": "approved",
                "approved_by_id": self.env.uid,
                "approved_at": fields.Datetime.now(),
                "move_id": move.id,
            }
        )
        self.message_post(
            body="Approved and posted by %s (entry %s)." % (self.env.user.name, move.name)
        )
        publish(
            env,
            "ap.consignment_settlement_raised",
            "fix.ap.consignment.settlement",
            self.id,
            {
                "settlement": self.name,
                "brand": self.brand_id.name,
                "partner_id": partner.id,
                "period_start": str(self.period_start),
                "period_end": str(self.period_end),
                "quantity": self.quantity_total,
                "value": self.value_untaxed,
                "vat": self.vat_amount,
                "payable": self.total_payable,
                "move_id": move.id,
            },
        )

    def action_reject(self):
        require_finance(self.env, "Rejecting a consignment settlement")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted settlement is rejected.")
            require_other_person(self.env, rec.submitted_by, "Rejecting settlement %s" % rec.name)
            rec._guarded().write(
                {
                    "state": "rejected",
                    "rejected_by_id": self.env.uid,
                    "rejected_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reset_draft(self):
        require_finance(self.env, "Resetting a consignment settlement to draft")
        for rec in self:
            if rec.state != "rejected":
                raise UserError("Only a rejected settlement returns to draft.")
            rec._guarded().write({"state": "draft"})
        return True

    def action_cancel(self):
        require_finance(self.env, "Cancelling a consignment settlement", manager=True)
        for rec in self:
            if rec.state not in ("draft", "rejected"):
                raise UserError(
                    "Settlement %s is %s: an approved settlement is not cancelled."
                    % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "cancelled"})
        return True


class FixApConsignmentSettlementLine(models.Model):
    """One consumed consignment part on a settlement, at the agreed rate."""

    _name = "fix.ap.consignment.settlement.line"
    _description = "Brand Consignment Settlement Line"
    _inherit = ["fix.guarded.mixin"]
    _order = "settlement_id, consumed_at, id"

    settlement_id = fields.Many2one(
        "fix.ap.consignment.settlement", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        related="settlement_id.company_id", store=True, readonly=True, index=True
    )
    operating_unit_id = fields.Many2one(
        related="settlement_id.operating_unit_id", store=True, readonly=True, index=True
    )
    currency_id = fields.Many2one(related="settlement_id.currency_id", store=True, readonly=True)
    consumption_id = fields.Many2one(
        CONSUMPTION_MODEL,
        string="M15 Consumption",
        required=True,
        index=True,
        ondelete="restrict",
        readonly=True,
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, index=True, readonly=True
    )
    part_number = fields.Char(
        related="part_id.part_number", string="Part Number", store=True, readonly=True
    )
    job_ref = fields.Char(
        related="consumption_id.service_order_ref", string="Warranty Job", store=True, readonly=True
    )
    consumed_at = fields.Datetime(
        related="consumption_id.consumed_at", string="Consumed At", store=True, readonly=True
    )
    quantity = fields.Float(string="Quantity", digits=(16, 4), readonly=True)
    rate = fields.Monetary(
        string="Agreed Rate",
        currency_field="currency_id",
        help="The brand's agreed price per unit for this part.",
    )
    value = fields.Monetary(
        string="Value",
        currency_field="currency_id",
        compute="_compute_value",
        store=True,
    )
    rate_source = fields.Selection(
        [("agreement", "Agreed price list"), ("manual", "Entered by finance")],
        string="Rate Source",
        readonly=True,
        default="manual",
    )
    rate_reference = fields.Char(string="Agreed Under", readonly=True)
    note = fields.Char()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "settlement_id",
            "consumption_id",
            "part_id",
            "quantity",
            "consumed_at",
            "rate_source",
            "rate_reference",
            "company_id",
            "operating_unit_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(line.settlement_id.state != "draft" for line in self):
            locked |= {"rate", "note"}
        return locked

    @api.depends("quantity", "rate")
    def _compute_value(self):
        for line in self:
            line.value = _q((line.quantity or 0.0) * (line.rate or 0.0))

    @api.constrains("rate")
    def _check_rate(self):
        for line in self:
            if (line.rate or 0.0) < 0:
                raise ValidationError("A settlement rate cannot be negative.")

    def write(self, vals):
        if self and not self._fix_guard_open():
            for line in self:
                if line.settlement_id.state != "draft" and any(
                    line._fix_guard_differs(k, vals[k], line[k])
                    for k in ("rate", "note")
                    if k in vals
                ):
                    raise UserError(
                        "Settlement %s left draft: its rates do not change."
                        % line.settlement_id.name
                    )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(line.settlement_id.state != "draft" for line in self):
            raise UserError("A settlement that left draft: its lines are evidence.")
        return super().unlink()
