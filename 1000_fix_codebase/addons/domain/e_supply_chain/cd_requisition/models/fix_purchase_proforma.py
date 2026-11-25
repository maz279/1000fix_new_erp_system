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
    "vat_amount",
    "other_charges",
    "pi_file",
    "pi_filename",
    "line_ids",
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
    # the supplier's document: its item lines, VAT and charges, and a copy
    pi_file = fields.Binary(string="Supplier's PI (copy)", attachment=True, copy=False)
    pi_filename = fields.Char(string="PI File Name", copy=False)
    line_ids = fields.One2many(
        "fix.purchase.proforma.line", "proforma_id", string="PI Lines", copy=True
    )
    lines_total = fields.Monetary(
        string="Goods Value",
        currency_field="currency_id",
        compute="_compute_lines_total",
        store=True,
        help="The lines before VAT and charges: what reconciles to the order total.",
    )
    vat_amount = fields.Monetary(string="VAT", currency_field="currency_id")
    other_charges = fields.Monetary(
        string="Other Charges",
        currency_field="currency_id",
        help="Carriage, installation and the like.",
    )
    computed_total = fields.Monetary(
        string="Lines + VAT + Charges",
        currency_field="currency_id",
        compute="_compute_lines_total",
        store=True,
    )
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

    @api.depends("line_ids.subtotal", "vat_amount", "other_charges")
    def _compute_lines_total(self):
        for rec in self:
            rec.lines_total = sum(rec.line_ids.mapped("subtotal"))
            rec.computed_total = (
                rec.lines_total + (rec.vat_amount or 0.0) + (rec.other_charges or 0.0)
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
            # an import's proforma is the M44 one: in the supplier's currency,
            # with HS codes, ports and the LC terms the bank needs
            if rec.purchase_order_id.purchase_type == "import":
                raise ValidationError(
                    "%s is an import purchase order: record its proforma on the import "
                    "order (M44 Proforma Invoices)." % rec.purchase_order_id.name
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
            # no lines given: start from the order's, to be adjusted to the PI
            if vals.get("purchase_order_id") and not vals.get("line_ids"):
                order = self.env["fix.purchase.order"].browse(vals["purchase_order_id"]).sudo()
                vals["line_ids"] = [
                    (
                        0,
                        0,
                        {
                            "po_line_id": line.id,
                            "product_id": line.product_id.id,
                            "description": line.description or line.product_id.display_name,
                            "quantity": line.qty_ordered,
                            "unit_price": line.unit_price,
                        },
                    )
                    for line in order.line_ids
                ]
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
            if not rec.line_ids:
                raise UserError(
                    "Proforma %s has no item lines: enter the supplier's PI lines (or start "
                    "from the order's) before it is approved." % rec.proforma_no
                )
            expected = order.amount_total or 0.0
            goods = rec.lines_total
            if expected <= 0 or abs(goods - expected) > expected * tol / 100.0 + 0.01:
                raise UserError(
                    "Proforma %s goods value (%.2f %s) does not reconcile to purchase order %s "
                    "(%.2f %s, tolerance %.2f%%)."
                    % (
                        rec.proforma_no,
                        goods,
                        rec.currency_id.name,
                        order.name,
                        expected,
                        order.currency_id.name,
                        tol,
                    )
                )
            if abs((rec.amount or 0.0) - rec.computed_total) > 0.01:
                raise UserError(
                    "Proforma %s does not add up: its total %.2f %s, but goods %.2f + VAT %.2f "
                    "+ other charges %.2f = %.2f."
                    % (
                        rec.proforma_no,
                        rec.amount or 0.0,
                        rec.currency_id.name,
                        goods,
                        rec.vat_amount or 0.0,
                        rec.other_charges or 0.0,
                        rec.computed_total,
                    )
                )
            rec._check_lines_against_order(order)
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

    def _check_lines_against_order(self, order):
        """Every PI line is a product of the order, and never more of it."""
        self.ensure_one()
        ordered = {}
        for line in order.line_ids:
            ordered[line.product_id.id] = ordered.get(line.product_id.id, 0.0) + line.qty_ordered
        asked = {}
        for line in self.line_ids:
            if line.product_id.id not in ordered:
                raise UserError(
                    "Proforma %s lists %s, which is not on purchase order %s."
                    % (self.proforma_no, line.product_id.display_name, order.name)
                )
            asked[line.product_id.id] = asked.get(line.product_id.id, 0.0) + line.quantity
        for product_id, qty in asked.items():
            if qty > ordered[product_id] + 1e-6:
                product = self.env["product.product"].sudo().browse(product_id)
                raise UserError(
                    "Proforma %s asks for %g of %s; purchase order %s orders %g."
                    % (self.proforma_no, qty, product.display_name, order.name, ordered[product_id])
                )

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

    # Two purchase formats (user request, 12 Nov 2026): a LOCAL purchase order
    # to a Bangladeshi supplier, in taka or US dollars; an IMPORT purchase order
    # in the supplier's currency, fulfilled through an M44 import order (raised
    # from the PO, or the PO raised from the import order).
    purchase_type = fields.Selection(
        [("local", "Local Purchase"), ("import", "Import Purchase")],
        string="Purchase Type",
        required=True,
        default="local",
        tracking=True,
        index=True,
    )

    @api.constrains("currency_id", "purchase_type")
    def _check_local_currency(self):
        for order in self:
            if (
                order.purchase_type == "local"
                and order.currency_id
                and not order.currency_id.fix_local_purchase
            ):
                raise ValidationError(
                    "Purchase order %s is in %s: a local purchase order is in BDT or USD. "
                    "Make it an import purchase order for the supplier's currency."
                    % (order.name or "", order.currency_id.name)
                )

    def write(self, vals):
        if "purchase_type" in vals:
            for order in self:
                if order.purchase_type != vals["purchase_type"] and (
                    order.state != "draft" or order.proforma_ids
                ):
                    raise UserError(
                        "Purchase order %s is %s or has a proforma: its purchase type is fixed."
                        % (order.name, order.state)
                    )
        return super().write(vals)


LOCAL_PURCHASE_CURRENCIES = ("BDT", "USD")


class ResCurrencyLocalPurchase(models.Model):
    """Whether a local purchase order may be in this currency: a stored flag
    the order form's picker can filter on (a picker filters on flags and
    links, never on a currency's name)."""

    _inherit = "res.currency"

    fix_local_purchase = fields.Boolean(
        string="Allowed for Local Purchase",
        compute="_compute_fix_local_purchase",
        store=True,
    )

    @api.depends("name")
    def _compute_fix_local_purchase(self):
        for currency in self:
            currency.fix_local_purchase = currency.name in LOCAL_PURCHASE_CURRENCIES


class FixPurchaseProformaLine(models.Model):
    """One item of a local supplier's proforma invoice."""

    _name = "fix.purchase.proforma.line"
    _description = "Supplier Proforma Line"
    _order = "proforma_id, sequence, id"

    proforma_id = fields.Many2one(
        "fix.purchase.proforma", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(related="proforma_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="proforma_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="proforma_id.currency_id")
    po_line_id = fields.Many2one(
        "fix.purchase.order.line", string="Order Line", ondelete="set null", copy=False
    )
    product_id = fields.Many2one("product.product", string="Product", required=True)
    supplier_part_no = fields.Char(string="Supplier's Item Code / Part No")
    description = fields.Char(required=True)
    quantity = fields.Float(required=True, default=1.0)
    uom = fields.Char(string="Unit", default="Pcs")
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id", required=True)
    subtotal = fields.Monetary(
        string="Line Total", currency_field="currency_id", compute="_compute_subtotal", store=True
    )

    _qty_positive = models.Constraint(
        "CHECK (quantity > 0)", "A proforma line needs a positive quantity"
    )
    _price_non_negative = models.Constraint(
        "CHECK (unit_price >= 0)", "A unit price cannot be negative"
    )

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (line.quantity or 0.0) * (line.unit_price or 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        Product = self.env["product.product"]
        for vals in vals_list:
            if not vals.get("description") and vals.get("product_id"):
                vals["description"] = Product.browse(vals["product_id"]).sudo().display_name
        records = super().create(vals_list)
        records._refuse_on_decided("added")
        return records

    def write(self, vals):
        self._refuse_on_decided("changed")
        return super().write(vals)

    def unlink(self):
        self._refuse_on_decided("removed")
        return super().unlink()

    def _refuse_on_decided(self, what):
        for line in self.sudo():
            if line.proforma_id.state != "received":
                raise UserError(
                    "Proforma %s is %s: its lines cannot be %s. Record a new proforma."
                    % (line.proforma_id.proforma_no, line.proforma_id.state, what)
                )
