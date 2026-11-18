# M10 capture audit, second pass (2026-11-18): the records the M10 sub-module
# pages could not capture, because the records did not exist.
#
# The 13 Nov pass gave every page a button, but only for models the estate
# already had. On six pages that button did not capture what the spec says
# the page is for:
#
#   page 1  fix.loyalty.membership     FR-LOY-001/002/003/009/010, BRU-LOY-03/12:
#                                      a PAID privilege membership with price,
#                                      term, grace, Pending/Active/Expiring/
#                                      Suspended/Lapsed/Cancelled. Only a free
#                                      points account existed.
#   page 2  fix.loyalty.benefit        FR-LOY-004/005, BRU-LOY-01 (H): what each
#                                      tier benefit applies to. A privilege
#                                      discount applies to labour only; the
#                                      tier's "Parts Discount %" contradicted it.
#   page 4  fix.loyalty.wallet(.txn)   FR-LOY-022..025, BRU-LOY-06/07/13, SOD-18:
#                                      a BDT stored-value wallet. The page's
#                                      only button was a POINTS adjustment.
#   page 5  fix.loyalty.voucher.batch  FR-LOY-027/028/030, AUT-LOY-14: bulk and
#                                      personalised code batches with an issue
#                                      limit and eligibility.
#           fix.loyalty.stacking.rule  FR-LOY-029, BRU-LOY-09 (H): what combines,
#                                      in what order, under what cap.
#   page 6  fix.loyalty.referral.event FR-LOY-034/036/037, BRU-LOY-10 (H): the
#                                      attribution of a new customer to a shared
#                                      code, with self/household and cap blocks.
#   page 8  fix.loyalty.liability.run  FR-LOY-040/041, BRU-LOY-11, AUT-LOY-12:
#                                      the period-end liability and breakage
#                                      calculation, reconciled to the ledger and
#                                      published by Finance, not by its author.
import re
import secrets
from datetime import datetime, time, timedelta

import pytz
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

LOCAL_TZ = "Asia/Dhaka"
FINANCE_GROUP = "account.group_account_manager"
OPEN_MEMBERSHIP = ("pending", "active", "expiring", "suspended")
NOTICE_DAYS = (60, 30, 7)  # AUT-LOY-05
MAX_BATCH = 10000  # issuance limit of one voucher batch (FR-LOY-027)

CHANNELS = [
    ("counter", "Service Counter"),
    ("portal", "Customer Portal"),
    ("app", "Mobile App"),
    ("contact_centre", "Contact Centre"),
    ("agent", "Field / Sales Agent"),
]


def _bdt(env):
    return env.ref("base.BDT", raise_if_not_found=False) or env.company.currency_id


def _local_today(env):
    tz = env.context.get("tz") or env.user.tz or LOCAL_TZ
    return fields.Date.context_today(env["res.users"].with_context(tz=tz))


def _local_day_end(env, day):
    """The UTC datetime at which ``day`` ends in Dhaka."""
    tz = pytz.timezone(env.context.get("tz") or env.user.tz or LOCAL_TZ)
    end = tz.localize(datetime.combine(day + timedelta(days=1), time.min))
    return end.astimezone(pytz.utc).replace(tzinfo=None)


def _norm(value):
    return re.sub(r"[^0-9a-z@.]", "", (value or "").lower())


def _refuse_posted_edit(records, vals, allowed, what):
    """A decided record is evidence: only its transitions may change it."""
    if records.env.su or records._fix_guard_open():
        return
    blocked = set(vals) - set(allowed)
    for rec in records:
        if rec.state in ("posted", "published", "issued", "closed", "rewarded", "blocked"):
            changed = [
                n
                for n in blocked
                if n in rec._fields and rec._fix_guard_differs(n, vals[n], rec[n])
            ]
            if changed:
                raise UserError(
                    "%s %s is decided and cannot be edited (%s)."
                    % (what, rec.display_name, ", ".join(sorted(changed)))
                )


# ---------------------------------------------------------------------------
# Tier: membership price and term, and BRU-LOY-01
# ---------------------------------------------------------------------------
class FixLoyaltyTierMembership(models.Model):
    _inherit = "fix.loyalty.tier"

    membership_fee_bdt = fields.Float(
        string="Membership Fee (BDT)",
        default=0.0,
        tracking=True,
        help="FR-LOY-001: the price of a paid membership in this tier. 0 = free tier.",
    )
    membership_duration_months = fields.Integer(
        string="Membership Term (months)", default=12, tracking=True
    )
    membership_grace_days = fields.Integer(
        string="Renewal Grace (days)",
        default=15,
        help="FR-LOY-009: days after expiry before the membership lapses.",
    )
    benefit_ids = fields.One2many("fix.loyalty.benefit", "tier_id", string="Benefits")

    @api.constrains("parts_discount_pct")
    def _check_bru_loy_01(self):
        for rec in self:
            if (rec.parts_discount_pct or 0.0) > 0.0:
                raise ValidationError(
                    "BRU-LOY-01: a privilege discount applies to labour charges only, "
                    "never to parts, consumables or transport. Parts Discount must be 0."
                )

    @api.constrains("membership_fee_bdt", "membership_duration_months", "membership_grace_days")
    def _check_membership_terms(self):
        for rec in self:
            if rec.membership_fee_bdt < 0:
                raise ValidationError("A membership fee cannot be negative.")
            if not 1 <= rec.membership_duration_months <= 60:
                raise ValidationError("A membership term is between 1 and 60 months.")
            if not 0 <= rec.membership_grace_days <= 90:
                raise ValidationError("A renewal grace period is between 0 and 90 days.")


class FixLoyaltyProgramCapture(models.Model):
    _inherit = "fix.loyalty.program"

    referral_window_days = fields.Integer(
        string="Referral Attribution Window (days)",
        default=90,
        help="FR-LOY-034: the referee must complete a paid service within this many days.",
    )
    referral_cap_per_month = fields.Integer(
        string="Referrals per Referrer per Month (0 = no cap)",
        default=0,
        help="FR-LOY-037: further registrations in the month are blocked.",
    )
    max_aggregate_discount_pct = fields.Float(
        string="Max Aggregate Discount %",
        default=100.0,
        help="BRU-LOY-09: the most that benefits, vouchers and promotions may take "
        "off a bill together. A CFO ruling; 100 until it is made.",
    )

    # The aggregate cap decides what every stacked bill may cost (BRU-LOY-09),
    # so only the programme's cost authority changes it. Compared with the
    # default / current value: the workspace form re-posts unchanged fields.
    @api.model_create_multi
    def create(self, vals_list):
        if not self._cost_settings_authorised() and any(
            abs((v.get("max_aggregate_discount_pct") or 100.0) - 100.0) > 1e-6
            for v in vals_list
            if "max_aggregate_discount_pct" in v
        ):
            self._cost_settings_refuse(["Max Aggregate Discount %"])
        return super().create(vals_list)

    def write(self, vals):
        if "max_aggregate_discount_pct" in vals and not self._cost_settings_authorised():
            new = vals["max_aggregate_discount_pct"] or 0.0
            if any(abs(new - (rec.max_aggregate_discount_pct or 0.0)) > 1e-6 for rec in self):
                self._cost_settings_refuse(["Max Aggregate Discount %"])
        return super().write(vals)

    @api.constrains("referral_window_days", "referral_cap_per_month", "max_aggregate_discount_pct")
    def _check_capture_settings(self):
        for rec in self:
            if rec.referral_window_days < 1:
                raise ValidationError("The referral attribution window is at least one day.")
            if rec.referral_cap_per_month < 0:
                raise ValidationError("A referral cap cannot be negative.")
            if not 0.0 < rec.max_aggregate_discount_pct <= 100.0:
                raise ValidationError("The aggregate discount cap lies above 0% and at most 100%.")


