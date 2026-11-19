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
#
# A08 finish (M50-10): the block has a caller (a blocked rider cannot be given
# a COD consignment or COD order, below); a booked shortage is handed to HR /
# payroll (cod.shortage_recovery_requested + an activity for the payroll
# manager); and a shortage falls in one of the two tiers of BRU-TRE-03 /
# FR-TRE-018. The spec names two thresholds and gives no value (M50 Q-04 is
# open, owner CFO / HR Manager), so both are configuration defaulting to 0:
# with nothing configured every shortage takes the strictest path.
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

from .courier_remittance import live_cod_orders
from .treasury_common import (
    GROUP_ACCOUNTANT,
    GROUP_ADMIN,
    bank_account_of,
    float_param,
    post_treasury_move,
    require_other_person,
    require_role,
    treasury_account,
    treasury_alert,
)

# Shortage a single settler may book (BDT). The spec leaves the variance
# thresholds open (M50 Q-04), so the default is 0: every shortage has a
# second approver.
PARAM_COD_TOLERANCE = "cd_cash_position.cod_shortage_tolerance"
# BRU-TRE-03 second threshold: above it the shortage is escalated (the approver
# states why it is accepted and every Accounting Administrator is alerted).
PARAM_COD_ESCALATION = "cd_cash_position.cod_shortage_escalation_threshold"
# Who receives the recovery hand-off; the payroll addon is not a dependency.
PAYROLL_MANAGER_GROUP = "cd_payroll_bd.group_payroll_manager"
# A02 ERP audit M03-F8: a shortage recovered by payroll deduction is debited
# to this role's account (cd_cash_position.account_code.rider_shortage_payroll,
# e.g. the salaries-payable clearing account). OWNER: the account is the
# finance team's choice; unset, a payroll recovery is refused (fail closed).
PAYROLL_RECOVERY_ROLE = "rider_shortage_payroll"


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
    shortage_tier = fields.Selection(
        [
            ("none", "No Shortage"),
            ("tolerated", "Within Tolerance"),
            ("second_approver", "Second Approver"),
            ("escalated", "Escalated"),
        ],
        compute="_compute_shortage_tier",
        help="Which BRU-TRE-03 threshold this shortage is above "
        "(cd_cash_position.cod_shortage_tolerance / cod_shortage_escalation_threshold).",
    )
    shortage_approval_note = fields.Char(
        string="Why the Shortage Is Accepted", readonly=True, copy=False, tracking=True
    )
    recovery_requested_at = fields.Datetime(
        string="Recovery Handed to HR", readonly=True, copy=False
    )
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
    # A02 ERP audit M03-F8: the recovery is a ledger entry, not a label
    recovery_method = fields.Selection(
        [("cash", "Repaid by the Rider"), ("payroll", "Payroll Deduction")],
        string="Recovered By",
        readonly=True,
        copy=False,
    )
    recovery_move_id = fields.Many2one(
        "account.move", string="Recovery GL Entry", readonly=True, copy=False
    )
    recovered_by_id = fields.Many2one(
        "res.users", string="Recovery Posted By", readonly=True, copy=False
    )
    recovered_at = fields.Datetime(string="Recovered At", readonly=True, copy=False)

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
            "shortage_approval_note",
            "recovery_requested_at",
            "recovery_state",
            "recovery_method",
            "recovery_move_id",
            "recovered_by_id",
            "recovered_at",
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

    def _shortage_tier(self) -> str:
        self.ensure_one()
        shortage = self._shortage()
        if shortage <= 0.005:
            return "none"
        if not self._needs_shortage_approval():
            return "tolerated"
        if shortage > float_param(self.env, PARAM_COD_ESCALATION, 0.0) + 0.005:
            return "escalated"
        return "second_approver"

    @api.depends("variance")
    def _compute_shortage_tier(self):
        for rec in self:
            rec.shortage_tier = rec._shortage_tier()

    def _rider_partner(self):
        """The rider as a ledger party (A02 ERP audit M03-F8: the shortage
        line carried no partner, so nobody's balance ever showed it)."""
        self.ensure_one()
        partner = self.rider_id.sudo().work_contact_id
        if not partner:
            raise UserError(
                "Rider %s has no work contact: the shortage is booked against the rider, so "
                "give the employee a work contact first." % self.rider_id.name
            )
        return partner

    @staticmethod
    def _cod_receipt_pending(order) -> bool:
        """A02 ERP audit M03-F9: the order's cash-on-delivery receipt is not
        booked yet (the courier remittance already refused these)."""
        return "posting_state" in order._fields and order.posting_state == "pending"

    def _check_orders(self):
        """Every order is a delivered COD order of THIS rider in this company,
        not in another live settlement."""
        for rec in self:
            pending = rec.order_ids.sudo().filtered(rec._cod_receipt_pending)
            if pending:
                raise UserError(
                    "%s carries orders whose cash-on-delivery receipt is not booked yet: %s. "
                    "Settle them once their receipt is posted."
                    % (rec.name, ", ".join(pending.mapped("name")))
                )
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
            # G2: the order's receivable was closed by money that never sat in
            # COD clearing; settling it here would count that money twice
            elsewhere = rec.order_ids.sudo().filtered(lambda o: o._fix_cod_paid_elsewhere())
            if elsewhere:
                raise UserError(
                    "%s carries orders already paid other than by the rider's cash on delivery "
                    "(prepaid or settled by another receipt): %s. Remove them from the settlement."
                    % (rec.name, ", ".join(elsewhere.mapped("name")))
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
            # G10: nor in a live courier remittance (one order, one settlement)
            taken = rec.order_ids & live_cod_orders(self.env, rec.company_id, exclude=rec)
            if taken:
                raise UserError(
                    "%s carries orders already in another COD settlement or courier "
                    "remittance: %s." % (rec.name, ", ".join(taken.mapped("name")))
                )

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
        # G10: an order in a live courier remittance is the courier's
        settled |= live_cod_orders(self.env, company)
        return (orders - settled).filtered(
            lambda o: not o.sudo()._fix_cod_paid_elsewhere()
            and not self._cod_receipt_pending(o.sudo())
        )

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

    def action_approve_shortage(self, note=None):
        """A second Accounting Administrator accepts a shortage above the
        tolerance before it is booked against the rider. Above the second
        threshold they state why, and every Accounting Administrator is told."""
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
            tier = rec._shortage_tier()
            why = (note or "").strip()
            if tier == "escalated" and not why:
                raise UserError(
                    "%s is %.2f short, above the escalation threshold (%s): state why the "
                    "shortage is accepted." % (rec.name, rec._shortage(), PARAM_COD_ESCALATION)
                )
            rec._guarded().write(
                {
                    "shortage_approved_by_id": self.env.uid,
                    "shortage_approved_at": fields.Datetime.now(),
                    "shortage_approval_note": why or False,
                }
            )
            rec.message_post(
                body="Shortage of %.2f approved by %s." % (rec._shortage(), self.env.user.name)
            )
            if tier == "escalated":
                treasury_alert(
                    rec,
                    "Escalated COD shortage",
                    "%s: rider %s is %.2f short. Accepted by %s: %s"
                    % (rec.name, rec.rider_id.name, rec._shortage(), self.env.user.name, why),
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
                    (
                        shortage,
                        "Rider short %s" % rec.rider_id.name,
                        -rec.variance,
                        0.0,
                        rec._rider_partner(),
                    )
                )
            elif rec.variance > 0.005:
                shortage = treasury_account(self.env, rec.company_id, "rider_shortage")
                lines.append(
                    (
                        shortage,
                        "Rider over %s" % rec.rider_id.name,
                        0.0,
                        rec.variance,
                        rec._rider_partner(),
                    )
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
            if rec.recovery_state == "open":
                rec._fix_request_recovery()
        return True

    def _fix_request_recovery(self):
        """Hand a booked shortage to HR / payroll: the event a payroll consumer
        takes (the same contract as advance.recovery_requested) and a to-do for
        the payroll managers. The block stays until action_mark_recovered."""
        self.ensure_one()
        amount = self._shortage()
        publish(
            self.env,
            "cod.shortage_recovery_requested",
            "fix.cod.settlement",
            self.id,
            {
                "employee_id": self.rider_id.id,
                "amount": amount,
                "currency": self.currency_id.name,
                "company_id": self.company_id.id,
                "settlement": self.name,
            },
        )
        self._guarded().write({"recovery_requested_at": fields.Datetime.now()})
        note = "Recover %.2f from %s (COD settlement %s), then record the reference on it." % (
            amount,
            self.rider_id.name,
            self.name,
        )
        self.sudo().message_post(body="Recovery handed to HR / payroll. %s" % note)
        group = self.env.ref(PAYROLL_MANAGER_GROUP, raise_if_not_found=False)
        users = (
            group.sudo().all_user_ids.filtered(
                lambda u, c=self.company_id: u.active and not u.share and c in u.company_ids
            )
            if group
            else self.env["res.users"]
        )
        if not users:
            treasury_alert(self, "Recover rider COD shortage", note)
        for user in users:
            self.sudo().activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Recover rider COD shortage",
                note=note,
                user_id=user.id,
            )

    def action_mark_recovered(self, reference=None, method=None, journal_id=None):
        """The rider's shortage was recovered: post it (A02 ERP audit M03-F8).

        The settlement debited the shortage to the rider; this closed the
        variance with a label and posted nothing, so the rider_shortage
        account only ever grew. The recovery now credits rider_shortage with
        the rider as partner, against
          - cash: the cash / bank journal the rider repaid into, or
          - payroll: the payroll-deduction account (setting, fail closed).
        It is posted by an Accounting Administrator other than the one who
        settled the shortage (maker-checker)."""
        require_role(self.env, GROUP_ADMIN, "Closing a rider shortage")
        method = (method or "").strip() or "cash"
        if method not in ("cash", "payroll"):
            raise UserError("A shortage is recovered by cash repayment or payroll deduction.")
        for rec in self:
            if rec.recovery_state != "open":
                raise UserError("%s has no open shortage." % rec.name)
            require_other_person(
                self.env, rec.settled_by_id, "Posting the recovery of %s" % rec.name
            )
            ref = (reference or rec.recovery_ref or "").strip()
            if not ref:
                raise UserError("Record the recovery reference (HR deduction / receipt) first.")
            amount = rec._shortage()
            if method == "cash":
                journal = (
                    self.env["account.journal"].browse(int(journal_id)).exists()
                    if journal_id
                    else rec.remittance_journal_id
                )
                debit_account = bank_account_of(journal)
                label = "Rider repaid shortage %s (%s)" % (rec.name, ref)
            else:
                debit_account = treasury_account(self.env, rec.company_id, PAYROLL_RECOVERY_ROLE)
                label = "Payroll deduction for shortage %s (%s)" % (rec.name, ref)
            shortage_account = treasury_account(self.env, rec.company_id, "rider_shortage")
            partner = rec._rider_partner()
            move = post_treasury_move(
                self.env,
                rec.company_id,
                fields.Date.context_today(rec),
                "COD shortage recovered %s — %s" % (rec.name, rec.rider_id.name),
                [
                    (debit_account, label, amount, 0.0, partner if method == "payroll" else None),
                    (
                        shortage_account,
                        "Rider shortage recovered %s" % rec.name,
                        0.0,
                        amount,
                        partner,
                    ),
                ],
                branch=rec.branch_id,
                source="treasury",
            )
            rec._guarded().write(
                {
                    "recovery_state": "recovered",
                    "recovery_ref": ref,
                    "recovery_method": method,
                    "recovery_move_id": move.id,
                    "recovered_by_id": self.env.uid,
                    "recovered_at": fields.Datetime.now(),
                }
            )
            rec.sudo().activity_ids.filtered(
                lambda a: a.summary == "Recover rider COD shortage"
            ).action_feedback(feedback="Recovered (%s): %s" % (method, ref))
        return True

    def action_dispute(self, reason=None):
        for rec in self:
            if rec.state not in ("draft", "submitted"):
                raise UserError("A settled COD is not disputed — reverse its entry instead.")
            why = (reason or rec.dispute_reason or "").strip()
            if not why:
                raise UserError("Record the dispute reason first.")
            rec._guarded().write({"state": "disputed", "dispute_reason": why})
        return True


def _refuse_blocked_riders(env, riders, what):
    """BRU-TRE-04: refuses even trusted service code; the block is lifted only
    by settling or recovering the variance, never by who is asking."""
    Settlement = env["fix.cod.settlement"]
    for rider in riders:
        if Settlement._fix_rider_has_open_variance(rider):
            raise UserError(
                "%s: rider %s has an unresolved COD variance and is blocked from further cash "
                "collection until it is settled and recovered (BRU-TRE-04)." % (what, rider.name)
            )


class FixConsignmentCodBlock(models.Model):
    """A consignment carrying COD orders cannot be given to a blocked rider."""

    _inherit = "fix.consignment"

    def write(self, vals):
        if vals.get("rider_id"):
            cod_orders = (
                self.env["fix.storefront.order"]
                .sudo()
                .search_count(
                    [
                        ("carrier_consignment_id", "in", self.ids),
                        ("payment_rail", "=", "cod"),
                        ("state", "not in", ("cancelled", "delivered")),
                    ]
                )
            )
            if cod_orders:
                rider = self.env["hr.employee"].sudo().browse(vals["rider_id"])
                _refuse_blocked_riders(self.env, rider, "Assigning a COD consignment")
        return super().write(vals)


class FixStorefrontOrderCodBlock(models.Model):
    """A COD order cannot go out on a blocked rider's consignment."""

    _inherit = "fix.storefront.order"

    def _fix_cod_paid_elsewhere(self) -> bool:
        """G2: money for this order that did not reach the rider: a payment
        confirmed before delivery (gateway or M20 receipt), or, with the
        storefront finance bridge, a receivable closed by a receipt that is
        not the courier's cash on delivery. The rider's COD settlement credits
        COD clearing, which only the bridge's cod receipt debits."""
        self.ensure_one()
        if self.payment_date:
            return True
        # the bridge (cd_storefront_finance) is not a dependency: ask if present
        other = getattr(self, "_sfb_cod_receipt_elsewhere", None)
        return bool(other and other())

    def _fix_check_cod_rider(self, consignment_id, rail=None):
        rider = self.env["fix.consignment"].sudo().browse(consignment_id).rider_id
        cod = rail == "cod" if rail else any(o.payment_rail == "cod" for o in self)
        if rider and cod:
            _refuse_blocked_riders(self.env, rider, "Dispatching a COD order")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("carrier_consignment_id") and vals.get("payment_rail") == "cod":
                self._fix_check_cod_rider(vals["carrier_consignment_id"], "cod")
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("carrier_consignment_id"):
            self._fix_check_cod_rider(vals["carrier_consignment_id"], vals.get("payment_rail"))
        return super().write(vals)
