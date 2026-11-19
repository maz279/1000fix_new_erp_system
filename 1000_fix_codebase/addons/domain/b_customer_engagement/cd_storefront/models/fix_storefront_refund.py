# fix_storefront_refund — M38: the controls every storefront refund shares.
#
# A04 workflow audit (2026-11-03) M38-4/5/6/9/10/13/17: a clerk wrote a return
# straight to "refunded"; a refund approved at BDT 100 was raised to 100,000
# and paid; BDT 500,000 was raised, approved, inspected and refunded by one
# plain clerk; a return was accepted on an unpaid order and on a 400-day-old
# one; an item inspected as scrap was refunded in full; the refund minted its
# own "MUSHAK-6.7/..." string and posted nothing; and the second RMA model
# (fix.storefront.rma) had none of the rules of the first.
#
# Both return models now inherit this mixin, so they cannot drift apart again:
#   requested --(operator authorises, inside the return window, on a paid
#   order)--> approved --(operator receives and inspects; the result sets the
#   refund)--> received --(M63 inbox: a refund approver holding the DOFA tier
#   of the amount, never the person who raised it)--> refund_approved
#   --(finance records the M20 credit note: a posted out_refund for this
#   customer and exactly this amount)--> refunded.
# The refund can never exceed what the customer paid on the order, less every
# other refund on it, and it is frozen once the return is authorised.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

GROUP_OPERATOR = "cd_storefront.group_fix_storefront_operator"
GROUP_PAYMENT = "cd_storefront.group_fix_storefront_payment_officer"
GROUP_REFUND_APPROVER = "cd_storefront.group_fix_storefront_refund_approver"

# A04 audit (2026-11-04): business defaults the business must confirm (report
# §7.3, refund policy). The return window is the Digital Commerce Operation
# Guidelines 2021 consumer window; the grade-B change-of-mind deduction is a
# restocking fee. Both are ir.config_parameter values so a ruling is a
# configuration act, not a release.
RETURN_WINDOW_PARAM = "cd_storefront.return_window_days"
RETURN_WINDOW_DAYS_DEFAULT = 7
RESTOCKING_FEE_PARAM = "cd_storefront.change_of_mind_restocking_pct"
RESTOCKING_FEE_PCT_DEFAULT = 20.0

# The refund approval reuses the estate's customer money-back ladder (the M34
# service-recovery concession ladder, cd_cx_feedback): every refund needs at
# least a Tier 1 sign-off. A default the business must confirm (report §7.3).
REFUND_DOFA_THRESHOLDS = [
    (1000.0, "tier_1"),
    (5000.0, "tier_2"),
    (10000.0, "tier_3"),
    (float("inf"), "tier_4"),
]

REFUND_STATES = [
    ("requested", "Return Requested"),
    ("approved", "Return Authorised"),
    ("received", "Item Received & Inspected"),
    ("refund_approved", "Refund Approved"),
    ("refunded", "Refund Disbursed"),
    ("rejected", "Return Rejected"),
]

INSPECTION_GRADES = [
    ("grade_a", "Grade A (Like New / Resalable)"),
    ("grade_b", "Grade B (Minor Wear / Refurbishable)"),
    ("scrap", "Damaged / Scrap Only"),
]

DISPOSITIONS = [
    ("restock", "Restock"),
    ("refurbish", "Refurbish"),
    ("scrap", "Scrap / E-Waste"),
]

# Fields that change only through the lifecycle below.
REFUND_GUARDED = frozenset(
    {
        "state",
        "inspected_condition",
        "disposition",
        "inspected_by_id",
        "inspected_at",
        "credit_note_id",
        "credit_note_ref",
        "refunded_at",
        "refunded_by_id",
        "rejection_reason",
    }
)
# Fields fixed once the return is authorised: the approval covers THIS
# refund for THIS customer on THIS order.
REFUND_FROZEN = frozenset({"order_id", "customer_id", "currency_id", "refund_amount", "reason"})


class FixApprovalMatrixStorefront(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("storefront_refund", "Storefront Refund")],
        ondelete={"storefront_refund": "cascade"},
    )


