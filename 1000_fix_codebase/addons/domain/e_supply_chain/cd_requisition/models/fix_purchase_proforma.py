# fix_purchase_proforma — M16: a LOCAL supplier's proforma invoice and the
# advance paid against it (user request, 12 Nov 2026).
#
# Imports had both (M44 fix.import.proforma / fix.import.advance); a purchase
# from a local company had neither: the system assumed every local supplier is
# paid after delivery through the three-way match. In practice a local
# supplier often issues a proforma invoice and asks for part of the price in
# advance. Now:
#   - a proforma is recorded against an open purchase order of the same
#     supplier, in the order's currency; a Procurement Approver other than the
#     person who recorded it approves it when it reconciles to the order total
#     (cd_requisition.proforma_tolerance_pct, default 0), is unexpired, the
#     order is issued and the supplier is still active in M42; it is final
#     once decided;
#   - an advance is requested by a Buyer against an APPROVED proforma of its
#     order and decided by a Procurement Approver other than the requester;
#     the order's approved advances never exceed the proforma amount, and an
#     approval above cd_requisition.advance_cap_pct of it (default 0, so every
#     advance is explained) needs a stated reason.
# Like the import advance, this records and approves the instrument; the money
# moves and posts through Treasury (M50), not here.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_requisition import (
    GROUP_APPROVER,
    GROUP_BUYER,
    float_param,
    require_role,
)

PARAM_PROFORMA_TOLERANCE = "cd_requisition.proforma_tolerance_pct"
PARAM_ADVANCE_CAP = "cd_requisition.advance_cap_pct"

# A proforma may be recorded while the order is still being prepared or is
# out with the supplier; it is approved only once the order is issued.
OPEN_PO_STATES = ("draft", "sent", "acknowledged", "partially_received")
ADVANCE_PO_STATES = ("sent", "acknowledged", "partially_received")

PROFORMA_TERMS = (
    "purchase_order_id",
    "proforma_no",
    "issued_on",
    "valid_until",
    "amount",
    "payment_terms",
)
ADVANCE_TERMS = ("purchase_order_id", "proforma_id", "amount", "purpose", "security_ref")


def _require_other_person(record, who, what):
    """The decider is never the person who raised the record."""
    if not record.env.su and who and who == record.env.user:
        raise UserError(
            "%s was recorded by you: a Procurement Approver other than you decides it." % what
        )


def _refuse_locked(records, vals, terms, why):
    for rec in records:
        if rec.state not in ("received", "draft") and set(vals) & set(terms):
            raise UserError("%s: %s" % (rec.display_name, why))


