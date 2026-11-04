# cd_requisition — M16 Procurement core (P06-M07, CD-M16-01).
#
# Requisition -> approval -> PO -> approval -> send -> vendor acknowledgement
# -> goods receipt (fix_purchase_receipt.py) -> inspection -> three-way match
# (cd_ap_ext). RFQ sourcing, blankets and expediting are in
# fix_procurement_ops.py.
#
# A06 workflow audit (2026-11-03), findings M16-1/2/3/6/9/11: one plain user
# raised, self-approved (or wrote state='approved'), converted, sent and
# received a BDT 5M order; the only "authority matrix" was a 25k constant
# that the IT administrator alone could pass; an acknowledged PO was re-priced
# x10. Now:
#   - requisition AND purchase-order approval are routed requests (M63) on the
#     DOFA ladder by amount, decided from the approver's inbox by a tier
#     holder who is not the requester, the buyer, the creator or anyone who
#     changed what the approval covers (fix.procurement.dofa.mixin);
#   - state, approval and evidence fields change only through their actions
#     (fix.guarded.mixin);
#   - what an approval covered (amount, quantity, price, vendor, lines,
#     currency) is pinned: a change voids the approval and returns the record
#     to draft; once a PO is sent it is locked and changes go through a
#     change order (a new revision that is approved again);
#   - a PO needs an approved requisition or a Procurement Manager's
#     documented exception, and is sent only to an active supplier (the gate
#     is filled in by cd_vendor_portal, which owns the supplier register).
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.addons.cd_entity_config.models.fix_dofa import TIER_GROUP
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

_logger = logging.getLogger(__name__)

GROUP_BUYER = "cd_requisition.group_fix_procurement_buyer"
GROUP_RECEIVER = "cd_requisition.group_fix_procurement_receiver"
GROUP_APPROVER = "cd_requisition.group_fix_procurement_approver"
GROUP_MANAGER = "cd_requisition.group_fix_procurement_manager"

# The procurement DoA ladder (spec 05-04 §7: <=50k Inventory Manager, <=500k
# Procurement Manager, <=2M CFO, above: CEO), mapped onto the DOFA tiers
# (tier 2, 3, 4, 5). The bounds are a business decision (A06 report §7 B2),
# so they are configuration; the defaults are the spec's. An amount at or
# below PARAM_FLOOR needs no approval; the default 0 means every requisition
# and PO with a value is approved by someone other than its requester.
PARAM_FLOOR = "cd_requisition.dofa_no_approval_max"
PARAM_TIER2 = "cd_requisition.dofa_tier2_max"
PARAM_TIER3 = "cd_requisition.dofa_tier3_max"
PARAM_TIER4 = "cd_requisition.dofa_tier4_max"
DEFAULT_LADDER = {
    PARAM_FLOOR: 0.0,
    PARAM_TIER2: 50000.0,
    PARAM_TIER3: 500000.0,
    PARAM_TIER4: 2000000.0,
}
# Split-purchase detection: requisitions of the same requester for the same
# product category (or the same vendor) inside this rolling window are summed
# when the approval tier is derived. 0 switches the check off.
PARAM_SPLIT_DAYS = "cd_requisition.split_window_days"
DEFAULT_SPLIT_DAYS = 30
# BRU-PRO-11: goods are matchable only after the inspection outcome is
# recorded. "0" lets a posted receipt count as accepted at once.
PARAM_INSPECTION = "cd_requisition.receipt_inspection_required"

ISSUED_PO_STATES = ("sent", "acknowledged", "partially_received", "received", "closed")
RECEIVABLE_PO_STATES = ("sent", "acknowledged", "partially_received")


