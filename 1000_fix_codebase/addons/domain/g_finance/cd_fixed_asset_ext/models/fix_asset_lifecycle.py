# fix_asset_lifecycle — M49 asset lifecycle documents:
#   * fix.asset.transfer    — branch / custodian moves, acknowledged by the receiver
#   * fix.asset.revaluation — IAS 16 revaluation, IAS 36 impairment / reversal
#   * fix.asset.disposal    — sale / scrap / write-off with gain or loss
#
# A08 workflow audit (2026-11-04): an accountant wrote a disposal 'approved'
# and 'posted', a revaluation 'posted' with a typed cost_delta of 1,000,000;
# managers rewrote requested_by_id and approved their own; proceeds were cut
# 100,000 -> 1 after approval; a 40,000,000 write-off and a 780,000 surplus
# were approved by one manager; a revaluation needed no valuer report; the
# custodian moved by a plain write. Revaluations and disposals are routed by
# amount through the M63 inbox (fix.asset.dofa.mixin), approve and post are
# separate steps, approved terms are pinned, a write-off needs an incident
# reference, a sale is invoiced through M20, and a transfer moves the asset
# only when the receiver acknowledges it.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_asset_common import (
    USER_GROUP,
    disposal_ladder,
    money,
    post_entry,
    require_accounts,
    require_group,
    revaluation_ladder,
)