# ---------------------------------------------------------------------------
# Page 1 - paid privilege membership
# ---------------------------------------------------------------------------
class FixLoyaltyMembership(models.Model):
    _name = "fix.loyalty.membership"
    _description = "Privilege Membership"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "started_on desc, id desc"

    _LOCK_AFTER_PENDING = ("partner_id", "program_id", "tier_id", "price_bdt", "duration_months")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "started_on",
            "paid_at",
            "payment_ref",
            "benefits_withdrawn_on",
            "status_reason",
            "notice_sent_days",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "pending":
            return locked | set(self._LOCK_AFTER_PENDING)
        return locked

    name = fields.Char(
        string="Membership No.", default="New", readonly=True, copy=False, index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Member", required=True, index=True, ondelete="restrict"
    )
    program_id = fields.Many2one("fix.loyalty.program", required=True, ondelete="restrict")
    tier_id = fields.Many2one("fix.loyalty.tier", required=True, ondelete="restrict")
    channel = fields.Selection(CHANNELS, required=True, default="counter")
    currency_id = fields.Many2one("res.currency", default=lambda self: _bdt(self.env))
    price_bdt = fields.Monetary(
        string="Price Paid (BDT)", currency_field="currency_id", help="Defaults to the tier's fee."
    )
    duration_months = fields.Integer(string="Term (months)")
    grace_days = fields.Integer(string="Grace (days)")
    started_on = fields.Date(readonly=True, copy=False)
    expires_on = fields.Date(compute="_compute_dates", store=True)
    grace_until = fields.Date(compute="_compute_dates", store=True)
    state = fields.Selection(
        [
            ("pending", "Pending Payment"),
            ("active", "Active"),
            ("expiring", "Expiring"),
            ("suspended", "Suspended"),
            ("lapsed", "Lapsed"),
            ("cancelled", "Cancelled"),
            ("completed", "Completed (Renewed)"),
        ],
        required=True,
        default="pending",
        tracking=True,
        index=True,
    )
    payment_ref = fields.Char(string="Payment Reference (M20)", copy=False, tracking=True)
    paid_at = fields.Datetime(readonly=True, copy=False)
    renewal_of_id = fields.Many2one("fix.loyalty.membership", string="Renewal Of", copy=False)
    status_reason = fields.Char(readonly=True, copy=False)
    benefits_withdrawn_on = fields.Date(readonly=True, copy=False)
    notice_sent_days = fields.Integer(readonly=True, copy=False, default=0)
    recognised_bdt = fields.Monetary(
        string="Revenue Recognised (BDT)", currency_field="currency_id", compute="_compute_deferral"
    )
    deferred_bdt = fields.Monetary(
        string="Revenue Deferred (BDT)", currency_field="currency_id", compute="_compute_deferral"
    )

    @api.depends("started_on", "duration_months", "grace_days")
    def _compute_dates(self):
        for rec in self:
            if rec.started_on and rec.duration_months:
                rec.expires_on = (
                    rec.started_on + relativedelta(months=rec.duration_months) - timedelta(days=1)
                )
                rec.grace_until = rec.expires_on + timedelta(days=rec.grace_days or 0)
            else:
                rec.expires_on = False
                rec.grace_until = False

    def _compute_deferral(self):
        """BRU-LOY-12: the fee is earned over the term, day by day, never at sale."""
        today = _local_today(self.env)
        for rec in self:
            price = rec.price_bdt or 0.0
            if rec.state == "pending" or not rec.started_on or not rec.expires_on:
                rec.recognised_bdt, rec.deferred_bdt = (
                    0.0,
                    price if rec.state != "cancelled" else 0.0,
                )
                continue
            total = (rec.expires_on - rec.started_on).days + 1
            end = (
                rec.benefits_withdrawn_on - timedelta(days=1)
                if rec.benefits_withdrawn_on
                else today
            )
            used = max(0, min(total, (min(end, rec.expires_on) - rec.started_on).days + 1))
            rec.recognised_bdt = round(price * used / total, 2) if total else price
            rec.deferred_bdt = round(price - rec.recognised_bdt, 2)

    @api.constrains("tier_id", "program_id", "price_bdt", "duration_months", "grace_days")
    def _check_terms(self):
        for rec in self:
            if rec.tier_id.program_id != rec.program_id:
                raise ValidationError(
                    "The tier %s is not in programme %s." % (rec.tier_id.name, rec.program_id.name)
                )
            if (rec.price_bdt or 0.0) < 0:
                raise ValidationError("A membership price cannot be negative.")
            if not 1 <= (rec.duration_months or 0) <= 60:
                raise ValidationError("A membership term is between 1 and 60 months.")
            if not 0 <= (rec.grace_days or 0) <= 90:
                raise ValidationError("A grace period is between 0 and 90 days.")

    @api.constrains("partner_id", "program_id", "state", "renewal_of_id")
    def _check_one_open(self):
        for rec in self.filtered(lambda r: r.state in OPEN_MEMBERSHIP):
            others = self.search(
                [
                    ("id", "!=", rec.id),
                    ("partner_id", "=", rec.partner_id.id),
                    ("program_id", "=", rec.program_id.id),
                    ("state", "in", OPEN_MEMBERSHIP),
                ]
            )
            # a renewal may wait alongside the membership it renews
            others = others.filtered(lambda o, r=rec: o != r.renewal_of_id and o.renewal_of_id != r)
            if others:
                raise ValidationError(
                    "%s already holds an open membership (%s) in %s. Renew it instead."
                    % (rec.partner_id.display_name, others[0].name, rec.program_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        Tier = self.env["fix.loyalty.tier"]
        for vals in vals_list:
            tier = Tier.browse(vals.get("tier_id"))
            if tier:
                vals.setdefault("program_id", tier.program_id.id)
                if not vals.get("price_bdt"):
                    vals["price_bdt"] = tier.membership_fee_bdt
                if not vals.get("duration_months"):
                    vals["duration_months"] = tier.membership_duration_months or 12
                if "grace_days" not in vals or vals.get("grace_days") is None:
                    vals["grace_days"] = tier.membership_grace_days
            vals.setdefault("duration_months", 12)
            vals.setdefault("grace_days", 15)
        records = super().create(vals_list)
        for rec in records:
            if rec.name in (False, "New"):
                rec._guarded().write(
                    {
                        "name": self.env["ir.sequence"].next_by_code("fix.loyalty.membership")
                        or "New"
                    }
                )
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "pending"):
                changed = [
                    n
                    for n in set(vals) & set(self._LOCK_AFTER_PENDING)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "The terms of membership %s are fixed once paid (%s). Cancel and "
                        "re-enrol, or renew." % (rec.name, ", ".join(sorted(changed)))
                    )
        return super().write(vals)

    # ---- transitions -----------------------------------------------------
    def action_confirm_payment(self, payment_ref=None):
        """AUT-LOY-01: payment confirmed (M20) activates the membership."""
        today = _local_today(self.env)
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending membership can be confirmed as paid.")
            ref = (payment_ref or rec.payment_ref or "").strip()
            if (rec.price_bdt or 0.0) > 0 and not ref:
                raise UserError(
                    "Give the M20 receipt or invoice reference: a paid membership is "
                    "activated on confirmed payment, not on enrolment."
                )
            start = today
            prev = rec.renewal_of_id
            if prev and prev.expires_on and prev.state in ("active", "expiring"):
                start = max(today, prev.expires_on + timedelta(days=1))
            rec._guarded().write(
                {
                    "state": "active",
                    "payment_ref": ref or False,
                    "paid_at": fields.Datetime.now(),
                    "started_on": start,
                    "status_reason": False,
                }
            )
            publish(
                rec.env,
                "loyalty.membership_activated",
                "fix.loyalty.membership",
                rec.id,
                {
                    "membership_no": rec.name,
                    "partner_id": rec.partner_id.id,
                    "tier": rec.tier_id.code or "",
                    "price_bdt": float(rec.price_bdt or 0.0),
                    "started_on": str(rec.started_on),
                    "expires_on": str(rec.expires_on),
                },
            )
        return True

    def action_suspend(self, reason=None):
        """FR-LOY-010: suspended for non-payment or conduct, from today."""
        if not (reason or "").strip():
            raise UserError("State why the membership is suspended.")
        for rec in self:
            if rec.state not in ("active", "expiring"):
                raise UserError("Only an active membership can be suspended.")
            rec._guarded().write({"state": "suspended", "status_reason": reason.strip()})
        return True

    def action_reinstate(self):
        today = _local_today(self.env)
        for rec in self:
            if rec.state != "suspended":
                raise UserError("Only a suspended membership can be reinstated.")
            if rec.grace_until and today > rec.grace_until:
                raise UserError("The term and its grace have ended; renew instead.")
            rec._guarded().write({"state": "active", "status_reason": False})
        return True

    def action_cancel(self, reason=None):
        """BRU-LOY-03: benefits stop on the stated date, never retroactively."""
        if not (reason or "").strip():
            raise UserError("State why the membership is cancelled.")
        today = _local_today(self.env)
        for rec in self:
            if rec.state not in OPEN_MEMBERSHIP:
                raise UserError("Membership %s is already closed." % rec.name)
            rec._guarded().write(
                {
                    "state": "cancelled",
                    "status_reason": reason.strip(),
                    "benefits_withdrawn_on": today if rec.state != "pending" else False,
                }
            )
        return True

    def action_renew(self):
        """A renewal is a new pending membership at the tier's prevailing price."""
        for rec in self:
            if rec.state not in ("active", "expiring", "lapsed"):
                raise UserError("Only an active, expiring or lapsed membership can be renewed.")
            if self.search_count(
                [("renewal_of_id", "=", rec.id), ("state", "in", OPEN_MEMBERSHIP)]
            ):
                raise UserError("Membership %s already has a renewal waiting." % rec.name)
            self.create(
                {
                    "partner_id": rec.partner_id.id,
                    "program_id": rec.program_id.id,
                    "tier_id": rec.tier_id.id,
                    "channel": rec.channel,
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "renewal_of_id": rec.id if rec.state != "lapsed" else False,
                }
            )
        return True

    @api.model
    def _live_for(self, partner, program, day=None):
        """The membership whose benefits a member holds on ``day``."""
        day = day or _local_today(self.env)
        return self.sudo().search(
            [
                ("partner_id", "=", partner.id),
                ("program_id", "=", program.id),
                ("state", "in", ("active", "expiring")),
                ("started_on", "<=", day),
                ("grace_until", ">=", day),
            ],
            limit=1,
        )

    @api.model
    def cron_membership_lifecycle(self):
        """AUT-LOY-05/06: notice at 60/30/7 days, then complete or lapse."""
        today = _local_today(self.env)
        moved = 0
        for rec in self.sudo().search([("state", "in", ("active", "expiring"))]):
            if not rec.expires_on:
                continue
            left = (rec.expires_on - today).days
            vals = {}
            if 0 <= left <= NOTICE_DAYS[0] and rec.state == "active":
                vals["state"] = "expiring"
            due = [
                d
                for d in NOTICE_DAYS
                if left <= d and (not rec.notice_sent_days or d < rec.notice_sent_days)
            ]
            if left >= 0 and due:
                vals["notice_sent_days"] = min(due)
            if left < 0:
                successor = self.sudo().search(
                    [("renewal_of_id", "=", rec.id), ("state", "in", ("active", "expiring"))],
                    limit=1,
                )
                if successor:
                    vals.update(
                        state="completed", benefits_withdrawn_on=rec.expires_on + timedelta(days=1)
                    )
                elif today > rec.grace_until:
                    vals.update(
                        state="lapsed", benefits_withdrawn_on=rec.grace_until + timedelta(days=1)
                    )
            if vals:
                rec._guarded().write(vals)
                moved += 1
                if vals.get("state") == "lapsed":
                    publish(
                        rec.env,
                        "loyalty.membership_lapsed",
                        "fix.loyalty.membership",
                        rec.id,
                        {
                            "membership_no": rec.name,
                            "partner_id": rec.partner_id.id,
                            "benefits_withdrawn_on": str(rec.benefits_withdrawn_on),
                        },
                    )
        return moved


# ---------------------------------------------------------------------------
# Page 2 - benefit definition with scope (BRU-LOY-01)
# ---------------------------------------------------------------------------
BENEFIT_TYPES = [
    ("labour_discount", "Labour Discount (%)"),
    ("priority_sla", "Priority SLA (hours)"),
    ("free_logistics", "Free Pick-up & Delivery (per year)"),
    ("extended_warranty", "Extended Repair Warranty (days)"),
    ("dedicated_line", "Dedicated Support Line"),
    ("health_check", "Free Annual Health Check (per year)"),
]
DISCOUNT_TYPES = ("labour_discount",)


class FixLoyaltyBenefit(models.Model):
    _name = "fix.loyalty.benefit"
    _description = "Tier Benefit Definition"
    _order = "tier_id, priority, id"

    tier_id = fields.Many2one("fix.loyalty.tier", required=True, ondelete="cascade", index=True)
    program_id = fields.Many2one(related="tier_id.program_id", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True
    )
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Name (Bengali)")
    benefit_type = fields.Selection(BENEFIT_TYPES, required=True)
    value = fields.Float(help="Percent for a discount; hours, days or a count for an entitlement.")
    applies_to = fields.Selection(
        [
            ("labour", "Labour charges"),
            ("parts", "Parts"),
            ("consumables", "Consumables"),
            ("transport", "Transport / logistics"),
            ("service", "Service entitlement (no price)"),
        ],
        required=True,
        default="labour",
    )
    priority = fields.Integer(default=10, help="Order in which benefits apply.")
    stackable = fields.Boolean(default=True, help="May combine with vouchers and promotions.")
    effective_from = fields.Date(default=fields.Date.context_today)
    effective_to = fields.Date()
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "UNIQUE (tier_id, code)", "A benefit code appears once per tier."
    )

    @api.constrains("benefit_type", "applies_to", "value", "effective_from", "effective_to")
    def _check_scope(self):
        for rec in self:
            if rec.benefit_type in DISCOUNT_TYPES:
                if rec.applies_to != "labour":
                    raise ValidationError(
                        "BRU-LOY-01: a privilege discount applies to labour charges only, "
                        "never to parts, consumables or transport."
                    )
                if not 0.0 < rec.value <= 100.0:
                    raise ValidationError("A discount lies above 0% and at most 100%.")
            elif rec.applies_to in ("parts", "consumables"):
                raise ValidationError(
                    "BRU-LOY-01: no privilege benefit applies to parts or consumables."
                )
            if rec.value < 0:
                raise ValidationError("A benefit value cannot be negative.")
            if rec.effective_to and rec.effective_from and rec.effective_to < rec.effective_from:
                raise ValidationError("The benefit ends before it starts.")

    def discount_for(self, line_kind, amount):
        """AUT-LOY-02 scope check: the discount this benefit gives one bill line.

        Only labour lines are ever discounted, whatever the caller asks."""
        self.ensure_one()
        if self.benefit_type not in DISCOUNT_TYPES or not self.active:
            return 0.0
        if line_kind != "labour" or self.applies_to != "labour":
            return 0.0
        return round((amount or 0.0) * self.value / 100.0, 2)


