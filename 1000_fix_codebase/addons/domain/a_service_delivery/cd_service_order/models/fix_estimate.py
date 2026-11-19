# fix.estimate — estimate and approval flow (P04-M03-T06).
# Customer-facing in Phase 5; built here per the roadmap.
from datetime import timedelta

from odoo import api, fields, models
from odoo.addons.cd_catalogue.models.fix_commercial_line import (
    LINE_TYPES,
    STOCK_LINE_TYPES,
)
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from . import fix_otp_util

# BRU-SRM-08's second key is a Branch Manager, i.e. DOFA Tier 2.
_BRANCH_MANAGER_GROUP = "cd_entity_config.group_dofa_tier_2"

# A02 audit M01-14: a line priced below its product's list price is refused;
# a lower price is a DISCOUNT, which goes through the DOFA tiers. "0" switches
# the floor off (business decision: e.g. a branch running clearance prices).
PRICE_FLOOR_PARAM = "cd_service_order.estimate_price_floor"

# What an approved estimate may no longer change: the price the customer
# approved (A02 audit M01-5). Revise it instead.
_PRICED_FIELDS = frozenset({"line_ids", "discount", "vat_rate", "currency_id", "order_id"})
# A02 ERP audit M01-F3: 'superseded' is an approved version a later approved
# version replaced. It is decided (frozen) and never governs the money: an
# order keeps exactly ONE approved estimate.
_DECIDED_STATES = ("approved", "rejected", "expired", "superseded")
# A new version is cut from an estimate the customer has seen or decided; a
# draft is edited instead.
_REVISABLE_STATES = ("sent", "approved", "rejected", "expired")
# The order states where the job, and so its price, is history.
_ORDER_FINISHED_STATES = ("delivered", "closed", "cancelled")

# The VAT rate is statutory, not typed: the standard rate in force, or for a
# Service Commercial Approver a zero / scheduled reduced rate. The fallback is
# used only where no Tax Rate Master (M51, cd_tax_engine_bd) can answer.
_COMMERCIAL_APPROVER_GROUP = "cd_service_order.group_so_commercial_approver"
_FALLBACK_VAT_RATE = 15.0
# In-process token (an object, which an RPC caller cannot put in the context):
# lets a revision carry the rate its estimate already has.
_VAT_CARRY_KEY = "fix_estimate_vat_carry"
_VAT_CARRY_TOKEN = object()