class FixPurchaseProforma(models.Model):
    _name = "fix.purchase.proforma"
    _description = "Supplier Proforma Invoice"
    _rec_name = "display_label"
    _order = "issued_on desc, id desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    purchase_order_id = fields.Many2one(
        "fix.purchase.order",
        string="Purchase Order",
        required=True,
        ondelete="restrict",
        index=True,
    )
    vendor_id = fields.Many2one(
        related="purchase_order_id.vendor_id", store=True, index=True, string="Supplier"
    )
    company_id = fields.Many2one(
        related="purchase_order_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="purchase_order_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(
        related="purchase_order_id.currency_id", store=True, string="Currency"
    )
    order_total = fields.Monetary(
        related="purchase_order_id.amount_total", string="Order Total", currency_field="currency_id"
    )
    proforma_no = fields.Char(
        string="Supplier's Proforma No", required=True, tracking=True, copy=False
    )
    issued_on = fields.Date(required=True, default=fields.Date.context_today, tracking=True)
    valid_until = fields.Date(tracking=True)
    amount = fields.Monetary(currency_field="currency_id", required=True, tracking=True)
    payment_terms = fields.Char(
        string="Payment Terms",
        help="As written on the proforma, e.g. 50% advance, rest on delivery.",
    )
    notes = fields.Text()
    display_label = fields.Char(compute="_compute_display_label")
    state = fields.Selection(
        [
            ("received", "Received"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="received",
        tracking=True,
    )
    recorded_by_id = fields.Many2one(
        "res.users",
        string="Recorded By",
        readonly=True,
        copy=False,
        default=lambda self: self.env.user,
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Datetime(string="Decided On", readonly=True, copy=False)
    rejection_reason = fields.Char(readonly=True, copy=False)
    advance_ids = fields.One2many("fix.purchase.advance", "proforma_id", string="Advances")
    advance_approved = fields.Monetary(
        string="Advances Approved",
        currency_field="currency_id",
        compute="_compute_advance_approved",
    )

    _amount_positive = models.Constraint("CHECK (amount > 0)", "A proforma amount must be positive")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "recorded_by_id",
            "decided_by_id",
            "decided_on",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "received":
            locked |= set(PROFORMA_TERMS) | {"notes"}
        return locked

    @api.depends("name", "proforma_no")
    def _compute_display_label(self):
        for rec in self:
            rec.display_label = (
                "%s · %s" % (rec.proforma_no, rec.name) if rec.proforma_no else rec.name
            )

    @api.depends("advance_ids.state", "advance_ids.amount")
    def _compute_advance_approved(self):
        for rec in self:
            rec.advance_approved = sum(
                rec.advance_ids.filtered(lambda a: a.state == "approved").mapped("amount")
            )

    @api.constrains("purchase_order_id")
    def _check_order_open(self):
        for rec in self.sudo():
            if rec.state == "received" and rec.purchase_order_id.state not in OPEN_PO_STATES:
                raise ValidationError(
                    "Record a proforma against an open purchase order (%s is %s)."
                    % (rec.purchase_order_id.name, rec.purchase_order_id.state)
                )

    @api.constrains("proforma_no", "vendor_id", "state")
    def _check_unique_number(self):
        for rec in self.sudo():
            twin = rec.search_count(
                [
                    ("id", "!=", rec.id),
                    ("vendor_id", "=", rec.vendor_id.id),
                    ("proforma_no", "=", rec.proforma_no),
                    ("state", "!=", "cancelled"),
                ]
            )
            if twin:
                raise ValidationError(
                    "%s's proforma %s is already recorded."
                    % (rec.vendor_id.display_name, rec.proforma_no)
                )

    @api.constrains("issued_on", "valid_until")
    def _check_dates(self):
        for rec in self:
            if rec.valid_until and rec.issued_on and rec.valid_until < rec.issued_on:
                raise ValidationError("A proforma cannot expire before it is issued.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.purchase.proforma")
                    or "SPI/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        _refuse_locked(
            self,
            vals,
            set(PROFORMA_TERMS) | {"notes"},
            "a decided proforma is final; record a new proforma instead.",
        )
        return super().write(vals)

    # ---- transitions ---------------------------------------------------------------
    def action_approve(self):
        require_role(self.env, GROUP_APPROVER, "Approving a supplier proforma")
        tol = max(float_param(self.env, PARAM_PROFORMA_TOLERANCE, 0.0), 0.0)
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "received":
                raise UserError("Approve a received proforma (%s is %s)." % (rec.name, rec.state))
            _require_other_person(rec, rec.recorded_by_id, "Proforma %s" % rec.proforma_no)
            order = rec.purchase_order_id.sudo()
            if order.state not in ADVANCE_PO_STATES:
                raise UserError(
                    "Approve the proforma once purchase order %s is sent to the supplier "
                    "(it is %s)." % (order.name, order.state)
                )
            expected = order.amount_total or 0.0
            if expected <= 0 or abs(rec.amount - expected) > expected * tol / 100.0 + 0.01:
                raise UserError(
                    "Proforma %s (%.2f %s) does not reconcile to purchase order %s "
                    "(%.2f %s, tolerance %.2f%%)."
                    % (
                        rec.proforma_no,
                        rec.amount,
                        rec.currency_id.name,
                        order.name,
                        expected,
                        order.currency_id.name,
                        tol,
                    )
                )
            if rec.valid_until and rec.valid_until < today:
                raise UserError("Proforma %s expired on %s." % (rec.proforma_no, rec.valid_until))
            live = rec.sudo().search_count(
                [
                    ("purchase_order_id", "=", order.id),
                    ("state", "=", "approved"),
                    ("id", "!=", rec.id),
                ]
            )
            if live:
                raise UserError("Purchase order %s already has an approved proforma." % order.name)
            order._fix_vendor_gate(order.vendor_id, "Approving proforma %s" % rec.proforma_no)
            rec._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": rec.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        require_role(self.env, GROUP_APPROVER, "Rejecting a supplier proforma")
        why = (reason or "").strip()
        if not why:
            raise UserError("State why the proforma is rejected.")
        for rec in self:
            if rec.state != "received":
                raise UserError("Reject a received proforma (%s is %s)." % (rec.name, rec.state))
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": rec.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "rejection_reason": why,
                }
            )
        return True

    def action_cancel(self):
        require_role(self.env, GROUP_BUYER, "Cancelling a supplier proforma")
        for rec in self:
            if rec.state != "received":
                raise UserError(
                    "Only an undecided proforma is cancelled (%s is %s)." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "cancelled"})
        return True