# ---------------------------------------------------------------------------
# Page 4 - BDT stored-value wallet
# ---------------------------------------------------------------------------
CREDIT_TYPES = ("refund", "trade_in", "prepayment", "goodwill")
DEBIT_TYPES = ("application", "payout")
NEEDS_SOURCE = ("refund", "trade_in", "prepayment")


class FixLoyaltyWallet(models.Model):
    _name = "fix.loyalty.wallet"
    _description = "Customer Stored-Value Wallet (BDT)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "balance_bdt desc, id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "balance_bdt", "last_activity_at"}

    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    partner_id = fields.Many2one("res.partner", required=True, index=True, ondelete="restrict")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one("res.currency", default=lambda self: _bdt(self.env))
    state = fields.Selection(
        [("active", "Active"), ("frozen", "Frozen"), ("closed", "Closed")],
        required=True,
        default="active",
        tracking=True,
    )
    balance_bdt = fields.Monetary(
        string="Balance (BDT)", currency_field="currency_id", readonly=True, default=0.0
    )
    last_activity_at = fields.Datetime(readonly=True)
    txn_ids = fields.One2many("fix.loyalty.wallet.txn", "wallet_id", string="Transactions")

    _partner_unique = models.Constraint(
        "UNIQUE (partner_id, company_id)", "A customer holds one wallet per company."
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.name in (False, "New"):
                rec._guarded().write(
                    {"name": self.env["ir.sequence"].next_by_code("fix.loyalty.wallet") or "New"}
                )
        return records

    @api.model
    def _for_partner(self, partner, company):
        wallet = self.sudo().search(
            [("partner_id", "=", partner.id), ("company_id", "=", company.id)], limit=1
        )
        return wallet or self.sudo().create({"partner_id": partner.id, "company_id": company.id})

    def _ledger_balance(self):
        self.ensure_one()
        lines = (
            self.env["fix.loyalty.wallet.txn"]
            .sudo()
            .search([("wallet_id", "=", self.id), ("state", "=", "posted")])
        )
        return round(sum(lines.mapped("signed_amount")), 2)

    def action_freeze(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why the wallet is frozen.")
        for rec in self:
            rec._guarded().write({"state": "frozen"})
            rec.message_post(body="Wallet frozen: %s" % reason)
        return True

    def action_unfreeze(self):
        if not (self.env.su or self.env.user.has_group(FINANCE_GROUP)):
            raise AccessError("Only Finance may release a frozen wallet.")
        for rec in self.filtered(lambda r: r.state == "frozen"):
            rec._guarded().write({"state": "active"})
        return True


class FixLoyaltyWalletTxn(models.Model):
    _name = "fix.loyalty.wallet.txn"
    _description = "Wallet Transaction (append-only)"
    _inherit = ["mail.thread", "fix.dofa.mixin"]
    _order = "create_date desc, id desc"
    _approval_routed = True

    # BRU-LOY-13: payout above BDT 5,000 needs approval (owner may move the bar).
    _DOFA_BDT_THRESHOLDS = [
        (5000.0, "tier_0"),
        (50000.0, "tier_2"),
        (200000.0, "tier_3"),
        (float("inf"), "tier_4"),
    ]

    def _dofa_thresholds(self):
        return self._DOFA_BDT_THRESHOLDS

    def _dofa_amount(self) -> float:
        """Money that leaves the business or is given away carries authority."""
        self.ensure_one()
        if self.entry_type in ("payout", "goodwill"):
            return abs(self.amount or 0.0)
        return 0.0

    @api.depends("amount", "entry_type")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "balance_after",
            "posted_at",
            "posted_by",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            return locked | {
                "partner_id",
                "entry_type",
                "amount",
                "source_ref",
                "invoice_id",
                "payout_method",
                "payout_account",
                "id_document_id",
                "reason",
            }
        return locked

    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    wallet_id = fields.Many2one(
        "fix.loyalty.wallet", readonly=True, index=True, ondelete="restrict"
    )
    partner_id = fields.Many2one("res.partner", required=True, index=True, ondelete="restrict")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one("res.currency", default=lambda self: _bdt(self.env))
    entry_type = fields.Selection(
        [
            ("refund", "Credit: Refund"),
            ("trade_in", "Credit: Trade-in Proceeds"),
            ("prepayment", "Credit: Prepayment"),
            ("goodwill", "Credit: Goodwill"),
            ("application", "Debit: Applied to Invoice"),
            ("payout", "Debit: Payout to Bank / MFS"),
        ],
        required=True,
    )
    amount = fields.Monetary(string="Amount (BDT)", currency_field="currency_id", required=True)
    signed_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_signed", store=True
    )
    balance_after = fields.Monetary(currency_field="currency_id", readonly=True)
    source_ref = fields.Char(
        string="Source Document", help="The refund, trade-in or receipt that created the credit."
    )
    invoice_id = fields.Many2one("account.move", string="Invoice", ondelete="restrict")
    payout_method = fields.Selection(
        [("bank", "Bank (BEFTN)"), ("bkash", "bKash"), ("nagad", "Nagad"), ("rocket", "Rocket")]
    )
    payout_account = fields.Char(string="Payout Account / Wallet No.")
    id_document_id = fields.Many2one(
        "fix.identity.document", string="Identity Verified With", ondelete="restrict"
    )
    reason = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted"), ("cancelled", "Cancelled")],
        required=True,
        default="draft",
        tracking=True,
        index=True,
    )
    posted_at = fields.Datetime(readonly=True, copy=False)
    posted_by = fields.Many2one("res.users", readonly=True, copy=False)

    @api.depends("amount", "entry_type")
    def _compute_signed(self):
        for rec in self:
            sign = -1.0 if rec.entry_type in DEBIT_TYPES else 1.0
            rec.signed_amount = sign * abs(rec.amount or 0.0)

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if (rec.amount or 0.0) <= 0:
                raise ValidationError("A wallet amount is positive; the type says its direction.")

    @api.model_create_multi
    def create(self, vals_list):
        Wallet = self.env["fix.loyalty.wallet"]
        Partner = self.env["res.partner"]
        for vals in vals_list:
            # the wallet is always the partner's own; a typed wallet_id is ignored
            if vals.get("partner_id"):
                company = self.env["res.company"].browse(vals.get("company_id")) or self.env.company
                vals["wallet_id"] = Wallet._for_partner(
                    Partner.browse(vals["partner_id"]), company
                ).id
        records = super().create(vals_list)
        for rec in records:
            if rec.name in (False, "New"):
                rec._guarded().write(
                    {
                        "name": self.env["ir.sequence"].next_by_code("fix.loyalty.wallet.txn")
                        or "New"
                    }
                )
        return records

    def write(self, vals):
        _refuse_posted_edit(self, vals, ("reason",), "Wallet transaction")
        if not self.env.su:
            if "wallet_id" in vals and any(
                rec._fix_guard_differs("wallet_id", vals["wallet_id"], rec.wallet_id)
                for rec in self
            ):
                raise UserError("A transaction stays on its customer's wallet.")
            if (
                vals.get("partner_id")
                and len(self) == 1
                and self.partner_id.id != vals["partner_id"]
            ):
                # a draft re-pointed to another customer moves to that customer's wallet
                partner = self.env["res.partner"].browse(vals["partner_id"])
                vals = dict(
                    vals,
                    wallet_id=self.env["fix.loyalty.wallet"]
                    ._for_partner(partner, self.company_id)
                    .id,
                )
        return super().write(vals)

    def unlink(self):
        if any(rec.state == "posted" for rec in self) and not self.env.su:
            raise UserError("A posted wallet transaction is evidence and cannot be deleted.")
        return super().unlink()

    def _credit_creators(self):
        self.ensure_one()
        credits = self.sudo().search(
            [
                ("wallet_id", "=", self.wallet_id.id),
                ("state", "=", "posted"),
                ("entry_type", "in", CREDIT_TYPES),
            ]
        )
        return credits.mapped("create_uid")

    def _check_before_post(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Only a draft wallet transaction can be posted.")
        if self.wallet_id.partner_id != self.partner_id:
            raise UserError("The wallet belongs to another customer.")
        if self.entry_type in NEEDS_SOURCE and not (self.source_ref or "").strip():
            raise UserError(
                "Name the refund, trade-in or receipt behind this credit: a wallet credit "
                "always has a source (FR-LOY-022)."
            )
        if self.entry_type == "goodwill" and not (self.reason or "").strip():
            raise UserError("A goodwill credit needs its reason.")
        if self.entry_type in DEBIT_TYPES and self.wallet_id.state != "active":
            raise UserError(
                "Wallet %s is %s; nothing can be taken out of it."
                % (self.wallet_id.name, self.wallet_id.state)
            )
        if self.entry_type == "application":
            inv = self.invoice_id.sudo()
            if not inv or inv.move_type != "out_invoice" or inv.state != "posted":
                raise UserError("Apply the wallet to a posted customer invoice.")
            if inv.partner_id.commercial_partner_id != self.partner_id.commercial_partner_id:
                raise UserError("That invoice belongs to another customer.")
            if self.amount > inv.amount_residual + 0.005:
                raise UserError("The invoice has only BDT %.2f outstanding." % inv.amount_residual)
        if self.entry_type == "payout":
            doc = self.id_document_id.sudo()
            if (
                not doc
                or doc.partner_id.commercial_partner_id != self.partner_id.commercial_partner_id
                or doc.verification_status != "verified"
            ):
                raise UserError(
                    "BRU-LOY-13: a payout needs the customer's identity verified. Select a "
                    "VERIFIED identity document of this customer."
                )
            if not self.payout_method or not (self.payout_account or "").strip():
                raise UserError("Give the bank account or mobile wallet the payout goes to.")
        self._dofa_assert_approved(
            "Wallet %s" % dict(self._fields["entry_type"].selection)[self.entry_type]
        )
        if self.entry_type == "payout" and not self.env.su:
            # SOD-18: payout approval is separated from wallet credit creation.
            decider = self.dofa_approved_by or self.env.user
            if decider in self._credit_creators():
                raise UserError(
                    "SOD-18: %s created credits on this wallet, so may not approve or "
                    "release its payout." % decider.name
                )

    def action_post(self):
        for rec in self:
            rec._check_before_post()
            # BRU-LOY-06 for money: lock the wallet, then re-read the balance.
            self.env.cr.execute(
                "SELECT id FROM fix_loyalty_wallet WHERE id = %s FOR UPDATE", (rec.wallet_id.id,)
            )
            balance = rec.wallet_id._ledger_balance()
            after = round(balance + rec.signed_amount, 2)
            if after < -0.005:
                raise UserError(
                    "Wallet %s holds BDT %.2f; BDT %.2f cannot be taken from it."
                    % (rec.wallet_id.name, balance, rec.amount)
                )
            rec._guarded().write(
                {
                    "state": "posted",
                    "balance_after": after,
                    "posted_at": fields.Datetime.now(),
                    "posted_by": self.env.user.id,
                }
            )
            rec.wallet_id._guarded().write(
                {"balance_bdt": after, "last_activity_at": fields.Datetime.now()}
            )
            publish(
                rec.env,
                "loyalty.wallet_txn_posted",
                "fix.loyalty.wallet.txn",
                rec.id,
                {
                    "txn_no": rec.name,
                    "wallet_no": rec.wallet_id.name,
                    "partner_id": rec.partner_id.id,
                    "entry_type": rec.entry_type,
                    "amount": float(rec.signed_amount),
                    "balance_after": float(after),
                    "invoice_id": rec.invoice_id.id or 0,
                },
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft wallet transaction can be cancelled.")
            rec._guarded().write({"state": "cancelled"})
        return True


# ---------------------------------------------------------------------------
# Page 5 - voucher batches and stacking
# ---------------------------------------------------------------------------
class FixLoyaltyVoucherBatched(models.Model):
    _inherit = "fix.loyalty.voucher"

    partner_id = fields.Many2one(required=False)
    batch_id = fields.Many2one("fix.loyalty.voucher.batch", index=True, ondelete="restrict")

    @api.constrains("partner_id", "batch_id")
    def _check_holder(self):
        for rec in self:
            if not rec.partner_id and not (rec.batch_id and rec.batch_id.batch_type == "bulk"):
                raise ValidationError(
                    "A voucher outside a bulk batch is issued to a named customer."
                )

    def _batch_eligibility_errors(self, partner, amount=None, channel=None):
        """FR-LOY-028: who may redeem a batch voucher. Empty list = eligible."""
        self.ensure_one()
        batch = self.batch_id
        if not batch:
            return []
        errors = []
        if self.partner_id and partner and self.partner_id != partner:
            errors.append("the voucher was issued to another customer")
        if batch.channel != "any" and channel and channel != batch.channel:
            errors.append("valid on the %s channel only" % batch.channel)
        if amount is not None and (batch.min_spend_bdt or 0.0) > (amount or 0.0):
            errors.append("minimum spend BDT %.2f" % batch.min_spend_bdt)
        if batch.tier_ids and partner:
            account = (
                self.env["fix.loyalty.account"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", partner.id),
                        ("program_id", "=", batch.program_id.id),
                        ("state", "=", "active"),
                    ],
                    limit=1,
                )
            )
            if account.tier_id not in batch.tier_ids:
                errors.append("restricted to tiers %s" % ", ".join(batch.tier_ids.mapped("name")))
        if batch.first_purchase_only and partner:
            done = (
                self.env["fix.service.order"]
                .sudo()
                .search_count([("customer_id", "=", partner.id), ("state", "=", "closed")], limit=1)
            )
            if done:
                errors.append("first purchase only")
        if partner and batch.max_per_customer:
            used = self.sudo().search_count(
                [
                    ("batch_id", "=", batch.id),
                    ("partner_id", "=", partner.id),
                    ("state", "=", "redeemed"),
                    ("id", "!=", self.id),
                ]
            )
            if used >= batch.max_per_customer:
                errors.append("already used %d time(s) from this batch" % used)
        return errors

    def action_redeem(self, service_order):
        self.ensure_one()
        if self.batch_id:
            partner = service_order.customer_id
            amount = getattr(service_order, "amount_total", None)
            errors = self._batch_eligibility_errors(partner, amount=amount)
            if errors:
                raise UserError("Voucher %s cannot be used: %s." % (self.name, "; ".join(errors)))
            if not self.partner_id:
                self.write({"partner_id": partner.id})
        return super().action_redeem(service_order)


class FixLoyaltyVoucherBatch(models.Model):
    _name = "fix.loyalty.voucher.batch"
    _description = "Voucher Batch"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "issued_at",
            "issued_by",
            "closed_unredeemed",
        }

    name = fields.Char(string="Batch Name", required=True)
    code_prefix = fields.Char(
        required=True, help="2-8 letters or digits, printed before each code."
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    program_id = fields.Many2one("fix.loyalty.program", required=True, ondelete="restrict")
    campaign_id = fields.Many2one("fix.campaign", string="Campaign (M35)")
    batch_type = fields.Selection(
        [
            ("bulk", "Bulk codes (holder named at redemption)"),
            ("personalised", "Personalised (one code per listed customer)"),
        ],
        required=True,
        default="personalised",
    )
    quantity = fields.Integer(string="Codes to Issue (bulk)", default=0)
    partner_ids = fields.Many2many("res.partner", string="Customers (personalised)")
    discount_type = fields.Selection(
        [("fixed_bdt", "Fixed BDT Discount"), ("percentage", "Percentage Discount (%)")],
        required=True,
        default="fixed_bdt",
    )
    discount_value = fields.Float(required=True)
    min_spend_bdt = fields.Float(string="Minimum Spend (BDT)", default=0.0)
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_until = fields.Date(required=True)
    tier_ids = fields.Many2many("fix.loyalty.tier", string="Eligible Tiers (empty = all)")
    channel = fields.Selection([("any", "Any channel"), *CHANNELS], required=True, default="any")
    first_purchase_only = fields.Boolean()
    max_per_customer = fields.Integer(default=1, help="0 = no limit.")
    state = fields.Selection(
        [("draft", "Draft"), ("issued", "Issued"), ("closed", "Closed")],
        required=True,
        default="draft",
        tracking=True,
    )
    issued_at = fields.Datetime(readonly=True, copy=False)
    issued_by = fields.Many2one("res.users", readonly=True, copy=False)
    voucher_ids = fields.One2many("fix.loyalty.voucher", "batch_id", string="Vouchers")
    issued_count = fields.Integer(compute="_compute_usage")
    redeemed_count = fields.Integer(compute="_compute_usage")
    face_value_redeemed = fields.Float(
        compute="_compute_usage", string="Redeemed Value (BDT, fixed)"
    )
    closed_unredeemed = fields.Integer(readonly=True, copy=False)

    @api.depends("voucher_ids.state")
    def _compute_usage(self):
        for rec in self:
            vouchers = rec.voucher_ids
            redeemed = vouchers.filtered(lambda v: v.state == "redeemed")
            rec.issued_count = len(vouchers)
            rec.redeemed_count = len(redeemed)
            rec.face_value_redeemed = (
                sum(redeemed.mapped("discount_value")) if rec.discount_type == "fixed_bdt" else 0.0
            )

    @api.constrains(
        "code_prefix",
        "discount_type",
        "discount_value",
        "valid_from",
        "valid_until",
        "quantity",
        "max_per_customer",
        "min_spend_bdt",
    )
    def _check_batch(self):
        for rec in self:
            if not re.fullmatch(r"[A-Z0-9]{2,8}", rec.code_prefix or ""):
                raise ValidationError("The code prefix is 2 to 8 capital letters or digits.")
            if rec.discount_value <= 0 or (
                rec.discount_type == "percentage" and rec.discount_value > 100.0
            ):
                raise ValidationError("A discount is above 0 and a percentage at most 100.")
            if rec.valid_until < rec.valid_from:
                raise ValidationError("The batch is valid until a date before it starts.")
            if not 0 <= rec.quantity <= MAX_BATCH:
                raise ValidationError("A batch issues at most %d codes." % MAX_BATCH)
            if rec.max_per_customer < 0 or rec.min_spend_bdt < 0:
                raise ValidationError("Limits cannot be negative.")

    def write(self, vals):
        _refuse_posted_edit(self, vals, ("name",), "Voucher batch")
        return super().write(vals)

    def action_issue(self):
        """FR-LOY-027: mint the batch's codes, within its issuance limit."""
        Voucher = self.env["fix.loyalty.voucher"].sudo()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Batch %s is already issued." % rec.name)
            if rec.batch_type == "bulk":
                if rec.quantity < 1:
                    raise UserError("Say how many codes the bulk batch issues.")
                holders = [False] * rec.quantity
            else:
                if not rec.partner_ids:
                    raise UserError("List the customers a personalised batch is issued to.")
                if len(rec.partner_ids) > MAX_BATCH:
                    raise UserError("A batch issues at most %d codes." % MAX_BATCH)
                holders = rec.partner_ids.ids
            vals = [
                {
                    "name": "%s-%s" % (rec.code_prefix, secrets.token_hex(5).upper()),
                    "partner_id": pid,
                    "batch_id": rec.id,
                    "campaign_id": rec.campaign_id.id,
                    "company_id": rec.company_id.id,
                    "discount_type": rec.discount_type,
                    "discount_value": rec.discount_value,
                    "min_spend_bdt": rec.min_spend_bdt,
                    "valid_from": rec.valid_from,
                    "valid_until": rec.valid_until,
                    "state": "active",
                }
                for pid in holders
            ]
            Voucher.create(vals)
            rec._guarded().write(
                {"state": "issued", "issued_at": fields.Datetime.now(), "issued_by": self.env.uid}
            )
            publish(
                rec.env,
                "loyalty.voucher_batch_issued",
                "fix.loyalty.voucher.batch",
                rec.id,
                {
                    "batch": rec.name,
                    "program": rec.program_id.code or "",
                    "codes": len(vals),
                    "discount_type": rec.discount_type,
                    "discount_value": float(rec.discount_value),
                    "valid_until": str(rec.valid_until),
                },
            )
        return True

    def action_close(self):
        """AUT-LOY-14: close the batch; unredeemed codes stop working."""
        for rec in self:
            if rec.state != "issued":
                raise UserError("Only an issued batch can be closed.")
            open_codes = rec.voucher_ids.filtered(lambda v: v.state in ("draft", "active"))
            open_codes.sudo().write({"state": "cancelled"})
            rec._guarded().write({"state": "closed", "closed_unredeemed": len(open_codes)})
        return True

    @api.model
    def cron_close_expired_batches(self):
        today = _local_today(self.env)
        batches = self.sudo().search([("state", "=", "issued"), ("valid_until", "<", today)])
        batches.action_close()
        return len(batches)


STACK_COMPONENTS = [
    ("tier_benefit", "Tier privilege discount"),
    ("voucher", "Voucher"),
    ("promotion", "Campaign promotion"),
    ("points", "Points redemption"),
]


class FixLoyaltyStackingRule(models.Model):
    _name = "fix.loyalty.stacking.rule"
    _description = "Benefit Stacking Rule"
    _order = "program_id, sequence, id"

    program_id = fields.Many2one("fix.loyalty.program", required=True, ondelete="cascade")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True
    )
    sequence = fields.Integer(default=10, help="Lower applies first.")
    component_a = fields.Selection(STACK_COMPONENTS, required=True)
    component_b = fields.Selection(STACK_COMPONENTS, required=True)
    allowed = fields.Boolean(default=True, help="Off: the later of the two is dropped.")
    max_aggregate_pct = fields.Float(
        string="Max Combined Discount %",
        default=100.0,
        help="When both apply, together they may take at most this share of the bill.",
    )
    note = fields.Char()
    active = fields.Boolean(default=True)

    _pair_unique = models.Constraint(
        "UNIQUE (program_id, component_a, component_b)", "One rule per pair in a programme."
    )

    @api.constrains("component_a", "component_b", "max_aggregate_pct")
    def _check_rule(self):
        for rec in self:
            if rec.component_a == rec.component_b:
                raise ValidationError("A stacking rule pairs two different components.")
            if not 0.0 < rec.max_aggregate_pct <= 100.0:
                raise ValidationError("The combined cap lies above 0% and at most 100%.")
            twin = self.search_count(
                [
                    ("id", "!=", rec.id),
                    ("program_id", "=", rec.program_id.id),
                    ("component_a", "=", rec.component_b),
                    ("component_b", "=", rec.component_a),
                ]
            )
            if twin:
                raise ValidationError("This pair already has a rule (in the other order).")

    @api.model
    def evaluate(self, program, components):
        """AUT-LOY-02 / AC-06: deterministic stacking with the rules that fired.

        components: [{'kind': <component>, 'pct': <percent of bill>}], in the
        order offered. Applied in rule order; a disallowed pair drops the
        later component; the total is capped (BRU-LOY-09)."""
        rules = self.sudo().search([("program_id", "=", program.id), ("active", "=", True)])
        order = {k: i for i, (k, _l) in enumerate(STACK_COMPONENTS)}
        items = sorted(components, key=lambda c: (order.get(c["kind"], 99), -c["pct"]))
        applied, dropped, fired = [], [], []
        cap = program.max_aggregate_discount_pct or 100.0
        for item in items:
            blocker = None
            for prev in applied:
                rule = rules.filtered(
                    lambda r, a=prev["kind"], b=item["kind"]: {r.component_a, r.component_b}
                    == {a, b}
                )[:1]
                if rule:
                    fired.append(rule.id)
                    cap = min(cap, rule.max_aggregate_pct)
                    if not rule.allowed:
                        blocker = rule
            if blocker:
                dropped.append(dict(item, reason="not combinable (rule %d)" % blocker.id))
                continue
            applied.append(dict(item))
        total, out = 0.0, []
        for item in applied:
            take = max(0.0, min(item["pct"], cap - total))
            total += take
            out.append(dict(item, pct=round(take, 4)))
        return {
            "applied": out,
            "dropped": dropped,
            "total_pct": round(total, 4),
            "cap_pct": cap,
            "fired": sorted(set(fired)),
        }