def float_param(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    if raw in (None, False, ""):
        return float(default)
    try:
        return float(raw)
    except (TypeError, ValueError):
        _logger.warning("%s is not a number (%r); using %s", key, raw, default)
        return float(default)


def bool_param(env, key, default=True):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    if raw in (None, False, ""):
        return default
    return str(raw).strip().lower() not in ("0", "false", "no", "off")


def procurement_ladder(env):
    """[(upper bound, tier)] ascending, the last entry the ceiling (tier_5)."""
    return [
        (float_param(env, PARAM_FLOOR, DEFAULT_LADDER[PARAM_FLOOR]), "tier_0"),
        (float_param(env, PARAM_TIER2, DEFAULT_LADDER[PARAM_TIER2]), "tier_2"),
        (float_param(env, PARAM_TIER3, DEFAULT_LADDER[PARAM_TIER3]), "tier_3"),
        (float_param(env, PARAM_TIER4, DEFAULT_LADDER[PARAM_TIER4]), "tier_4"),
        (float("inf"), "tier_5"),
    ]


def has_role(env, xmlid) -> bool:
    """Superuser code (crons, seeds, service calls) is trusted."""
    return env.su or env.user.has_group(xmlid)


def require_role(env, xmlid, what):
    if not has_role(env, xmlid):
        group = env.ref(xmlid, raise_if_not_found=False)
        raise UserError(
            "%s needs the %s role, which you do not hold." % (what, group.name if group else xmlid)
        )


def to_company_currency(record, amount, currency, company):
    company = company or record.env.company
    if currency and company.currency_id and currency != company.currency_id:
        return currency._convert(
            amount or 0.0, company.currency_id, company, fields.Date.context_today(record)
        )
    return amount or 0.0


class FixProcurementDofaMixin(models.AbstractModel):
    """The routed, amount-tiered approval of requisitions and purchase orders,
    with the A06 local defences.

    The M63 rule book is still writable by every user (A11 audit, E1-E4 not
    built), so nothing here takes an approver from it: the deciding group is
    always the DOFA tier group of the live amount, and the requester, the
    buyer, the creator, the last amount-changer and anyone who changed a
    pinned field are excluded — when routing AND again when deciding."""

    _name = "fix.procurement.dofa.mixin"
    _inherit = ["fix.dofa.mixin"]
    _description = "Procurement Approval (DOFA, routed)"

    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    pinned_changed_by_ids = fields.Many2many(
        "res.users",
        string="Changed After Approval By",
        readonly=True,
        copy=False,
        help="Users who changed what an approval covered. They never decide this record.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"pinned_changed_by_ids"}

    def _dofa_thresholds(self):
        return procurement_ladder(self.env)

    # ---- the local defences ------------------------------------------------
    def _approval_group_for(self, rule, tier):
        """The tier group of the live amount, never rule.approver_group_id."""
        xmlid = TIER_GROUP.get(tier) if tier else None
        return self.env.ref(xmlid, raise_if_not_found=False) if xmlid else None

    def _a06_extra_conflicts(self):
        """Per model: the requester, the buyer…"""
        return self.env["res.users"]

    def _a06_conflicted_users(self):
        self.ensure_one()
        rec = self.sudo()
        users = (
            rec.create_uid
            | rec.approval_amount_changed_by_id
            | rec.pinned_changed_by_ids
            | rec.approval_request_id.requested_by_id
            | rec._a06_extra_conflicts()
        )
        return users.sudo()

    def _approval_excluded(self):
        return (super()._approval_excluded() | self._a06_conflicted_users()).sudo()

    def _a06_assert_decider(self):
        self.ensure_one()
        if self.env.su:
            return
        task = self._approval_task()
        deciders = self.env.user | task.on_behalf_of_id
        clash = deciders & self._a06_conflicted_users()
        if clash:
            raise UserError(
                "Segregation of duties: %s raised, bought, requested or changed %s and "
                "cannot approve it." % (", ".join(clash.mapped("name")), self.display_name)
            )

    def _a06_before_approve(self):
        """Per model: the state and content checks that must hold to approve."""
        return None

    def _a06_after_approve(self):
        """Per model: what an approval does beyond the DOFA stamp."""
        return None

    def action_dofa_approve(self):
        """The engine's apply method: only from the approver's inbox task, by a
        tier holder outside the conflicted set. The stamp is written as the
        system after those checks (an approver need not hold the buyer's
        write rights on the document); the stamp still names the approver."""
        self._approval_assert_routed()
        for rec in self:
            rec._a06_assert_decider()
            rec._a06_before_approve()
        result = super(FixProcurementDofaMixin, self.sudo()).action_dofa_approve()
        for rec in self.sudo():
            rec._a06_after_approve()
        return result

    def action_approve(self):
        """Kept for old callers and screens: approval is decided from the M63
        inbox, so a direct call is refused by the routing guard."""
        return self.action_dofa_approve()

    def _a06_pinned_changed(self, reason):
        """Something the approval covered changed: withdraw the approval and
        remember who changed it (they never decide it)."""
        for rec in self:
            if not self.env.su:
                rec._guarded().write({"pinned_changed_by_ids": [(4, self.env.uid)]})
            if rec.approval_state in ("pending", "approved", "returned") or rec.dofa_approved:
                rec._dofa_void_approval(reason)
                rec._guarded().write({"approval_state": "none"})


# ============================================================== requisition
class FixRequisition(models.Model):
    """An internal requisition that may mature into a PO (CD-M16-01)."""

    _name = "fix.requisition"
    _description = "Requisition"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.procurement.dofa.mixin"]
    _approval_domain = "requisition"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Requesting Branch", index=True)
    requested_by = fields.Many2one("hr.employee", string="Requested By", required=True)
    description = fields.Char(required=True)
    justification = fields.Text(
        string="Business Justification",
        help="Why this is needed. Carried to the approver as the DOFA justification.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    estimate_amount = fields.Monetary(string="Estimated Amount", currency_field="currency_id")
    urgency = fields.Selection(
        [
            ("normal", "Normal"),
            ("urgent", "Urgent (stock-out)"),
            ("emergency", "Emergency (job-stopped)"),
        ],
        default="normal",
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted for Approval"),
            ("approved", "Approved"),
            ("converted", "Converted to PO"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    purchase_order_id = fields.Many2one(
        "fix.purchase.order", string="Purchase Order", readonly=True, index=True, copy=False
    )
    product_id = fields.Many2one("product.product", string="Product", index=True)
    qty = fields.Float(string="Quantity", default=1.0)
    vendor_id = fields.Many2one("res.partner", string="Preferred Vendor", index=True)
    submitted_at = fields.Datetime(readonly=True, copy=False)
    submitted_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True, copy=False)
    cancel_reason = fields.Char(readonly=True, copy=False)
    split_prior_amount = fields.Monetary(
        string="Related Requisitions (split check)",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="Value of this requester's other requisitions for the same product category "
        "or vendor inside the split window, added when the approval tier is derived.",
    )
    split_requisition_ids = fields.Many2many(
        "fix.requisition",
        "fix_requisition_split_rel",
        "requisition_id",
        "related_id",
        string="Related Requisitions",
        readonly=True,
        copy=False,
    )

    REQ_PINNED = ("estimate_amount", "qty", "product_id", "vendor_id", "currency_id")
    REQ_GUARDED = {
        "state",
        "purchase_order_id",
        "submitted_at",
        "submitted_by_id",
        "cancel_reason",
        "split_prior_amount",
        "split_requisition_ids",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.REQ_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state in ("converted", "cancelled") for r in self):
            locked |= set(self.REQ_PINNED) | {
                "description",
                "justification",
                "requested_by",
                "operating_unit_id",
                "branch_id",
                "urgency",
            }
        return locked

    # ---- DOFA -------------------------------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        own = to_company_currency(self, self.estimate_amount, self.currency_id, self.company_id)
        return own + (self.split_prior_amount or 0.0)

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        if not self.split_prior_amount:
            return "BDT %.2f" % self._dofa_amount()
        return (
            "BDT %.2f (this requisition %.2f plus %.2f from %d related requisition(s) of the "
            "same requester in the split window)"
            % (
                self._dofa_amount(),
                self.estimate_amount or 0.0,
                self.split_prior_amount,
                len(self.split_requisition_ids),
            )
        )

    @api.depends("estimate_amount", "split_prior_amount", "currency_id")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _a06_extra_conflicts(self):
        rec = self.sudo()
        return rec.requested_by.user_id | rec.submitted_by_id

    def _a06_before_approve(self):
        if self.state != "submitted":
            raise UserError(
                "Only a submitted requisition can be approved (%s is %s)."
                % (self.display_name, self.state)
            )

    def _a06_after_approve(self):
        self._guarded().write({"state": "approved"})

    def _approval_on_rejected(self, comment):
        for rec in self.sudo():
            if rec.state == "submitted":
                rec._guarded().write({"state": "rejected"})

    # ---- split detection --------------------------------------------------
    def _split_related(self):
        """Other live requisitions of the same requester for the same product
        category or vendor inside the rolling window."""
        self.ensure_one()
        days = int(float_param(self.env, PARAM_SPLIT_DAYS, DEFAULT_SPLIT_DAYS))
        if days <= 0 or not self.requested_by:
            return self.browse()
        since = fields.Datetime.now() - timedelta(days=days)
        domain = [
            ("id", "!=", self.id),
            ("requested_by", "=", self.requested_by.id),
            ("company_id", "=", self.company_id.id),
            ("state", "in", ("submitted", "approved", "converted")),
            ("create_date", ">=", since),
        ]
        alternatives = []
        if self.product_id.categ_id:
            alternatives.append([("product_id.categ_id", "=", self.product_id.categ_id.id)])
        if self.vendor_id:
            alternatives.append([("vendor_id", "=", self.vendor_id.id)])
        if not alternatives:
            return self.browse()
        if len(alternatives) == 2:
            domain += ["|", *alternatives[0], *alternatives[1]]
        else:
            domain += alternatives[0]
        return self.sudo().search(domain).with_env(self.env)

    # ---- write: pinning ---------------------------------------------------
    def write(self, vals):
        touched = self.browse()
        pinned = set(self.REQ_PINNED) & set(vals)
        if pinned and not self._fix_guard_has_token():
            for rec in self:
                if not any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in pinned):
                    continue
                if rec.state in ("converted", "cancelled"):
                    raise UserError(
                        "Requisition %s is %s: its amount, quantity, product, vendor and "
                        "currency can no longer change." % (rec.display_name, rec.state)
                    )
                if rec.state in ("submitted", "approved") or rec.approval_state in (
                    "pending",
                    "approved",
                ):
                    touched |= rec
        result = super().write(vals)
        for rec in touched:
            rec._a06_pinned_changed(
                "the amount, quantity, product, vendor or currency changed after it was "
                "submitted; it is back in draft and must be approved again."
            )
            rec._guarded().write({"state": "draft"})
        return result

    # ---- actions ----------------------------------------------------------
    def action_submit(self, justification=None):
        """Submit for approval: the tier comes from the amount (plus related
        requisitions in the split window) and the request is routed through
        the M63 engine to a tier holder other than the requester.

        Usable by code (M43 creates a draft requisition, then submits it): if
        nobody holds the tier yet the requisition stays submitted and says so;
        Request Approval routes it once an approver is appointed."""
        for rec in self:
            resubmit = rec.state == "submitted" and rec.approval_state in (
                "none",
                "returned",
                "rejected",
            )
            if rec.state != "draft" and not resubmit:
                raise UserError(
                    "Only a draft requisition can be submitted (%s is %s)."
                    % (rec.display_name, rec.state)
                )
            if (rec.estimate_amount or 0.0) <= 0.0:
                raise UserError(
                    "Requisition %s has no value. A requisition is submitted with its "
                    "estimated amount (zero-value requisitions are refused)." % rec.display_name
                )
            if rec.product_id and (rec.qty or 0.0) <= 0.0:
                raise UserError("Requisition %s needs a positive quantity." % rec.display_name)
            related = rec._split_related()
            prior = sum(
                to_company_currency(r, r.estimate_amount, r.currency_id, r.company_id)
                for r in related.sudo()
            )
            text = (justification or rec.justification or rec.description or "").strip()
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_at": fields.Datetime.now(),
                    "submitted_by_id": self.env.uid,
                    "split_prior_amount": prior,
                    "split_requisition_ids": [(6, 0, related.ids)],
                    "approval_state": "none",
                }
            )
            if text and rec.dofa_justification != text:
                rec.write({"dofa_justification": text})
            if not rec._approval_needed():
                rec._guarded().write({"state": "approved"})
                rec.message_post(
                    body="At or below the approval floor (%s): approved without routing."
                    % rec._dofa_amount_label()
                )
                continue
            try:
                with self.env.cr.savepoint():
                    rec.action_request_approval()
            except UserError as exc:
                rec.message_post(body="Submitted. Approval could not be routed yet: %s" % exc)
        return True

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(
                    "Submit requisition %s before requesting its approval." % rec.display_name
                )
        return super().action_request_approval(justification=justification)

    def action_reset_draft(self):
        """A rejected (or returned) requisition goes back to its requester."""
        for rec in self:
            if rec.state not in ("rejected", "submitted") or rec.approval_state in (
                "pending",
                "approved",
            ):
                raise UserError(
                    "Only a rejected or returned requisition goes back to draft (%s is %s)."
                    % (rec.display_name, rec.state)
                )
            rec._guarded().write({"state": "draft", "approval_state": "none"})
        return True

    def action_cancel(self, reason=None):
        for rec in self:
            if rec.state in ("converted", "cancelled"):
                raise UserError(
                    "Requisition %s is %s and cannot be cancelled." % (rec.display_name, rec.state)
                )
            if not (reason or "").strip():
                raise UserError("State why requisition %s is cancelled." % rec.display_name)
            if rec.approval_state == "pending":
                rec._approval_void("the requisition was cancelled")
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason.strip()})
        return True

    def action_convert_to_po(self):
        """Create the PO from an approved requisition, one line at the
        requisition's estimated unit price. The PO keeps the requisition link
        (maverick spend = a PO with no approved requisition) and must itself
        be approved before it is sent."""
        Order = self.env["fix.purchase.order"]
        for req in self:
            require_role(self.env, GROUP_BUYER, "Converting a requisition to a purchase order")
            if req.state != "approved":
                raise UserError("Convert an approved requisition")
            if req._approval_needed() and req.approval_state != "approved":
                raise UserError(
                    "Requisition %s carries no routed approval; it cannot be converted."
                    % req.display_name
                )
            req._dofa_assert_approved("Converting requisition %s" % req.display_name)
            if not req.product_id or (req.qty or 0.0) <= 0:
                raise UserError("A requisition needs a product and a positive quantity to convert")
            if not req.vendor_id:
                raise UserError("A requisition needs a vendor before it can become a PO")
            if req.purchase_order_id:
                raise UserError("Requisition %s is already converted" % req.description)
            Order._fix_vendor_gate(
                req.vendor_id, "Converting requisition %s to a PO" % req.display_name
            )
            unit_price = (req.estimate_amount or 0.0) / (req.qty or 1.0)
            order = Order._guarded().create(
                {
                    "operating_unit_id": req.operating_unit_id.id,
                    "branch_id": req.branch_id.id,
                    "vendor_id": req.vendor_id.id,
                    "currency_id": req.currency_id.id,
                    "requisition_id": req.id,
                    "dofa_justification": req.dofa_justification or req.justification or False,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": req.product_id.id,
                                "description": req.description,
                                "qty_ordered": req.qty,
                                "unit_price": unit_price,
                            },
                        )
                    ],
                }
            )
            req._guarded().write({"state": "converted", "purchase_order_id": order.id})
        return True