class FixPurchaseAdvance(models.Model):
    _name = "fix.purchase.advance"
    _description = "Supplier Advance Payment"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    purchase_order_id = fields.Many2one(
        "fix.purchase.order",
        string="Purchase Order",
        required=True,
        ondelete="restrict",
        index=True,
    )
    proforma_id = fields.Many2one(
        "fix.purchase.proforma",
        string="Against Proforma",
        required=True,
        ondelete="restrict",
        index=True,
    )
    vendor_id = fields.Many2one(
        related="purchase_order_id.vendor_id", store=True, index=True, string="Supplier"
    )
    company_id = fields.Many2one(
        related="purchase_order_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="purchase_order_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(
        related="purchase_order_id.currency_id", store=True, string="Currency"
    )
    proforma_amount = fields.Monetary(
        related="proforma_id.amount", string="Proforma Amount", currency_field="currency_id"
    )
    amount = fields.Monetary(currency_field="currency_id", required=True, tracking=True)
    purpose = fields.Char(help="Why the supplier is paid before delivery.")
    security_ref = fields.Char(
        string="Advance Security Reference",
        help="The supplier's security cheque or bank guarantee for the advance, if any.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    requested_on = fields.Datetime(readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    decision_reason = fields.Char(readonly=True, copy=False)
    above_cap = fields.Boolean(
        string="Above the Cap at Approval",
        readonly=True,
        copy=False,
        help="The approval took the order's advances above cd_requisition.advance_cap_pct.",
    )

    _amount_positive = models.Constraint("CHECK (amount > 0)", "An advance must be positive")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "requested_on",
            "decided_by_id",
            "decided_on",
            "decision_reason",
            "above_cap",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(ADVANCE_TERMS)
        return locked

    @api.constrains("purchase_order_id", "proforma_id")
    def _check_proforma_of_order(self):
        for rec in self.sudo():
            if rec.proforma_id.purchase_order_id != rec.purchase_order_id:
                raise ValidationError(
                    "Proforma %s belongs to purchase order %s, not %s."
                    % (
                        rec.proforma_id.proforma_no,
                        rec.proforma_id.purchase_order_id.name,
                        rec.purchase_order_id.name,
                    )
                )

    @api.onchange("proforma_id")
    def _onchange_proforma(self):
        if self.proforma_id and not self.purchase_order_id:
            self.purchase_order_id = self.proforma_id.purchase_order_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("proforma_id") and not vals.get("purchase_order_id"):
                proforma = self.env["fix.purchase.proforma"].browse(vals["proforma_id"])
                vals["purchase_order_id"] = proforma.sudo().purchase_order_id.id
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.purchase.advance")
                    or "SADV/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        _refuse_locked(
            self,
            vals,
            ADVANCE_TERMS,
            "a requested advance is fixed; cancel it and record a new one.",
        )
        return super().write(vals)

    def _approved_total_with_this(self):
        self.ensure_one()
        others = self.sudo().search(
            [
                ("purchase_order_id", "=", self.purchase_order_id.id),
                ("state", "=", "approved"),
                ("id", "!=", self.id),
            ]
        )
        return sum(others.mapped("amount")) + (self.amount or 0.0)

    # ---- transitions ---------------------------------------------------------------
    def action_request(self):
        require_role(self.env, GROUP_BUYER, "Requesting a supplier advance")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Request a draft advance (%s is %s)." % (rec.name, rec.state))
            if rec.proforma_id.state != "approved":
                raise UserError(
                    "An advance is paid against an approved proforma (%s is %s)."
                    % (rec.proforma_id.proforma_no, rec.proforma_id.state)
                )
            if rec.purchase_order_id.state not in ADVANCE_PO_STATES:
                raise UserError(
                    "Purchase order %s is %s: an advance is requested on an issued order "
                    "that is not yet fully received."
                    % (rec.purchase_order_id.name, rec.purchase_order_id.state)
                )
            rec._guarded().write(
                {
                    "state": "requested",
                    "requested_by_id": rec.env.user.id,
                    "requested_on": fields.Datetime.now(),
                }
            )
        return True

    def action_approve(self, reason=None):
        require_role(self.env, GROUP_APPROVER, "Approving a supplier advance")
        pct = max(float_param(self.env, PARAM_ADVANCE_CAP, 0.0), 0.0)
        why = (reason or "").strip()
        for rec in self:
            if rec.state != "requested":
                raise UserError("Approve a requested advance (%s is %s)." % (rec.name, rec.state))
            if not rec.env.su and rec.requested_by_id == rec.env.user:
                raise UserError(
                    "Advance %s was requested by you: a Procurement Approver other than you "
                    "decides it." % rec.name
                )
            proforma = rec.proforma_id.sudo()
            if proforma.state != "approved":
                raise UserError(
                    "Proforma %s is no longer approved (%s)."
                    % (proforma.proforma_no, proforma.state)
                )
            ceiling = proforma.amount or 0.0
            total = rec._approved_total_with_this()
            if total > ceiling + 0.01:
                raise UserError(
                    "Advances on %s would total %.2f %s, above proforma %s (%.2f)."
                    % (
                        rec.purchase_order_id.name,
                        total,
                        rec.currency_id.name,
                        proforma.proforma_no,
                        ceiling,
                    )
                )
            above = total > ceiling * pct / 100.0 + 0.01
            if above and not why:
                raise UserError(
                    "Advances on %s would total %.2f %s, above the advance cap of %.2f%% of the "
                    "proforma (%.2f): state why this one is approved."
                    % (rec.purchase_order_id.name, total, rec.currency_id.name, pct, ceiling)
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": rec.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "decision_reason": why or False,
                    "above_cap": above,
                }
            )
        return True

    def action_reject(self, reason=None):
        require_role(self.env, GROUP_APPROVER, "Rejecting a supplier advance")
        why = (reason or "").strip()
        if not why:
            raise UserError("State why the advance is rejected.")
        for rec in self:
            if rec.state != "requested":
                raise UserError("Reject a requested advance (%s is %s)." % (rec.name, rec.state))
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": rec.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "decision_reason": why,
                }
            )
        return True

    def action_cancel(self):
        require_role(self.env, GROUP_BUYER, "Cancelling a supplier advance")
        for rec in self:
            if rec.state not in ("draft", "requested"):
                raise UserError(
                    "Only an undecided advance is cancelled (%s is %s)." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "cancelled"})
        return True


class FixPurchaseOrderProforma(models.Model):
    _inherit = "fix.purchase.order"

    proforma_ids = fields.One2many(
        "fix.purchase.proforma", "purchase_order_id", string="Supplier Proformas"
    )
    advance_ids = fields.One2many(
        "fix.purchase.advance", "purchase_order_id", string="Supplier Advances"
    )
    advance_approved_total = fields.Monetary(
        string="Advances Approved",
        currency_field="currency_id",
        compute="_compute_advance_approved_total",
    )

    @api.depends("advance_ids.state", "advance_ids.amount")
    def _compute_advance_approved_total(self):
        for order in self:
            order.advance_approved_total = sum(
                order.advance_ids.filtered(lambda a: a.state == "approved").mapped("amount")
            )
