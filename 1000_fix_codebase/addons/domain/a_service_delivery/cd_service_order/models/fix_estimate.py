# fix.estimate — estimate and approval flow (P04-M03-T06).
# Customer-facing in Phase 5; built here per the roadmap.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

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
_DECIDED_STATES = ("approved", "rejected", "expired")


class FixEstimate(models.Model):
    """A repair estimate — parts + labour + total, sent for customer approval."""

    _name = "fix.estimate"
    _description = "Repair Estimate"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]

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
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(e.state in _DECIDED_STATES for e in self):
            # An approved (or rejected/expired) estimate is frozen: revise it.
            locked |= _PRICED_FIELDS | {"signed_estimate_attachment_id", "expiry_date"}
        return locked

    # Discount authority, in percent of the chargeable total. Up to 5% is
    # front-desk authority (Tier 1) and needs no sign-off; above it the
    # discount goes through fix.dofa.mixin like every other approval, so it
    # gets the same tier check, self-approval refusal, mandatory
    # justification, amount pin and M30 ladder (A03 audit, R4).
    _DOFA_DISCOUNT_THRESHOLDS = [
        (0.0, "tier_0"),
        (5.0, "tier_1"),
        (15.0, "tier_2"),
        (30.0, "tier_3"),
        (50.0, "tier_4"),
        (float("inf"), "tier_5"),
    ]

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.discount_pct or 0.0

    def _dofa_thresholds(self):
        return self._DOFA_DISCOUNT_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "a %.1f%% discount (BDT %.2f)" % (self.discount_pct or 0.0, self.discount or 0.0)

    def _dofa_current_tier(self) -> str:
        # Tier 1 is the front desk's own authority: nothing to sign off.
        tier = super()._dofa_current_tier()
        return "tier_0" if tier == "tier_1" else tier

    _order = "order_id, version desc"

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
    discount = fields.Monetary(string="Discount", currency_field="currency_id", default=0.0)
    vat_rate = fields.Float(
        string="VAT Rate (%)", default=15.0, help="Bangladesh standard VAT rate"
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
            ("tier_0", "Tier 0 — No Discount (0%)"),
            ("tier_1", "Tier 1 — Front-Desk / Advisor (Up to 5%)"),
            ("tier_2", "Tier 2 — Branch Manager (5% to 15%)"),
            ("tier_3", "Tier 3 — Regional Operations Manager (15% to 30%)"),
            ("tier_4", "Tier 4 — Head of Service Delivery (30% to 50%)"),
            ("tier_5", "Tier 5 — COO / Managing Director (> 50% / Full Waiver)"),
        ],
        string="DOFA Discount Tier",
        compute="_compute_totals",
        store=True,
        help="5-tier Delegation of Financial Authority required for commercial discount.",
    )
    dofa_approved_by = fields.Many2one(
        "res.users",
        string="DOFA Discount Approver",
        readonly=True,
        copy=False,
        tracking=True,
        help="Required when discount_pct > 5.0% (Tier 2+ DOFA governance).",
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
            totals = {"part": 0.0, "labour": 0.0, "diagnostic": 0.0}
            for line in est.line_ids:
                totals[line.line_type] += line.line_total
            est.parts_total = totals["part"]
            est.labour_total = totals["labour"]
            est.diagnostic_total = totals["diagnostic"]
            chargeable = est._chargeable_total()
            subtotal = chargeable - est.discount
            est.vat_amount = subtotal * (est.vat_rate / 100.0)
            est.grand_total = subtotal + est.vat_amount
            pct = (est.discount / chargeable * 100.0) if chargeable > 0 else 0.0
            est.discount_pct = round(pct, 2)
            est.dofa_tier_required = est._dofa_tier_for_amount(pct) if pct > 0.0 else "tier_0"

    def _chargeable_total(self) -> float:
        """Parts + labour + diagnostic: the VAT-exclusive amount before discount."""
        self.ensure_one()
        return self.parts_total + self.labour_total + self.diagnostic_total

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

    def write(self, vals):
        if self and not self._fix_guard_open():
            # A02 audit M01-5: the customer approved BDT 4,600 and staff then
            # added a BDT 50,000 line to the approved estimate. A decided
            # estimate's price is frozen; a new price is a revision.
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
            est._emit_event("estimate.sent")
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
            est._emit_event("estimate.approved")
            est._fix_drive_order("approved")

    def action_manager_approve(self):
        """The BRU-SRM-08 second key: the branch manager records their
        approval on an estimate already carrying customer approval."""
        dual_threshold = self._threshold_dual()
        for est in self:
            if est.grand_total <= dual_threshold:
                continue  # single approval suffices
            if est.state not in ("draft", "sent"):
                raise UserError("Estimate %s is %s." % (est.display_name, est.state))
            if not est.customer_approval_ref:
                raise UserError(
                    "BRU-SRM-08: customer approval must be documented before "
                    "the manager approves"
                )
            # The "second key" had no key: whoever called this became the
            # branch manager (A03 audit).
            if not self.env.user.has_group(_BRANCH_MANAGER_GROUP):
                raise UserError(
                    "BRU-SRM-08: the second approval needs Branch Manager authority "
                    "(DOFA Tier 2)."
                )
            if est.create_uid == self.env.user:
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
            est._emit_event("estimate.rejected")
            order = est.order_id
            if order and order.state in ("estimate_sent", "awaiting_approval"):
                # The order cannot be approved on a rejected price; it waits
                # for a revised estimate or is cancelled ('estimate_declined').
                order.message_post(
                    body="Estimate v%d rejected by the customer. Revise the estimate, or "
                    "cancel the order with reason 'estimate declined'." % est.version
                )

    def action_revise(self):
        """Create a new version (T06: part-approval and revision), lines included."""
        self.ensure_one()
        new = self.copy({"version": self.version + 1, "state": "draft"})
        return {
            "type": "ir.actions.act_window",
            "res_model": "fix.estimate",
            "res_id": new.id,
            "view_mode": "form",
        }

    @api.model
    def _cron_expire_estimates(self):
        """BRU-SRM-13: a sent estimate past its validity date expires."""
        today = fields.Date.context_today(self)
        stale = self.sudo().search([("state", "=", "sent"), ("expiry_date", "<", today)])
        for est in stale:
            est._guarded().write({"state": "expired"})
            est._emit_event("estimate.expired")
        return len(stale)

    def _emit_event(self, event: str):
        from libs.py.fix_events import publish

        publish(
            self.env,
            event,
            "fix.estimate",
            self.id,
            {
                "estimate_id": self.id,
                "order_id": self.order_id.id,
                "version": self.version,
                "state": self.state,
                "grand_total": self.grand_total,
            },
        )


class FixEstimateLine(models.Model):
    _name = "fix.estimate.line"
    _description = "Estimate Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    estimate_id = fields.Many2one("fix.estimate", required=True, ondelete="cascade")
    line_type = fields.Selection(
        [("part", "Part"), ("labour", "Labour"), ("diagnostic", "Diagnostic")],
        required=True,
        default="part",
    )
    product_id = fields.Many2one("product.product", string="Product")
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

    @api.model_create_multi
    def create(self, vals_list):
        ids = {v.get("estimate_id") for v in vals_list if v.get("estimate_id")}
        self._fix_assert_estimate_open(self.env["fix.estimate"].browse(list(ids)))
        lines = super().create(vals_list)
        lines._fix_check_price_floor()
        lines.estimate_id._fix_void_on_raise()
        return lines

    def write(self, vals):
        self._fix_assert_estimate_open(self.estimate_id)
        if vals.get("estimate_id"):
            self._fix_assert_estimate_open(self.env["fix.estimate"].browse(vals["estimate_id"]))
        result = super().write(vals)
        if {"unit_price", "product_id"} & set(vals):
            self._fix_check_price_floor()
        self.estimate_id._fix_void_on_raise()
        return result

    def unlink(self):
        estimates = self.estimate_id
        self._fix_assert_estimate_open(estimates)
        result = super().unlink()
        estimates.exists()._check_discount()
        return result


def _param_on(env, key, default="1"):
    raw = env["ir.config_parameter"].sudo().get_param(key, default)
    return str(raw).strip().lower() not in ("0", "false", "no", "off", "")
