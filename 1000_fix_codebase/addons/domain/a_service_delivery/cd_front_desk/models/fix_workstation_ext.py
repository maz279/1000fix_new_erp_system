# M04 workstation extensions. FILE NAME IS LOAD-BEARING: it must sort
# AFTER fix_cash_shift/fix_token_queue/fix_walkin_intake in the alphabetical
# models import (these three are the base models this file extends; loading
# the extension first kills the whole registry). Do not rename to anything
# that sorts before fix_workin*.
#
# A02 audit B1 (P1): the counter-sale refund and the price below list are
# routed M63 approvals (one request at a time per sale; the request says
# which). A02 audit M04-P2: token recall and no-show, queue roles, and the
# counter sale's tender, VAT split and Mushak-6.3 number.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_cash_shift import GROUP_CASHIER, GROUP_MANAGER

GROUP_REFUND_APPROVER = "cd_front_desk.group_fd_refund_approver"
GROUP_QUEUE_AGENT = "cd_front_desk.group_fd_queue_agent"
QUEUE_GROUPS = (GROUP_QUEUE_AGENT, GROUP_CASHIER, GROUP_MANAGER)
# Token recall (A02 audit M04-P2). The limit is a policy number; the switch
# that turns a token past it into a no-show is a business choice, off today.
RECALL_LIMIT_PARAM = "cd_front_desk.token_recall_limit"
DEFAULT_RECALL_LIMIT = 3
AUTO_NO_SHOW_PARAM = "cd_front_desk.token_auto_no_show"
# Counter-sale VAT: counter prices include VAT; the rate splits the total into
# net and VAT for the Mushak-6.3 (NBR standard rate). A policy number.
VAT_RATE_PARAM = "cd_front_desk.counter_vat_rate_pct"
DEFAULT_VAT_RATE = 15.0
# "1": a cash sale needs the amount tendered before it is confirmed. Off today.
TENDER_REQUIRED_PARAM = "cd_front_desk.counter_tender_required"


def _param_on(env, key) -> bool:
    raw = env["ir.config_parameter"].sudo().get_param(key, "0")
    return str(raw).strip().lower() in ("1", "true", "yes")


def _param_float(env, key, default) -> float:
    raw = env["ir.config_parameter"].sudo().get_param(key)
    try:
        return float(raw) if raw not in (None, False, "") else default
    except ValueError:
        return default


# A price below the product's list price is a discount that needs a Branch
# Manager's approval. The percentage a cashier may give on her own is a policy
# number; the default 0 means every discount is approved (A02 audit M04-5).
PRICE_TOLERANCE_PARAM = "cd_front_desk.price_override_tolerance_pct"
REFUND_REASONS = [
    ("defective", "Defective / Faulty Item"),
    ("wrong_item", "Wrong Item Sold"),
    ("customer_cancelled", "Customer Cancelled"),
    ("duplicate", "Duplicate Charge"),
    ("other", "Other"),
]