# ============================================================ purchase order
class FixPurchaseOrder(models.Model):
    """A purchase order: the ORDERED side of the three-way match."""

    _name = "fix.purchase.order"
    _description = "Purchase Order"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.procurement.dofa.mixin"]
    _order = "date_order desc, id desc"
    _approval_domain = "purchase_order"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Deliver-to Branch", index=True)
    vendor_id = fields.Many2one(
        "res.partner", string="Vendor", required=True, index=True, ondelete="restrict"
    )
    name = fields.Char(string="PO Reference", readonly=True, index=True, copy=False)
    date_order = fields.Datetime(string="Order Date", default=fields.Datetime.now, required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("acknowledged", "Acknowledged"),
            ("partially_received", "Partially Received"),
            ("received", "Received"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
            ("superseded", "Superseded by Change Order"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.purchase.order.line", "order_id", string="Lines")
    receipt_ids = fields.One2many("fix.purchase.receipt", "purchase_order_id", string="Receipts")
    buyer_id = fields.Many2one(
        "res.users",
        string="Buyer",
        readonly=True,
        copy=False,
        default=lambda self: self.env.user,
        help="Who raised the order. Never approves or receives it.",
    )
    sent_at = fields.Datetime(readonly=True, copy=False)
    sent_by_id = fields.Many2one("res.users", string="Sent By", readonly=True, copy=False)
    acknowledged_at = fields.Datetime(readonly=True, copy=False, help="Vendor acknowledgement")
    ack_channel = fields.Selection(
        [("portal", "Vendor (P05 portal)"), ("buyer_on_behalf", "Buyer on the vendor's behalf")],
        string="Acknowledged Through",
        readonly=True,
        copy=False,
    )
    ack_by_id = fields.Many2one("res.users", string="Acknowledged By", readonly=True, copy=False)
    ack_evidence = fields.Char(
        string="Acknowledgement Evidence",
        readonly=True,
        copy=False,
        help="For a buyer-recorded acknowledgement: the vendor's confirmation it rests on.",
    )
    vendor_confirmed_date = fields.Date(
        string="Vendor-Confirmed Delivery", readonly=True, copy=False
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount_total = fields.Monetary(
        string="Total", currency_field="currency_id", compute="_compute_total", store=True
    )
    requisition_id = fields.Many2one(
        "fix.requisition", string="Source Requisition", index=True, readonly=True, copy=False
    )
    promised_date = fields.Date(string="Promised Date")
    received_on = fields.Date(string="Received On", readonly=True, copy=False)
    blanket_id = fields.Many2one(
        "fix.procurement.blanket",
        string="Blanket Agreement",
        index=True,
        help="The agreement this order calls off; its cap and validity are checked at send.",
    )
    award_id = fields.Many2one(
        "fix.procurement.award", string="Award", readonly=True, index=True, copy=False
    )
    no_requisition_exception = fields.Boolean(
        string="Documented No-Requisition Exception", readonly=True, copy=False
    )
    exception_reason = fields.Text(readonly=True, copy=False)
    exception_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    exception_at = fields.Datetime(readonly=True, copy=False)
    revision = fields.Integer(readonly=True, default=0, copy=False)
    revision_of_id = fields.Many2one(
        "fix.purchase.order", string="Revision Of", readonly=True, index=True, copy=False
    )
    change_order_id = fields.Many2one(
        "fix.purchase.order", string="Open Change Order", readonly=True, copy=False
    )
    cancel_reason = fields.Char(readonly=True, copy=False)

    PO_PINNED = (
        "vendor_id",
        "currency_id",
        "line_ids",
        "blanket_id",
        "promised_date",
        "date_order",
        "operating_unit_id",
        "branch_id",
        "company_id",
    )
    PO_GUARDED = {
        "state",
        "buyer_id",
        "sent_at",
        "sent_by_id",
        "acknowledged_at",
        "ack_channel",
        "ack_by_id",
        "ack_evidence",
        "vendor_confirmed_date",
        "requisition_id",
        "received_on",
        "award_id",
        "no_requisition_exception",
        "exception_reason",
        "exception_by_id",
        "exception_at",
        "revision",
        "revision_of_id",
        "change_order_id",
        "cancel_reason",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.PO_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.PO_PINNED)
        return locked

    @api.depends("line_ids.line_total")
    def _compute_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped("line_total"))

    # ---- DOFA -------------------------------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return to_company_currency(self, self.amount_total, self.currency_id, self.company_id)

    @api.depends("amount_total", "currency_id")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _a06_extra_conflicts(self):
        rec = self.sudo()
        users = rec.buyer_id | rec.requisition_id.requested_by.user_id
        return users | rec.requisition_id.submitted_by_id | rec.revision_of_id.buyer_id

    def _a06_before_approve(self):
        if self.state != "draft":
            raise UserError(
                "Only a draft PO is approved (%s is %s)." % (self.display_name, self.state)
            )
        self._a06_check_content()
        self._a06_check_requisition()
        self._fix_vendor_gate(self.vendor_id, "Approving PO %s" % self.display_name)

    def _a06_after_approve(self):
        for line in self.line_ids:
            line._guarded().write(
                {"approved_unit_price": line.unit_price, "approved_qty": line.qty_ordered}
            )

    # ---- the supplier gate (filled in by cd_vendor_portal) ----------------
    @api.model
    def _fix_vendor_blockers(self, partner):
        """Why `partner` may not be ordered from. The supplier register (M42)
        lives in cd_vendor_portal, which extends this; without it nothing is
        known about the vendor."""
        return [] if partner else ["no vendor"]

    @api.model
    def _fix_vendor_gate(self, partner, what):
        problems = self._fix_vendor_blockers(partner)
        if problems:
            raise UserError(
                "%s refused: %s is not an active supplier (%s). BRU-PRO-02: purchase "
                "orders go only to suppliers M42 has activated."
                % (what, partner.display_name or "the vendor", "; ".join(problems))
            )

    # ---- create / write ---------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.purchase.order") or (
                    "PO/%s" % fields.Date.today()
                )
        return super().create(vals_list)

    def write(self, vals):
        voided = self.browse()
        pinned = set(self.PO_PINNED) & set(vals)
        if pinned and not self._fix_guard_has_token():
            for rec in self:
                differs = any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in pinned if n != "line_ids"
                ) or bool("line_ids" in pinned and vals.get("line_ids"))
                if not differs:
                    continue
                if rec.state != "draft":
                    raise UserError(
                        "PO %s is %s: its vendor, lines, prices, quantities, currency and dates "
                        "are fixed. Raise a change order (a new revision that is approved "
                        "again)." % (rec.display_name, rec.state)
                    )
                if rec.approval_state in ("pending", "approved", "returned") or rec.dofa_approved:
                    voided |= rec
        result = super().write(vals)
        voided._a06_pinned_changed(
            "the vendor, lines, currency, dates or blanket changed after approval was "
            "requested; request it again."
        )
        return result

    def unlink(self):
        if any(o.state != "draft" for o in self):
            raise UserError("Only a draft purchase order can be deleted; cancel it instead.")
        return super().unlink()

    # ---- checks -----------------------------------------------------------
    def _a06_check_content(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError("PO %s has no lines." % self.display_name)
        if any((line.qty_ordered or 0.0) <= 0 for line in self.line_ids):
            raise UserError("Every line of PO %s needs a positive quantity." % self.display_name)
        if any((line.unit_price or 0.0) < 0 for line in self.line_ids):
            raise UserError("PO %s has a negative price." % self.display_name)
        if (self.amount_total or 0.0) <= 0.0:
            raise UserError("PO %s has no value." % self.display_name)

    def _a06_check_requisition(self):
        """BRU-PRO-01: every PO from an approved requisition, unless a
        Procurement Manager recorded a documented exception."""
        self.ensure_one()
        if self.no_requisition_exception:
            return
        req = self.sudo().requisition_id
        if not req:
            raise UserError(
                "BRU-PRO-01: PO %s has no requisition. Convert an approved requisition, or "
                "have a Procurement Manager record a documented exception." % self.display_name
            )
        if req.state != "converted":
            raise UserError(
                "BRU-PRO-01: requisition %s behind PO %s is %s, not approved and converted."
                % (req.display_name, self.display_name, req.state)
            )

    def _a06_check_blanket(self):
        self.ensure_one()
        blanket = self.sudo().blanket_id
        if not blanket:
            return
        today = fields.Date.context_today(self)
        order_day = fields.Date.to_date(self.date_order) if self.date_order else today
        if blanket.state != "active":
            raise UserError(
                "Blanket agreement %s is %s; call-offs need an active agreement."
                % (blanket.display_name, blanket.state)
            )
        if blanket.vendor_id.commercial_partner_id != self.vendor_id.commercial_partner_id:
            raise UserError(
                "PO %s is to %s but blanket agreement %s is with %s."
                % (
                    self.display_name,
                    self.vendor_id.display_name,
                    blanket.display_name,
                    blanket.vendor_id.display_name,
                )
            )
        if not (blanket.valid_from <= order_day <= blanket.valid_to) or today > blanket.valid_to:
            raise UserError(
                "Blanket agreement %s is valid %s to %s; PO %s falls outside it."
                % (blanket.display_name, blanket.valid_from, blanket.valid_to, self.display_name)
            )
        consumed = blanket._consumed_amount(exclude=self)
        if consumed + (self.amount_total or 0.0) > (blanket.cap_amount or 0.0) + 0.005:
            raise UserError(
                "Blanket agreement %s: cap %.2f, already called off %.2f; PO %s (%.2f) would "
                "exceed it."
                % (
                    blanket.display_name,
                    blanket.cap_amount or 0.0,
                    consumed,
                    self.display_name,
                    self.amount_total or 0.0,
                )
            )

    def _a06_check_award(self):
        self.ensure_one()
        award = self.sudo().award_id
        if not award:
            return
        if award.state != "decided":
            raise UserError("Award %s behind PO %s is not decided." % (award.name, self.name))
        bid = award.bid_id
        if bid.vendor_id.commercial_partner_id != self.vendor_id.commercial_partner_id:
            raise UserError(
                "PO %s is to %s but award %s went to %s."
                % (self.name, self.vendor_id.display_name, award.name, bid.vendor_id.display_name)
            )
        for line in self.line_ids:
            if (
                line.product_id == award.rfq_id.product_id
                and line.unit_price > bid.unit_price + 0.005
            ):
                raise UserError(
                    "PO %s prices %s at %.2f, above the awarded bid %s at %.2f."
                    % (
                        self.name,
                        line.product_id.display_name,
                        line.unit_price,
                        bid.name,
                        bid.unit_price,
                    )
                )

    def _a06_assert_receivable(self):
        self.ensure_one()
        if self.state not in RECEIVABLE_PO_STATES:
            raise UserError(
                "Goods are received only against a sent or acknowledged purchase order "
                "(%s is %s)." % (self.display_name, self.state)
            )

    # ---- approval request -------------------------------------------------
    def action_request_approval(self, justification=None):
        """Route the PO for approval by amount, after its own checks."""
        for po in self:
            require_role(self.env, GROUP_BUYER, "Requesting approval of a purchase order")
            if po.state != "draft":
                raise UserError(
                    "Only a draft PO is submitted for approval (%s is %s)." % (po.name, po.state)
                )
            po._a06_check_content()
            po._a06_check_requisition()
            po._fix_vendor_gate(po.vendor_id, "Requesting approval of PO %s" % po.name)
            po._a06_check_blanket()
            po._a06_check_award()
            text = (
                justification
                or po.dofa_justification
                or po.sudo().requisition_id.justification
                or po.exception_reason
                or ""
            ).strip()
            if not text:
                raise UserError("State the business justification for PO %s." % po.name)
            if po.dofa_justification != text:
                po.write({"dofa_justification": text})
        return super().action_request_approval()

    def action_submit_for_approval(self, justification=None):
        return self.action_request_approval(justification=justification)

    def action_record_requisition_exception(self, reason=None):
        """BRU-PRO-01 exception: a Procurement Manager documents why this PO
        has no requisition. Never on a PO they raised."""
        require_role(self.env, GROUP_MANAGER, "Recording a no-requisition exception")
        for po in self:
            if po.state != "draft":
                raise UserError(
                    "Record the exception on a draft PO (%s is %s)." % (po.name, po.state)
                )
            if po.requisition_id:
                raise UserError(
                    "PO %s already has requisition %s." % (po.name, po.requisition_id.display_name)
                )
            if len((reason or "").strip()) < 10:
                raise UserError(
                    "Document the exception: state why PO %s has no requisition." % po.name
                )
            if not self.env.su and self.env.user in (po.create_uid | po.buyer_id):
                raise UserError(
                    "Segregation of duties: you raised PO %s; another Procurement Manager "
                    "records its exception." % po.name
                )
            if po.approval_state in ("pending", "approved") or po.dofa_approved:
                po._a06_pinned_changed("a no-requisition exception was recorded")
            po._guarded().write(
                {
                    "no_requisition_exception": True,
                    "exception_reason": reason.strip(),
                    "exception_by_id": self.env.uid,
                    "exception_at": fields.Datetime.now(),
                }
            )
            po.message_post(body="No-requisition exception recorded: %s" % reason.strip())
        return True

    # ---- send -------------------------------------------------------------
    def action_send(self):
        for order in self:
            require_role(self.env, GROUP_BUYER, "Sending a purchase order")
            if order.state != "draft":
                raise UserError(
                    "Only a draft, approved PO can be sent (%s is %s)." % (order.name, order.state)
                )
            order._a06_check_content()
            order._a06_check_requisition()
            order._fix_vendor_gate(order.vendor_id, "Sending PO %s" % order.name)
            order._a06_check_blanket()
            order._a06_check_award()
            if order._approval_needed() and order.approval_state != "approved":
                raise UserError(
                    "PO %s (%s) has not been approved. Request approval: it is routed to a "
                    "%s holder."
                    % (order.name, order._dofa_amount_label(), order._dofa_current_tier())
                )
            order._dofa_assert_approved("Sending PO %s" % order.name)
            for line in order.line_ids:
                if line.approved_qty and (
                    abs(line.approved_unit_price - line.unit_price) > 0.005
                    or abs(line.approved_qty - line.qty_ordered) > 1e-6
                ):
                    raise UserError(
                        "PO %s line %s differs from what was approved."
                        % (order.name, line.display_name)
                    )
                line._guarded().write(
                    {"approved_unit_price": line.unit_price, "approved_qty": line.qty_ordered}
                )
            original = order.sudo().revision_of_id
            if original:
                if any(line.qty_received for line in original.line_ids):
                    raise UserError(
                        "PO %s has receipts; its change order %s cannot replace it."
                        % (original.name, order.name)
                    )
                original._guarded().write({"state": "superseded", "change_order_id": order.id})
                original.message_post(body="Superseded by change order %s." % order.name)
            order._guarded().write(
                {"state": "sent", "sent_at": fields.Datetime.now(), "sent_by_id": self.env.uid}
            )
            publish(
                self.env,
                "po.issued",
                "fix.purchase.order",
                order.id,
                {
                    "po_ref": order.name,
                    "vendor_id": order.vendor_id.id,
                    "amount_total": order.amount_total,
                    "currency": order.currency_id.name,
                },
            )
        return True

    # ---- acknowledgement (M16-11) ------------------------------------------
    def action_acknowledge(self, confirmed_date=None):
        """The vendor acknowledges its own PO through the P05 portal. Staff
        record an acknowledgement only on the vendor's behalf, with the
        vendor's confirmation as evidence (Acknowledge on Behalf)."""
        user = self.env.user
        if not user.share:
            raise UserError(
                "A purchase order is acknowledged by the vendor in the P05 portal. To record "
                "a vendor's confirmation received another way, use Acknowledge on Behalf "
                "with the evidence."
            )
        partner = user.commercial_partner_id
        for order in self:
            if order.vendor_id.commercial_partner_id != partner:
                raise UserError("Purchase order not found")
            order._a06_acknowledge("portal", confirmed_date, evidence=False)
        return True

    def action_acknowledge_on_behalf(self, evidence=None, confirmed_date=None):
        require_role(self.env, GROUP_BUYER, "Recording a vendor acknowledgement")
        if len((evidence or "").strip()) < 8:
            raise UserError(
                "Record the vendor's confirmation (e-mail, letter, call reference) that this "
                "acknowledgement rests on."
            )
        for order in self:
            order._a06_acknowledge("buyer_on_behalf", confirmed_date, evidence=evidence.strip())
        return True

    def _a06_acknowledge(self, channel, confirmed_date, evidence):
        self.ensure_one()
        if self.state != "sent":
            raise UserError("Only a sent PO can be acknowledged")
        confirmed = fields.Date.to_date(confirmed_date) if confirmed_date else self.promised_date
        self._guarded().write(
            {
                "state": "acknowledged",
                "acknowledged_at": fields.Datetime.now(),
                "ack_channel": channel,
                "ack_by_id": self.env.uid,
                "ack_evidence": evidence,
                "vendor_confirmed_date": confirmed,
            }
        )
        publish(
            self.env,
            "po.acknowledged",
            "fix.purchase.order",
            self.id,
            {
                "po_ref": self.name,
                "vendor_id": self.vendor_id.id,
                "channel": channel,
                "confirmed_date": str(confirmed) if confirmed else None,
            },
        )

    # ---- change order / cancel / close --------------------------------------
    def action_create_change_order(self):
        """A sent or acknowledged PO is locked. A change is a new revision,
        copied from it, that is approved again; sending the revision
        supersedes the original."""
        require_role(self.env, GROUP_BUYER, "Raising a change order")
        revisions = self.browse()
        for po in self:
            if po.state not in ("sent", "acknowledged"):
                raise UserError(
                    "A change order revises a sent or acknowledged PO (%s is %s)."
                    % (po.name, po.state)
                )
            if any(line.qty_received for line in po.line_ids):
                raise UserError(
                    "PO %s already has receipts: close it for what was received and raise a "
                    "new PO for the balance." % po.name
                )
            open_co = po.change_order_id
            if open_co and open_co.state == "draft":
                raise UserError("PO %s already has open change order %s." % (po.name, open_co.name))
            revision = po.revision + 1
            new = self._guarded().create(
                {
                    "name": "%s/R%d" % ((po.revision_of_id or po).name, revision),
                    "operating_unit_id": po.operating_unit_id.id,
                    "branch_id": po.branch_id.id,
                    "vendor_id": po.vendor_id.id,
                    "currency_id": po.currency_id.id,
                    "date_order": fields.Datetime.now(),
                    "promised_date": po.promised_date,
                    "requisition_id": po.requisition_id.id,
                    "blanket_id": po.blanket_id.id,
                    "award_id": po.award_id.id,
                    "no_requisition_exception": po.no_requisition_exception,
                    "exception_reason": po.exception_reason,
                    "exception_by_id": po.exception_by_id.id,
                    "exception_at": po.exception_at,
                    "revision": revision,
                    "revision_of_id": po.id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": line.product_id.id,
                                "description": line.description,
                                "qty_ordered": line.qty_ordered,
                                "unit_price": line.unit_price,
                            },
                        )
                        for line in po.line_ids
                    ],
                }
            )
            po._guarded().write({"change_order_id": new.id})
            po.message_post(body="Change order %s raised (revision %d)." % (new.name, revision))
            revisions |= new
        return {"change_order_ids": revisions.ids}

    def action_cancel(self, reason=None):
        for po in self:
            if not (reason or "").strip():
                raise UserError("State why PO %s is cancelled." % po.name)
            if po.state in ("partially_received", "received", "closed", "cancelled", "superseded"):
                raise UserError("PO %s is %s and cannot be cancelled." % (po.name, po.state))
            if po.state == "acknowledged":
                # BRU-PRO-18: cancelling after the vendor committed needs a manager.
                require_role(self.env, GROUP_MANAGER, "Cancelling an acknowledged purchase order")
            else:
                require_role(self.env, GROUP_BUYER, "Cancelling a purchase order")
            if po.approval_state == "pending":
                po._approval_void("the purchase order was cancelled")
            po._guarded().write({"state": "cancelled", "cancel_reason": reason.strip()})
            original = po.sudo().revision_of_id
            if original and original.change_order_id == po:
                original._guarded().write({"change_order_id": False})
            publish(self.env, "po.cancelled", "fix.purchase.order", po.id, {"po_ref": po.name})
        return True

    def action_close(self, reason=None):
        for po in self:
            if po.state == "received":
                require_role(self.env, GROUP_BUYER, "Closing a purchase order")
            elif po.state == "partially_received":
                require_role(self.env, GROUP_MANAGER, "Short-closing a partly received PO")
                if not (reason or "").strip():
                    raise UserError("State why PO %s is closed short." % po.name)
            else:
                raise UserError("Only a received PO is closed (%s is %s)." % (po.name, po.state))
            po._guarded().write(
                {"state": "closed", "cancel_reason": (reason or "").strip() or False}
            )
        return True

    # ---- receipts -----------------------------------------------------------
    def action_record_receipt(self, receipts=None):
        """GRN intake: {line_id: qty_received_this_delivery}. Creates and posts
        a fix.purchase.receipt (R5): only on a sent/acknowledged PO, by a
        Receiver who is neither the requester nor the buyer."""
        receipts = {int(k): v for k, v in (receipts or {}).items()}
        Receipt = self.env["fix.purchase.receipt"]
        for order in self:
            order._a06_assert_receivable()
            lines = [
                (0, 0, {"po_line_id": line.id, "qty_received": float(receipts[line.id])})
                for line in order.line_ids
                if float(receipts.get(line.id) or 0.0) > 0
            ]
            if not lines:
                raise UserError(
                    "Nothing to receive on PO %s: give a positive quantity." % order.name
                )
            receipt = Receipt.create({"purchase_order_id": order.id, "line_ids": lines})
            receipt.action_post()
        return True

    def _a06_refresh_receipt_state(self):
        for order in self:
            lines = order.line_ids
            if not lines or order.state not in RECEIVABLE_PO_STATES:
                continue
            fully = all(line.qty_received >= line.qty_ordered - 1e-6 for line in lines)
            partly = any(line.qty_received > 0 for line in lines)
            if fully:
                order._guarded().write(
                    {"state": "received", "received_on": fields.Date.context_today(self)}
                )
            elif partly and order.state != "partially_received":
                order._guarded().write({"state": "partially_received"})

    # ---- cron ---------------------------------------------------------------
    @api.model
    def _cron_open_overdue_expedites(self):
        """POs past the vendor-confirmed (else promised) date with goods still
        due get an expediting case, once."""
        today = fields.Date.context_today(self)
        Expedite = self.env["fix.procurement.expedite"].sudo()
        made = Expedite
        for order in self.sudo().search([("state", "in", RECEIVABLE_PO_STATES)]):
            due = order.vendor_confirmed_date or order.promised_date
            if not due or due >= today:
                continue
            if Expedite.search_count(
                [("purchase_order_id", "=", order.id), ("state", "!=", "resolved")]
            ):
                continue
            made |= Expedite.create(
                {
                    "purchase_order_id": order.id,
                    "reason": "Overdue: due %s, not fully received" % due,
                    "promised_date": due,
                }
            )
        return made


