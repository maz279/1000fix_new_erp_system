# G12 (owner decision 12 Nov 2026): a billed part that was never fitted.
#
# D-11 (fix_service_order_parts_gate) refuses the close of an order whose
# approved estimate bills a stocked part that no M15 issue covers. When the
# part was genuinely never fitted - not needed after all, the customer
# declined it on the bench, the wrong part was quoted - the order could never
# close: a delivered order is neither cancelled nor revised. The owner
# approved "an approved exemption or credit-note path". This is the
# exemption:
#
#   * raised for ONE part line of the order's approved estimate, with the
#     quantity not fitted and the reason (a code and the words), by the
#     service desk or the technician lead (an internal user; never a portal
#     user) on a delivered or closed order - before delivery the estimate is
#     revised instead;
#   * decided from the M63 inbox by someone else holding branch authority:
#     the routed approval of the sibling fix.so.approval (BRU-SRM-08 manager
#     key), DOFA Tier 2 with the engine's escalation. The engine routes away
#     from the requester and the creator; action_apply refuses a direct press,
#     a decider without Tier 2 authority and the requester (also as a
#     delegate);
#   * an APPROVED exemption counts as covered at the D-11 close gate;
#   * billing (cd_billing_engine, which extends this model) leaves the
#     exempted quantity off the invoice, or - when the order was invoiced
#     before the exemption - raises an M20 credit note for that part;
#   * request and decision are logged on the order's chatter, and the M63
#     request keeps its own immutable history.
#
# The quantity never exceeds what was billed on the line, less what M15
# issued for the part (a fitted part is not "not fitted") and less every
# other live exemption. It is checked again at the decision, because a part
# can be issued while the request waits.
from __future__ import annotations

from odoo import api, fields, models
from odoo.addons.cd_catalogue.models.fix_commercial_line import STOCK_LINE_TYPES
from odoo.exceptions import UserError

_EPS = 1e-6
# BRU-SRM-08's key holder: the branch manager, DOFA Tier 2.
_BRANCH_AUTHORITY_GROUP = "cd_entity_config.group_dofa_tier_2"
_RAISE_STATES = ("delivered", "closed")
LIVE_STATES = ("pending", "approved")