class FixAssetTransfer(models.Model):
    _name = "fix.asset.transfer"
    _description = "Asset Transfer"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    asset_id = fields.Many2one(
        "fix.fixed.asset",
        string="Asset",
        required=True,
        index=True,
        domain="[('state', '=', 'active')]",
        tracking=True,
    )
    company_id = fields.Many2one(related="asset_id.company_id", store=True, index=True)
    date = fields.Date(
        string="Transfer Date", required=True, default=fields.Date.context_today, tracking=True
    )
    from_operating_unit_id = fields.Many2one(
        "operating.unit", string="From Branch", readonly=True, copy=False
    )
    from_custodian_id = fields.Many2one(
        "hr.employee", string="From Custodian", readonly=True, copy=False
    )
    operating_unit_id = fields.Many2one("operating.unit", string="To Branch", tracking=True)
    to_custodian_id = fields.Many2one("hr.employee", string="To Custodian", tracking=True)
    reason = fields.Text(string="Reason")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Awaiting Acknowledgement"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    done_by_id = fields.Many2one("res.users", string="Confirmed By", readonly=True, copy=False)
    acknowledged_by_id = fields.Many2one(
        "res.users", string="Acknowledged By", readonly=True, copy=False
    )
    acknowledged_at = fields.Datetime(string="Acknowledged On", readonly=True, copy=False)

    _TERMS = frozenset({"asset_id", "operating_unit_id", "to_custodian_id", "date"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "from_operating_unit_id",
            "from_custodian_id",
            "done_by_id",
            "acknowledged_by_id",
            "acknowledged_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS)
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open() and set(vals) & self._TERMS:
            done = self.filtered(lambda t: t.state != "draft")
            if any(
                t._fix_guard_differs(n, vals[n], t[n])
                for t in done
                for n in set(vals) & self._TERMS
            ):
                raise UserError(
                    self.env._("A confirmed transfer cannot change; cancel it instead.")
                )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.asset.transfer") or "/"
        return super().create(vals_list)

    def action_confirm(self):
        """Send the asset: the from-side is captured; the asset moves when the
        receiver acknowledges (BRU-FXA-09)."""
        require_group(self.env, USER_GROUP, "Confirming a transfer")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft transfers can be confirmed."))
            asset = rec.asset_id
            if asset.state != "active":
                raise UserError(self.env._("Only active assets can be transferred."))
            to_ou = rec.operating_unit_id or asset.operating_unit_id
            to_custodian = rec.to_custodian_id or asset.custodian_id
            if to_ou == asset.operating_unit_id and to_custodian == asset.custodian_id:
                raise UserError(
                    self.env._("Choose a different branch or custodian — nothing would move.")
                )
            rec._guarded().write(
                {
                    "from_operating_unit_id": asset.operating_unit_id.id,
                    "from_custodian_id": asset.custodian_id.id,
                    "operating_unit_id": to_ou.id,
                    "to_custodian_id": to_custodian.id,
                    "state": "confirmed",
                    "done_by_id": self.env.user.id,
                }
            )
        return True

    def action_acknowledge(self):
        """The receiver acknowledges: the receiving custodian (their user), or,
        when the custodian has no login, a finance user other than the sender.
        Only then do the asset's branch and custodian change."""
        for rec in self:
            if rec.state != "confirmed":
                raise UserError(self.env._("Only a confirmed transfer is acknowledged."))
            receiver = rec.to_custodian_id.sudo().user_id
            if not self.env.su:
                if receiver and receiver != self.env.user:
                    raise UserError(
                        self.env._(
                            "%s is acknowledged by the receiving custodian %s.",
                            rec.name,
                            rec.to_custodian_id.name,
                        )
                    )
                if not receiver:
                    require_group(self.env, USER_GROUP, "Acknowledging a transfer")
                    if self.env.user == rec.done_by_id:
                        raise UserError(
                            self.env._(
                                "Segregation of duties: the sender of %s does not acknowledge "
                                "its receipt.",
                                rec.name,
                            )
                        )
            asset = rec.asset_id
            if asset.state != "active":
                raise UserError(self.env._("Only active assets can be transferred."))
            asset._guarded().write(
                {
                    "operating_unit_id": rec.operating_unit_id.id,
                    "custodian_id": rec.to_custodian_id.id,
                }
            )
            rec._guarded().write(
                {
                    "state": "done",
                    "acknowledged_by_id": self.env.uid,
                    "acknowledged_at": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "confirmed"):
                raise UserError(self.env._("Only an open transfer can be cancelled."))
            rec._guarded().write({"state": "cancelled"})
        return True


class FixAssetRevaluation(models.Model):
    _name = "fix.asset.revaluation"
    _description = "Asset Revaluation / Impairment"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.asset.dofa.mixin"]
    _order = "date desc, id desc"
    _approval_domain = "asset_revaluation"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    asset_id = fields.Many2one(
        "fix.fixed.asset",
        string="Asset",
        required=True,
        index=True,
        domain="[('state', '=', 'active')]",
        tracking=True,
    )
    company_id = fields.Many2one(related="asset_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="asset_id.operating_unit_id", store=True, string="Branch"
    )
    currency_id = fields.Many2one(related="asset_id.currency_id")
    kind = fields.Selection(
        [
            ("revaluation", "Revaluation (IAS 16)"),
            ("impairment", "Impairment (IAS 36)"),
            ("impairment_reversal", "Impairment Reversal (IAS 36)"),
        ],
        string="Type",
        required=True,
        default="revaluation",
        tracking=True,
    )
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    new_value = fields.Monetary(
        string="Fair Value / Recoverable Amount",
        required=True,
        tracking=True,
        help="Revaluation: the fair value (IAS 16.31). Impairment: the recoverable "
        "amount — higher of fair value less costs of disposal and value in use (IAS 36.18).",
    )
    basis = fields.Text(string="Basis / Valuer Report")
    valuer_report_ids = fields.Many2many(
        "ir.attachment",
        "fix_asset_revaluation_valuer_report_rel",
        "revaluation_id",
        "attachment_id",
        string="Valuer Report",
        help="The independent valuer's report (revaluation) or the impairment test",
    )
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    posted_by_id = fields.Many2one("res.users", string="Posted By", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    carrying_amount = fields.Monetary(string="Carrying Amount Before", readonly=True, copy=False)
    cost_delta = fields.Monetary(string="Change in Cost", readonly=True, copy=False)
    accum_delta = fields.Monetary(string="Change in Impairment", readonly=True, copy=False)
    surplus_amount = fields.Monetary(
        string="To Revaluation Surplus (OCI)", readonly=True, copy=False
    )
    pl_amount = fields.Monetary(
        string="To Profit or Loss (Loss +, Gain -)", readonly=True, copy=False
    )
    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True, copy=False)

    _TERMS = frozenset({"asset_id", "kind", "date", "new_value"})

    # ---- DOFA --------------------------------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        if self.state == "posted":
            return abs(self.cost_delta - self.accum_delta)
        return abs((self.new_value or 0.0) - (self.asset_id.sudo().book_nbv or 0.0))

    def _dofa_thresholds(self):
        return revaluation_ladder(self.env)

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (change in carrying amount, %s)" % (self._dofa_amount(), self.name)

    @api.depends("new_value", "asset_id", "state")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _fix_terms_fields(self) -> set:
        return set(self._TERMS)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "approved_by_id",
            "posted_by_id",
            "carrying_amount",
            "cost_delta",
            "accum_delta",
            "surplus_amount",
            "pl_amount",
            "move_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS) | {"basis", "valuer_report_ids"}
        return locked

    def write(self, vals):
        moving = set(vals) & (self._TERMS | {"basis", "valuer_report_ids"})
        if self and moving and not self._fix_guard_open():
            frozen = self.filtered(lambda r: r.state in ("posted", "cancelled"))
            if any(r._fix_guard_differs(n, vals[n], r[n]) for r in frozen for n in moving):
                raise UserError(self.env._("A posted or cancelled revaluation cannot change."))
            moved = self.filtered(
                lambda r: (
                    r.state in ("submitted", "approved")
                    and any(r._fix_guard_differs(n, vals[n], r[n]) for n in moving)
                )
            )
            res = super().write(vals)
            for rec in moved:
                # the approval covered the figures and evidence it was given for
                rec.sudo()._dofa_void_approval("the revaluation terms changed")
                rec.sudo()._guarded().write({"state": "draft", "approved_by_id": False})
            return res
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.asset.revaluation") or "/"
        return super().create(vals_list)

    @api.constrains("new_value")
    def _check_value(self):
        for rec in self:
            if rec.new_value < 0:
                raise ValidationError(
                    self.env._("A fair value / recoverable amount cannot be negative.")
                )

    def _split(self):
        """The IAS 16 / IAS 36 split of the change in carrying amount:
        cost_delta, accum_delta, surplus_amount (+ credit OCI), pl_amount
        (+ loss, - gain)."""
        self.ensure_one()
        asset = self.asset_id
        others = asset.revaluation_ids.filtered(lambda r: r.state == "posted" and r != self)
        carrying = asset.book_nbv
        surplus = money(sum(others.mapped("surplus_amount")))
        if self.kind == "revaluation":
            diff = money(self.new_value - carrying)
            if not diff:
                raise UserError(self.env._("The fair value equals the carrying amount."))
            if diff > 0:
                # IAS 16.39: reverse earlier revaluation losses in P&L first
                prior_loss = money(
                    sum(others.filtered(lambda r: r.kind == "revaluation").mapped("pl_amount"))
                )
                to_pl = min(diff, max(prior_loss, 0.0))
                return carrying, diff, 0.0, money(diff - to_pl), -to_pl
            decrease = -diff
            from_surplus = min(decrease, max(surplus, 0.0))  # IAS 16.40
            return carrying, diff, 0.0, -from_surplus, money(decrease - from_surplus)
        if self.kind == "impairment":
            loss = money(carrying - self.new_value)
            if loss <= 0:
                raise UserError(
                    self.env._(
                        "The recoverable amount is not below the carrying amount — no impairment."
                    )
                )
            from_surplus = min(loss, max(surplus, 0.0))  # IAS 36.61 (revalued assets)
            return carrying, 0.0, loss, -from_surplus, money(loss - from_surplus)
        gain = money(self.new_value - carrying)
        if gain <= 0:
            raise UserError(self.env._("The recoverable amount is not above the carrying amount."))
        impaired = money(sum(others.mapped("accum_delta")))
        if gain > impaired:
            raise UserError(
                self.env._(
                    "An impairment reversal is capped at the net impairment recognised "
                    "(%s) — IAS 36.117.",
                    impaired,
                )
            )
        return carrying, 0.0, -gain, 0.0, -gain

    def action_submit(self):
        """Request the CFO-tier approval, with the evidence attached
        (A08 M49-9: the valuer report is required for a revaluation)."""
        require_group(self.env, USER_GROUP, "Submitting a revaluation / impairment")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft documents can be submitted."))
            if rec.asset_id.state != "active":
                raise UserError(self.env._("Only active assets can be revalued or impaired."))
            if not (rec.basis or "").strip():
                raise UserError(self.env._("State the basis of %s (valuer / test).", rec.name))
            if rec.kind == "revaluation" and not rec.valuer_report_ids:
                raise UserError(
                    self.env._("Attach the valuer's report to revaluation %s.", rec.name)
                )
            rec._split()  # refuses a revaluation that changes nothing
            rec._guarded().write({"state": "submitted"})
            if rec._approval_needed():
                rec.action_request_approval(justification=rec.basis)
        return True

    def _fix_before_approve(self):
        if self.state != "submitted":
            raise UserError(self.env._("Only submitted revaluations are approved."))

    def _fix_after_approve(self):
        self._fix_stamp_approved({"state": "approved"})

    def _approval_on_rejected(self, comment):
        self.sudo()._guarded().write({"state": "draft"})

    def action_post(self):
        """Post an APPROVED revaluation / impairment (a separate step from the
        approval): Dr/Cr asset and accumulated, surplus (OCI) and P&L."""
        require_group(self.env, USER_GROUP, "Posting a revaluation / impairment")
        for rec in self:
            if rec.state != "approved":
                raise UserError(
                    self.env._("%s is %s: it is posted once approved.", rec.name, rec.state)
                )
            if rec._approval_needed():
                rec._dofa_assert_approved("Posting %s" % rec.name)
            asset = rec.asset_id
            if asset.state != "active":
                raise UserError(self.env._("Only active assets can be revalued or impaired."))
            cat = asset.category_id
            if not cat:
                raise UserError(
                    self.env._("Choose the asset category of %s first.", asset.display_name)
                )
            carrying, cost_delta, accum_delta, surplus, pl = rec._split()
            needed = ["journal_id"]
            if cost_delta:
                needed.append("asset_account_id")
            if accum_delta:
                needed.append("accumulated_account_id")
            if surplus:
                needed.append("revaluation_surplus_account_id")
            if pl:
                needed.append("impairment_account_id")
            require_accounts(cat, needed, "Revaluation / impairment")
            label = "%s %s" % (rec.name, asset.display_name)
            lines = []
            if cost_delta:
                lines.append((cat.asset_account_id, cost_delta, 0.0, label))
            if accum_delta:
                lines.append((cat.accumulated_account_id, 0.0, accum_delta, label))
            if surplus:
                lines.append((cat.revaluation_surplus_account_id, 0.0, surplus, label))
            if pl:
                lines.append((cat.impairment_account_id, pl, 0.0, label))
            move = post_entry(
                self.env,
                asset.company_id,
                cat.journal_id,
                rec.date,
                rec.name,
                lines,
                asset.operating_unit_id,
            )
            rec._guarded().write(
                {
                    "state": "posted",
                    "posted_by_id": self.env.uid,
                    "carrying_amount": carrying,
                    "cost_delta": cost_delta,
                    "accum_delta": accum_delta,
                    "surplus_amount": surplus,
                    "pl_amount": pl,
                    "move_id": move.id,
                }
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state in ("posted", "cancelled"):
                raise UserError(self.env._("Only an unposted document can be cancelled."))
            if rec.approval_state == "pending":
                rec.sudo()._approval_void("the revaluation was cancelled")
            rec.sudo()._dofa_void_approval("the revaluation was cancelled")
            rec._guarded().write({"state": "cancelled"})
        return True


class FixAssetDisposal(models.Model):
    _name = "fix.asset.disposal"
    _description = "Asset Disposal / Write-Off"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.asset.dofa.mixin"]
    _order = "date desc, id desc"
    _approval_domain = "asset_disposal"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    asset_id = fields.Many2one(
        "fix.fixed.asset",
        string="Asset",
        required=True,
        index=True,
        domain="[('state', '=', 'active')]",
        tracking=True,
    )
    company_id = fields.Many2one(related="asset_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="asset_id.operating_unit_id", store=True, string="Branch"
    )
    currency_id = fields.Many2one(related="asset_id.currency_id")
    kind = fields.Selection(
        [("sale", "Sale"), ("scrap", "Scrap"), ("write_off", "Write-Off (Lost / Missing)")],
        string="Type",
        required=True,
        default="sale",
        tracking=True,
    )
    date = fields.Date(
        string="Disposal Date", required=True, default=fields.Date.context_today, tracking=True
    )
    partner_id = fields.Many2one("res.partner", string="Buyer")
    proceeds = fields.Monetary(string="Proceeds", tracking=True)
    proceeds_account_id = fields.Many2one(
        "account.account",
        string="Proceeds Clearing Account",
        help="The account the M20 sale invoice credits and this disposal debits with the "
        "proceeds (clears to zero).",
    )
    reason = fields.Text(string="Reason")
    incident_ref = fields.Char(
        string="Incident Reference",
        tracking=True,
        help="Loss / theft / destruction: the incident (police GD, HSE case) reference "
        "(BRU-FXA-19)",
    )
    insurance_claim_ref = fields.Char(string="Insurance Claim", tracking=True)
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    posted_by_id = fields.Many2one("res.users", string="Posted By", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    cost = fields.Monetary(string="Cost Removed", readonly=True, copy=False)
    accumulated = fields.Monetary(
        string="Accumulated Depreciation Removed", readonly=True, copy=False
    )
    nbv = fields.Monetary(string="Net Book Value", readonly=True, copy=False)
    gain_loss = fields.Monetary(string="Gain (+) / Loss (-)", readonly=True, copy=False)
    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True, copy=False)
    sale_invoice_ref = fields.Char(string="M20 Sale Invoice", readonly=True, copy=False)
    sale_invoice_res_id = fields.Integer(string="M20 Sale Invoice ID", readonly=True, copy=False)

    _TERMS = frozenset(
        {"asset_id", "kind", "date", "partner_id", "proceeds", "proceeds_account_id"}
    )

    # ---- DOFA --------------------------------------------------------------
    def _dofa_amount(self) -> float:
        """What leaves the books: the larger of the NBV and the proceeds."""
        self.ensure_one()
        if self.state == "posted":
            return max(abs(self.nbv), abs(self.proceeds or 0.0))
        nbv = self.asset_id.sudo().book_nbv if self.asset_id else 0.0
        return max(abs(nbv or 0.0), abs(self.proceeds or 0.0))

    def _dofa_thresholds(self):
        return disposal_ladder(self.env, write_off=self.kind == "write_off")

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (disposal %s)" % (self._dofa_amount(), self.name)

    @api.depends("proceeds", "asset_id", "kind", "state")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _fix_terms_fields(self) -> set:
        return set(self._TERMS)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "approved_by_id",
            "posted_by_id",
            "cost",
            "accumulated",
            "nbv",
            "gain_loss",
            "move_id",
            "sale_invoice_ref",
            "sale_invoice_res_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS) | {"incident_ref", "reason"}
        return locked

    def write(self, vals):
        moving = set(vals) & (self._TERMS | {"incident_ref"})
        if self and moving and not self._fix_guard_open():
            frozen = self.filtered(lambda r: r.state in ("posted", "cancelled"))
            if any(r._fix_guard_differs(n, vals[n], r[n]) for r in frozen for n in moving):
                raise UserError(self.env._("A posted or cancelled disposal cannot change."))
            moved = self.filtered(
                lambda r: (
                    r.state in ("submitted", "approved")
                    and any(r._fix_guard_differs(n, vals[n], r[n]) for n in moving)
                )
            )
            res = super().write(vals)
            for rec in moved:
                # A08 M49-4: approved at 100,000, posted at 1.00 — no more
                rec.sudo()._dofa_void_approval("the disposal terms changed after approval")
                rec.sudo()._guarded().write({"state": "draft", "approved_by_id": False})
            return res
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.asset.disposal") or "/"
        return super().create(vals_list)

    @api.constrains("proceeds", "kind")
    def _check_proceeds(self):
        for rec in self:
            if rec.proceeds < 0:
                raise ValidationError(self.env._("Proceeds cannot be negative."))
            if rec.kind == "write_off" and rec.proceeds:
                raise ValidationError(
                    self.env._("A write-off has no proceeds — use Sale or Scrap.")
                )

    def action_submit(self):
        """Route the disposal for approval by the authority its amount needs."""
        require_group(self.env, USER_GROUP, "Submitting a disposal")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft disposals can be submitted."))
            if rec.asset_id.state != "active":
                raise UserError(self.env._("%s is not an active asset.", rec.asset_id.display_name))
            if rec.kind == "write_off" and not (
                (rec.incident_ref or "").strip() and (rec.reason or "").strip()
            ):
                raise UserError(
                    self.env._(
                        "A write-off for loss, theft or destruction needs the incident reference "
                        "and the reason (BRU-FXA-19)."
                    )
                )
            if rec.proceeds and not (rec.partner_id and rec.proceeds_account_id):
                raise UserError(
                    self.env._("A sale names the buyer and the proceeds clearing account.")
                )
            rec._guarded().write({"state": "submitted"})
            if rec._approval_needed():
                rec.action_request_approval(
                    justification=rec.reason or rec.incident_ref or rec.kind
                )
            else:
                rec._guarded().write({"state": "approved"})
        return True

    def _fix_before_approve(self):
        if self.state != "submitted":
            raise UserError(self.env._("Only submitted disposals can be approved."))

    def _fix_after_approve(self):
        self._fix_stamp_approved({"state": "approved"})

    def _approval_on_rejected(self, comment):
        self.sudo()._guarded().write({"state": "draft"})

    def _fix_sale_invoice(self):
        """The M20 sale invoice of the proceeds (B4's AR API): it credits the
        proceeds clearing account; this disposal debits it."""
        self.ensure_one()
        if "fix.ar.invoice" not in self.env or not hasattr(
            self.env["fix.ar.invoice"], "_fix_ar_invoice_from_source"
        ):
            raise UserError(
                self.env._(
                    "A disposal sale is invoiced through AR (M20): the AR invoice API "
                    "(fix.ar.invoice._fix_ar_invoice_from_source) is not installed."
                )
            )
        invoice = self.env["fix.ar.invoice"]._fix_ar_invoice_from_source(
            self,
            self.partner_id,
            [
                {
                    "description": "Sale of asset %s" % self.asset_id.display_name,
                    "taxable_amount": self.proceeds,
                }
            ],
            "Asset disposal %s approved by %s" % (self.name, self.approved_by_id.name or "-"),
            credit_account=self.proceeds_account_id,
            operating_unit=self.asset_id.operating_unit_id or None,
            invoice_date=self.date,
        )
        self._guarded().write(
            {"sale_invoice_ref": invoice.name or str(invoice.id), "sale_invoice_res_id": invoice.id}
        )
        return invoice

    def action_post(self):
        """Derecognise the asset (IAS 16.67-71): Dr accumulated depreciation,
        Dr proceeds clearing, Cr asset cost; the difference is the gain or
        loss. Only an APPROVED disposal, at the terms approved; a sale is
        invoiced to the buyer through M20 first."""
        require_group(self.env, USER_GROUP, "Posting a disposal")
        for rec in self:
            if rec.state != "approved":
                raise UserError(self.env._("Approve the disposal before posting it."))
            if rec._approval_needed():
                rec._dofa_assert_approved("Posting %s" % rec.name)
            asset = rec.asset_id
            if asset.state != "active":
                raise UserError(self.env._("%s is not an active asset.", asset.display_name))
            cat = asset.category_id
            if not cat:
                raise UserError(
                    self.env._("Choose the asset category of %s first.", asset.display_name)
                )
            cost = asset.cost
            accumulated = money(asset.accumulated_depreciation + asset.impairment_total)
            nbv = money(cost - accumulated)
            gain_loss = money(rec.proceeds - nbv)
            needed = ["journal_id", "asset_account_id"]
            if accumulated:
                needed.append("accumulated_account_id")
            if gain_loss > 0:
                needed.append("gain_account_id")
            elif gain_loss < 0:
                needed.append("loss_account_id")
            require_accounts(cat, needed, "Disposal")
            if rec.proceeds and not rec.proceeds_account_id:
                raise UserError(self.env._("Choose the proceeds account for %s.", rec.name))
            if rec.proceeds:
                rec._fix_sale_invoice()
            label = "%s %s" % (rec.name, asset.display_name)
            lines = [
                (cat.accumulated_account_id, accumulated, 0.0, label),
                (rec.proceeds_account_id, rec.proceeds, 0.0, label),
                (cat.asset_account_id, 0.0, cost, label),
            ]
            if gain_loss > 0:
                lines.append((cat.gain_account_id, 0.0, gain_loss, label))
            elif gain_loss < 0:
                lines.append((cat.loss_account_id, -gain_loss, 0.0, label))
            lines = [ln for ln in lines if ln[0]]
            move = post_entry(
                self.env,
                asset.company_id,
                cat.journal_id,
                rec.date,
                rec.name,
                lines,
                asset.operating_unit_id,
            )
            rec._guarded().write(
                {
                    "state": "posted",
                    "posted_by_id": self.env.uid,
                    "cost": cost,
                    "accumulated": accumulated,
                    "nbv": nbv,
                    "gain_loss": gain_loss,
                    "move_id": move.id,
                }
            )
            asset._mark_disposed(rec.date, move)
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state in ("posted", "cancelled"):
                raise UserError(self.env._("A posted disposal cannot be cancelled."))
            if rec.approval_state == "pending":
                rec.sudo()._approval_void("the disposal was cancelled")
            rec.sudo()._dofa_void_approval("the disposal was cancelled")
            rec._guarded().write({"state": "cancelled"})
        return True
