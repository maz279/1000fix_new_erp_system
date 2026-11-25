# M39 bills an MSP fee change (A02 ERP audit M05-F4 / owner item O14, 20 Nov 2026;
# A02 ERP pass 2 M05-S05 / S06 / S07, owner decision D8).
#
# The MSP recurring charge is the M39 subscription on the same M08 contract;
# the price master is the M05 contract's terms (D8). Every commercial
# amendment of an MSP contract (covered devices up OR down, per-device price)
# is recorded in its terms history (fix.msp.terms.amendment) with the monthly
# fee delta, and published as msp.commercial_terms_amended. This consumer
# turns the amendments not yet billed into price changes of the subscription,
# ONE PER EFFECTIVE DATE applied in sequence (owner decision, 21 Nov 2026),
# through M39's own controlled path (a draft proration routed for approval:
# never applied by its requester).
#
# Pass 2 fixed how uplifts were lost or overwritten (M05-S05):
#   * the consumer refused an event whose device count was not the contract's
#     CURRENT count, so of two quick amendments (50 -> 60 -> 80) the first was
#     refused and its 10 devices never billed. The amount now comes from the
#     terms history rows, so delivery order does not matter;
#   * each event asked for "recurring amount + its own delta", so two changes
#     waiting for approval both started from the same amount and the second
#     approval overwrote the first. A change still waiting is superseded by
#     one covering every unbilled amendment, and a proration is applied only
#     while the subscription still has the amount it was computed from
#     (fix_subscription_ops).
#
# msp.client_offboarded (M05-S07): the offboarded client's subscription churns.
#
# Relay-only (superuser) like every hand-back consumer. cd_subscription does
# not depend on cd_msp_contract: the M05 records are reached by model name,
# and without M05 there is nothing to bill.
from odoo import SUPERUSER_ID, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

CYCLE_MONTHS = {"monthly": 1, "quarterly": 3, "annual": 12}
MARKER = "MSP fee change"
LIVE = ("cancelled", "churned")
AMENDMENT_REF = "fix.subscription.proration,%s"