# ---------------------------------------------------------------------------
# Page 6 - referral attribution events
# ---------------------------------------------------------------------------
class FixLoyaltyReferralEvent(models.Model):
    _name = "fix.loyalty.referral.event"
    _description = "Referral Attribution Event"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "registered_at desc, id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "block_reason",
            "qualified_at",
            "rewarded_at",
            "reward_referrer_points",
            "reward_referee_points",
        }

    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    code_id = fields.Many2one(
        "fix.loyalty.referral.code",
        string="Referral Code",
        required=True,
        ondelete="restrict",
        index=True,
    )
    program_id = fields.Many2one(related="code_id.program_id", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    referrer_partner_id = fields.Many2one(related="code_id.referrer_partner_id", store=True)
    referee_partner_id = fields.Many2one(
        "res.partner", string="New Customer", required=True, ondelete="restrict", index=True
    )
    channel = fields.Selection(CHANNELS, default="counter")
    registered_at = fields.Datetime(default=fields.Datetime.now, required=True)
    window_until = fields.Date(compute="_compute_window", store=True)
    state = fields.Selection(
        [
            ("registered", "Registered"),
            ("qualified", "Qualified"),
            ("rewarded", "Rewarded"),
            ("not_qualified", "Not Qualified"),
            ("blocked", "Blocked"),
        ],
        required=True,
        default="registered",
        tracking=True,
        index=True,
    )
    block_reason = fields.Char(readonly=True)
    qualified_at = fields.Datetime(readonly=True)
    rewarded_at = fields.Datetime(readonly=True)
    reward_referrer_points = fields.Integer(readonly=True)
    reward_referee_points = fields.Integer(readonly=True)

    @api.depends("registered_at", "code_id.program_id.referral_window_days")
    def _compute_window(self):
        for rec in self:
            days = rec.code_id.program_id.referral_window_days or 90
            rec.window_until = (
                rec.registered_at.date() + timedelta(days=days) if rec.registered_at else False
            )

    def _block_reason(self):
        """AUT-LOY-09 / BRU-LOY-10: the reason this registration is blocked, or None."""
        self.ensure_one()
        code = self.code_id.sudo()
        referrer = code.referrer_partner_id
        referee = self.referee_partner_id
        if code.state != "pending":
            return "the referral code is %s" % code.state
        if code.referee_partner_id and code.referee_partner_id != referee:
            return "the code was issued for another named customer"
        if referrer.commercial_partner_id == referee.commercial_partner_id:
            return "self-referral (same customer or company)"
        a, b = referrer, referee
        for f in ("phone", "mobile", "email"):
            if f in a._fields and _norm(a[f]) and _norm(a[f]) == _norm(b[f]):
                return "self-referral: same %s as the referrer" % f
        if (
            _norm(a.street)
            and _norm(a.street) == _norm(b.street)
            and _norm(a.city) == _norm(b.city)
        ):
            return "household referral: same address as the referrer"
        circular = self.sudo().search_count(
            [
                ("id", "!=", self.id),
                ("referrer_partner_id", "=", referee.id),
                ("referee_partner_id", "=", referrer.id),
                ("state", "!=", "blocked"),
            ]
        )
        if circular:
            return "circular referral: the new customer referred the referrer"
        prior = self.sudo().search(
            [
                ("id", "!=", self.id),
                ("referee_partner_id", "=", referee.id),
                ("program_id", "=", code.program_id.id),
                ("state", "!=", "blocked"),
            ],
            limit=1,
        )
        if prior:
            return "already attributed to %s (first attribution wins)" % prior.code_id.name
        if (
            referee.create_date
            and self.registered_at
            and referee.create_date < self.registered_at - timedelta(days=1)
        ):
            orders = (
                self.env["fix.service.order"]
                .sudo()
                .search_count([("customer_id", "=", referee.id), ("state", "=", "closed")], limit=1)
            )
            if orders:
                return "not a new customer: already served"
        cap = code.program_id.referral_cap_per_month
        if cap:
            start = self.registered_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            count = self.sudo().search_count(
                [
                    ("id", "!=", self.id),
                    ("referrer_partner_id", "=", referrer.id),
                    ("registered_at", ">=", start),
                    ("state", "!=", "blocked"),
                ]
            )
            if count >= cap:
                return "referrer cap of %d per month reached" % cap
        return None

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            vals = {
                "name": self.env["ir.sequence"].next_by_code("fix.loyalty.referral.event") or "New"
            }
            reason = rec._block_reason()
            if reason:
                vals.update(state="blocked", block_reason=reason)
            rec._guarded().write(vals)
            if reason:
                publish(
                    rec.env,
                    "loyalty.referral_blocked",
                    "fix.loyalty.referral.event",
                    rec.id,
                    {
                        "event_no": rec.name,
                        "code": rec.code_id.name,
                        "referrer_partner_id": rec.referrer_partner_id.id,
                        "referee_partner_id": rec.referee_partner_id.id,
                        "reason": reason,
                    },
                )
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            locked = {"code_id", "referee_partner_id", "registered_at"} & set(vals)
            for rec in self:
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in locked):
                    raise UserError("An attribution is a record of what happened; register anew.")
        return super().write(vals)

    def action_qualify(self):
        """AUT-LOY-10: the referee's first completed service rewards both sides."""
        today = _local_today(self.env)
        for rec in self:
            if rec.state != "registered":
                raise UserError("Only a registered referral can qualify.")
            if rec.window_until and today > rec.window_until:
                rec._guarded().write(
                    {"state": "not_qualified", "block_reason": "attribution window expired"}
                )
                continue
            closed = (
                self.env["fix.service.order"]
                .sudo()
                .search_count(
                    [("customer_id", "=", rec.referee_partner_id.id), ("state", "=", "closed")],
                    limit=1,
                )
            )
            if not closed:
                raise UserError(
                    "%s has no completed service yet. A referral qualifies on the new "
                    "customer's first completed paid service." % rec.referee_partner_id.display_name
                )
            rec._guarded().write({"state": "qualified", "qualified_at": fields.Datetime.now()})
            rec._reward()
        return True

    def _reward(self):
        self.ensure_one()
        program = self.program_id
        Account = self.env["fix.loyalty.account"].sudo()
        Ledger = self.env["fix.loyalty.ledger"].sudo()
        Receipt = self.env["fix.loyalty.event.receipt"]
        given = {}
        for role, partner, points in (
            ("referrer", self.referrer_partner_id, program.referral_referrer_points),
            ("referee", self.referee_partner_id, program.referral_referee_points),
        ):
            given[role] = 0
            key = "referral_event:%d:%s" % (self.id, role)
            if points <= 0 or Receipt._seen(key):
                continue
            account = Account.search(
                [("partner_id", "=", partner.id), ("program_id", "=", program.id)], limit=1
            )
            if not account or account.state != "active":
                Receipt._record(
                    key,
                    {},
                    "No award: the %s has no active account." % role,
                    account=account or None,
                )
                continue
            line = Ledger.create(
                {
                    "account_id": account.id,
                    "transaction_type": "referral_bonus",
                    "points": points,
                    "company_id": account.company_id.id,
                    "notes": "Referral %s qualified: %s award." % (self.name, role),
                }
            )
            line.action_post()
            Receipt._record(key, {}, "Awarded %d points to the %s." % (points, role), account, line)
            given[role] = points
        self._guarded().write(
            {
                "state": "rewarded",
                "rewarded_at": fields.Datetime.now(),
                "reward_referrer_points": given["referrer"],
                "reward_referee_points": given["referee"],
            }
        )

    @api.model
    def cron_expire_referral_events(self):
        today = _local_today(self.env)
        late = self.sudo().search([("state", "=", "registered"), ("window_until", "<", today)])
        late._guarded().write(
            {"state": "not_qualified", "block_reason": "attribution window expired"}
        )
        return len(late)


