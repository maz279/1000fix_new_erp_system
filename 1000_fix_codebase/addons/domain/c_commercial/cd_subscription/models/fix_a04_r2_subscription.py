# A04 ERP audit, round 2 (21 Nov 2026), stream R2-2: the deferred M39 items.
#
# M39-F16 (BRU-SUB-07 / FR-SUB-022): a price increase applied with no
#   customer notice. A plan change that raises the recurring price now applies
#   only once the customer was told: Send Price Notice notifies the customer
#   (chatter mail to the customer, stamped notice_sent_at) and the new price
#   applies no earlier than the notice date + cd_subscription.price_change_
#   notice_days (default 30); an effective date inside that window moves to
#   its end. A decrease, a quantity change and a cancellation need no notice.
#   Two exemptions, each with its evidence: the customer asked for the change
#   (a reference, approved by a second person), or a signed contract amendment
#   (the M05 terms history, set by the system only).
# M39-F17: nothing consumed msp/data/rental.usage_reported, nor the
#   suspension / pause / cancellation events. Usage is ingested into
#   fix.subscription.usage idempotently by (subscription, source, source key);
#   usage that matches no subscription fails the delivery (the relay keeps it
#   as a dead letter, never dropped - BRU-SUB-08). The lifecycle events close
#   or reopen the subscription's service gate, and the M01 order intake warns
#   (default) or refuses (cd_subscription.suspended_service_policy = refuse)
#   service under a closed gate.
# M39-F11: one contract is billed by exactly one engine (fix.contract.
#   billing_engine, cd_contract_core): a subscription on a contract the M08
#   walker bills is refused, the walker skips a contract billed by M39, and
#   contract.activated creates a subscription only for a contract billed by M39.
import datetime

from odoo import api, fields, models
from odoo.addons.cd_contract_core.models.fix_contract import require_role
from odoo.exceptions import AccessError, UserError

from .fix_m39_capture import (
    DEAD_STATES,
    DEFAULT_PRICE_NOTICE_DAYS,
    PARAM_PRICE_NOTICE_DAYS,
    _int_param,
)
from .fix_subscription_ops import SUB_OFFICER

PARAM_GATE_POLICY = "cd_subscription.suspended_service_policy"
NOTICE_CHANNELS = [
    ("email", "E-mail"),
    ("sms", "SMS"),
    ("letter", "Letter"),
    ("portal", "Customer portal"),
]
NOTICE_EXEMPTIONS = [
    ("customer_request", "Customer requested the change"),
    ("contract_amendment", "Signed contract amendment (system)"),
]
NOTICE_INPUTS = {"notice_exemption", "notice_exemption_ref"}


def _dhaka_date(env, value):
    if not value:
        return None
    user = env["res.users"].with_context(tz="Asia/Dhaka")
    return fields.Datetime.context_timestamp(user, value).date()


