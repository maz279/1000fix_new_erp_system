# Customer notifications for the A05 circular-economy milestones (A05 ERP
# audit XC-20 / M13-26, 20 Nov 2026).
#
# The rental and trade-in modules raised their milestones and nobody told the
# customer: a rental due back tomorrow, a rental overdue (spec reminders at 1,
# 3 and 7 days), a trade-in offer issued with its expiry, a trade-in payout
# made. The M13 / M14 events (interface I5: rental.return_due, rental.overdue,
# tradein.offer_issued, tradein.paid) are published by those modules; M27
# chooses channel, language and timing. These R8 consumers queue an SMS, and
# an e-mail where the customer has an address, through the one exit,
# fix.notif.delivery.queue(), so consent, the BTRC curfew, the provider and
# the evidence row apply exactly as for the A02 messages; one event queues
# one message per channel (dedup key).
#
# The wording is in fix.cc.notif.template records (data/fix_a05_notif_
# templates.xml) with a Bengali body (DE-17), editable by a contact-centre
# supervisor without a code change. The A05 modules are not dependencies of
# the contact centre, so their records are read through the registry.
from odoo import api, models
from odoo.exceptions import ValidationError

# kind -> the template XML ids, per channel
_TEMPLATES = {
    "rental_return_due": (
        "cd_contact_centre.notif_tmpl_a05_rental_return_due_sms",
        "cd_contact_centre.notif_tmpl_a05_rental_return_due_email",
    ),
    "rental_overdue": (
        "cd_contact_centre.notif_tmpl_a05_rental_overdue_sms",
        "cd_contact_centre.notif_tmpl_a05_rental_overdue_email",
    ),
    "tradein_offer": (
        "cd_contact_centre.notif_tmpl_a05_tradein_offer_sms",
        "cd_contact_centre.notif_tmpl_a05_tradein_offer_email",
    ),
    "tradein_paid": (
        "cd_contact_centre.notif_tmpl_a05_tradein_paid_sms",
        "cd_contact_centre.notif_tmpl_a05_tradein_paid_email",
    ),
}
# Spec M13 (overdue handling, M13-26): the customer is reminded on the 1st,
# 3rd and 7th day overdue; the contact centre may change the days.
P_OVERDUE_DAYS = "cd_contact_centre.rental_overdue_notify_days"
DEFAULT_OVERDUE_DAYS = "1,3,7"


def _money(value):
    try:
        return f"{float(value or 0.0):,.2f}"
    except (TypeError, ValueError):
        return str(value or "")


def _day(value):
    return str(value or "")[:10]