# ---------------------------------------------------------------------------
# Page 8 - period-end liability and breakage run
# ---------------------------------------------------------------------------
class FixLoyaltyLiabilityRun(models.Model):
    _name = "fix.loyalty.liability.run"
    _description = "Points Liability & Breakage Run (IFRS 15)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "period_end desc, id desc"

    _FIGURES = (
        "points_outstanding",
        "ledger_points",
        "account_points",
        "reconciles",
        "valuation",
        "gross_liability",
        "breakage_rate_pct",
        "breakage_amount",
        "net_liability",
        "prior_net_liability",
        "movement",
        "membership_deferred_bdt",
        "calculated_by",
        "calculated_at",
        "published_by",
        "published_at",
        "state",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._FIGURES)

    def _default_period_end(self):
        return _local_today(self.env).replace(day=1) - timedelta(days=1)

    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    program_id = fields.Many2one("fix.loyalty.program", required=True, ondelete="restrict")
    period_end = fields.Date(required=True, default=_default_period_end)
    currency_id = fields.Many2one("res.currency", default=lambda self: _bdt(self.env))
    state = fields.Selection(
        [("draft", "Draft"), ("calculated", "Calculated"), ("published", "Published to M19")],
        required=True,
        default="draft",
        tracking=True,
    )
    points_outstanding = fields.Integer(readonly=True)
    ledger_points = fields.Integer(readonly=True, help="Posted ledger points up to period end.")
    account_points = fields.Integer(readonly=True, help="Sum of member balances now.")
    reconciles = fields.Boolean(readonly=True)
    valuation = fields.Float(string="BDT per Point", readonly=True)
    gross_liability = fields.Monetary(currency_field="currency_id", readonly=True)
    breakage_rate_pct = fields.Float(readonly=True)
    breakage_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    net_liability = fields.Monetary(currency_field="currency_id", readonly=True)
    prior_net_liability = fields.Monetary(currency_field="currency_id", readonly=True)
    movement = fields.Monetary(currency_field="currency_id", readonly=True)
    membership_deferred_bdt = fields.Monetary(
        string="Membership Fees Deferred", currency_field="currency_id", readonly=True
    )
    breakage_basis = fields.Text(
        string="Breakage Basis", help="FR-LOY-041 / AC-10: how the breakage rate was set."
    )
    calculated_by = fields.Many2one("res.users", readonly=True)
    calculated_at = fields.Datetime(readonly=True)
    published_by = fields.Many2one("res.users", readonly=True)
    published_at = fields.Datetime(readonly=True)

    _period_unique = models.Constraint(
        "UNIQUE (program_id, period_end)", "One liability run per programme and period."
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write(
                {"name": self.env["ir.sequence"].next_by_code("fix.loyalty.liability.run") or "New"}
            )
        return records

    def write(self, vals):
        _refuse_posted_edit(self, vals, (), "Liability run")
        return super().write(vals)

    def unlink(self):
        if any(r.state == "published" for r in self) and not self.env.su:
            raise UserError("A published liability run is part of the books.")
        return super().unlink()

    def action_calculate(self):
        """AUT-LOY-12: outstanding points at period end, valued, net of breakage."""
        for rec in self:
            if rec.state == "published":
                raise UserError("Run %s is published; calculate the next period." % rec.name)
            program = rec.program_id
            accounts = (
                self.env["fix.loyalty.account"].sudo().search([("program_id", "=", program.id)])
            )
            end = _local_day_end(self.env, rec.period_end)
            lines = (
                self.env["fix.loyalty.ledger"]
                .sudo()
                .search(
                    [
                        ("account_id", "in", accounts.ids),
                        ("state", "=", "posted"),
                        ("create_date", "<", end),
                    ]
                )
            )
            ledger_now = (
                self.env["fix.loyalty.ledger"]
                .sudo()
                .search([("account_id", "in", accounts.ids), ("state", "=", "posted")])
            )
            ledger_points = int(sum(lines.mapped("points")))
            account_points = int(sum(accounts.mapped("points_balance")))
            outstanding = max(0, ledger_points)
            rate = program.bdt_per_point or 0.0
            gross = round(outstanding * rate, 2)
            breakage = program.breakage_rate()
            prior = self.sudo().search(
                [
                    ("program_id", "=", program.id),
                    ("state", "=", "published"),
                    ("period_end", "<", rec.period_end),
                ],
                order="period_end desc",
                limit=1,
            )
            net = round(gross * (1.0 - breakage), 2)
            members = (
                self.env["fix.loyalty.membership"]
                .sudo()
                .search(
                    [("program_id", "=", program.id), ("state", "not in", ("pending", "cancelled"))]
                )
            )
            rec._guarded().write(
                {
                    "state": "calculated",
                    "points_outstanding": outstanding,
                    "ledger_points": ledger_points,
                    "account_points": account_points,
                    "reconciles": int(sum(ledger_now.mapped("points"))) == account_points,
                    "valuation": rate,
                    "gross_liability": gross,
                    "breakage_rate_pct": round(breakage * 100.0, 2),
                    "breakage_amount": round(gross - net, 2),
                    "net_liability": net,
                    "prior_net_liability": prior.net_liability if prior else 0.0,
                    "movement": round(net - (prior.net_liability if prior else 0.0), 2),
                    "membership_deferred_bdt": round(sum(members.mapped("deferred_bdt")), 2),
                    "calculated_by": self.env.user.id,
                    "calculated_at": fields.Datetime.now(),
                }
            )
        return True

    def action_publish(self):
        """BRU-LOY-11: Finance publishes, and not the person who calculated."""
        for rec in self:
            if rec.state != "calculated":
                raise UserError("Calculate run %s before publishing it." % rec.name)
            if not self.env.su:
                if not self.env.user.has_group(FINANCE_GROUP):
                    raise AccessError("Only Finance publishes the points liability to M19.")
                if rec.calculated_by == self.env.user:
                    raise UserError(
                        "Segregation of duties: you calculated run %s; another Finance "
                        "user must publish it." % rec.name
                    )
            if not rec.reconciles:
                raise UserError(
                    "Member balances do not reconcile to the posted ledger. Run 'Reconcile "
                    "Balance with Ledger' on the members, recalculate, then publish (AC-09)."
                )
            if rec.breakage_rate_pct > 0 and not (rec.breakage_basis or "").strip():
                raise UserError(
                    "FR-LOY-041: state the basis of the breakage rate before publishing."
                )
            rec._guarded().write(
                {
                    "state": "published",
                    "published_by": self.env.user.id,
                    "published_at": fields.Datetime.now(),
                }
            )
            publish(
                rec.env,
                "loyalty.liability_published",
                "fix.loyalty.liability.run",
                rec.id,
                {
                    "run_no": rec.name,
                    "program": rec.program_id.code or "",
                    "period_end": str(rec.period_end),
                    "points_outstanding": rec.points_outstanding,
                    "gross_liability": float(rec.gross_liability),
                    "breakage_amount": float(rec.breakage_amount),
                    "net_liability": float(rec.net_liability),
                    "movement": float(rec.movement),
                },
            )
        return True
