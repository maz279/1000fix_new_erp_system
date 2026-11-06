# cd_cash_position — Rider COD Settlement (A08 · M50, finance side only).
#
# Source of truth for what a rider collected: storefront orders paid "Cash on
# Delivery" (fix.storefront.order.payment_rail = cod) whose logistics
# consignment (fix.consignment) was delivered by that rider. The rider app
# and the collection itself belong to Logistics; finance settles the
# rider's remittance against the expected COD and books any shortage.
# Service-order cash collected by field technicians is NOT a COD source yet
# (no model records it) — the settlement says so instead of guessing.
#
# A08 workflow audit (M50-10): the submitter / settler stamps, the order set
# and the state are guarded (one manager rewrote submitted_by_id and settled
# his own COD; a bKash-paid order was written onto a rider's COD); the order
# set is re-checked at submit and settle; a shortage above the configured
# tolerance needs a second Accounting Administrator's approval before the
# settlement posts it to the rider receivable, and the rider then carries an
# open variance until recovered (BRU-TRE-04: `_fix_rider_has_open_variance`).
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError

from .treasury_common import (
    GROUP_ACCOUNTANT,
    GROUP_ADMIN,
    bank_account_of,
    float_param,
    post_treasury_move,
    require_other_person,
    require_role,
    treasury_account,
)

# Shortage a single settler may book (BDT). The spec leaves the variance
# thresholds open (M50 Q-04), so the default is 0: every shortage has a
# second approver.
PARAM_COD_TOLERANCE = "cd_cash_position.cod_shortage_tolerance"