class FixEstimate(models.Model):
    """A repair estimate — parts + labour + total, sent for customer approval."""

    _name = "fix.estimate"
    _description = "Repair Estimate"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "fix.dofa.mixin",
        "fix.commercial.document.mixin",
    ]

    # A11 audit P2 (A02 area): the discount DOFA used to be decided by
    # whoever pressed Approve while holding the tier — no request, no named
    # approver, no deadline, no delegate, no history. The DOFA stamp is now
    # given from the approver's M63 inbox only: the preparer asks
    # (action_request_approval), the engine routes to the tier holders minus
    # the preparer and the amount-changer, and action_dofa_approve refuses a
    # direct press. The discount pct is the approval amount, so a change
    # while the request is pending withdraws it (E4/M63-6) and the changer
    # is never its approver.
    _approval_domain = "estimate_discount"
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        # The approval keys are evidence; only their actions stamp them. The
        # DOFA stamp (dofa_approved, _by, _tier, _amount) comes with the mixin.
        # A02 audit M01-4/M01-9: the estimate's own state, approval stamps and
        # the customer's approval reference were writable - a clerk wrote
        # state='approved' on a BDT 34,500 estimate, and "trust me" passed as
        # the customer's documented approval.
        return super()._fix_guarded_fields() | {
            "manager_approval_uid",
            "manager_approved_total",
            "state",
            "approved_at",
            "approved_by",
            "approved_total",
            "customer_approval_ref",
            "customer_approval_method",
            "customer_approval_at",
            "customer_approval_recorded_by",
            "customer_approved_total",
            "customer_otp_expires_at",
            "customer_otp_attempts",
            # A02 ERP audit M01-F3: the version decides which estimate governs
            # the order's money; it is set only by Revise.
            "version",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(e.state in _DECIDED_STATES for e in self):
            # An approved (or rejected/expired) estimate is frozen: revise it.
            locked |= _PRICED_FIELDS | {"signed_estimate_attachment_id", "expiry_date"}
        if not (self.env.su or self.env.user.has_group(_COMMERCIAL_APPROVER_GROUP)):
            # shown, not typed: the server refuses any other rate anyway
            locked.add("vat_rate")
        return locked

    # Discount authority, in percent of the chargeable total. The discount
    # goes through fix.dofa.mixin like every other approval, so it gets the
    # same tier check, self-approval refusal, mandatory justification, amount
    # pin and M30 ladder (A03 audit, R4).
    #
    # D3-03 (owner decision 12 Nov 2026, E3-02): ONE discount ladder. The
    # estimate kept its own 5/15/30/50 bands while the M11 discount approval
    # read the pricing ladder (10/20/35), so an 8% discount was Tier 2 here
    # and the agent's own authority there. The bands are now READ from M11
    # (fix.discount.policy.discount_ladder(), cd_rate_card): the company's
    # released bands, the spec's BRU-PRC-06 default while none is released.
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.discount_pct or 0.0

    def _dofa_thresholds(self):
        company = self.company_id[:1] or self.env.company
        Policy = self.env.get("fix.discount.policy")
        if Policy is not None and hasattr(Policy, "discount_ladder"):
            return Policy.sudo().discount_ladder(company)
        # cd_rate_card not installed: its module still holds the one default
        # (read from there, never copied here).
        from odoo.addons.cd_rate_card.models.pricing_roles import DEFAULT_DISCOUNT_LADDER

        return list(DEFAULT_DISCOUNT_LADDER)

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "a %.1f%% discount (BDT %.2f)" % (self.discount_pct or 0.0, self.discount or 0.0)

    _order = "order_id, version desc"

    # An estimate had no name source, so every message and picker showed
    # "fix.estimate,15" ("you prepared estimate fix.estimate,15, so you cannot
    # approve it" - order rehearsal, 12 Nov 2026). It reads as its order and
    # revision; a pre-sales quote (cd_crm_ext) has no order and keeps its id.
    @api.depends("order_id.name", "version")
    def _compute_display_name(self):
        for est in self:
            if est.order_id:
                est.display_name = "%s · Estimate v%d" % (est.order_id.name, est.version or 1)
            elif isinstance(est.id, int):
                est.display_name = "Estimate #%d v%d" % (est.id, est.version or 1)
            else:
                est.display_name = "New Estimate"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    order_id = fields.Many2one(
        "fix.service.order", string="Service Order", required=True, ondelete="cascade", index=True
    )
    version = fields.Integer(default=1, required=True, help="Incremented on each revision")

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent to Customer"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("expired", "Expired"),
            ("superseded", "Superseded by a Later Version"),
        ],
        default="draft",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )

    # copy=True: a revision (action_revise) carries the lines - One2many fields
    # are not copied by default, so every revision used to be an EMPTY estimate.
    line_ids = fields.One2many("fix.estimate.line", "estimate_id", string="Lines", copy=True)

    # BRU-SRM-07/08 approval evidence — documented customer approval above
    # BDT 5,000; customer + branch manager above BDT 25,000
    customer_approval_ref = fields.Char(
        string="Customer Approval Ref",
        copy=False,
        readonly=True,
        help="BRU-SRM-07: documented customer approval (SMS/OTP ref, signature id) "
        "— required above BDT 5,000 before work begins. Stamped by the verified "
        "customer OTP, the recorded signed estimate, or the customer's own portal "
        "approval; never typed.",
    )
    customer_approval_method = fields.Selection(
        [
            ("otp", "Customer OTP"),
            ("signed_form", "Signed Estimate"),
            ("portal", "Customer Portal"),
        ],
        string="Customer Approval Method",
        readonly=True,
        copy=False,
    )
    customer_approval_at = fields.Datetime(readonly=True, copy=False)
    customer_approval_recorded_by = fields.Many2one(
        "res.users", string="Customer Approval Recorded By", readonly=True, copy=False
    )
    customer_approved_total = fields.Monetary(
        string="Total the Customer Approved",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The customer's approval covers this amount; a higher total voids it.",
    )
    customer_otp_expires_at = fields.Datetime(readonly=True, copy=False)
    customer_otp_attempts = fields.Integer(readonly=True, copy=False)
    customer_otp_digest = fields.Char(readonly=True, copy=False, groups="base.group_system")
    manager_approval_uid = fields.Many2one(
        "res.users",
        string="Manager Approval",
        copy=False,
        readonly=True,
        help="BRU-SRM-08: branch-manager approval — required above BDT 25,000",
    )
    manager_approved_total = fields.Monetary(
        string="Total the Manager Approved",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="A02 audit M01-5: a manager key given at 34,500 covered 230,000. The "
        "key covers this amount; a higher total voids it.",
    )
    APPROVAL_THRESHOLD = 5000  # BRU-SRM-07 default; config-param overridable
    DUAL_APPROVAL_THRESHOLD = 25000  # BRU-SRM-08 default; config-param overridable

    @api.model
    def _threshold_customer(self) -> float:
        """BRU-SRM-07 customer-approval threshold (BDT) — overridable via the
        ``cd_service_order.estimate_threshold_customer`` config parameter so
        the Approval Thresholds screen reflects one live value."""
        return float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cd_service_order.estimate_threshold_customer", self.APPROVAL_THRESHOLD)
        )

    @api.model
    def _threshold_dual(self) -> float:
        """BRU-SRM-08 dual-approval threshold (BDT) — overridable via
        ``cd_service_order.estimate_threshold_dual``."""
        return float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cd_service_order.estimate_threshold_dual", self.DUAL_APPROVAL_THRESHOLD)
        )

    # AS-10: Monetary totals
    parts_total = fields.Monetary(
        string="Parts Total", currency_field="currency_id", compute="_compute_totals", store=True
    )
    labour_total = fields.Monetary(
        string="Labour Total", currency_field="currency_id", compute="_compute_totals", store=True
    )
    # The diagnostic fee is a priced estimate line (RF-009 sample estimate line 3,
    # FR-SRM-029 / BRU-QTE-12): it was summed into NO total, so a charged
    # diagnostic fee never reached the subtotal, the VAT base or the grand total.
    diagnostic_total = fields.Monetary(
        string="Diagnostic Total",
        currency_field="currency_id",
        compute="_compute_totals",
        store=True,
    )
    # Commercial line standard (17 Nov 2026): call-out, transport, AMC,
    # subcontract, warranty extension and fee lines are charges too; they
    # were no line type at all. Stock lines (part / accessory / finished goods)
    # sum into parts; labour, service, support and installation into labour.
    other_total = fields.Monetary(
        string="Other Charges Total",
        currency_field="currency_id",
        compute="_compute_totals",
        store=True,
        help="Call-out, transport / delivery, AMC, rental, subcontract, warranty extension "
        "and other fees.",
    )
    discount = fields.Monetary(string="Discount", currency_field="currency_id", default=0.0)
    vat_rate = fields.Float(
        string="VAT Rate (%)",
        default=lambda self: self._fix_vat_rates_in_force()[0],
        help="The standard VAT rate in force (Tax Rate Master). Only a Service "
        "Commercial Approver applies a zero or scheduled reduced rate.",
    )
    vat_amount = fields.Monetary(
        string="VAT Amount", currency_field="currency_id", compute="_compute_totals", store=True
    )
    grand_total = fields.Monetary(
        string="Grand Total", currency_field="currency_id", compute="_compute_totals", store=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )

    approved_by = fields.Many2one("res.partner", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    approved_total = fields.Monetary(
        string="Total When Approved",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The grand total the approval covers (A02 audit M01-5).",
    )
    expiry_date = fields.Date(string="Estimate Valid Until")

    # --- A02 Enterprise Data Capture & 5-Tier DOFA Discount Governance ---
    discount_pct = fields.Float(
        string="Discount (%)",
        compute="_compute_totals",
        store=True,
        help="Discount percentage relative to pre-discount chargeable total.",
    )
    dofa_tier_required = fields.Selection(
        [
            # D3-03: the bands are the M11 pricing ladder's (cd_rate_card),
            # so the labels name the authority, not a percentage.
            ("tier_0", "Tier 0 — Within the Agent's Authority"),
            ("tier_1", "Tier 1 — Team Lead"),
            ("tier_2", "Tier 2 — Branch Manager"),
            ("tier_3", "Tier 3 — Sales Manager / Commercial Director"),
            ("tier_4", "Tier 4 — CCO / Head of Service Delivery"),
            ("tier_5", "Tier 5 — COO / Managing Director"),
        ],
        string="DOFA Discount Tier",
        compute="_compute_totals",
        store=True,
        help="DOFA tier the discount needs on the M11 pricing ladder "
        "(fix.discount.policy, BRU-PRC-06).",
    )
    dofa_approved_by = fields.Many2one(
        "res.users",
        string="DOFA Discount Approver",
        readonly=True,
        copy=False,
        tracking=True,
        help="Required when the discount is above the agent's own authority on the M11 "
        "pricing ladder (D3-03).",
    )
    diagnostic_notes = fields.Text(
        string="Engineering Quotation Notes & Scope",
        help="Detailed technical scope, warranty exclusions, and spare part lead-time notes.",
    )
    signed_estimate_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Signed Customer Estimate PDF",
        help="Uploaded customer-signed quotation or corporate PO attachment.",
    )

    # line_type is a dependency: re-typing a line moves it between the totals
    # (it was missing, so a re-typed line kept its old bucket until another change).
    @api.depends("line_ids.line_total", "line_ids.line_type", "discount", "vat_rate")
    def _compute_totals(self):
        for est in self:
            totals = {"part": 0.0, "labour": 0.0, "diagnostic": 0.0, "other": 0.0}
            for line in est.line_ids:
                totals[_ESTIMATE_BUCKET.get(line.line_type, "other")] += line.line_total
            est.parts_total = totals["part"]
            est.labour_total = totals["labour"]
            est.diagnostic_total = totals["diagnostic"]
            est.other_total = totals["other"]
            chargeable = est._chargeable_total()
            subtotal = chargeable - est.discount
            est.vat_amount = subtotal * (est.vat_rate / 100.0)
            est.grand_total = subtotal + est.vat_amount
            pct = (est.discount / chargeable * 100.0) if chargeable > 0 else 0.0
            est.discount_pct = round(pct, 2)
            est.dofa_tier_required = est._dofa_tier_for_amount(pct) if pct > 0.0 else "tier_0"

    # --- commercial document standard (17 Nov 2026) -------------------------
    @api.depends("order_id.customer_id")
    def _compute_customer_category(self):
        return super()._compute_customer_category()

    def _fix_doc_partner(self):
        """The customer: the service order's (a CRM-led estimate names the
        lead's partner in cd_crm_ext)."""
        self.ensure_one()
        partner = self.order_id.customer_id if self.order_id else self.env["res.partner"]
        if not partner and "lead_id" in self._fields and self.lead_id:
            partner = self.lead_id.partner_id
        return partner

    def _fix_doc_lines(self):
        return self.line_ids.sorted(lambda r: (r.sequence, r.id))

    def _chargeable_total(self) -> float:
        """Parts + labour + diagnostic + other charges: the VAT-exclusive
        amount before discount."""
        self.ensure_one()
        return self.parts_total + self.labour_total + self.diagnostic_total + self.other_total

    @api.constrains("discount", "line_ids")
    def _check_discount(self):
        """A discount is never negative and never exceeds the parts + labour +
        diagnostic amount it discounts - otherwise the subtotal goes negative, VAT
        is charged on a negative base and a negative "revenue" reaches the Role
        Centre (R01 re-audit 2026-10-22: estimate with no lines, discount 200 ->
        grand total -200.30)."""
        for est in self:
            if est.discount < 0:
                raise ValidationError("An estimate discount cannot be negative.")
            chargeable = est._chargeable_total()
            if est.discount > chargeable:
                raise ValidationError(
                    "The discount (%.2f) cannot exceed the parts, labour and diagnostic "
                    "total (%.2f)." % (est.discount, chargeable)
                )

    def _check_has_lines(self, action: str) -> None:
        for est in self:
            if not est.line_ids:
                raise UserError(
                    "An estimate with no parts, labour or diagnostic lines cannot be %s." % action
                )

    # --- the VAT rate is the statutory one (it was a free-entry field) ---
    @api.model
    def _fix_vat_rates_in_force(self, company=None):
        """``(standard, other scheduled rates)`` in percent, today. From the
        Tax Rate Master when cd_tax_engine_bd is installed (M01 does not
        depend on it); a quote still gets the usual rate where the master
        cannot answer - the tax invoice is determined by M51, not here."""
        Rate = self.env.get("fix.tax.rate")
        if Rate is not None:
            try:
                rates = Rate._fix_vat_rates(None, company or self.env.company)
                return float(rates.standard), {float(rate) for rate in rates.reduced}
            except UserError:
                pass
        return _FALLBACK_VAT_RATE, set()

    def _fix_assert_vat_rate(self, rate, company=None) -> None:
        standard, scheduled = self._fix_vat_rates_in_force(company)
        rate = float(rate or 0.0)
        if abs(rate - standard) < 1e-6:
            return
        allowed = sorted(scheduled | {0.0})
        if self.env.user.has_group(_COMMERCIAL_APPROVER_GROUP) and any(
            abs(rate - other) < 1e-6 for other in allowed
        ):
            return
        raise UserError(
            "VAT rate %g%% cannot be set on an estimate: the standard VAT rate in force "
            "is %g%%. Only a Service Commercial Approver applies a zero or scheduled "
            "reduced rate (%s)." % (rate, standard, " / ".join("%g%%" % r for r in allowed))
        )

    @api.model_create_multi
    def create(self, vals_list):
        carried = self.env.context.get(_VAT_CARRY_KEY) is _VAT_CARRY_TOKEN
        if not (self.env.su or carried):
            Company = self.env["res.company"]
            for vals in vals_list:
                if "vat_rate" in vals:
                    self._fix_assert_vat_rate(
                        vals["vat_rate"], Company.browse(vals.get("company_id") or [])
                    )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            if "vat_rate" in vals:
                # the form posts the rate it shows: only a CHANGE is judged
                for est in self:
                    if est._fix_guard_differs("vat_rate", vals["vat_rate"], est.vat_rate):
                        est._fix_assert_vat_rate(vals["vat_rate"], est.company_id)
            # A02 audit M01-5: the customer approved BDT 4,600 and staff then
            # added a BDT 50,000 line to the approved estimate. A decided
            # estimate's price is frozen; a new price is a revision.
            if "order_id" in vals:
                self._fix_assert_order_link_open(vals["order_id"])
            priced = _PRICED_FIELDS & set(vals)
            frozen = self.filtered(lambda e: e.state in _DECIDED_STATES)
            if priced == {"order_id"} and not frozen.filtered("order_id"):
                # A pre-sales (CRM) estimate is adopted by the order its won
                # deal converts into: the price does not change.
                priced = set()
            if priced and frozen:
                raise UserError(
                    "Estimate %s is %s: its price is frozen. Revise it to quote a new "
                    "price." % (", ".join(frozen.mapped("display_name")), frozen[:1].state)
                )
            if "signed_estimate_attachment_id" in vals and frozen:
                raise UserError("The signed estimate of a decided estimate cannot be replaced.")
        result = super().write(vals)
        if vals.get("customer_approval_ref") and "customer_approved_total" not in vals:
            # The portal records the customer's own approval (sudo): pin the
            # amount it covers so a later raise voids it.
            for est in self:
                est._guarded().write(
                    {
                        "customer_approved_total": est.grand_total,
                        "customer_approval_method": est.customer_approval_method or "portal",
                        "customer_approval_at": est.customer_approval_at or fields.Datetime.now(),
                    }
                )
        self._fix_void_on_raise()
        return result

    def _fix_assert_order_link_open(self, order_value) -> None:
        """A02 ERP audit M01-F3: an estimate that is with the customer, or
        carries any approval, belongs to its order. Moving a sent estimate
        that held the customer's OTP approval to another order carried that
        approval (and its price) onto a job the customer never saw. A draft
        estimate may still be re-pointed; a CRM quote with no order is
        adopted by the order its deal converts into."""
        for est in self:
            if not est.order_id or not est._fix_guard_differs(
                "order_id", order_value, est.order_id
            ):
                continue
            if (
                est.state != "draft"
                or est.customer_approval_ref
                or est.manager_approval_uid
                or est.dofa_approved_by
            ):
                raise UserError(
                    "Estimate %s is %s and belongs to order %s: it cannot be moved to "
                    "another order. Raise a new estimate on that order instead."
                    % (est.display_name, est.state, est.order_id.name)
                )

    def _fix_void_on_raise(self) -> None:
        """M01-5 (S4): an approval covers the amount it saw. A higher grand
        total voids the estimate's approval, the manager key and the
        customer's approval; they are given again on the new amount."""
        for est in self:
            if not isinstance(est.id, int):
                continue
            total = est.grand_total or 0.0
            changes = {}
            notes = []
            # A pin is only what an approval stamped: superuser data loads that
            # write an approved estimate without its totals are not re-judged.
            if (
                est.state == "approved"
                and est.approved_at
                and est.approved_total
                and total > est.approved_total + 0.005
            ):
                changes.update(
                    state="sent", approved_at=False, approved_by=False, approved_total=0.0
                )
                notes.append("the approval")
            if (
                est.manager_approval_uid
                and est.manager_approved_total
                and total > est.manager_approved_total + 0.005
            ):
                changes.update(manager_approval_uid=False, manager_approved_total=0.0)
                notes.append("the branch-manager key")
            if (
                est.customer_approval_ref
                and est.customer_approved_total
                and total > est.customer_approved_total + 0.005
            ):
                changes.update(
                    customer_approval_ref=False,
                    customer_approval_method=False,
                    customer_approval_at=False,
                    customer_approval_recorded_by=False,
                    customer_approved_total=0.0,
                )
                notes.append("the customer's approval")
            if changes:
                est._guarded().write(changes)
                est.message_post(
                    body="The total rose to BDT %.2f: %s voided and must be given again."
                    % (total, ", ".join(notes))
                )

    def _fix_drive_order(self, target: str) -> None:
        """Estimate send/approve moves the order (A02 audit M01-2: approving
        the estimate left the order waiting). Only an order still before the
        customer's decision is driven; a revision on a running job is not."""
        path = ["diagnostic", "estimate_pending", "estimate_sent", "awaiting_approval", "approved"]
        for est in self:
            order = est.order_id
            if not order or order.state not in path[:-1]:
                continue
            for step in path[path.index(order.state) + 1 : path.index(target) + 1]:
                order._fix_advance(step)

    def action_send(self):
        self._check_has_lines("sent to the customer")
        for est in self:
            if est.state == "sent":
                continue
            if est.state != "draft":
                raise UserError(
                    "Only a draft estimate is sent; this one is %s. Revise it to send a "
                    "new version." % est.state
                )
            est._guarded().write({"state": "sent"})
            publish(self.env, "estimate.sent", "fix.estimate", est.id, est._fix_event_payload())
            est._fix_drive_order("estimate_sent")

    def action_approve(self):
        """BRU-SRM-07 (H): above the customer threshold the CUSTOMER approval
        must be documented before the estimate can be approved; BRU-SRM-08
        (H): above the dual threshold the BRANCH MANAGER approves too. Hard
        gates. Thresholds default to BDT 5,000 / 25,000 and are config-param
        overridable — the live values drive the Approval Thresholds screen.

        A02 audit M01-4: only an estimate the customer has (state 'sent'),
        and only before it expires. The approval pins the amount and moves
        the order to approved."""
        self._check_has_lines("approved")
        customer_threshold = self._threshold_customer()
        dual_threshold = self._threshold_dual()
        today = fields.Date.context_today(self)
        for est in self:
            if est.state != "sent":
                raise UserError(
                    "Only an estimate sent to the customer can be approved; this one is "
                    "%s." % est.state
                )
            if est.expiry_date and est.expiry_date < today:
                raise UserError(
                    "This estimate expired on %s (BRU-SRM-13). Revise it and send the new "
                    "version to the customer." % est.expiry_date
                )
            newer = est._fix_newer_live_versions()
            if newer:
                raise UserError(
                    "Estimate %s is superseded by version %d, which is with the customer. "
                    "Approve the latest version." % (est.display_name, max(newer.mapped("version")))
                )
            if est.grand_total > dual_threshold:
                if not est.customer_approval_ref:
                    raise UserError(
                        "BRU-SRM-07: documented customer approval is required "
                        "before approving an estimate above BDT %.0f" % dual_threshold
                    )
                if not est.manager_approval_uid:
                    raise UserError(
                        "BRU-SRM-08: branch-manager approval is required above "
                        "BDT %.0f (record the customer approval first, then have "
                        "the manager approve)" % dual_threshold
                    )
            elif est.grand_total > customer_threshold and not est.customer_approval_ref:
                raise UserError(
                    "BRU-SRM-07: documented customer approval is required before "
                    "approving an estimate above BDT %.0f" % customer_threshold
                )
            # Segregation of duties: nothing is approved on its preparer's word
            # alone (at or under the customer threshold nothing else was asked).
            # The customer's documented approval - verified code, portal, or a
            # signed form someone else recorded - is the second party; without
            # it another member of staff records the approval.
            if (
                not self.env.su
                and est.create_uid == self.env.user
                and not est.customer_approval_ref
            ):
                raise UserError(
                    "Segregation of duties: you prepared estimate %s, so you cannot "
                    "approve it on your own word. Take the customer's approval code "
                    "(Send / Verify Customer OTP), or have another member of staff "
                    "record the approval." % est.display_name
                )
            # A discount above front-desk authority is approved before the
            # estimate is. action_approve used to ignore the DOFA tier, so a
            # 40% discount whose only approval was REJECTED was approved,
            # quoted and accepted (A03 audit). The approval must also still
            # cover the discount: one signed off at 12% does not cover 14%.
            est._dofa_assert_approved("Estimate approval")
            est._guarded().write(
                {
                    "state": "approved",
                    "approved_at": fields.Datetime.now(),
                    "approved_by": est.order_id.customer_id.id or False,
                    "approved_total": est.grand_total,
                }
            )
            est._fix_supersede_other_versions()
            publish(self.env, "estimate.approved", "fix.estimate", est.id, est._fix_event_payload())
            est._fix_drive_order("approved")

    def _fix_other_versions(self):
        self.ensure_one()
        if not self.order_id:
            return self.browse()
        return self.sudo().order_id.estimate_ids.filtered(lambda e: e.id != self.id)

    def _fix_newer_live_versions(self):
        """Later versions of this estimate that are with the customer or
        approved: an older version is no longer the price on the table."""
        self.ensure_one()
        return self._fix_other_versions().filtered(
            lambda e: e.version > self.version and e.state in ("sent", "approved")
        )

    def _fix_supersede_other_versions(self) -> None:
        """A02 ERP audit M01-F3: approving a version retires every other
        version still with the customer or approved, so the order has exactly
        one approved estimate (the billing engine and the settlement read
        ``estimate_ids.filtered(state == 'approved')``)."""
        for est in self:
            others = est._fix_other_versions().filtered(lambda e: e.state in ("sent", "approved"))
            if not others:
                continue
            others._guarded().write({"state": "superseded"})
            for other in others:
                other.message_post(
                    body="Superseded: version %d of this estimate was approved." % est.version
                )

    def action_request_manager_key(self, justification=None):
        """Route the BRU-SRM-08 second key to a branch manager's M63 inbox
        (A02 audit B1): the key was a plain group check on whoever pressed
        the button, with no request, deadline, delegate or history."""
        dual_threshold = self._threshold_dual()
        for est in self:
            if not self._fix_check_manager_key_due(est, dual_threshold):
                raise UserError(
                    "Estimate %s is BDT %.2f: at or below BDT %.0f no branch-manager key "
                    "is needed." % (est.display_name, est.grand_total, dual_threshold)
                )
            if est.manager_approval_uid:
                raise UserError("Estimate %s already carries the manager key." % est.display_name)
            self.env["fix.so.approval"]._fix_open(
                "manager_key",
                est.order_id,
                (justification or "").strip() or "BRU-SRM-08 second key",
                estimate=est,
            )
        return True

    def action_manager_approve(self):
        """The BRU-SRM-08 second key: the branch manager records their
        approval on an estimate already carrying customer approval. Decided
        from the approver's M63 inbox (action_request_manager_key)."""
        dual_threshold = self._threshold_dual()
        Approval = self.env["fix.so.approval"]
        for est in self:
            if not self._fix_check_manager_key_due(est, dual_threshold):
                continue
            Approval._fix_assert_routed(est, "manager_key")
            # The "second key" had no key: whoever called this became the
            # branch manager (A03 audit). A delegate decides on the absent
            # manager's authority.
            if not Approval._fix_authority_user().has_group(_BRANCH_MANAGER_GROUP):
                raise UserError(
                    "BRU-SRM-08: the second approval needs Branch Manager authority "
                    "(DOFA Tier 2)."
                )
            if est.create_uid in Approval._fix_acting_users():
                raise UserError(
                    "Segregation of duties: the person who prepared the estimate "
                    "cannot give the branch-manager approval."
                )
            est._guarded().write(
                {
                    "manager_approval_uid": self.env.user.id,
                    "manager_approved_total": est.grand_total,
                }
            )

    def _fix_check_manager_key_due(self, est, dual_threshold) -> bool:
        """Whether the BRU-SRM-08 second key can be given on ``est`` now."""
        if est.grand_total <= dual_threshold:
            return False  # single approval suffices
        if est.state not in ("draft", "sent"):
            raise UserError("Estimate %s is %s." % (est.display_name, est.state))
        if not est.customer_approval_ref:
            raise UserError(
                "BRU-SRM-08: customer approval must be documented before the manager approves"
            )
        return True

    # --- the customer's documented approval (BRU-SRM-07, A02 audit M01-9) ---
    def action_send_customer_otp(self):
        """Send the customer a one-time code to approve this estimate."""
        for est in self:
            if est.state != "sent":
                raise UserError("Send the estimate to the customer first.")
            partner = est.order_id.customer_id
            phone = fix_otp_util.bd_mobile(partner) if partner else ""
            if not phone:
                raise UserError(
                    "The customer has no valid Bangladesh mobile number for an approval code."
                )
            code = fix_otp_util.issue_code()
            fix_otp_util.dispatch_otp(phone, code, fix_otp_util.OTP_TTL_SECONDS)
            est.sudo().write(
                {
                    "customer_otp_digest": fix_otp_util.digest(
                        self.env, "estimate_approval", est.id, code
                    ),
                    "customer_otp_expires_at": fields.Datetime.now()
                    + timedelta(seconds=fix_otp_util.OTP_TTL_SECONDS),
                    "customer_otp_attempts": 0,
                }
            )
            est.message_post(
                body="Approval code sent to the customer's phone %s." % fix_otp_util.mask(phone)
            )
        return True

    def action_verify_customer_otp(self, otp=None, code=None):
        """Record the customer's approval from the code they read back. A
        wrong code is counted, not raised (a raise would roll the counter
        back); five misses burn it."""
        code = (otp or code or "").strip()
        result = {"verified": True}
        for est in self:
            stored = est.sudo().customer_otp_digest
            if est.state != "sent" or not stored or not est.customer_otp_expires_at:
                raise UserError("Send the customer an approval code first.")
            if fields.Datetime.now() > est.customer_otp_expires_at:
                raise UserError("The approval code has expired. Send a new one.")
            if not fix_otp_util.matches(self.env, "estimate_approval", est.id, code, stored):
                attempts = est.customer_otp_attempts + 1
                burnt = attempts >= fix_otp_util.OTP_MAX_ATTEMPTS
                est.sudo().write(
                    {
                        "customer_otp_attempts": attempts,
                        "customer_otp_digest": False if burnt else stored,
                    }
                )
                result = {
                    "verified": False,
                    "error": "That approval code is not correct."
                    + (" Too many attempts: send a new code." if burnt else ""),
                }
                continue
            phone = fix_otp_util.bd_mobile(est.order_id.customer_id)
            now = fields.Datetime.now()
            est.sudo().write({"customer_otp_digest": False})
            est._guarded().write(
                {
                    "customer_approval_ref": "OTP %s %s" % (fix_otp_util.mask(phone), now),
                    "customer_approval_method": "otp",
                    "customer_approval_at": now,
                    "customer_approval_recorded_by": self.env.user.id,
                    "customer_approved_total": est.grand_total,
                }
            )
            est.message_post(
                body="Customer approval verified by code (BDT %.2f)." % est.grand_total
            )
        return result

    def action_record_signed_approval(self):
        """Record the customer's signed estimate as the documented approval.
        The signed PDF must be attached, and the person recording it is not
        the person who prepared the estimate."""
        for est in self:
            if est.state != "sent":
                raise UserError("Send the estimate to the customer first.")
            if not est.signed_estimate_attachment_id:
                raise UserError("Attach the customer's signed estimate first.")
            if est.create_uid == self.env.user and not self.env.su:
                raise UserError(
                    "Segregation of duties: the person who prepared the estimate cannot "
                    "record the customer's signed approval of it."
                )
            now = fields.Datetime.now()
            est._guarded().write(
                {
                    "customer_approval_ref": "SIGNED %s"
                    % (
                        est.signed_estimate_attachment_id.name
                        or est.signed_estimate_attachment_id.id
                    ),
                    "customer_approval_method": "signed_form",
                    "customer_approval_at": now,
                    "customer_approval_recorded_by": self.env.user.id,
                    "customer_approved_total": est.grand_total,
                }
            )
        return True

    def action_reject(self):
        for est in self:
            if est.state != "sent":
                raise UserError(
                    "Only an estimate awaiting the customer's decision can be rejected; "
                    "this one is %s." % est.state
                )
            est._guarded().write({"state": "rejected"})
            publish(self.env, "estimate.rejected", "fix.estimate", est.id, est._fix_event_payload())
            order = est.order_id
            if order and order.state in ("estimate_sent", "awaiting_approval"):
                # The order cannot be approved on a rejected price; it waits
                # for a revised estimate or is cancelled ('estimate_declined').
                order.message_post(
                    body="Estimate v%d rejected by the customer. Revise the estimate, or "
                    "cancel the order with reason 'estimate declined'." % est.version
                )

    def action_revise(self):
        """Create a new version (T06: part-approval and revision), lines included.

        Only where a new version makes sense (it was allowed from any state):
        from an estimate the customer has seen or decided, the latest one,
        while the job is still open."""
        self.ensure_one()
        if self.state not in _REVISABLE_STATES:
            raise UserError(
                "Estimate %s is still a draft: edit it. A revision is a new version of "
                "an estimate the customer has already seen." % self.display_name
            )
        order = self.sudo().order_id
        if order.state in _ORDER_FINISHED_STATES:
            raise UserError(
                "Order %s is %s: its estimate can no longer be revised." % (order.name, order.state)
            )
        newer = order.estimate_ids.filtered(lambda e: e.version > self.version)
        if newer:
            raise UserError(
                "Estimate %s is superseded by version %d. Revise the latest version."
                % (self.display_name, max(newer.mapped("version")))
            )
        # the revision carries the rate this estimate already has
        carrier = self.with_context(**{_VAT_CARRY_KEY: _VAT_CARRY_TOKEN})
        # the version is guarded (M01-F3): only a revision numbers one
        new = carrier._guarded().copy({"version": self.version + 1, "state": "draft"})
        new = new.with_env(self.env)
        return {
            "type": "ir.actions.act_window",
            "res_model": "fix.estimate",
            "res_id": new.id,
            "view_mode": "form",
        }

    def _approval_on_rejected(self, comment):
        """A11 audit P2: an inbox rejection of the discount is evidence on the
        estimate's thread — the preparer lowers the discount or asks again."""
        for rec in self:
            rec.message_post(
                body="Discount approval rejected by %s: %s"
                % (rec.env.user.name, comment or "no comment recorded")
            )

    @api.model
    def _cron_expire_estimates(self):
        """BRU-SRM-13: a sent estimate past its validity date expires."""
        today = fields.Date.context_today(self)
        stale = self.sudo().search([("state", "=", "sent"), ("expiry_date", "<", today)])
        for est in stale:
            est._guarded().write({"state": "expired"})
            publish(self.env, "estimate.expired", "fix.estimate", est.id, est._fix_event_payload())
        return len(stale)

    def _fix_event_payload(self) -> dict:
        self.ensure_one()
        return {
            "estimate_id": self.id,
            "order_id": self.order_id.id,
            "service_order_id": self.order_id.id,
            "version": self.version,
            "state": self.state,
            "grand_total": self.grand_total,
        }