class FixStorefrontRefundMixin(models.AbstractModel):
    """The refund lifecycle shared by fix.storefront.return and .rma."""

    _name = "fix.storefront.refund.mixin"
    _description = "Storefront Refund Controls"
    # fix.dofa.mixin alone: it brings the routed-approval and guard mixins.
    _inherit = ["fix.dofa.mixin"]

    _approval_domain = "storefront_refund"
    _approval_apply_method = "action_approve_refund"
    _approval_routed = True

    state = fields.Selection(
        REFUND_STATES, default="requested", required=True, tracking=True, copy=False
    )
    inspected_condition = fields.Selection(
        INSPECTION_GRADES, string="Inspection Result", copy=False
    )
    disposition = fields.Selection(DISPOSITIONS, readonly=True, copy=False)
    inspected_by_id = fields.Many2one("res.users", string="Inspected By", readonly=True, copy=False)
    inspected_at = fields.Datetime(string="Inspected At", readonly=True, copy=False)
    credit_note_id = fields.Many2one(
        "account.move",
        string="M20 Credit Note",
        readonly=True,
        copy=False,
        ondelete="restrict",
        help="The posted Mushak 6.7 credit note (out_refund) that paid this refund.",
    )
    credit_note_ref = fields.Char(
        string="NBR Mushak 6.7 Credit Note Ref",
        readonly=True,
        copy=False,
        help="The number of the M20 credit note, never a reference typed or minted here.",
    )
    refunded_at = fields.Datetime(readonly=True, copy=False)
    refunded_by_id = fields.Many2one(
        "res.users", string="Refund Recorded By", readonly=True, copy=False
    )
    rejection_reason = fields.Char(readonly=True, copy=False)

    # ------------------------------------------------------------ per model
    def _sf_change_of_mind(self) -> bool:
        """True when the customer returns for their own reason, not a fault."""
        return False

    def _sf_label(self) -> str:
        self.ensure_one()
        return self.name or self._description

    # ------------------------------------------------------------ DOFA hooks
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.refund_amount or 0.0

    def _dofa_thresholds(self):
        return REFUND_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "refund %s of BDT %.2f" % (self._sf_label(), self.refund_amount or 0.0)

    @api.depends("refund_amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_needed(self) -> bool:
        return self.state == "received" and super()._approval_needed()

    def _approval_holders(self, group):
        """The DOFA ladder picks the tier group; only its members who also hold
        the refund-approver role decide a refund."""
        users = super()._approval_holders(group)
        approvers = self.env.ref(GROUP_REFUND_APPROVER, raise_if_not_found=False)
        return users & approvers.sudo().all_user_ids if approvers else users.browse()

    def _approval_on_rejected(self, comment):
        for rec in self.filtered(lambda r: r.state == "received"):
            rec._guarded().write(
                {
                    "state": "rejected",
                    "rejection_reason": comment or "Refund rejected by the approver",
                }
            )

    def _dofa_void_approval(self, reason: str):
        """An approval that no longer covers the refund sends it back to the
        inspected state, to be approved again."""
        approved = self.filtered(lambda r: r.state == "refund_approved")
        result = super()._dofa_void_approval(reason)
        approved._guarded().write({"state": "received"})
        return result

    # ------------------------------------------------------------ the guard
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | REFUND_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state != "requested":
            locked |= REFUND_FROZEN
        if rec and rec.state in ("refunded", "rejected"):
            locked |= {"dofa_justification"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "requested"):
                changed = [
                    n
                    for n in REFUND_FROZEN & set(vals)
                    if n in rec._fields and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "%s cannot be changed on %s: the return is %s, and its refund was "
                        "authorised for these terms (A04 audit M38-4)."
                        % (
                            ", ".join(sorted(rec._fields[n].string or n for n in changed)),
                            rec._sf_label(),
                            dict(REFUND_STATES)[rec.state],
                        )
                    )
        return super().write(vals)

    # ------------------------------------------------------------ rules
    def _sf_require(self, xmlids, what):
        if self.env.su or any(self.env.user.has_group(x) for x in xmlids):
            return
        raise UserError(
            "%s needs the %s role." % (what, " or ".join(self.env.ref(x).name for x in xmlids))
        )

    def _sf_window_days(self) -> int:
        # a return on an order: that order's window (its return policy)
        if len(self) == 1 and self.order_id:
            return self.order_id.sudo()._sf_window_days()
        raw = self.env["ir.config_parameter"].sudo().get_param(RETURN_WINDOW_PARAM)
        try:
            return int(raw) if raw else RETURN_WINDOW_DAYS_DEFAULT
        except ValueError:
            return RETURN_WINDOW_DAYS_DEFAULT

    def _sf_refunded_elsewhere(self, order):
        """Refunds already committed on `order` by every other live return."""
        total = 0.0
        for model in ("fix.storefront.return", "fix.storefront.rma"):
            others = (
                self.env[model]
                .sudo()
                .search([("order_id", "=", order.id), ("state", "!=", "rejected")])
            )
            if model == self._name:
                others -= self.sudo()
            total += sum(others.mapped("refund_amount"))
        return total

    def _sf_check_order_returnable(self, order, customer, what):
        """A return refers to a paid order of its customer, inside the window."""
        order = order.sudo()
        if not order:
            raise ValidationError("%s needs the storefront order it returns." % what)
        if order.customer_id.commercial_partner_id != customer.commercial_partner_id:
            raise ValidationError(
                "%s: order %s belongs to %s, not to %s."
                % (what, order.name, order.customer_id.display_name, customer.display_name)
            )
        if order._sf_amount_paid() <= 0.0:
            raise ValidationError(
                "%s: order %s is %s and has not been paid; only a paid order can be "
                "returned (A04 audit M38-9)." % (what, order.name, order.state)
            )
        deadline = order._sf_return_deadline()
        today = fields.Date.context_today(self)
        if order.returns_closed or (deadline and today > deadline):
            raise ValidationError(
                "%s: the %d-day return window of order %s closed on %s."
                % (what, order._sf_window_days(), order.name, deadline)
            )

    def _sf_assert_returnable(self, what):
        for rec in self:
            rec._sf_check_order_returnable(rec.order_id, rec.customer_id, what)

    @api.constrains("refund_amount", "order_id", "state")
    def _check_refund_cap(self):
        """A04 audit M38-4: the cap lived only in the HTTP controller, so the
        model accepted BDT 100,000 on a BDT 2,500 order."""
        for rec in self:
            if rec.state == "rejected":
                continue
            amount = rec.refund_amount or 0.0
            if amount < 0:
                raise ValidationError("A refund cannot be negative.")
            if not rec.order_id:
                if amount > 0.005:
                    raise ValidationError(
                        "%s: a refund needs the storefront order it refunds." % rec._sf_label()
                    )
                continue
            order = rec.order_id.sudo()
            refundable = order._sf_amount_paid() - rec._sf_refunded_elsewhere(order)
            if amount > refundable + 0.005:
                raise ValidationError(
                    "%s: the refund of BDT %.2f exceeds what is refundable on order %s "
                    "(BDT %.2f paid, less the other refunds on it)."
                    % (rec._sf_label(), amount, order.name, max(refundable, 0.0))
                )

    @api.model_create_multi
    def create(self, vals_list):
        # Every path, the customer API (superuser) included: a return on an
        # unpaid order or outside the window is refused at the model.
        Order, Partner = self.env["fix.storefront.order"], self.env["res.partner"]
        for vals in vals_list:
            self._sf_check_order_returnable(
                Order.browse(vals.get("order_id") or []),
                Partner.browse(vals.get("customer_id") or []),
                "A return",
            )
        return super().create(vals_list)

    # ------------------------------------------------------------ lifecycle
    def action_approve(self):
        """Authorise the return (RMA): a storefront operator, on a paid order,
        inside the return window. The money is approved later, from the
        inbox, once the item has been inspected."""
        self._sf_require([GROUP_OPERATOR], "Authorising a return")
        for rec in self:
            if rec.state != "requested":
                raise UserError("Only a requested return can be approved")
            rec._sf_assert_returnable("Authorising the return")
            if (rec.refund_amount or 0.0) <= 0.0:
                raise UserError(
                    "%s: state the refund requested before authorising the return."
                    % rec._sf_label()
                )
            rec._guarded().write({"state": "approved"})
        return True

    def _sf_refund_after_inspection(self, condition):
        """A04 audit M38-10: the inspection result drives the refund. A fault
        (defective, wrong, not as described) is refunded as requested at any
        grade. A change of mind is refunded in full at grade A, less the
        restocking fee at grade B, and not at all when the item comes back as
        scrap (the customer returned it damaged)."""
        self.ensure_one()
        requested = self.refund_amount or 0.0
        if not self._sf_change_of_mind() or condition == "grade_a":
            return requested
        if condition == "scrap":
            return 0.0
        # the order's return policy (M38 capture audit, 19 Nov 2026), else
        # the configured default
        fee = self.order_id.sudo()._sf_restocking_pct()
        return self.currency_id.round(requested * (100.0 - fee) / 100.0)

    def action_receive_and_inspect(self, condition=None):
        """Record the inspector's result - never a default grade. The result
        sets the disposition and the refund the approver will be asked for."""
        self._sf_require([GROUP_OPERATOR], "Receiving and inspecting a return")
        valid = dict(INSPECTION_GRADES)
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved return can be received")
            result = condition or rec.inspected_condition
            if not result:
                raise UserError("Record the inspection result before receiving the return")
            if result not in valid:
                raise UserError(
                    "Unknown inspection result %r (expected one of: %s)."
                    % (result, ", ".join(sorted(valid)))
                )
            refund = rec._sf_refund_after_inspection(result)
            vals = {
                "inspected_condition": result,
                "disposition": {"grade_a": "restock", "grade_b": "refurbish"}.get(result, "scrap"),
                "inspected_by_id": self.env.user.id,
                "inspected_at": fields.Datetime.now(),
                "refund_amount": refund,
                "state": "received",
            }
            if refund <= 0.0:
                vals.update(
                    {
                        "state": "rejected",
                        "rejection_reason": "Change-of-mind item came back as scrap: no refund "
                        "is due under the return policy.",
                    }
                )
            rec._guarded().write(vals)
            rec._sf_restock_graded_stock(result)
            if hasattr(rec, "message_post"):
                rec.message_post(
                    body="Inspected as %s: refund due BDT %.2f." % (valid[result], refund)
                )
        return True

    def _sf_restock_graded_stock(self, condition):
        """A graded device that comes back goes back into the refurb stock it
        was sold from (grade A/B) or is scrapped."""
        self.ensure_one()
        stock = self.order_id.sudo().line_ids.mapped("graded_stock_id")
        for item in stock.filtered(lambda s: s.state in ("reserved", "sold")):
            item.write({"state": "scrapped" if condition == "scrap" else "in_stock"})

    def action_approve_refund(self):
        """Approve the refund, from the approver's M63 inbox only. The approver
        holds the refund-approver role and the DOFA tier of the amount, did
        not raise the return, and the amount is pinned. The refund instruction
        goes to finance (storefront.refund_approved); the refund is complete
        only when finance records the M20 credit note."""
        self._approval_assert_routed()
        self._sf_require([GROUP_REFUND_APPROVER], "Approving a refund")
        for rec in self:
            if rec.state != "received":
                raise UserError("Cannot refund prior to physical receipt and inspection")
            if (rec.refund_amount or 0.0) <= 0.0:
                raise UserError("%s: there is no refund to approve." % rec._sf_label())
            rec._sf_assert_returnable_amount()
            # tier group, segregation of duties, justification, amount pin
            rec.action_dofa_approve()
            rec._guarded().write({"state": "refund_approved"})
            order = rec.order_id.sudo()
            publish(
                rec.env,
                "storefront.refund_approved",
                rec._name,
                rec.id,
                {
                    "return_model": rec._name,
                    "return_id": rec.id,
                    "rma_number": rec.name,
                    "order_id": order.id,
                    "order_name": order.name,
                    "customer_id": rec.customer_id.id,
                    "refund_amount": float(rec.refund_amount or 0.0),
                    "currency": rec.currency_id.name,
                    "rail": order.payment_rail,
                    "payment_ref": order.payment_ref or "",
                    "receipt_id": order.payment_receipt_id.id or None,
                    "approved_by": rec.env.user.id,
                },
            )
        return True

    def _sf_assert_returnable_amount(self):
        """Re-check the cap at the point of decision (a cap that only fires on
        save does not cover a refund approved after another one was paid)."""
        self._check_refund_cap()

    def action_reject(self, reason=None):
        self._sf_require([GROUP_OPERATOR, GROUP_REFUND_APPROVER], "Rejecting a return")
        reason = (str(reason).strip() if reason else "") or False
        for rec in self:
            if rec.state in ("refund_approved", "refunded", "rejected"):
                raise UserError(
                    "%s is already %s." % (rec._sf_label(), dict(REFUND_STATES)[rec.state])
                )
            if rec.approval_state == "pending":
                rec._approval_void("the return was rejected by %s" % self.env.user.name)
            rec._guarded().write({"state": "rejected", "rejection_reason": reason})
        return True

    def _sf_find_credit_note(self, credit_note):
        if isinstance(credit_note, models.BaseModel):
            return credit_note.sudo().exists()
        Move = self.env["account.move"].sudo()
        try:
            return Move.browse(int(credit_note)).exists()
        except (TypeError, ValueError):
            pass
        ref = (str(credit_note or "")).strip()
        return Move.search([("name", "=", ref)], limit=1) if ref else Move

    def action_record_credit_note(self, credit_note=None):
        """Complete an approved refund with the M20 credit note that paid it:
        a POSTED customer credit note (out_refund) of this customer for
        exactly the approved amount, used by no other refund. Finance (the
        payment officer) records it, or the M20 bridge does as the superuser.
        A04 audit M38-7/17: the reference is the credit note's own number,
        never one typed or minted here."""
        self._sf_require([GROUP_PAYMENT], "Recording a refund's credit note")
        for rec in self:
            if rec.state != "refund_approved":
                raise UserError(
                    "%s: only an approved refund is completed by its credit note." % rec._sf_label()
                )
            rec._dofa_assert_approved("The refund")
            move = rec._sf_find_credit_note(credit_note)
            if not move:
                raise UserError("No M20 credit note %r exists." % (credit_note,))
            if move.move_type != "out_refund" or move.state != "posted":
                raise UserError(
                    "%s is not a posted customer credit note (Mushak 6.7)." % move.display_name
                )
            if move.partner_id.commercial_partner_id != rec.customer_id.commercial_partner_id:
                raise UserError(
                    "Credit note %s is for %s, not for %s."
                    % (move.name, move.partner_id.display_name, rec.customer_id.display_name)
                )
            if abs((move.amount_total or 0.0) - (rec.refund_amount or 0.0)) > 0.005:
                raise UserError(
                    "Credit note %s is for BDT %.2f; the approved refund is BDT %.2f."
                    % (move.name, move.amount_total, rec.refund_amount)
                )
            for model in ("fix.storefront.return", "fix.storefront.rma"):
                used = self.env[model].sudo().search([("credit_note_id", "=", move.id)])
                if model == rec._name:
                    used -= rec.sudo()
                if used:
                    raise UserError(
                        "Credit note %s already pays %s." % (move.name, used[0].display_name)
                    )
            rec._guarded().write(
                {
                    "credit_note_id": move.id,
                    "credit_note_ref": move.name,
                    "refunded_at": fields.Datetime.now(),
                    "refunded_by_id": self.env.user.id,
                    "state": "refunded",
                }
            )
            publish(
                rec.env,
                "storefront.refund_processed",
                rec._name,
                rec.id,
                {
                    "rma_number": rec.name,
                    "customer": rec.customer_id.name,
                    "refund_amount": float(rec.refund_amount or 0.0),
                    "condition": rec.inspected_condition,
                    "credit_note_ref": rec.credit_note_ref,
                },
            )
        return True