class FixSubscriptionMspUplift(models.AbstractModel):
    _name = "fix.subscription.msp.uplift"
    _description = "M39: bill an MSP fee change"

    def _msp_assert_relay(self):
        if not self.env.su:
            raise AccessError("Only the event relay turns an MSP fee change into a price change.")

    def _msp_contract(self, event):
        payload = event.get("payload") or {}
        msp_id = int(event.get("aggregate_id") or payload.get("msp_contract_id") or 0)
        msp = self.env["fix.msp.contract"].sudo().browse(msp_id).exists()
        if not msp:
            raise UserError("MSP fee change refused: MSP contract %s does not exist." % msp_id)
        return msp

    def _msp_live_subscriptions(self, msp):
        return (
            self.env["fix.subscription"]
            .sudo()
            .search([("contract_id", "=", msp.contract_id.id), ("state", "not in", LIVE)])
        )

    @api.model
    def consume_msp_commercial_terms_amended(self, event: dict) -> dict:
        self._msp_assert_relay()
        if "fix.msp.terms.amendment" not in self.env:
            return {"skipped": "M05 not installed"}
        msp = self._msp_contract(event)
        payload = event.get("payload") or {}
        amendment = (
            self.env["fix.msp.terms.amendment"]
            .sudo()
            .browse(int(payload.get("amendment_id") or 0))
            .exists()
        )
        if not amendment or amendment.msp_contract_id != msp:
            raise UserError(
                "MSP fee change refused: amendment %s is not a terms change of %s."
                % (payload.get("amendment_id"), msp.name)
            )
        return self._msp_bill_pending(msp)

    @api.model
    def consume_msp_device_uplift(self, event: dict) -> dict:
        """The pre-pass-2 event (still in the outbox on a live server): the
        contract's unbilled amendments are billed the same way.

        A02 pass-2 review: a pre-pass-2 uplift has no terms history row (the
        history did not exist when it was published), so it found "nothing
        new to bill" and its devices were never billed. Its row is recorded
        from the event first (once per event), then billed."""
        self._msp_assert_relay()
        if "fix.msp.terms.amendment" not in self.env:
            return {"skipped": "M05 not installed"}
        msp = self._msp_contract(event)
        self._msp_record_legacy_uplift(msp, event)
        return self._msp_bill_pending(msp)

    # the terms an amendment row carries besides the fee (copied from the
    # terms in force, so the SLA measured from the history does not move)
    _MSP_SLA_TERMS = (
        "sla_target_pct",
        "alert_resolve_hours_major",
        "alert_resolve_hours_minor",
        "response_hours_major",
        "response_hours_minor",
        "coverage_window",
        "holiday_calendar_id",
        "parts_included",
        "remote_hours_monthly",
        "overage_hourly_rate",
    )

    def _msp_record_legacy_uplift(self, msp, event):
        payload = event.get("payload") or {}
        if payload.get("amendment_id"):
            return False  # a pass-2 event names its own row
        try:
            old = int(payload.get("old_device_count") or 0)
            new = int(payload.get("new_device_count") or 0)
            added = int(payload.get("added_devices") or 0)
            rate = float(payload.get("per_device_monthly") or 0.0)
        except (TypeError, ValueError):
            return False
        if added <= 0 or new != old + added or rate <= 0:
            return False
        marker = "legacy msp.device_uplift event %s" % (
            event.get("event_id") or event.get("id") or "%s:%s->%s" % (msp.id, old, new)
        )
        Amendment = self.env["fix.msp.terms.amendment"].sudo()._guarded()
        if Amendment.search_count(
            [("msp_contract_id", "=", msp.id), ("reason", "=like", marker + "%")]
        ):
            return False
        try:
            effective = fields.Date.to_date(payload.get("effective_date")) or fields.Date.today()
        except (TypeError, ValueError):
            effective = fields.Date.today()
        terms = msp._msp_terms_at(effective)
        vals = {}
        for name in self._MSP_SLA_TERMS:
            value = terms[name]
            vals[name] = value.id if isinstance(value, models.BaseModel) else value
        Amendment.create(
            dict(
                vals,
                msp_contract_id=msp.id,
                company_id=msp.company_id.id,
                operating_unit_id=msp.operating_unit_id.id or False,
                kind="amendment",
                effective_date=effective,
                reason=("%s: %s" % (marker, payload.get("reason") or ""))[:250],
                device_count_before=old,
                device_count=new,
                per_device_monthly_before=rate,
                per_device_monthly=rate,
                monthly_value_before=round(old * rate, 2),
                monthly_value=round(new * rate, 2),
                billing_state="pending",
            )
        )
        return True

    def _msp_bill_pending(self, msp):
        """The next price change for the amendments of ``msp`` not yet billed:
        ONE PRORATION PER EFFECTIVE DATE, oldest first (owner decision,
        21 Nov 2026).

        One proration carries one effective date. Batching every unbilled
        amendment into one prorated them all from the EARLIEST date, so an
        uplift dated the 20th was charged from the 10th as well. Now the
        amendments sharing the earliest date are billed together, prorated
        from that date; the later ones wait, and are billed when that change
        is decided (applied, rejected or voided: _msp_bill_next), from the
        amount it left on the subscription. Each amendment is thus charged
        from its own date and on the price in force then, exactly once.

        An in-flight change is superseded (voided, its amendments billed
        again) when the earliest unbilled date gains an amendment, or an
        amendment dated before it arrives; a change for a later date never
        touches it."""
        Amendment = self.env["fix.msp.terms.amendment"].sudo()._guarded()
        Proration = self.env["fix.subscription.proration"].sudo()
        rows = Amendment.search(
            [("msp_contract_id", "=", msp.id), ("billing_state", "in", ("pending", "requested"))],
            order="effective_date, id",
        )
        # a requested change whose proration is no longer in flight: billed
        # when it was approved; flagged when a person voided or rejected it
        # (finance decided; the reconciliation report shows the difference)
        in_flight = Proration
        for row in rows.filtered(lambda r: r.billing_state == "requested"):
            pro = self._msp_proration_of(row)
            if pro and pro.state in ("draft", "pending"):
                in_flight |= pro
            elif pro and pro.state in ("approved", "invoiced"):
                row.write({"billing_state": "billed"})
            else:
                row.write(
                    {
                        "billing_state": "flagged",
                        "billing_note": "Its price change was voided or rejected in M39.",
                    }
                )
        rows = rows.filtered(lambda r: r.billing_state in ("pending", "requested"))
        if not rows.filtered(lambda r: r.billing_state == "pending"):
            return {"created": False, "reason": "nothing new to bill"}
        first = min(rows.mapped("effective_date"))
        group = rows.filtered(lambda r: r.effective_date == first)
        covered = rows.filtered(lambda r: r.billing_state == "requested")
        later = rows - group
        waiting_note = "Billed after the change from %s is decided." % first
        if in_flight and covered == group:
            # the change for the earliest date is already with its approver;
            # the later amendments follow once it is decided
            later.write({"billing_note": waiting_note})
            return {"created": False, "reason": "waiting for the change from %s" % first}
        subs = self._msp_live_subscriptions(msp)
        if len(subs) != 1:
            note = (
                "the M08 contract has %d live M39 subscriptions; finance bills it on the right one"
                % len(subs)
            )
            rows.filtered(lambda r: r.billing_state == "pending").write(
                {"billing_state": "flagged", "billing_note": note[:250]}
            )
            msp.message_post(
                body="MSP fee change of BDT %.2f a month not billed automatically: %s."
                % (sum(rows.mapped("monthly_delta")), note)
            )
            return {"skipped": "%d subscriptions" % len(subs)}
        sub = subs
        for pro in in_flight:
            # superseded: the earliest date changed (a new amendment on it, or
            # one dated before it); its amendments are billed again
            pro._approval_void("superseded by a later MSP fee change")
            pro._guarded().write({"state": "void", "approval_state": "none"})
            pro.message_post(body="Voided: superseded by a later MSP fee change of %s." % msp.name)
        (covered - group).write({"billing_state": "pending", "billing_ref": False})
        months = CYCLE_MONTHS.get(sub.billing_cycle, 1)
        delta = round(sum(group.mapped("monthly_delta")), 2)
        new_amount = round(max((sub.recurring_amount or 0.0) + delta * months, 0.0), 2)
        if new_amount <= 0.005:
            # A02 pass-2 review: a price change to 0 is an M39 'cancel', and
            # an approved cancel changes no price, so the fee kept billing.
            # Ending the subscription is finance's decision in M39.
            note = (
                "the monthly fee falls to BDT 0: a price change cannot end the subscription; "
                "finance cancels %s in M39" % sub.name
            )
            group.write({"billing_state": "flagged", "billing_note": note[:250]})
            msp.message_post(body="MSP fee change not billed automatically: %s." % note)
            return {"skipped": "fee falls to 0"}
        effective = max(first, sub.start_date or fields.Date.today())
        reason = "%s of %s (%s): BDT %+.2f a month - %s" % (
            MARKER,
            msp.name,
            ", ".join("terms #%s from %s" % (r.id, r.effective_date) for r in group),
            delta,
            "; ".join(r.reason or "" for r in group)[:200],
        )
        # A04 ERP round 2 M39-F16: the client signed these terms amendments;
        # that is the notice of the fee change (set by the system only)
        proration = Proration.create_for_plan_change(
            sub,
            new_amount,
            effective_date=effective,
            notice_exemption="contract_amendment",
            notice_exemption_ref=("MSP terms %s" % ", ".join("#%s" % r.id for r in rows))[:250],
        )
        proration.action_request_approval(justification=reason)
        group.write(
            {
                "billing_state": "requested",
                "billing_ref": AMENDMENT_REF % proration.id,
                "billing_note": False,
            }
        )
        later.write({"billing_note": waiting_note})
        sub.message_post(body=reason)
        return {
            "model": sub._name,
            "id": sub.id,
            "created": True,
            "new_amount": new_amount,
            "proration_id": proration.id,
            "waiting": len(later),
        }

    @api.model
    def _msp_bill_next(self, msps):
        """After a change is decided, the next date's amendments of each MSP
        contract are billed, by the system (the approver of one change does
        not raise the next). A failure is noted and never undoes the
        decision."""
        system = self.env(user=SUPERUSER_ID, su=True)["fix.subscription.msp.uplift"]
        for msp in msps:
            try:
                with self.env.cr.savepoint():
                    system._msp_bill_pending(msp.with_env(system.env))
            except (UserError, ValidationError) as exc:
                msp.sudo().message_post(
                    body="The next MSP fee change was not billed automatically: %s" % exc
                )

    def _msp_proration_of(self, row):
        ref = row.billing_ref or ""
        if not ref.startswith("fix.subscription.proration,"):
            return self.env["fix.subscription.proration"]
        return (
            self.env["fix.subscription.proration"]
            .sudo()
            .browse(int(ref.split(",")[1] or 0))
            .exists()
        )

    @api.model
    def consume_msp_client_offboarded(self, event: dict) -> dict:
        """M05-S07: an offboarded client's MSP subscription churns (billing
        stops; outstanding balances ride the M20 collections ladder)."""
        self._msp_assert_relay()
        if "fix.msp.contract" not in self.env:
            return {"skipped": "M05 not installed"}
        msp = self._msp_contract(event)
        if msp.lifecycle != "offboarded":
            raise UserError("MSP offboarding refused: %s is not offboarded." % msp.name)
        churned = 0
        for sub in self._msp_live_subscriptions(msp):
            sub._guarded().write({"state": "churned", "cancelled_on": fields.Date.today()})
            sub.message_post(
                body="Churned: the MSP client of %s was offboarded (%s)."
                % (msp.name, msp.offboarded_at)
            )
            publish(
                self.env,
                "subscription.churned",
                "fix.subscription",
                sub.id,
                {"reason": "msp_offboarded", "msp_contract_id": msp.id},
            )
            churned += 1
        return {"churned": churned}


class FixSubscriptionProrationMsp(models.Model):
    """When an MSP fee change is decided (applied, rejected or voided), the
    next date's amendments of its contract are billed: one proration per
    effective date, in sequence."""

    _inherit = "fix.subscription.proration"

    def _msp_contracts(self):
        Amendment = self.env.get("fix.msp.terms.amendment")
        if Amendment is None or not self:
            return None
        rows = Amendment.sudo().search(
            [("billing_ref", "in", [AMENDMENT_REF % rec.id for rec in self])]
        )
        return rows.mapped("msp_contract_id")

    def _msp_bill_next(self, msps):
        if msps:
            self.env["fix.subscription.msp.uplift"]._msp_bill_next(msps)

    def _proration_apply_to_subscription(self):
        msps = self._msp_contracts()
        result = super()._proration_apply_to_subscription()
        self._msp_bill_next(msps)
        return result

    def _approval_on_rejected(self, comment):
        msps = self._msp_contracts()
        result = super()._approval_on_rejected(comment)
        self._msp_bill_next(msps)
        return result

    def action_void(self):
        msps = self._msp_contracts()
        result = super().action_void()
        self._msp_bill_next(msps)
        return result