class FixTokenQueueExt(models.Model):
    _inherit = "fix.token.queue"

    # A02 audit M04-P2: a called customer who does not come is re-called, and
    # the queue counts it.
    recall_count = fields.Integer(string="Times Re-called", readonly=True, copy=False)
    last_recalled_at = fields.Datetime(string="Last Re-called At", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"recall_count", "last_recalled_at"}

    def _fd_require_queue_role(self, what):
        """A02 audit M04-P2: the queue actions are front-desk work."""
        if self.env.su or any(self.env.user.has_group(g) for g in QUEUE_GROUPS):
            return
        raise UserError(
            "%s needs the Front Desk Queue Agent, Cashier or Branch Manager role." % what
        )

    def _fd_recall_limit(self) -> int:
        return int(_param_float(self.env, RECALL_LIMIT_PARAM, DEFAULT_RECALL_LIMIT))

    def action_call(self):
        """Call a waiting token; call again a called or no-show one (a
        recall, counted). With token_auto_no_show on, a token re-called more
        than token_recall_limit times becomes a no-show instead."""
        self._fd_require_queue_role("Calling a token")
        for token in self:
            if token.state not in ("waiting", "called", "no_show"):
                raise UserError(
                    "Token %s cannot be called from state '%s'."
                    % (token.token_display, token.state)
                )
        first = self.filtered(lambda t: t.state == "waiting")
        recalls = self - first
        if first:
            super(FixTokenQueueExt, first).action_call()
        limit = self._fd_recall_limit()
        auto = _param_on(self.env, AUTO_NO_SHOW_PARAM)
        dropped = []
        for token in recalls:
            count = token.recall_count + 1
            if auto and count > limit:
                if token.state != "no_show":
                    token._guarded().write({"state": "no_show"})
                token.message_post(
                    body="Re-called %d times without the customer coming: no-show." % (count - 1)
                )
                dropped.append(token.token_display)
                continue
            token._guarded().write(
                {
                    "state": "called",
                    "called_at": token.called_at or fields.Datetime.now(),
                    "recall_count": count,
                    "last_recalled_at": fields.Datetime.now(),
                }
            )
        if dropped:
            return {
                "warning": "Recall limit (%d) reached: %s marked no-show. Issue a new token "
                "if the customer returns." % (limit, ", ".join(dropped))
            }
        return True

    def action_evaluate_wait_sla(self):
        self._fd_require_queue_role("Checking the wait SLA")
        return super().action_evaluate_wait_sla()

    def action_serving(self):
        self._fd_require_queue_role("Serving a token")
        for token in self:
            if token.state != "called":
                raise UserError(
                    "Token %s must be called before serving (current: %s)."
                    % (token.token_display, token.state)
                )
        return super().action_serving()

    def action_complete(self):
        self._fd_require_queue_role("Completing a token")
        for token in self:
            if token.state != "serving":
                raise UserError(
                    "Token %s must be serving before completion (current: %s)."
                    % (token.token_display, token.state)
                )
        return super().action_complete()

    def action_no_show(self):
        """Mark a called token as no-show (it can be re-called later)."""
        self._fd_require_queue_role("Marking a token no-show")
        for token in self:
            if token.state not in ("waiting", "called"):
                raise UserError(
                    "Only waiting or called tokens can be marked no-show (current: %s)."
                    % token.state
                )
            token._guarded().write({"state": "no_show"})

    def action_cancel(self):
        self._fd_require_queue_role("Cancelling a token")
        for token in self:
            if token.state == "completed":
                raise UserError("Completed token %s cannot be cancelled." % token.token_display)
            token._guarded().write({"state": "cancelled"})


class FixWalkinIntakeExt(models.Model):
    _inherit = "fix.walkin.intake"

    def action_submit_for_handover(self):
        """The handover_pending state existed in the Selection but no code
        ever set it — intake jumped straight to completed. Submitting parks
        the device at the counter awaiting the customer's acknowledgement."""
        for intake in self:
            if intake.state != "in_progress":
                raise UserError(
                    "Only in-progress intakes can be submitted for handover (current: %s)."
                    % intake.state
                )
        # BRU-FRD-12: the device is identified before it is parked for handover
        self._resolve_device()
        # A02 audit M04-P2: a waived fee goes to a Branch Manager's inbox now,
        # so it is decided while the device waits at the counter.
        self._fd_request_fee_waiver()
        for intake in self:
            intake._guarded().write({"state": "handover_pending"})

    def action_complete_handover(self):
        for intake in self:
            if intake.state not in ("in_progress", "handover_pending"):
                raise UserError(
                    "Intake %s cannot complete handover from state '%s'."
                    % (intake.display_name or intake.id, intake.state)
                )
        orders = super().action_complete_handover()
        # the token↔order link existed as a field nobody ever wrote
        for intake in self:
            if intake.token_id and intake.service_order_id:
                intake.token_id._guarded().write({"service_order_id": intake.service_order_id.id})
        return orders


# fix.cash.shift: action_confirm_closed and the closed -> reconcile path now
# live in fix_cash_shift.py with the rest of the drawer's transitions.