class FixNotifDeliveryA05(models.Model):
    _inherit = "fix.notif.delivery"

    @api.model
    def _a05_record(self, model, rec_id):
        Model = self.env.get(model)
        if Model is None or not rec_id:
            return None
        try:
            return Model.sudo().browse(int(rec_id)).exists() or None
        except (TypeError, ValueError):
            return None

    @api.model
    def _a05_partner(self, payload, record, field="customer_id"):
        partner = self._a05_record("res.partner", payload.get("partner_id"))
        if partner:
            return partner
        return record[field] if record and field in record._fields and record[field] else None

    @api.model
    def _a05_notify(self, event, record, partner, kind, values, key):
        """Queue ``kind`` to ``partner`` by SMS, and by e-mail when the party
        has an address, once per event key; or say why not."""
        self._m01_assert_relay()
        if not partner:
            return {"queued": False, "reason": "no customer"}
        operating_unit = False
        if "operating_unit_id" in record._fields and record.operating_unit_id:
            operating_unit = record.operating_unit_id
        elif "branch_id" in record._fields and record.branch_id:
            operating_unit = record.branch_id.operating_unit_id
        out = {"queued": False, "delivery_ids": []}
        reasons = []
        for xmlid in _TEMPLATES[kind]:
            template = self.env.ref(xmlid, raise_if_not_found=False)
            if not template or not template.active:
                reasons.append("template %s missing or archived" % xmlid)
                continue
            if template.channel == "email" and not partner.email:
                continue  # e-mail is a second channel: no address, no e-mail
            try:
                delivery = self.queue(
                    channel=template.channel,
                    purpose="service_updates",
                    partner=partner,
                    template=template,
                    template_values=values,
                    lawful_basis="contract",
                    source_model=record._name,
                    source_id=record.id,
                    source_event_id=event.get("event_id"),
                    dedup_key="a05-notify:%s:%s:%s" % (kind, key, template.channel),
                    operating_unit=operating_unit,
                    company=record.company_id if "company_id" in record._fields else None,
                )
            except ValidationError as exc:
                # no phone / address on file is not worth retries and a dead letter
                reasons.append(str(exc))
                if hasattr(record, "message_post"):
                    record.message_post(body="Customer not notified (%s): %s" % (kind, exc))
                continue
            out["delivery_ids"].append(delivery.id)
            if delivery.state != "suppressed":
                out["queued"] = True
        if out["delivery_ids"]:
            out["delivery_id"] = out["delivery_ids"][0]
        if reasons:
            out["reason"] = "; ".join(reasons)
        return out

    # ------------------------------------------------------------------ M13
    @api.model
    def consume_rental_return_due(self, event: dict) -> dict:
        """The unit is due back (S1 cron at T-24h): remind the customer."""
        self._m01_assert_relay()
        payload = event.get("payload") or {}
        res = self._a05_record(
            "fix.rental.reservation", payload.get("reservation_id") or event.get("aggregate_id")
        )
        if not res or res.state not in ("delivered", "active"):
            return {"queued": False, "reason": "the rental is not out"}
        due = _day(payload.get("due_at") or res.date_to)
        return self._a05_notify(
            event,
            res,
            self._a05_partner(payload, res),
            "rental_return_due",
            {"ref": res.name, "due": due},
            "%s:%s" % (res.id, due),
        )

    @api.model
    def consume_rental_overdue(self, event: dict) -> dict:
        """Spec reminders on the 1st, 3rd and 7th day overdue (M13-26)."""
        self._m01_assert_relay()
        payload = event.get("payload") or {}
        res = self._a05_record(
            "fix.rental.reservation", payload.get("reservation_id") or event.get("aggregate_id")
        )
        if not res or res.state not in ("delivered", "active"):
            return {"queued": False, "reason": "the rental is not out"}
        try:
            days = int(payload.get("days_overdue") or 0)
        except (TypeError, ValueError):
            days = 0
        raw = (
            self.env["ir.config_parameter"].sudo().get_param(P_OVERDUE_DAYS) or DEFAULT_OVERDUE_DAYS
        )
        wanted = {int(x) for x in str(raw).replace(" ", "").split(",") if x.isdigit()}
        if days not in wanted:
            return {"queued": False, "reason": "day %d is not a reminder day" % days}
        return self._a05_notify(
            event,
            res,
            self._a05_partner(payload, res),
            "rental_overdue",
            {"ref": res.name, "days": days, "due": _day(res.date_to)},
            "%s:%s" % (res.id, days),
        )

    # ------------------------------------------------------------------ M14
    @api.model
    def consume_tradein_offer_issued(self, event: dict) -> dict:
        self._m01_assert_relay()
        payload = event.get("payload") or {}
        req = self._a05_record(
            "fix.tradein.request", payload.get("tradein_id") or event.get("aggregate_id")
        )
        if not req or req.state == "rejected":
            return {"queued": False, "reason": "no live trade-in"}
        amount = payload.get("amount")
        if amount in (None, ""):
            amount = req.offered_value
        valid = _day(payload.get("valid_until")) or "-"
        return self._a05_notify(
            event,
            req,
            self._a05_partner(payload, req),
            "tradein_offer",
            {"ref": req.name, "amount": _money(amount), "valid_until": valid},
            "%s:%s:%s" % (req.id, _money(amount), valid),
        )

    @api.model
    def consume_tradein_paid(self, event: dict) -> dict:
        self._m01_assert_relay()
        payload = event.get("payload") or {}
        req = self._a05_record(
            "fix.tradein.request", payload.get("tradein_id") or event.get("aggregate_id")
        )
        if not req:
            return {"queued": False, "reason": "no trade-in"}
        amount = payload.get("amount")
        if amount in (None, ""):
            amount = payload.get("payout")
        if amount in (None, ""):
            amount = req.net_payout
        return self._a05_notify(
            event,
            req,
            self._a05_partner(payload, req),
            "tradein_paid",
            {"ref": req.name, "amount": _money(amount)},
            "%s" % req.id,
        )