class FixCodSettlement(models.Model):
    _name = "fix.cod.settlement"
    _description = "Rider COD Settlement"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "settlement_date desc, id desc"

    name = fields.Char(string="Settlement Ref", readonly=True, copy=False, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Receiving Branch", index=True)
    rider_id = fields.Many2one("hr.employee", string="Rider", required=True, index=True)
    settlement_date = fields.Date(required=True, default=fields.Date.context_today)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    order_ids = fields.Many2many(
        "fix.storefront.order",
        "fix_cod_settlement_order_rel",
        "settlement_id",
        "order_id",
        string="COD Orders",
        readonly=True,
    )
    order_count = fields.Integer(compute="_compute_amounts", store=True, string="Orders")
    expected_amount = fields.Monetary(
        string="COD Expected", currency_field="currency_id", compute="_compute_amounts", store=True
    )
    remittance_method = fields.Selection(
        [("cash", "Cash to Branch"), ("bank", "Bank Deposit"), ("mfs", "bKash / Nagad")],
        default="cash",
        required=True,
    )
    remittance_journal_id = fields.Many2one(
        "account.journal",
        string="Received Into",
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]",
    )
    remitted_amount = fields.Monetary(
        string="Remitted", currency_field="currency_id", tracking=True
    )
    remittance_ref = fields.Char(string="Remittance Ref / TrxID")
    variance = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
        help="Remitted less expected: negative = rider short",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("settled", "Settled"),
            ("disputed", "Disputed"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    submitted_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    settled_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    dispute_reason = fields.Char(tracking=True)
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)
    shortage_approved_by_id = fields.Many2one(
        "res.users", string="Shortage Approved By", readonly=True, copy=False
    )
    shortage_approved_at = fields.Datetime(readonly=True, copy=False)
    recovery_state = fields.Selection(
        [("none", "No Shortage"), ("open", "Recovery Open"), ("recovered", "Recovered")],
        default="none",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        help="A booked shortage stays open against the rider until HR / the rider repays it "
        "(BRU-TRE-04).",
    )
    recovery_ref = fields.Char(string="Recovery Reference", tracking=True)

    _COD_GUARDED = frozenset(
        {
            "name",
            "state",
            "submitted_by_id",
            "settled_by_id",
            "move_id",
            "order_ids",
            "shortage_approved_by_id",
            "shortage_approved_at",
            "recovery_state",
        }
    )
    _COD_TERMS = (
        "rider_id",
        "remitted_amount",
        "remittance_method",
        "remittance_journal_id",
        "remittance_ref",
        "settlement_date",
        "company_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._COD_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self._COD_TERMS)
        return locked

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            terms = set(self._COD_TERMS) & set(vals)
            for rec in self.filtered(lambda r: r.state != "draft"):
                changed = [f for f in terms if rec._fix_guard_differs(f, vals[f], rec[f])]
                if changed:
                    raise UserError(
                        "%s was submitted: %s cannot change." % (rec.name, ", ".join(changed))
                    )
        return super().write(vals)

    @api.depends("order_ids.total_amount", "remitted_amount")
    def _compute_amounts(self):
        for rec in self:
            rec.order_count = len(rec.order_ids)
            rec.expected_amount = sum(rec.order_ids.mapped("total_amount"))
            rec.variance = round(rec.remitted_amount - rec.expected_amount, 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.cod.settlement") or "COD"
                )
        if self.env.su or self._fix_guard_has_token():
            return super().create(vals_list)
        guarded = self._fix_guarded_fields() - {"name"}
        for vals in vals_list:
            bad = [k for k in guarded & set(vals) if vals[k] not in (False, None, "", 0, [])]
            if vals.get("state", "draft") != "draft":
                bad.append("state")
            if bad:
                self._fix_guard_refuse(set(bad))
        return super(FixCodSettlement, self._guarded()).create(vals_list).with_env(self.env)

    def _shortage(self) -> float:
        self.ensure_one()
        return round(max(-self.variance, 0.0), 2)

    def _needs_shortage_approval(self) -> bool:
        self.ensure_one()
        tolerance = float_param(self.env, PARAM_COD_TOLERANCE, 0.0)
        return self._shortage() > tolerance + 0.005

    def _check_orders(self):
        """Every order is a delivered COD order of THIS rider in this company,
        not in another live settlement."""
        for rec in self:
            bad = rec.order_ids.sudo().filtered(
                lambda o, r=rec: (
                    o.payment_rail != "cod"
                    or o.company_id != r.company_id
                    or o.carrier_consignment_id.rider_id != r.rider_id
                    or o.carrier_consignment_id.state != "delivered"
                    or o.state in ("cancelled", "draft")
                )
            )
            if bad:
                raise UserError(
                    "%s carries orders that are not this rider's delivered COD orders: %s."
                    % (rec.name, ", ".join(bad.mapped("name")))
                )
            other = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "!=", "disputed"),
                    ("order_ids", "in", rec.order_ids.ids),
                ],
                limit=1,
            )
            if other:
                raise UserError("Some orders of %s are already in %s." % (rec.name, other.name))

    @api.model
    def _fix_rider_has_open_variance(self, rider) -> bool:
        """BRU-TRE-04: a rider with an unrecovered COD shortage (or one awaiting
        settlement / in dispute) is blocked from further cash collection.
        Logistics asks this before assigning a COD consignment."""
        return bool(
            self.sudo().search_count(
                [
                    ("rider_id", "=", rider.id),
                    "|",
                    ("recovery_state", "=", "open"),
                    "&",
                    ("state", "in", ("submitted", "disputed")),
                    ("variance", "<", -0.005),
                ]
            )
        )

    @api.model
    def _open_cod_orders(self, rider, company):
        """Delivered COD orders of this rider not yet in a live settlement."""
        orders = self.env["fix.storefront.order"].search(
            [
                ("company_id", "=", company.id),
                ("payment_rail", "=", "cod"),
                ("state", "not in", ("cancelled", "draft")),
                ("carrier_consignment_id.rider_id", "=", rider.id),
                ("carrier_consignment_id.state", "=", "delivered"),
            ]
        )
        settled = self.search(
            [("company_id", "=", company.id), ("state", "!=", "disputed")]
        ).mapped("order_ids")
        return orders - settled

    def action_load_orders(self):
        """Pull every delivered, unsettled COD order of the rider."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Orders are loaded on a draft settlement only.")
            orders = self._open_cod_orders(rec.rider_id, rec.company_id) | rec.order_ids
            rec._guarded().write({"order_ids": [(6, 0, orders.ids)]})
        return True

    def action_submit(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Submitting a COD settlement")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft settlement is submitted.")
            if not rec.order_ids:
                raise UserError(
                    "No delivered COD orders for %s — nothing to settle." % rec.rider_id.name
                )
            if rec.remitted_amount < 0:
                raise UserError("The remitted amount cannot be negative.")
            if not rec.remittance_journal_id:
                raise UserError("Select the cash/bank account the remittance was received into.")
            if rec.remittance_method != "cash" and not (rec.remittance_ref or "").strip():
                raise UserError("A bank/MFS remittance needs its reference (TrxID / slip no).")
            rec._check_orders()
            rec._guarded().write({"state": "submitted", "submitted_by_id": self.env.uid})
        return True

    def action_approve_shortage(self):
        """A second Accounting Administrator accepts a shortage above the
        tolerance before it is booked against the rider."""
        require_role(self.env, GROUP_ADMIN, "Approving a rider COD shortage")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted settlement's shortage is approved.")
            if not rec._needs_shortage_approval():
                raise UserError("%s has no shortage above the tolerance." % rec.name)
            require_other_person(
                self.env,
                rec.submitted_by_id | rec.create_uid,
                "Approving the shortage of %s" % rec.name,
            )
            rec._guarded().write(
                {
                    "shortage_approved_by_id": self.env.uid,
                    "shortage_approved_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Shortage of %.2f approved by %s." % (rec._shortage(), self.env.user.name)
            )
        return True

    def action_settle(self):
        """Approve and post: Dr cash/bank (remitted) + Dr rider shortage
        (short) / Cr COD clearing (expected) [+ Cr rider shortage if over].
        The approver must not be the submitter (SoD)."""
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted settlement is settled.")
            if not self.env.su and rec.submitted_by_id == self.env.user:
                raise UserError("Segregation of duties: the submitter cannot settle their own COD.")
            require_role(self.env, GROUP_ADMIN, "Settling COD")
            rec._check_orders()
            if rec._needs_shortage_approval():
                if not rec.shortage_approved_by_id:
                    raise UserError(
                        "%s is %.2f short (tolerance %.2f, %s): a second Accounting "
                        "Administrator approves the shortage before it is settled."
                        % (
                            rec.name,
                            rec._shortage(),
                            float_param(self.env, PARAM_COD_TOLERANCE, 0.0),
                            PARAM_COD_TOLERANCE,
                        )
                    )
                require_other_person(
                    self.env, rec.shortage_approved_by_id, "Settling the shortage of %s" % rec.name
                )
            cash = bank_account_of(rec.remittance_journal_id)
            clearing = treasury_account(self.env, rec.company_id, "cod_clearing")
            lines = [(cash, "COD remitted %s" % rec.name, rec.remitted_amount, 0.0, None)]
            if rec.variance < -0.005:
                shortage = treasury_account(self.env, rec.company_id, "rider_shortage")
                lines.append(
                    (shortage, "Rider short %s" % rec.rider_id.name, -rec.variance, 0.0, None)
                )
            elif rec.variance > 0.005:
                shortage = treasury_account(self.env, rec.company_id, "rider_shortage")
                lines.append(
                    (shortage, "Rider over %s" % rec.rider_id.name, 0.0, rec.variance, None)
                )
            lines.append((clearing, "COD collected %s" % rec.name, 0.0, rec.expected_amount, None))
            move = post_treasury_move(
                self.env,
                rec.company_id,
                rec.settlement_date,
                "COD %s — %s" % (rec.name, rec.rider_id.name),
                lines,
                branch=rec.branch_id,
                source="treasury",
            )
            rec._guarded().write(
                {
                    "state": "settled",
                    "settled_by_id": self.env.uid,
                    "move_id": move.id,
                    "recovery_state": "open" if rec.variance < -0.005 else "none",
                }
            )
        return True

    def action_mark_recovered(self):
        """The rider's shortage was recovered (HR deduction / repayment)."""
        require_role(self.env, GROUP_ADMIN, "Closing a rider shortage")
        for rec in self:
            if rec.recovery_state != "open":
                raise UserError("%s has no open shortage." % rec.name)
            if not (rec.recovery_ref or "").strip():
                raise UserError("Record the recovery reference (HR deduction / receipt) first.")
            rec._guarded().write({"recovery_state": "recovered"})
        return True

    def action_dispute(self):
        for rec in self:
            if rec.state not in ("draft", "submitted"):
                raise UserError("A settled COD is not disputed — reverse its entry instead.")
            if not (rec.dispute_reason or "").strip():
                raise UserError("Record the dispute reason first.")
            rec._guarded().write({"state": "disputed"})
        return True