class FixApprovalMatrixEstimateDiscount(models.Model):
    """A11 audit P2: lets a DoA matrix row target the routed estimate
    discount (SLA, escalation, policy) without touching any other DOFA
    approval."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("estimate_discount", "Estimate Discount Approval")],
        ondelete={"estimate_discount": "cascade"},
    )


class FixEstimateLine(models.Model):
    _name = "fix.estimate.line"
    _description = "Estimate Line"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.commercial.line.mixin"]
    _order = "estimate_id, sequence, id"

    estimate_id = fields.Many2one("fix.estimate", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    # The commercial line standard: stock lines (part, accessory, finished
    # goods) and charge lines (service, labour, support, diagnostic, call-out,
    # transport, installation, ...). Was part / labour / diagnostic only.
    line_type = fields.Selection(LINE_TYPES, string="Type", required=True, default="part")
    product_id = fields.Many2one("product.product", string="Item / Charge Code")
    description = fields.Char(required=True)
    quantity = fields.Float(default=1.0, digits="Product Unit of Measure")
    # AS-10: Monetary
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    line_total = fields.Monetary(
        string="Line Total", currency_field="currency_id", compute="_compute_line_total", store=True
    )

    @api.depends("quantity", "unit_price")
    def _compute_line_total(self):
        for line in self:
            line.line_total = line.quantity * line.unit_price

    # The estimate-level _check_discount only runs when the ESTIMATE is written;
    # a line priced down, re-typed or deleted directly lowered parts + labour
    # under the discount unchecked (negative subtotal, negative VAT).
    @api.constrains("quantity", "unit_price", "line_type", "estimate_id")
    def _check_estimate_discount(self):
        self.estimate_id._check_discount()

    # --- A02 audit M01-5 / M01-14: a decided estimate's lines are frozen,
    # and no line is priced under its product's list price ---
    def _fix_assert_estimate_open(self, estimates) -> None:
        decided = estimates.filtered(
            lambda e: e.state in _DECIDED_STATES and not e._fix_guard_open()
        )
        if decided:
            raise UserError(
                "Estimate %s is %s: its lines are frozen. Revise it to quote a new price."
                % (", ".join(decided.mapped("display_name")), decided[:1].state)
            )

    def _fix_check_price_floor(self) -> None:
        if self.env.su or not _param_on(self.env, PRICE_FLOOR_PARAM):
            return
        for line in self:
            floor = line.product_id.lst_price if line.product_id else 0.0
            if floor and (line.unit_price or 0.0) + 0.005 < floor:
                raise UserError(
                    "%s is listed at BDT %.2f; it cannot be quoted at BDT %.2f. Quote the "
                    "list price and give a discount, which the DOFA tiers approve."
                    % (line.product_id.display_name, floor, line.unit_price or 0.0)
                )

    def _fix_check_not_negative(self) -> None:
        """The floor every line has, product or not: zero. A negative price or
        quantity took money off the total with no discount, so no DOFA tier."""
        if self.env.su:
            return
        for line in self:
            if (line.unit_price or 0.0) < 0 or (line.quantity or 0.0) < 0:
                raise UserError(
                    "Estimate line '%s' cannot have a negative price or quantity. Give a "
                    "discount on the estimate instead, which the DOFA tiers approve."
                    % (line.description or "")
                )

    def _fix_check_sellable(self) -> None:
        """A04 audit (2026-11-04) M37-2 / M11-4: the catalogue lifecycle
        (a discontinued, archived or out-of-scope item is not quoted) and the
        M11 price floor were read by no estimate. product.product's
        _fix_check_sale (cd_catalogue, extended by cd_rate_card) is the one
        check every selling document runs."""
        if self.env.su:
            return
        for line in self.filtered("product_id"):
            line.product_id._fix_check_sale(unit_price=line.unit_price or 0.0, channel="estimate")

    @api.model_create_multi
    def create(self, vals_list):
        ids = {v.get("estimate_id") for v in vals_list if v.get("estimate_id")}
        self._fix_assert_estimate_open(self.env["fix.estimate"].browse(list(ids)))
        vals_list = [self._fix_commercial_prepare(dict(v)) for v in vals_list]
        for vals in vals_list:
            if not vals.get("description") and vals.get("product_id"):
                product = self.env["product.product"].browse(vals["product_id"])
                vals["description"] = product.name
        lines = super().create(vals_list)
        lines._fix_check_not_negative()
        lines._fix_check_price_floor()
        lines._fix_check_sellable()
        lines.estimate_id._fix_void_on_raise()
        return lines

    def write(self, vals):
        self._fix_assert_estimate_open(self.estimate_id)
        if vals.get("estimate_id"):
            self._fix_assert_estimate_open(self.env["fix.estimate"].browse(vals["estimate_id"]))
        result = super().write(vals)
        if {"unit_price", "quantity"} & set(vals):
            self._fix_check_not_negative()
        if {"unit_price", "product_id"} & set(vals):
            self._fix_check_price_floor()
            self._fix_check_sellable()
        self.estimate_id._fix_void_on_raise()
        return result

    def unlink(self):
        estimates = self.estimate_id
        self._fix_assert_estimate_open(estimates)
        result = super().unlink()
        estimates.exists()._check_discount()
        return result


# Which estimate total a line type sums into.
_ESTIMATE_BUCKET = dict.fromkeys(STOCK_LINE_TYPES, "part")
_ESTIMATE_BUCKET.update(
    {
        "labour": "labour",
        "service": "labour",
        "support": "labour",
        "installation": "labour",
        "diagnostic": "diagnostic",
    }
)


def _param_on(env, key, default="1"):
    raw = env["ir.config_parameter"].sudo().get_param(key, default)
    return str(raw).strip().lower() not in ("0", "false", "no", "off", "")