class FixSubscriptionProrationNotice(models.Model):
    _inherit = "fix.subscription.proration"

    notice_sent_at = fields.Datetime(string="Price Notice Sent", readonly=True, copy=False)
    notice_sent_by_id = fields.Many2one(
        "res.users", string="Notice Sent By", readonly=True, copy=False
    )
    notice_channel = fields.Selection(
        NOTICE_CHANNELS, string="Notice Channel", readonly=True, copy=False
    )
    notice_ref = fields.Char(string="Notice Evidence", readonly=True, copy=False)
    notice_exemption = fields.Selection(
        NOTICE_EXEMPTIONS,
        string="No Notice Because",
        copy=False,
        help="A price increase needs the customer's notice unless the customer asked for it "
        "(give the reference) or it is a signed contract amendment (set by the system).",
    )
    notice_exemption_ref = fields.Char(string="Exemption Evidence", copy=False)
    notice_hold_noted = fields.Boolean(readonly=True, copy=False)
    is_price_increase = fields.Boolean(compute="_compute_notice_state", string="Price Increase")
    price_applies_from = fields.Date(
        compute="_compute_notice_state",
        string="New Price Applies From",
        help="The earliest day the new price may apply: the effective date, and for an "
        "increase no earlier than the notice date plus the notice period.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "notice_sent_at",
            "notice_sent_by_id",
            "notice_channel",
            "notice_ref",
            "notice_hold_noted",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= NOTICE_INPUTS
        return locked

    # ---- the rule ----------------------------------------------------------------
    def _fix_is_increase(self):
        self.ensure_one()
        return (
            self.change_type not in ("cancel", "quantity")
            and (self.new_amount or 0.0) > (self.old_amount or 0.0) + 0.005
        )

    def _fix_notice_exempt(self):
        self.ensure_one()
        return bool(self.notice_exemption and (self.notice_exemption_ref or "").strip())

    def _fix_notice_days(self):
        return _int_param(self.env, PARAM_PRICE_NOTICE_DAYS, DEFAULT_PRICE_NOTICE_DAYS)

    def _fix_applies_from(self):
        """The first day the change may apply; False while an increase still
        waits for its notice."""
        self.ensure_one()
        if not self._fix_is_increase() or self._fix_notice_exempt():
            return self.effective_date
        sent = _dhaka_date(self.env, self.notice_sent_at)
        if not sent:
            return False
        return max(self.effective_date, sent + datetime.timedelta(days=self._fix_notice_days()))

    def _fix_notice_satisfied(self, on_date=None):
        self.ensure_one()
        ready = self._fix_applies_from()
        day = on_date or fields.Date.context_today(self)
        return bool(ready) and self.effective_date >= ready and day >= ready

    @api.depends(
        "change_type",
        "new_amount",
        "old_amount",
        "effective_date",
        "notice_sent_at",
        "notice_exemption",
        "notice_exemption_ref",
    )
    def _compute_notice_state(self):
        for rec in self:
            rec.is_price_increase = rec._fix_is_increase()
            rec.price_applies_from = rec._fix_applies_from() if rec.effective_date else False

    # ---- input rules ---------------------------------------------------------------
    def _fix_refuse_forged_exemption(self, vals):
        if vals.get("notice_exemption") == "contract_amendment" and not self.env.su:
            raise UserError(
                "A signed contract amendment is recorded by the system from the contract's "
                "terms history; choose 'Customer requested the change' with its evidence."
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._fix_refuse_forged_exemption(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._fix_refuse_forged_exemption(vals)
        if self and not self._fix_guard_open() and NOTICE_INPUTS & set(vals):
            for rec in self.filtered(lambda r: r.state != "draft"):
                if any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in NOTICE_INPUTS & set(vals)
                ):
                    raise UserError(
                        "Proration %s is %s: its notice terms are fixed." % (rec.name, rec.state)
                    )
        return super().write(vals)

    @api.model
    def create_for_plan_change(
        self,
        subscription,
        new_amount,
        to_plan=None,
        effective_date=None,
        notice_exemption=None,
        notice_exemption_ref=None,
        notice_sent_on=None,
        notice_ref=None,
    ):
        rec = super().create_for_plan_change(
            subscription, new_amount, to_plan=to_plan, effective_date=effective_date
        )
        if notice_exemption:
            rec.write(
                {"notice_exemption": notice_exemption, "notice_exemption_ref": notice_exemption_ref}
            )
        if notice_sent_on and rec._fix_is_increase():
            # a renewal escalation whose notice the lifecycle request evidenced
            rec.sudo()._guarded().write(
                {
                    "notice_sent_at": fields.Datetime.to_datetime(notice_sent_on),
                    "notice_ref": (notice_ref or "lifecycle request")[:250],
                }
            )
        return rec

    # ---- sending the notice -----------------------------------------------------------
    def action_send_price_notice(self, channel=None, reference=None):
        """FR-SUB-022 / AUT-SUB-10: tell the customer, record it as evidence,
        and keep the new price out until the notice period has run."""
        require_role(self.env, SUB_OFFICER, "Sending a price-change notice")
        channel = channel or "email"
        if channel not in dict(NOTICE_CHANNELS):
            raise UserError("Unknown notice channel %s." % channel)
        today = fields.Date.context_today(self)
        days = self._fix_notice_days()
        for rec in self:
            if not rec._fix_is_increase():
                raise UserError("Proration %s does not raise the price: no notice." % rec.name)
            if rec.state not in ("draft", "pending", "approved") or rec.applied_to_subscription:
                raise UserError("Proration %s is %s: no notice to send." % (rec.name, rec.state))
            if rec.notice_sent_at:
                raise UserError(
                    "The customer was told about %s on %s." % (rec.name, rec.notice_sent_at)
                )
            sub = rec.subscription_id.sudo()
            earliest = today + datetime.timedelta(days=days)
            vals = {
                "notice_sent_at": fields.Datetime.now(),
                "notice_sent_by_id": self.env.uid,
                "notice_channel": channel,
            }
            if rec.effective_date < earliest:
                vals["effective_date"] = earliest
            body = (
                "Notice of a price change: the recurring charge of your subscription %s changes "
                "from %s %.2f to %s %.2f from %s (%d days' notice, BRU-SUB-07)."
                % (
                    sub.name,
                    sub.currency_id.name or "BDT",
                    rec.old_amount or 0.0,
                    sub.currency_id.name or "BDT",
                    rec.new_amount or 0.0,
                    vals.get("effective_date", rec.effective_date),
                    days,
                )
            )
            message = sub.message_post(
                body=body,
                partner_ids=sub.customer_id.ids,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
            vals["notice_ref"] = ((reference or "").strip() or "mail.message %s" % message.id)[:250]
            rec.sudo()._guarded().write(vals)
            if rec.state == "draft" and "effective_date" in vals:
                rec._proration_refresh()
            rec.message_post(body="Price notice sent (%s): %s" % (channel, body))
        return True

    # ---- applying: never before the notice has run -------------------------------------
    def _proration_apply_to_subscription(self):
        held = self.filtered(lambda r: r._fix_is_increase() and not r._fix_notice_satisfied())
        for rec in held:
            if not rec.notice_hold_noted:
                rec.message_post(
                    body="Approved, not applied: the price rises from %.2f to %.2f and the "
                    "customer must be given %d days' notice first (Send Price Notice; "
                    "BRU-SUB-07). It applies by itself once the notice has run."
                    % (rec.old_amount, rec.new_amount, rec._fix_notice_days())
                )
                rec.sudo()._guarded().write({"notice_hold_noted": True})
        return super(FixSubscriptionProrationNotice, self - held)._proration_apply_to_subscription()


# ==========================================================================
# M39-F17: usage ingestion
# ==========================================================================
USAGE_SOURCES = {
    "msp.usage_reported": "m05",
    "data.usage_reported": "m06",
    "rental.usage_reported": "m13",
}


class FixSubscriptionUsageIntake(models.AbstractModel):
    _name = "fix.subscription.usage.intake"
    _description = "M39: ingest metered usage (M05 / M06 / M13)"

    def _usage_subscription(self, payload):
        Sub = self.env["fix.subscription"].sudo()
        if payload.get("subscription_id"):
            sub = Sub.browse(int(payload["subscription_id"])).exists()
            if not sub:
                raise UserError(
                    "Usage refused: subscription %s does not exist." % payload["subscription_id"]
                )
            return sub
        contract_id = payload.get("contract_id")
        if not contract_id and payload.get("msp_contract_id") and "fix.msp.contract" in self.env:
            msp = (
                self.env["fix.msp.contract"].sudo().browse(int(payload["msp_contract_id"])).exists()
            )
            contract_id = msp.contract_id.id if msp else False
        if not contract_id:
            raise UserError("Usage refused: it names no subscription or contract to rate against.")
        subs = Sub.search(
            [("contract_id", "=", int(contract_id)), ("state", "not in", list(DEAD_STATES))]
        )
        if len(subs) != 1:
            raise UserError(
                "Usage refused: contract %s has %d live subscriptions (it is rated on exactly "
                "one); the delivery stays in the relay's queue (BRU-SUB-08)."
                % (contract_id, len(subs))
            )
        return subs

    def _usage_ingest(self, event, source):
        if not self.env.su:
            raise AccessError("Usage is ingested by the event relay only.")
        payload = event.get("payload") or {}
        key = str(payload.get("source_key") or event.get("event_id") or "").strip()
        if not key:
            raise UserError("Usage refused: no source key to de-duplicate it by (T-05).")
        sub = self._usage_subscription(payload)
        Usage = self.env["fix.subscription.usage"].sudo()
        existing = Usage.search(
            [
                ("subscription_id", "=", sub.id),
                ("source_module", "=", source),
                ("source_key", "=", key),
            ],
            limit=1,
        )
        if existing:
            return {"duplicate": True, "id": existing.id}
        try:
            qty = float(payload.get("quantity"))
            start = fields.Date.to_date(payload.get("period_start"))
            end = fields.Date.to_date(payload.get("period_end") or payload.get("period_start"))
        except (TypeError, ValueError):
            raise UserError("Usage refused: quantity and period are required.") from None
        metric = (payload.get("metric") or "").strip()
        if not metric or not start or not end:
            raise UserError("Usage refused: metric and period are required.")
        rec = Usage.create(
            {
                "subscription_id": sub.id,
                "metric": metric,
                "quantity": qty,
                "period_start": start,
                "period_end": end,
                "source_module": source,
                "source_key": key,
            }
        )
        return {"id": rec.id, "state": rec.state}

    @api.model
    def consume_msp_usage_reported(self, event):
        return self._usage_ingest(event, USAGE_SOURCES["msp.usage_reported"])

    @api.model
    def consume_data_usage_reported(self, event):
        return self._usage_ingest(event, USAGE_SOURCES["data.usage_reported"])

    @api.model
    def consume_rental_usage_reported(self, event):
        return self._usage_ingest(event, USAGE_SOURCES["rental.usage_reported"])


# ==========================================================================
# M39-F17: the service gate (suspension / pause / cancellation)
# ==========================================================================
GATE_EVENTS = {
    # event: (gate, subscription states the event must still be true of, why)
    "subscription.service_order_locked": ("closed", ("hold",), "suspended for non-payment"),
    "subscription.paused": ("closed", ("paused",), "paused"),
    "subscription.cancelled": ("closed", DEAD_STATES, "cancelled"),
    "subscription.cancel_applied": ("closed", DEAD_STATES, "cancelled"),
    "subscription.churned": ("closed", DEAD_STATES, "churned"),
    "subscription.reinstated": ("open", ("active", "trial", "past_due"), "reinstated"),
    "subscription.resumed": ("open", ("active", "trial", "past_due"), "resumed"),
}


class FixSubscriptionServiceGate(models.Model):
    _inherit = "fix.subscription"

    service_gate = fields.Selection(
        [("open", "Service Open"), ("closed", "Service Gated")],
        string="Service Gate",
        default="open",
        required=True,
        readonly=True,
        copy=False,
        help="Closed while the subscription is suspended, paused or ended: M01 warns or "
        "refuses new service under it (cd_subscription.suspended_service_policy).",
    )
    service_gate_reason = fields.Char(readonly=True, copy=False)
    service_gate_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "service_gate",
            "service_gate_reason",
            "service_gate_at",
        }

    @api.model
    def consume_service_gate_event(self, event):
        """Relay consumer of the suspension / pause / cancellation / resume
        events. The payload is a claim: the subscription's state is re-read."""
        if not self.env.su:
            raise AccessError("The service gate is moved by the event relay only.")
        spec = GATE_EVENTS.get(event.get("event_type"))
        if not spec:
            return {"skipped": "not a service gate event"}
        gate, states, why = spec
        sub = self.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not sub:
            raise UserError(
                "Service gate refused: subscription %s does not exist." % event.get("aggregate_id")
            )
        if sub.state not in states:
            return {"skipped": "subscription %s is %s" % (sub.name, sub.state)}
        if sub.service_gate == gate:
            return {"unchanged": gate}
        sub._guarded().write(
            {
                "service_gate": gate,
                "service_gate_reason": ("Subscription %s" % why) if gate == "closed" else False,
                "service_gate_at": fields.Datetime.now(),
            }
        )
        sub.message_post(
            body="Service gate %s: %s." % ("closed" if gate == "closed" else "reopened", why)
        )
        return {"gate": gate, "id": sub.id}

    # ---- M39-F11: one engine per contract -------------------------------------
    def _fix_assert_contract_engine(self, contract_ids):
        contracts = self.env["fix.contract"].sudo().browse(list(contract_ids)).exists()
        walker = contracts.filtered(
            lambda c: c.billing_engine != "subscription" and (c.annual_value or 0.0) > 0.0
        )
        if walker:
            raise UserError(
                "%s is billed by the M08 contract billing, so a subscription on it would bill "
                "the customer twice (M39-F11). A Contract Manager moves the contract to M39 "
                "(Billed By) before it is billed."
                % ", ".join(walker.mapped(lambda c: c.code or c.name))
            )

    # ---- M37-F5 (with R2-3): a subscription made from a plan definition ---------
    plan_def_id = fields.Many2one(
        "fix.subscription.plan.def",
        string="Plan Definition (M37)",
        index=True,
        ondelete="restrict",
        help="The catalogue plan this subscription was made from: its billing cycle comes "
        "from the plan, its price from the M11 rate card (channel 'subscription').",
    )

    def _fix_plan_vals(self, vals):
        """Cycle and VAT-exclusive per-cycle price of the plan in `vals`, when
        no amount was given explicitly. The plan hook refuses a plan with no
        released M11 price."""
        if not vals.get("plan_def_id") or vals.get("recurring_amount"):
            return vals
        plan = self.env["fix.subscription.plan.def"].browse(int(vals["plan_def_id"])).exists()
        if not plan:
            raise UserError("Plan definition %s does not exist." % vals["plan_def_id"])
        if not hasattr(plan, "_fix_subscription_vals"):
            raise UserError("The M11 plan pricing (cd_rate_card) is not installed.")
        partner = self.env["res.partner"].browse(vals.get("customer_id") or [])
        company = self.env["res.company"].browse(vals.get("company_id") or []) or self.env.company
        contract = self.env["fix.contract"].browse(vals.get("contract_id") or [])
        priced = plan._fix_subscription_vals(
            partner=partner or None,
            company=company,
            date=fields.Date.to_date(vals.get("start_date")) or fields.Date.context_today(self),
            contract=contract or None,
        )
        out = dict(vals, billing_cycle=priced["billing_cycle"])
        out["recurring_amount"] = priced["recurring_amount"]
        if priced.get("currency_id"):
            out["currency_id"] = priced["currency_id"]
        return out

    @api.model_create_multi
    def create(self, vals_list):
        self._fix_assert_contract_engine(
            {v["contract_id"] for v in vals_list if v.get("contract_id")}
        )
        vals_list = [self._fix_plan_vals(dict(v)) for v in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("contract_id"):
            self._fix_assert_contract_engine({vals["contract_id"]})
        if "plan_def_id" in vals and not self._fix_guard_open():
            for sub in self:
                if sub._fix_guard_differs("plan_def_id", vals["plan_def_id"], sub.plan_def_id):
                    raise UserError(
                        "The plan of %s is set when it is created; a plan change is an "
                        "approved proration." % sub.name
                    )
        return super().write(vals)

    @api.model
    def consume_contract_activated(self, event):
        """AUT-SUB-01, only for a contract billed by M39: its subscription
        (monthly, the annual value / 12, over the contract term)."""
        if not self.env.su:
            raise AccessError("The contract activation consumer runs only from the event relay.")
        contract = (
            self.env["fix.contract"].sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        )
        if not contract:
            raise UserError("Contract %s does not exist." % event.get("aggregate_id"))
        if contract.billing_engine != "subscription":
            return {"skipped": "billed by the M08 contract billing"}
        if contract.state not in ("active", "expiring"):
            return {"skipped": "contract is %s" % contract.state}
        live = self.sudo().search(
            [("contract_id", "=", contract.id), ("state", "not in", list(DEAD_STATES))], limit=1
        )
        if live:
            return {"existing": live.id}
        if (contract.annual_value or 0.0) <= 0.0:
            contract.message_post(
                body="Billed by M39, but the contract states no annual value: finance sets up "
                "its subscription."
            )
            return {"skipped": "no annual value"}
        ou = contract.operating_unit_id or self.env["operating.unit"].sudo().search(
            [("company_id", "=", contract.company_id.id)], limit=1
        )
        sub = self.sudo().create(
            {
                "name": "%s subscription" % (contract.code or contract.name),
                "company_id": contract.company_id.id,
                "operating_unit_id": ou.id,
                "customer_id": contract.customer_id.id,
                "contract_id": contract.id,
                "billing_cycle": "monthly",
                "currency_id": contract.currency_id.id,
                "recurring_amount": round(contract.annual_value / 12.0, 2),
                "start_date": contract.date_start,
                "next_invoice_date": contract.date_start,
                "contract_end_date": contract.date_end,
            }
        )
        sub.message_post(
            body="Created on the activation of contract %s, which M39 bills (AUT-SUB-01): "
            "monthly at the annual value / 12. Finance reviews it before the first run."
            % (contract.code or contract.name)
        )
        return {"created": sub.id}


class FixContractWalkerSkipsM39(models.Model):
    """The M08 walker leaves a contract billed by its M39 subscription alone."""

    _inherit = "fix.contract.billing.period"

    def _bill_contract(self, contract, today):
        if contract.billing_engine == "subscription":
            return 0
        return super()._bill_contract(contract, today)


class FixServiceOrderSubscriptionGate(models.Model):
    """M01 intake: new service under a gated subscription warns (default) or
    is refused (cd_subscription.suspended_service_policy = refuse)."""

    _inherit = "fix.service.order"

    def _fix_gated_subscriptions(self):
        self.ensure_one()
        Sub = self.env["fix.subscription"].sudo()
        if self.contract_id:
            domain = [("contract_id", "=", self.contract_id.id)]
        elif self.customer_id:
            partners = self.customer_id | self.customer_id.commercial_partner_id
            domain = [("customer_id", "in", partners.ids)]
        else:
            return Sub
        return Sub.search([*domain, ("service_gate", "=", "closed")])

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        policy = (
            self.env["ir.config_parameter"].sudo().get_param(PARAM_GATE_POLICY) or "warn"
        ).strip()
        for order in orders:
            gated = order._fix_gated_subscriptions()
            if not gated:
                continue
            why = "; ".join("%s (%s)" % (s.name, s.service_gate_reason or s.state) for s in gated)
            if policy == "refuse":
                raise UserError(
                    "Service is gated for this customer: %s. Finance reinstates the subscription "
                    "before new service is booked (M39-F17)." % why
                )
            order.message_post(
                body="Warning: the customer's subscription is gated (%s). Service is booked; "
                "check entitlement and payment before work starts." % why
            )
        return orders