class FixPurchaseOrderLine(models.Model):
    _name = "fix.purchase.order.line"
    _description = "Purchase Order Line"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    order_id = fields.Many2one("fix.purchase.order", required=True, ondelete="cascade", index=True)
    product_id = fields.Many2one("product.product", string="Product", required=True)
    description = fields.Char()
    currency_id = fields.Many2one(related="order_id.currency_id")
    qty_ordered = fields.Float(string="Ordered", required=True, default=1.0)
    receipt_line_ids = fields.One2many(
        "fix.purchase.receipt.line", "po_line_id", string="Receipt Lines"
    )
    qty_received = fields.Float(
        string="Received",
        compute="_compute_received",
        store=True,
        copy=False,
        help="Sum of POSTED goods-receipt lines. Never typed.",
    )
    qty_accepted = fields.Float(
        string="Accepted",
        compute="_compute_received",
        store=True,
        copy=False,
        help="Received and passed (or not subject to) inspection.",
    )
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id", required=True)
    line_total = fields.Monetary(
        string="Line Total", currency_field="currency_id", compute="_compute_line", store=True
    )
    approved_unit_price = fields.Monetary(
        string="Approved Unit Price",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The price the approval covered: the basis of the three-way match.",
    )
    approved_qty = fields.Float(string="Approved Quantity", readonly=True, copy=False)

    LINE_PINNED = ("product_id", "qty_ordered", "unit_price", "order_id", "description")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "qty_received",
            "qty_accepted",
            "approved_unit_price",
            "approved_qty",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(line.order_id.state != "draft" for line in self):
            locked |= set(self.LINE_PINNED)
        return locked

    @api.depends("qty_ordered", "unit_price")
    def _compute_line(self):
        for line in self:
            line.line_total = line.qty_ordered * line.unit_price

    @api.depends(
        "receipt_line_ids.qty_received",
        "receipt_line_ids.qty_accepted",
        "receipt_line_ids.state",
    )
    def _compute_received(self):
        for line in self:
            posted = line.receipt_line_ids.filtered(lambda r: r.state == "posted")
            line.qty_received = sum(posted.mapped("qty_received"))
            line.qty_accepted = sum(posted.mapped("qty_accepted"))

    @api.constrains("qty_ordered", "qty_received")
    def _check_quantities(self):
        for line in self:
            if line.qty_ordered <= 0:
                raise UserError("Ordered quantity must be positive")
            if line.qty_received < 0 or line.qty_received > line.qty_ordered + 1e-6:
                raise UserError(
                    "Received %.2f outside 0..%.2f for %s"
                    % (line.qty_received, line.qty_ordered, line.description or "?")
                )

    def _a06_orders_check(self, orders, what):
        """Lines of a sent PO never change; on a draft PO whose approval was
        requested a change withdraws it."""
        if self._fix_guard_has_token():
            return self.env["fix.purchase.order"]
        locked = orders.filtered(lambda o: o.state != "draft")
        if locked:
            raise UserError(
                "PO %s is %s: %s is not possible. Raise a change order (a new revision that "
                "is approved again)." % (locked[0].name, locked[0].state, what)
            )
        return orders.filtered(
            lambda o: o.approval_state in ("pending", "approved", "returned") or o.dofa_approved
        )

    @api.model_create_multi
    def create(self, vals_list):
        orders = self.env["fix.purchase.order"].browse(
            [v["order_id"] for v in vals_list if v.get("order_id")]
        )
        voided = self._a06_orders_check(orders, "adding a line")
        lines = super().create(vals_list)
        voided._a06_pinned_changed("a line was added after approval was requested")
        return lines

    def write(self, vals):
        voided = self.env["fix.purchase.order"]
        pinned = set(self.LINE_PINNED) & set(vals)
        if pinned:
            changed = self.filtered(
                lambda line: any(line._fix_guard_differs(n, vals[n], line[n]) for n in pinned)
            )
            if changed:
                voided = changed._a06_orders_check(changed.order_id, "changing a line")
        result = super().write(vals)
        voided._a06_pinned_changed("a line changed after approval was requested")
        return result

    def unlink(self):
        orders = self.order_id
        voided = self._a06_orders_check(orders, "removing a line")
        result = super().unlink()
        voided.exists()._a06_pinned_changed("a line was removed after approval was requested")
        return result
