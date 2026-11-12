# cd_cash_position — Courier COD Remittance (G10, owner decision 12 Nov 2026).
#
# Third-party couriers (fix.courier.partner: Pathao, RedX, Steadfast) collect
# the cash on the COD storefront orders they deliver. The storefront bridge
# books that cash once, on the verified delivery, as the M20 cod receipt
# (Dr COD clearing / Cr AR). The rider COD settlement (cod_settlement.py)
# clears COD clearing only for in-house riders, so courier cash sat there
# with nothing to settle it.
#
# A courier pays out in batches, by bank transfer, net of what it charges
# (delivery fees, a COD handling charge, other deductions). One remittance is
# one such payout: the courier's batch reference, the delivered COD orders it
# covers (consignments carried by that courier), the charges it deducted and
# the net the bank received. It posts
#   Dr bank (net) + Dr courier charges (deductions) / Cr COD clearing (gross)
# and touches no receivable (the cod receipt already closed it).
#
# Controls, as on the rider settlement: an accountant prepares and submits, a
# different Accounting Administrator settles (maker-checker). The order set
# is loaded by the system, never typed, and re-checked at submit and settle:
# each order is a delivered COD order this courier carried, not prepaid or
# paid by another receipt (_fix_cod_paid_elsewhere), not waiting for its COD
# receipt, and not in another live remittance or rider settlement. The
# courier's statement must add up (gross - charges = net) and a batch is
# settled once. The rider settlement routes no DOFA band, so neither does
# this; the second person is the control.
from __future__ import annotations

import re

from odoo import api, fields, models
from odoo.exceptions import UserError

from .treasury_common import (
    GROUP_ACCOUNTANT,
    GROUP_ADMIN,
    bank_account_of,
    post_treasury_move,
    require_other_person,
    require_role,
    treasury_account,
)

_REF_SPLIT = re.compile(r"[\s,;]+")


def live_cod_orders(env, company, exclude=None):
    """Storefront orders already counted by a live COD settlement of the
    company: a rider settlement or a courier remittance that is not disputed.
    `exclude` is the settlement / remittance asking (it does not count)."""
    orders = env["fix.storefront.order"]
    for model in ("fix.cod.settlement", "fix.courier.remittance"):
        if model not in env:
            continue
        domain = [("company_id", "=", company.id), ("state", "!=", "disputed")]
        if exclude is not None and exclude._name == model and exclude.id:
            domain.append(("id", "!=", exclude.id))
        orders |= env[model].sudo().search(domain).mapped("order_ids")
    return orders