class FixCounterSale(models.Model):
    """A counter sale — parts, accessories and protection plans sold over
    the branch counter (walk-in, no service order). The module's registry
    always listed Counter Sales; the model never existed. Money fields are
    BDT per AS-10; the shift link puts the sale in the drawer's takings."""

    _name = "fix.counter.sale"
    _description = "Counter Sale"
    # fix.approvable.mixin brings fix.guarded.mixin with it (A02 audit B1)
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "id desc"

    # A02 audit B1: a sale carries two approvals, one at a time: the price
    # below list while it is a draft, the refund once confirmed. Both are
    # decided from the inbox; _approval_apply runs the one requested.
    _approval_apply_method = "action_approve_refund"
    _approval_group = GROUP_REFUND_APPROVER
    _approval_routed = True

    @property
    def _approval_domain(self):
        kind = self._fd_approval_kind() if len(self) == 1 else False
        return "price_override" if kind == "price" else "counter_refund"

    def _fix_guarded_fields(self) -> set:
        # A02 audit M04-5 (P04-07): the sale and refund outcome, and who
        # approved what, are set only by the transitions below.
        return super()._fix_guarded_fields() | {
            "state",
            "total",
            "confirmed_by",
            "confirmed_at",
            "price_override_approved_by",
            "price_override_approved_price",
            "refund_state",
            "refund_reason_code",
            "refund_reason",
            "refund_requested_by",
            "refund_requested_at",
            "refund_approved_by",
            "refund_approved_at",
            "refund_shift_id",
            # A02 audit M04-P2: the change, the VAT split and the Mushak-6.3
            # number are computed or issued, never typed
            "change_due",
            "vat_rate",
            "amount_untaxed",
            "vat_amount",
            "mushak_63_ref",
        }

    # What was rung up: frozen once the sale is confirmed (its cash is in a
    # drawer; a changed price or quantity afterwards rewrites the takings).
    _FROZEN_WHEN_CONFIRMED = frozenset(
        {
            "company_id",
            "operating_unit_id",
            "shift_id",
            "branch_id",
            "customer_id",
            "product_id",
            "quantity",
            "unit_price",
            "payment_method",
            "transaction_ref",
            "sale_date",
            "sold_by",
            "tendered_amount",
        }
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            return locked | self._FROZEN_WHEN_CONFIRMED
        return locked

    def write(self, vals):
        if not self.env.su:
            frozen = self._FROZEN_WHEN_CONFIRMED & set(vals)
            for sale in self.filtered(lambda r: r.state != "draft"):
                changed = [n for n in frozen if sale._fix_guard_differs(n, vals[n], sale[n])]
                if changed:
                    raise UserError(
                        "Counter sale %s is %s: what was sold can no longer be changed."
                        % (sale.name, dict(sale._fields["state"].selection)[sale.state])
                    )
        return super().write(vals)

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(string="Sale No.", readonly=True, index=True, copy=False)
    shift_id = fields.Many2one(
        "fix.cash.shift", string="Cash Shift", index=True, ondelete="set null"
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    customer_id = fields.Many2one("res.partner", string="Customer")
    product_id = fields.Many2one("product.product", string="Product", required=True, index=True)
    quantity = fields.Float(default=1.0, required=True)
    unit_price = fields.Float(
        string="Unit Price (BDT)",
        required=True,
        help="Counter price in BDT — defaults from the product's sale price.",
    )
    total = fields.Float(string="Total (BDT)", compute="_compute_total", store=True)
    payment_method = fields.Selection(
        [
            ("cash", "Cash"),
            ("bkash", "bKash"),
            ("nagad", "Nagad"),
            ("card", "Card"),
        ],
        default="cash",
        required=True,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("refunded", "Refunded")],
        default="draft",
        required=True,
        tracking=True,
    )
    sale_date = fields.Datetime(default=fields.Datetime.now, required=True)
    sold_by = fields.Many2one("hr.employee", string="Sold By")
    confirmed_by = fields.Many2one("res.users", string="Confirmed By", readonly=True)
    confirmed_at = fields.Datetime(string="Confirmed At", readonly=True)

    # A02 audit M04-5: a price below the list price is approved, and the
    # approval is pinned to the price it saw.
    list_price_floor = fields.Float(
        string="List Price (BDT)",
        related="product_id.lst_price",
        help="The product's list price: the floor below which a manager approves the price.",
    )
    price_override_approved_by = fields.Many2one(
        "res.users", string="Price Override Approved By", readonly=True, tracking=True
    )
    price_override_approved_price = fields.Float(
        string="Approved Unit Price (BDT)", readonly=True, tracking=True
    )

    # A02 audit M04-5 (P04-09): a refund is requested with a reason, approved
    # by a manager who did not sell, and posted to the drawer that is open now.
    refund_state = fields.Selection(
        [("none", "No Refund"), ("requested", "Requested"), ("refunded", "Refunded")],
        string="Refund Status",
        default="none",
        required=True,
        readonly=True,
        tracking=True,
    )
    refund_reason_code = fields.Selection(
        REFUND_REASONS, string="Refund Reason", readonly=True, tracking=True
    )
    refund_reason = fields.Char(string="Refund Reason Note", readonly=True)
    refund_requested_by = fields.Many2one("res.users", string="Refund Requested By", readonly=True)
    refund_requested_at = fields.Datetime(string="Refund Requested At", readonly=True)
    refund_approved_by = fields.Many2one(
        "res.users", string="Refund Approved By", readonly=True, tracking=True
    )
    refund_approved_at = fields.Datetime(string="Refund Approved At", readonly=True)
    refund_shift_id = fields.Many2one(
        "fix.cash.shift", string="Refund Paid From Shift", readonly=True, index=True
    )

    # --- A02 Enterprise Data Capture (M04 Counter Sale Multi-Tab Specification) ---
    serial_or_warranty_ref = fields.Char(
        string="Part Serial / Protection Plan Ref",
        tracking=True,
    )
    # A02 audit M04-P2: the Mushak-6.3 number is issued from a sequence when
    # the sale is confirmed (it was a free text field).
    mushak_63_ref = fields.Char(
        string="NBR Mushak-6.3 Tax Challan Ref",
        tracking=True,
        readonly=True,
        copy=False,
        help="Issued from the Mushak-6.3 sequence when the sale is confirmed.",
    )
    # A02 audit M04-P2: tender and the VAT split. Counter prices include VAT.
    tendered_amount = fields.Float(
        string="Cash Tendered (BDT)", help="The cash the customer handed over."
    )
    change_due = fields.Float(string="Change Due (BDT)", compute="_compute_tender_vat", store=True)
    vat_rate = fields.Float(
        string="VAT Rate (%)",
        readonly=True,
        default=lambda self: _param_float(self.env, VAT_RATE_PARAM, DEFAULT_VAT_RATE),
        help="The VAT rate included in the counter price (cd_front_desk.counter_vat_rate_pct).",
    )
    amount_untaxed = fields.Float(
        string="Net of VAT (BDT)", compute="_compute_tender_vat", store=True
    )
    vat_amount = fields.Float(string="VAT (BDT)", compute="_compute_tender_vat", store=True)
    transaction_ref = fields.Char(
        string="bKash / Nagad / POS TrxID",
        tracking=True,
    )
    notes = fields.Char(string="Counter Sale Notes")

    @api.depends("quantity", "unit_price")
    def _compute_total(self):
        for sale in self:
            sale.total = round(sale.quantity * sale.unit_price, 2)

    @api.depends("total", "vat_rate", "tendered_amount", "payment_method")
    def _compute_tender_vat(self):
        for sale in self:
            rate = max(sale.vat_rate or 0.0, 0.0)
            net = round(sale.total / (1.0 + rate / 100.0), 2) if rate else sale.total
            sale.amount_untaxed = net
            sale.vat_amount = round(sale.total - net, 2)
            tendered = sale.tendered_amount or 0.0
            cash = sale.payment_method == "cash"
            sale.change_due = round(max(tendered - sale.total, 0.0), 2) if cash else 0.0

    @api.constrains("quantity", "unit_price")
    def _check_quantity_and_price(self):
        """A02 audit M04-5 (P04-08): a quantity of -5 was a BDT 5,000 cash-out
        disguised as a sale."""
        for sale in self:
            if sale.quantity <= 0:
                raise ValidationError("A counter sale needs a quantity greater than zero.")
            if sale.unit_price < 0:
                raise ValidationError("A counter sale cannot have a negative unit price.")

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id and not self.unit_price:
            self.unit_price = self.product_id.list_price or 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                seq = self.env["ir.sequence"].next_by_code("fix.counter.sale")
                vals["name"] = seq or "CS/%s" % fields.Date.today()
            if not vals.get("operating_unit_id"):
                vals["operating_unit_id"] = self._fd_default_operating_unit(vals)
        return super().create(vals_list)

    def _fd_default_operating_unit(self, vals):
        """The unit that rang the sale: its cash shift's, else its branch's,
        else the seller's default. The workspace form never asked for it, so
        no counter sale could be saved there (fix_real, 12 Nov 2026)."""
        if vals.get("shift_id"):
            shift = self.env["fix.cash.shift"].browse(vals["shift_id"]).exists()
            if shift and shift.operating_unit_id:
                return shift.operating_unit_id.id
        if vals.get("branch_id"):
            branch = self.env["fix.branch"].browse(vals["branch_id"]).exists()
            if branch and "operating_unit_id" in branch._fields and branch.operating_unit_id:
                return branch.operating_unit_id.id
        user_ou = getattr(self.env.user, "default_operating_unit_id", False)
        return user_ou.id if user_ou else False

    # ------------------------------------------------------------ roles

    def _fd_has(self, *xmlids) -> bool:
        return self.env.su or any(self.env.user.has_group(x) for x in xmlids)

    def _fd_sellers(self):
        """The users who rang this sale up."""
        self.ensure_one()
        return self.create_uid | self.confirmed_by | self.sold_by.user_id

    def _fd_price_floor(self) -> float:
        self.ensure_one()
        raw = self.env["ir.config_parameter"].sudo().get_param(PRICE_TOLERANCE_PARAM)
        try:
            pct = float(raw) if raw not in (None, False, "") else 0.0
        except ValueError:
            pct = 0.0
        return round((self.product_id.lst_price or 0.0) * (1.0 - max(pct, 0.0) / 100.0), 2)

    def _fd_needs_price_approval(self) -> bool:
        self.ensure_one()
        return self.unit_price < self._fd_price_floor() - 0.005

    def _fd_price_approved(self) -> bool:
        self.ensure_one()
        return bool(self.price_override_approved_by) and (
            abs(self.price_override_approved_price - self.unit_price) < 0.005
        )

    # ------------------------------------------------------------ routing

    def _fd_approval_kind(self):
        """Which approval this sale needs now: 'refund', 'price' or False."""
        self.ensure_one()
        if self.state == "confirmed" and self.refund_state == "requested":
            return "refund"
        if (
            self.state == "draft"
            and self._fd_needs_price_approval()
            and not self._fd_price_approved()
        ):
            return "price"
        return False

    def _approval_amount(self) -> float:
        return abs(self.total or 0.0) if len(self) == 1 else 0.0

    def _approval_needed(self) -> bool:
        return bool(self._fd_approval_kind())

    def _approval_group_xmlid(self):
        return GROUP_MANAGER if self._fd_approval_kind() == "price" else GROUP_REFUND_APPROVER

    def _approval_holders(self, group):
        """A refund may be decided by a Refund Approver or a Branch Manager."""
        users = super()._approval_holders(group)
        if self._fd_approval_kind() == "refund":
            managers = self.env.ref(GROUP_MANAGER, raise_if_not_found=False)
            users |= super()._approval_holders(managers)
        return users

    def _approval_excluded(self):
        """The seller and the refund requester never receive the task."""
        return super()._approval_excluded() | (self._fd_sellers() | self.refund_requested_by).sudo()

    def _approval_apply(self):
        kind = self._fd_approval_kind()
        if kind == "price":
            return self.action_approve_price_override()
        if kind == "refund":
            return self.action_approve_refund()
        raise UserError("Sale %s has nothing waiting for approval." % self.name)

    def _approval_on_rejected(self, comment):
        """A rejected refund request is closed; the sale stays confirmed."""
        for sale in self.filtered(lambda r: r.refund_state == "requested"):
            sale._guarded().write({"refund_state": "none"})
            sale.message_post(body="Refund request rejected: %s" % (comment or ""))

    # ------------------------------------------------------------ transitions

    def action_approve_price_override(self):
        """A Branch Manager who is not the seller approves a price below the
        list price. The approval holds for exactly this unit price. A02 audit
        B1: it runs only from the manager's M63 inbox."""
        self._approval_assert_routed()
        if not self._fd_has(GROUP_MANAGER):
            raise UserError(
                "Only a Branch Manager may approve a price below the list price. If no one "
                "holds this role yet, ask the administrator to appoint one."
            )
        for sale in self:
            if sale.state != "draft":
                raise UserError("Only a draft counter sale's price can be approved.")
            if not sale._fd_needs_price_approval():
                raise UserError(
                    "Sale %s is at or above the list price and needs no approval." % sale.name
                )
            if not self.env.su and self.env.user in sale._fd_sellers():
                raise UserError(
                    "You are ringing up sale %s, so you cannot approve its price. Another "
                    "Branch Manager must do this." % sale.name
                )
            sale._guarded().write(
                {
                    "price_override_approved_by": self.env.uid,
                    "price_override_approved_price": sale.unit_price,
                }
            )
            sale.message_post(
                body="Unit price BDT %.2f (list BDT %.2f) approved by %s."
                % (sale.unit_price, sale.product_id.lst_price, self.env.user.name)
            )
        return True

    def action_confirm(self):
        if not self._fd_has(GROUP_CASHIER, GROUP_MANAGER):
            raise UserError("Only a Front Desk Cashier may confirm a counter sale.")
        Shift = self.env["fix.cash.shift"]
        for sale in self:
            if sale.state != "draft":
                raise UserError("Only draft counter sales can be confirmed.")
            if sale._fd_needs_price_approval() and not sale._fd_price_approved():
                raise UserError(
                    "Sale %s is priced at BDT %.2f, below the list price of BDT %.2f. A Branch "
                    "Manager must approve this price before the sale is confirmed."
                    % (sale.name, sale.unit_price, sale.product_id.lst_price)
                )
            if sale.payment_method != "cash" and not (sale.transaction_ref or "").strip():
                # no drawer counts this money: the TrxID / card slip is the only
                # thing the MFS or POS statement can be matched to
                raise UserError(
                    "Sale %s is paid by %s: enter its transaction reference (the bKash / "
                    "Nagad TrxID or the card slip number) before confirming."
                    % (
                        sale.name,
                        dict(sale._fields["payment_method"].selection)[sale.payment_method],
                    )
                )
            if sale.payment_method == "cash":
                tendered = sale.tendered_amount or 0.0
                if tendered and tendered + 0.005 < sale.total:
                    raise UserError(
                        "Sale %s: BDT %.2f tendered does not cover the BDT %.2f total."
                        % (sale.name, tendered, sale.total)
                    )
                if not tendered and _param_on(self.env, TENDER_REQUIRED_PARAM):
                    raise UserError("Sale %s: enter the cash tendered." % sale.name)
            vals = {
                "state": "confirmed",
                "confirmed_by": self.env.uid,
                "confirmed_at": fields.Datetime.now(),
            }
            if not sale.mushak_63_ref:
                vals["mushak_63_ref"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.counter.sale.mushak")
                )
            shift = sale.shift_id
            if sale.payment_method == "cash":
                # cash joins the drawer's expected takings, on an OPEN shift only
                # (A02 audit M04-4: sales kept posting into a reconciled shift)
                if not shift and sale.branch_id:
                    shift = Shift._fd_open_shift_for(sale.branch_id, sale.company_id)
                    vals["shift_id"] = shift.id
                if not shift:
                    raise UserError(
                        "Cash sale %s has no open cash shift to take the money. Open the "
                        "branch's cash shift first." % sale.name
                    )
                if sale.branch_id and shift.branch_id != sale.branch_id:
                    raise UserError(
                        "Cash sale %s is for %s but shift #%s belongs to %s."
                        % (
                            sale.name,
                            sale.branch_id.display_name,
                            shift.id,
                            shift.branch_id.display_name,
                        )
                    )
                shift._post_cash_movement("cash_payments", sale.total)
            sale._guarded().write(vals)

    def _fd_parse_reason(self, reason, reason_code):
        """`reason_code: note` from the workspace prompt, or the two apart."""
        codes = dict(REFUND_REASONS)
        text = (reason or "").strip()
        code = (reason_code or "").strip()
        if not code and ":" in text:
            head, tail = text.split(":", 1)
            if head.strip() in codes:
                code, text = head.strip(), tail.strip()
        if not code and text in codes:
            code, text = text, ""
        if code not in codes:
            raise UserError(
                "A refund needs a reason code: %s. Write it as 'code: note'." % ", ".join(codes)
            )
        if code == "other" and not text:
            raise UserError("A refund for 'other' reasons needs a note saying why.")
        return code, text

    def action_request_refund(self, reason=None, reason_code=None):
        """Ask for a refund of a confirmed sale, with a reason. Any front-desk
        user may ask; a manager who did not sell approves."""
        if not self._fd_has(GROUP_CASHIER, GROUP_MANAGER, GROUP_REFUND_APPROVER):
            raise UserError("Only front-desk staff may request a counter-sale refund.")
        code, text = self._fd_parse_reason(reason, reason_code)
        for sale in self:
            if sale.state != "confirmed":
                raise UserError("Only confirmed sales can be refunded.")
            if sale.refund_state != "none":
                raise UserError("Sale %s already has a refund %s." % (sale.name, sale.refund_state))
            sale._guarded().write(
                {
                    "refund_state": "requested",
                    "refund_reason_code": code,
                    "refund_reason": text,
                    "refund_requested_by": self.env.uid,
                    "refund_requested_at": fields.Datetime.now(),
                }
            )
            # A02 audit B1: the request IS the approval request; it goes to a
            # Refund Approver or Branch Manager who neither sold nor asked.
            # Trusted superuser code (seeds, service calls) is not routed; it
            # can be sent on with Request Approval.
            if self.env.su:
                continue
            sale.action_request_approval(
                justification="%s%s" % (dict(REFUND_REASONS)[code], ": %s" % text if text else "")
            )
        return True

    def action_approve_refund(self):
        """A02 audit M04-5 (P04-09): the seller refunded her own sale after
        close, with no reason. A refund is now approved by a Refund Approver
        or Branch Manager who neither sold nor requested it, and the cash
        leaves the drawer that is OPEN now — never a closed or reconciled one.
        A02 audit B1: it runs only from the approver's M63 inbox."""
        self._approval_assert_routed()
        if not self._fd_has(GROUP_REFUND_APPROVER, GROUP_MANAGER):
            raise UserError(
                "Only a Refund Approver or Branch Manager may approve a refund. If no one "
                "holds this role yet, ask the administrator to appoint one."
            )
        Shift = self.env["fix.cash.shift"]
        for sale in self:
            if sale.state != "confirmed":
                raise UserError("Only confirmed sales can be refunded.")
            if sale.refund_state != "requested":
                raise UserError(
                    "Sale %s has no refund request. Request the refund, with its reason, first."
                    % sale.name
                )
            if not self.env.su and self.env.user in (sale._fd_sellers() | sale.refund_requested_by):
                raise UserError(
                    "You sold sale %s or asked for its refund, so you cannot approve the "
                    "refund. Another approver must do this." % sale.name
                )
            vals = {
                "state": "refunded",
                "refund_state": "refunded",
                "refund_approved_by": self.env.uid,
                "refund_approved_at": fields.Datetime.now(),
            }
            if sale.payment_method == "cash":
                branch = sale.branch_id or sale.shift_id.branch_id
                shift = Shift._fd_open_shift_for(branch, sale.company_id) if branch else Shift
                if not shift:
                    raise UserError(
                        "There is no open cash shift at %s to pay refund %s from. Open the "
                        "branch's cash shift first." % (branch.display_name or "", sale.name)
                    )
                shift._post_cash_movement("cash_refunds", sale.total)
                vals["refund_shift_id"] = shift.id
            sale._guarded().write(vals)
        return True