REASONS = [
    ("not_needed", "Not Needed After All"),
    ("customer_declined", "Customer Declined on the Bench"),
    ("wrong_part", "Wrong Part Quoted"),
    ("other", "Other (see reason)"),
]
STATES = [
    ("pending", "Pending Approval"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("withdrawn", "Withdrawn"),
]


def _qty(value: float) -> str:
    return ("%.4f" % value).rstrip("0").rstrip(".")


class FixSoPartExemption(models.Model):
    _name = "fix.so.part.exemption"
    _description = "Billed Part Not Fitted (Exemption)"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "id desc"

    _approval_domain = "so_part_exemption"
    _approval_apply_method = "action_apply"
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        # Everything: what was asked for is the request, the rest is the decision.
        return super()._fix_guarded_fields() | {
            "order_id",
            "estimate_line_id",
            "part_id",
            "quantity",
            "amount",
            "reason_code",
            "reason",
            "state",
            "requested_by_id",
            "requested_on",
            "approved_by_id",
            "decided_by_id",
            "decided_on",
            "decision_note",
        }

    name = fields.Char(compute="_compute_name", store=True)
    order_id = fields.Many2one(
        "fix.service.order", required=True, readonly=True, index=True, ondelete="cascade"
    )
    estimate_line_id = fields.Many2one(
        "fix.estimate.line",
        string="Estimate Line",
        required=True,
        readonly=True,
        index=True,
        ondelete="restrict",
    )
    estimate_id = fields.Many2one(related="estimate_line_id.estimate_id", store=True)
    product_id = fields.Many2one(related="estimate_line_id.product_id", store=True)
    part_id = fields.Many2one(
        "fix.spare.part",
        string="Spare Part",
        readonly=True,
        help="The M15 spare part the line bills; empty for a part that is not stocked.",
    )
    quantity = fields.Float(
        string="Quantity Not Fitted", required=True, readonly=True, digits="Product Unit of Measure"
    )
    company_id = fields.Many2one(related="order_id.company_id", store=True)
    branch_id = fields.Many2one(related="order_id.branch_id", store=True)
    operating_unit_id = fields.Many2one(related="order_id.operating_unit_id", store=True)
    currency_id = fields.Many2one(related="estimate_line_id.currency_id")
    amount = fields.Monetary(
        string="Value Not Billed",
        currency_field="currency_id",
        readonly=True,
        help="What the exempted quantity added to the estimate's grand total: its gross, "
        "less its share of the estimate discount, plus VAT at the estimate's rate. Pinned "
        "at the request.",
    )
    reason_code = fields.Selection(REASONS, string="Reason", required=True, readonly=True)
    reason = fields.Text(string="Reason (details)", required=True, readonly=True)
    state = fields.Selection(
        STATES, default="pending", required=True, readonly=True, index=True, tracking=True
    )
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True)
    requested_on = fields.Datetime(readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_on = fields.Datetime(readonly=True)
    decision_note = fields.Text(readonly=True)

    @api.depends("order_id.name", "estimate_line_id.description", "quantity")
    def _compute_name(self):
        for rec in self:
            rec.name = "Not fitted: %s x %s on %s" % (
                _qty(rec.quantity or 0.0),
                rec.estimate_line_id.description or "",
                rec.order_id.name or "",
            )

    # ---- engine hooks -----------------------------------------------------
    def _approval_amount(self) -> float:
        return self.amount or 0.0

    def _approval_tier(self):
        # Branch authority: the branch manager (Tier 2), escalating to Tier 3.
        return "tier_2"

    def _approval_excluded(self):
        excluded = super()._approval_excluded()
        return (excluded | self.requested_by_id).sudo()

    # ---- the quantities ---------------------------------------------------
    @api.model
    def _fix_live(self, domain, exclude=None):
        recs = self.sudo().search([*domain, ("state", "in", LIVE_STATES)])
        return recs - exclude if exclude else recs

    def _fix_room(self, line, part, order, exclude=None) -> tuple[float, str]:
        """(the most that may still be exempted on `line`, why that much)."""
        billed_line = line.quantity or 0.0
        on_line = sum(
            self._fix_live([("estimate_line_id", "=", line.id)], exclude).mapped("quantity")
        )
        room = billed_line - on_line
        why = "billed %s, already exempted %s" % (_qty(billed_line), _qty(on_line))
        if part:
            billed = order._fix_billed_stock_parts().get(part, 0.0)
            issued = order._fix_issued_stock_parts().get(part, 0.0)
            exempted = sum(
                self._fix_live(
                    [("order_id", "=", order.id), ("part_id", "=", part.id)], exclude
                ).mapped("quantity")
            )
            part_room = billed - issued - exempted
            if part_room < room:
                room = part_room
                why = "billed %s, issued %s, already exempted %s" % (
                    _qty(billed),
                    _qty(issued),
                    _qty(exempted),
                )
        return max(room, 0.0), why

    @api.model
    def _fix_value(self, line, qty) -> float:
        """What `qty` of `line` adds to its estimate's grand total."""
        est = line.estimate_id.sudo()
        if not line.quantity:
            return 0.0
        gross = qty * (line.unit_price or 0.0)
        chargeable = est._chargeable_total()
        share = (est.discount or 0.0) * gross / chargeable if chargeable > _EPS else 0.0
        # X5-03: the line's own VAT rate (M51 per line), as the invoice charges it
        rate = est._fix_line_vat_rates().get(line.id, est.vat_rate or 0.0)
        return round((gross - share) * (1.0 + (rate or 0.0) / 100.0), 2)

    # ---- requester side ---------------------------------------------------
    @api.model
    def _fix_raise(self, order, line, quantity, reason_code, reason):
        """Create the exemption and route it. Returns the record."""
        order.ensure_one()
        user = self.env.user
        if not self.env.su and (user.share or not user.has_group("base.group_user")):
            raise UserError(
                "A billed-part exemption is raised by the service desk or the technician lead."
            )
        if order.state not in _RAISE_STATES:
            raise UserError(
                "Order %s is %s: a billed part that was not fitted is exempted on a delivered "
                "or closed order. Before delivery, revise the estimate instead."
                % (order.name, order.state)
            )
        reason = (reason or "").strip()
        if reason_code not in dict(REASONS):
            raise UserError(
                "Give the reason the part was not fitted: %s."
                % ", ".join(label for _code, label in REASONS)
            )
        if not reason:
            raise UserError("Describe why the part was not fitted.")
        line = line.sudo().exists() if line else line
        estimate = order._fix_governing_estimate()
        if not line or not estimate or estimate.state != "approved" or line.estimate_id != estimate:
            raise UserError(
                "The exemption is for a part line of order %s's approved estimate." % order.name
            )
        if line.line_type not in STOCK_LINE_TYPES:
            raise UserError(
                "%s is a %s line: only a billed part can be exempted as not fitted."
                % (line.description, line.line_type)
            )
        quantity = float(quantity or 0.0)
        if quantity <= _EPS:
            raise UserError("The quantity not fitted must be more than zero.")
        part = order._fix_stock_part_for(line.product_id)
        room, why = self._fix_room(line, part, order)
        if quantity - room > _EPS:
            raise UserError(
                "%s on order %s: at most %s can be exempted as not fitted (%s)."
                % (
                    "%s %s" % (part.part_number, part.name) if part else line.description,
                    order.name,
                    _qty(room),
                    why,
                )
            )
        created = self._guarded().create(
            {
                "order_id": order.id,
                "estimate_line_id": line.id,
                "part_id": part.id if part else False,
                "quantity": quantity,
                "amount": self._fix_value(line, quantity),
                "reason_code": reason_code,
                "reason": reason,
                "state": "pending",
                "requested_by_id": user.id,
                "requested_on": fields.Datetime.now(),
            }
        )
        # Re-browsed WITHOUT the guard token: the record handed back (and
        # routed) must not carry the transition's licence to its caller.
        rec = self.browse(created.id)
        rec.action_request_approval(justification=reason)
        rec._fix_log(
            "Billed part not fitted: exemption requested by %s for %s x %s (%s: %s); routed "
            "to a branch manager's inbox."
            % (user.name, _qty(quantity), rec._fix_part_label(), dict(REASONS)[reason_code], reason)
        )
        return rec

    def _fix_part_label(self) -> str:
        self.ensure_one()
        part = self.sudo().part_id
        if part:
            return "%s %s" % (part.part_number, part.name)
        return self.sudo().estimate_line_id.description or ""

    def _fix_log(self, body):
        for rec in self:
            rec.order_id.sudo().message_post(body=body)

    # ---- the decision -----------------------------------------------------
    def action_apply(self):
        """The engine runs this when the approver approves from the inbox."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "pending":
                raise UserError("%s is %s, not pending." % (rec.name, rec.state))
            if not self.env.su:
                authority = rec._approval_authority_user()
                if not authority.has_group(_BRANCH_AUTHORITY_GROUP):
                    raise UserError(
                        "A billed-part exemption is decided by someone holding branch "
                        "authority (DOFA Tier 2)."
                    )
                if (rec.requested_by_id | rec.create_uid) & rec._approval_acting_users():
                    raise UserError(
                        "Segregation of duties: whoever requested the exemption cannot "
                        "approve it."
                    )
            order = rec.order_id.sudo()
            line = rec.estimate_line_id.sudo()
            estimate = order._fix_governing_estimate()
            if line.estimate_id != estimate or estimate.state != "approved":
                raise UserError(
                    "%s was requested on an estimate that no longer governs order %s."
                    % (rec.name, order.name)
                )
            room, why = rec._fix_room(line, rec.part_id, order, exclude=rec)
            if rec.quantity - room > _EPS:
                raise UserError(
                    "%s: only %s can still be exempted (%s). The part may have been issued "
                    "since the request; decline it and request the right quantity."
                    % (rec.name, _qty(room), why)
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "decided_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )
            rec._fix_log(
                "Billed part not fitted: exemption for %s x %s approved by %s; the customer "
                "is not billed for it."
                % (_qty(rec.quantity), rec._fix_part_label(), self.env.user.name)
            )
            rec._fix_after_approved()
        return True

    def _fix_after_approved(self):
        """Hook: billing (cd_billing_engine) credits an already-issued invoice."""
        return None

    def _approval_on_rejected(self, comment):
        for rec in self:
            if rec.state != "pending":
                continue
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "decision_note": comment or False,
                }
            )
            rec._fix_log(
                "Billed part not fitted: exemption for %s x %s rejected by %s%s."
                % (
                    _qty(rec.quantity),
                    rec._fix_part_label(),
                    self.env.user.name,
                    ": %s" % comment if comment else "",
                )
            )

    def action_recall_approval(self):
        result = super().action_recall_approval()
        for rec in self.filtered(lambda r: r.state == "pending"):
            rec._guarded().write({"state": "withdrawn", "decided_on": fields.Datetime.now()})
            rec._fix_log(
                "Billed part not fitted: exemption for %s x %s withdrawn by %s."
                % (_qty(rec.quantity), rec._fix_part_label(), self.env.user.name)
            )
        return result


class FixServiceOrderPartExemption(models.Model):
    _inherit = "fix.service.order"

    part_exemption_ids = fields.One2many(
        "fix.so.part.exemption", "order_id", string="Billed Parts Not Fitted", readonly=True
    )

    def action_request_part_exemption(self, estimate_line_id, quantity, reason_code, reason):
        """G12: the service desk or technician lead asks that a billed part
        line, never fitted, be exempted; a branch manager decides it."""
        self.ensure_one()
        line = self.env["fix.estimate.line"].browse(int(estimate_line_id or 0))
        return self.env["fix.so.part.exemption"]._fix_raise(
            self, line, quantity, reason_code, reason
        )

    def _fix_part_exemptions(self, estimate=None, states=("approved",)):
        """The exemptions on `estimate` (default: the governing one) in `states`."""
        self.ensure_one()
        estimate = estimate if estimate is not None else self._fix_governing_estimate()
        if not estimate:
            return self.env["fix.so.part.exemption"]
        return (
            self.env["fix.so.part.exemption"]
            .sudo()
            .search(
                [
                    ("order_id", "=", self.id),
                    ("estimate_line_id.estimate_id", "=", estimate.id),
                    ("state", "in", list(states)),
                ]
            )
        )


class FixApprovalMatrixPartExemption(models.Model):
    _inherit = "fix.approval.matrix"

    # G12: lets a DoA matrix row target the billed-part exemption.
    decision_domain = fields.Selection(
        selection_add=[("so_part_exemption", "Billed Part Not Fitted (Exemption)")],
        ondelete={"so_part_exemption": "cascade"},
    )