class FixCourierRemittance(models.Model):
    _name = "fix.courier.remittance"
    _description = "Courier COD Remittance"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "remittance_date desc, id desc"

    name = fields.Char(string="Remittance Ref", readonly=True, copy=False, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    courier_id = fields.Many2one(
        "fix.courier.partner", string="Courier", required=True, index=True, tracking=True
    )
    batch_ref = fields.Char(
        string="Courier Payout Ref",
        required=True,
        index=True,
        tracking=True,
        help="The courier's remittance / payout batch reference, as on its statement.",
    )
    remittance_date = fields.Date(
        string="Remittance Date", required=True, default=fields.Date.context_today
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Received Into (Bank)",
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
    )
    bank_ref = fields.Char(string="Bank Credit Ref", help="The bank's reference for the credit.")
    order_ids = fields.Many2many(
        "fix.storefront.order",
        "fix_courier_remittance_order_rel",
        "remittance_id",
        "order_id",
        string="COD Orders",
        readonly=True,
    )
    order_count = fields.Integer(compute="_compute_amounts", store=True, string="Orders")
    gross_amount = fields.Monetary(
        string="COD Collected",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
        help="The cash on delivery of the orders covered: what COD clearing holds for them.",
    )
    delivery_charges = fields.Monetary(
        string="Delivery Charges Deducted", currency_field="currency_id", tracking=True
    )
    cod_charges = fields.Monetary(
        string="COD Charges Deducted", currency_field="currency_id", tracking=True
    )
    other_charges = fields.Monetary(
        string="Other Deductions", currency_field="currency_id", tracking=True
    )
    total_charges = fields.Monetary(
        string="Charges Deducted",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
    )
    net_amount = fields.Monetary(
        string="Net Received",
        currency_field="currency_id",
        tracking=True,
        help="What the bank received from the courier for this batch.",
    )
    difference = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
        help="COD collected - charges - net received: must be 0 to submit.",
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
    submitted_by_id = fields.Many2one("res.users", string="Prepared By", readonly=True, copy=False)
    settled_by_id = fields.Many2one("res.users", string="Settled By", readonly=True, copy=False)
    dispute_reason = fields.Char(tracking=True)
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)

    _GUARDED = frozenset(
        {"name", "state", "submitted_by_id", "settled_by_id", "move_id", "order_ids"}
    )
    _TERMS = (
        "courier_id",
        "batch_ref",
        "remittance_date",
        "journal_id",
        "bank_ref",
        "delivery_charges",
        "cod_charges",
        "other_charges",
        "net_amount",
        "company_id",
        "currency_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self._TERMS)
        return locked

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            terms = set(self._TERMS) & set(vals)
            for rec in self.filtered(lambda r: r.state != "draft"):
                changed = [f for f in terms if rec._fix_guard_differs(f, vals[f], rec[f])]
                if changed:
                    raise UserError(
                        "%s was submitted: %s cannot change." % (rec.name, ", ".join(changed))
                    )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.courier.remittance") or "CCR"
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
        return super(FixCourierRemittance, self._guarded()).create(vals_list).with_env(self.env)

    @api.depends(
        "order_ids.total_amount", "delivery_charges", "cod_charges", "other_charges", "net_amount"
    )
    def _compute_amounts(self):
        for rec in self:
            rec.order_count = len(rec.order_ids)
            rec.gross_amount = round(sum(rec.order_ids.mapped("total_amount")), 2)
            rec.total_charges = round(
                (rec.delivery_charges or 0.0)
                + (rec.cod_charges or 0.0)
                + (rec.other_charges or 0.0),
                2,
            )
            rec.difference = round(
                rec.gross_amount - rec.total_charges - (rec.net_amount or 0.0), 2
            )

    # ------------------------------------------------------------ the orders
    def _order_problem(self, order, live):
        """Why `order` cannot be settled by this remittance, or ''."""
        self.ensure_one()
        order = order.sudo()
        cons = order.carrier_consignment_id
        if (
            order.payment_rail != "cod"
            or order.company_id != self.company_id
            or order.state != "delivered"
            or cons.state != "delivered"
            or cons.courier_partner_id != self.courier_id
        ):
            return "%s is not a delivered cash-on-delivery order carried by %s" % (
                order.name,
                self.courier_id.name,
            )
        if order._fix_cod_paid_elsewhere():
            return (
                "%s was paid other than by the courier's cash on delivery (prepaid or settled by "
                "another receipt)" % order.name
            )
        if "posting_state" in order._fields and order.posting_state == "pending":
            return "%s: its cash-on-delivery receipt is not booked yet (%s)" % (
                order.name,
                (order.posting_note or "books pending").strip(),
            )
        if order in live:
            return "%s is already in another COD settlement or courier remittance" % order.name
        return ""

    def _check_orders(self):
        for rec in self:
            live = live_cod_orders(self.env, rec.company_id, exclude=rec)
            problems = [p for p in (rec._order_problem(o, live) for o in rec.order_ids) if p]
            if problems:
                raise UserError("%s: %s." % (rec.name, "; ".join(problems)))

    def _open_orders(self):
        """Delivered COD orders this courier carried that no live settlement
        counts yet and that may be settled here."""
        self.ensure_one()
        orders = (
            self.env["fix.storefront.order"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("payment_rail", "=", "cod"),
                    ("state", "=", "delivered"),
                    ("carrier_consignment_id.courier_partner_id", "=", self.courier_id.id),
                    ("carrier_consignment_id.state", "=", "delivered"),
                ]
            )
        )
        live = live_cod_orders(self.env, self.company_id, exclude=self)
        return orders.filtered(lambda o: not self._order_problem(o, live))

    def _orders_named(self, references):
        """The orders the courier's statement names, by order number,
        consignment number or courier tracking (AWB) number."""
        self.ensure_one()
        Order = self.env["fix.storefront.order"].sudo()
        tokens = [t for t in _REF_SPLIT.split(references or "") if t]
        found = Order
        unknown = []
        for token in tokens:
            match = Order.search(
                [("company_id", "=", self.company_id.id), ("name", "=", token)]
            ) or Order.search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("carrier_consignment_id.name", "=", token),
                ]
            )
            if not match and "fix.courier.booking" in self.env:
                bookings = (
                    self.env["fix.courier.booking"]
                    .sudo()
                    .search([("awb_no", "=", token), ("company_id", "=", self.company_id.id)])
                )
                if bookings.consignment_id:
                    match = Order.search(
                        [("carrier_consignment_id", "in", bookings.consignment_id.ids)]
                    )
            if not match:
                unknown.append(token)
            found |= match
        if unknown:
            raise UserError(
                "%s: no storefront order, consignment or tracking number %s."
                % (self.name, ", ".join(unknown))
            )
        return found

    def action_load_orders(self, references=None):
        """Add orders to a draft remittance: the ones the courier's statement
        names (order, consignment or tracking numbers), or with none named,
        every open delivered COD order of the courier. A named order that
        cannot be settled here is refused with the reason."""
        require_role(self.env, GROUP_ACCOUNTANT, "Loading a courier remittance")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Orders are loaded on a draft remittance only.")
            if references and str(references).strip():
                named = rec._orders_named(str(references))
                live = live_cod_orders(self.env, rec.company_id, exclude=rec)
                problems = [p for p in (rec._order_problem(o, live) for o in named) if p]
                if problems:
                    raise UserError("%s: %s." % (rec.name, "; ".join(problems)))
            else:
                named = rec._open_orders()
            orders = rec.order_ids | named
            rec._guarded().write({"order_ids": [(6, 0, orders.ids)]})
        return True

    def action_remove_orders(self, references=None):
        """Take orders the courier's batch does not cover off a draft."""
        require_role(self.env, GROUP_ACCOUNTANT, "Changing a courier remittance")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Orders are removed from a draft remittance only.")
            if not (references and str(references).strip()):
                raise UserError("Name the orders to remove (order or consignment numbers).")
            named = rec._orders_named(str(references))
            rec._guarded().write({"order_ids": [(6, 0, (rec.order_ids - named).ids)]})
        return True

    # ------------------------------------------------------------ workflow
    def _check_terms(self):
        self.ensure_one()
        if not self.order_ids:
            raise UserError(
                "%s covers no delivered COD orders of %s: nothing to settle."
                % (self.name, self.courier_id.name)
            )
        if min(self.delivery_charges, self.cod_charges, self.other_charges) < 0:
            raise UserError("Charges deducted by the courier cannot be negative.")
        if (self.net_amount or 0.0) < 0:
            raise UserError("The net amount received cannot be negative.")
        if not (self.batch_ref or "").strip():
            raise UserError("Record the courier's payout reference.")
        if self.net_amount > 0.005:
            if not self.journal_id:
                raise UserError("Select the bank account the courier's payout was received into.")
            if self.journal_id.type != "bank":
                raise UserError("%s is not a bank account." % self.journal_id.display_name)
            if not (self.bank_ref or "").strip():
                raise UserError(
                    "Record the bank's reference for the courier's credit (statement / slip)."
                )
        if abs(self.difference) > 0.005:
            raise UserError(
                "%s does not add up: COD collected %.2f - charges %.2f - net received %.2f "
                "leaves %.2f unexplained. Correct the charges or the net from the courier's "
                "statement, or remove the orders the payout does not cover."
                % (
                    self.name,
                    self.gross_amount,
                    self.total_charges,
                    self.net_amount,
                    self.difference,
                )
            )
        other = self.sudo().search(
            [
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("courier_id", "=", self.courier_id.id),
                ("batch_ref", "=ilike", self.batch_ref.strip()),
                ("state", "!=", "disputed"),
            ],
            limit=1,
        )
        if other:
            raise UserError(
                "%s's payout %s is already settled or in progress on %s."
                % (self.courier_id.name, self.batch_ref, other.name)
            )

    def action_submit(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Submitting a courier remittance")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft remittance is submitted.")
            rec._check_terms()
            rec._check_orders()
            rec._guarded().write({"state": "submitted", "submitted_by_id": self.env.uid})
        return True

    def action_settle(self):
        """Approve and post: Dr bank (net) + Dr courier charges / Cr COD
        clearing (gross). Settled by an Accounting Administrator who did not
        prepare it."""
        require_role(self.env, GROUP_ADMIN, "Settling a courier remittance")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted remittance is settled.")
            require_other_person(
                self.env,
                rec.submitted_by_id | rec.create_uid,
                "Settling courier remittance %s" % rec.name,
            )
            rec._check_terms()
            rec._check_orders()
            clearing = treasury_account(self.env, rec.company_id, "cod_clearing")
            label = "%s payout %s" % (rec.courier_id.name, rec.batch_ref)
            lines = []
            if rec.net_amount > 0.005:
                lines.append((bank_account_of(rec.journal_id), label, rec.net_amount, 0.0, None))
            if rec.total_charges > 0.005:
                charges = treasury_account(self.env, rec.company_id, "courier_charges")
                lines.append(
                    (
                        charges,
                        "%s charges %s" % (rec.courier_id.name, rec.batch_ref),
                        rec.total_charges,
                        0.0,
                        None,
                    )
                )
            lines.append(
                (clearing, "COD collected by %s" % rec.courier_id.name, 0.0, rec.gross_amount, None)
            )
            move = post_treasury_move(
                self.env,
                rec.company_id,
                rec.remittance_date,
                "CCR %s - %s" % (rec.name, label),
                lines,
                source="treasury",
            )
            rec._guarded().write(
                {"state": "settled", "settled_by_id": self.env.uid, "move_id": move.id}
            )
            rec._fix_mark_bookings_settled()
        return True

    def _fix_mark_bookings_settled(self):
        """M03's courier bookings of the settled consignments show their COD
        as settled (the hub's 'COD pending' figure reads cod_settled_on)."""
        self.ensure_one()
        if "fix.courier.booking" not in self.env:
            return
        bookings = (
            self.env["fix.courier.booking"]
            .sudo()
            .search(
                [
                    ("consignment_id", "in", self.order_ids.carrier_consignment_id.ids),
                    ("partner_id", "=", self.courier_id.id),
                    ("cod_settled_on", "=", False),
                ]
            )
        )
        if bookings:
            bookings._guarded().write({"cod_settled_on": self.remittance_date})

    def action_dispute(self, reason=None):
        require_role(self.env, GROUP_ACCOUNTANT, "Disputing a courier remittance")
        for rec in self:
            if rec.state not in ("draft", "submitted"):
                raise UserError("A settled remittance is not disputed - reverse its entry instead.")
            why = (reason or rec.dispute_reason or "").strip()
            if not why:
                raise UserError("Record the dispute reason first.")
            rec._guarded().write({"state": "disputed", "dispute_reason": why})
        return True
