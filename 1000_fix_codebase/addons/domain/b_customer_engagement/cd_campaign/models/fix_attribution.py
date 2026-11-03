# M35 — multi-touch attribution.
#
# WHAT WAS HERE BEFORE. The ROI pack divided campaign spend by response
# count, which is single-touch attribution by accident: whichever campaign
# happened to own the response row got all the credit, and a customer who saw
# three campaigns before buying credited exactly one of them. The dossier was
# honest that attributed revenue was a declared gap and never estimated it.
#
# WHAT THIS ADDS. A touchpoint ledger and five attribution models over it.
# The ledger is the part that matters: attribution models are arithmetic, and
# arithmetic over no data is where invented numbers come from. So touches are
# RECORDED — from campaign sends (the S1 delivery log already knows every
# message that went out), from responses, and from conversions.
#
# One deliberate limitation, stated rather than papered over: a conversion's
# VALUE comes from the response record, and fix.campaign.response has no
# order-value key. So revenue attribution returns None where value is unknown
# instead of estimating it, and the conversion COUNT attribution — which is
# fully supported by the data — is reported separately. A split credit over
# an unknown total is still unknown.
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

TOUCH_TYPES = [
    ("send", "Message sent"),
    ("open", "Message opened"),
    ("click", "Link clicked"),
    ("response", "Responded"),
    ("conversion", "Converted"),
]

ATTRIBUTION_MODELS = [
    ("last_touch", "Last touch — all credit to the final touch"),
    ("first_touch", "First touch — all credit to the first touch"),
    ("linear", "Linear — credit split evenly"),
    ("time_decay", "Time decay — later touches weighted more"),
    ("position", "Position-based — 40/20/40 first, middle, last"),
]

# Half-life for time decay, in days. A touch twice this old carries a quarter
# of the weight of one today.
TIME_DECAY_HALF_LIFE_DAYS = 7

# How far back a touch may be and still be credited for a conversion. Beyond
# this the connection is not evidence, it is coincidence.
DEFAULT_LOOKBACK_DAYS = 90


class FixCampaignTouch(models.Model):
    """One recorded interaction between a party and a campaign."""

    _name = "fix.campaign.touch"
    _description = "Campaign Touchpoint"
    _order = "occurred_at desc, id desc"
    _rec_name = "display_label"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    campaign_id = fields.Many2one("fix.campaign", required=True, ondelete="cascade", index=True)
    partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade", index=True)
    touch_type = fields.Selection(TOUCH_TYPES, required=True, default="send", index=True)
    channel = fields.Char(index=True)
    occurred_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    delivery_id = fields.Many2one(
        "fix.notif.delivery",
        string="Delivery Row",
        ondelete="set null",
        help="The S1 message this touch came from, when it came from one. "
        "That log is why the ledger can be populated from real sends rather "
        "than from an assumption about who was reached.",
    )
    response_id = fields.Many2one("fix.campaign.response", string="Response", ondelete="set null")
    value_bdt = fields.Monetary(
        currency_field="currency_id",
        help="Conversion value, when it is known. Left at zero rather than "
        "estimated; value_known says which.",
    )
    value_known = fields.Boolean(
        default=False,
        help="False means no order value was available for this conversion. "
        "Revenue attribution reports None rather than splitting a guess.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    display_label = fields.Char(compute="_compute_display_label", store=True)
    source_key = fields.Char(
        index=True,
        help="Idempotency key, so replaying the send log does not double-count " "a touch.",
    )

    _source_unique = models.Constraint(
        "UNIQUE (source_key)", "That touchpoint has already been recorded."
    )

    @api.depends("campaign_id", "partner_id", "touch_type")
    def _compute_display_label(self):
        for rec in self:
            rec.display_label = "%s · %s · %s" % (
                rec.campaign_id.name or "?",
                rec.partner_id.name or "?",
                rec.touch_type or "?",
            )

    # ------------------------------------------------------------------
    # Ledger population
    # ------------------------------------------------------------------
    @api.model
    def record(
        self,
        campaign,
        partner,
        touch_type,
        occurred_at=None,
        delivery=None,
        response=None,
        value_bdt=None,
        channel=None,
        source_key=None,
    ):
        """Record one touch, idempotently."""
        key = source_key or "%s:%s:%s:%s" % (
            getattr(campaign, "id", campaign),
            getattr(partner, "id", partner),
            touch_type,
            (occurred_at or fields.Datetime.now()),
        )
        existing = self.sudo().search([("source_key", "=", key)], limit=1)
        if existing:
            return existing
        return self.sudo().create(
            {
                "campaign_id": getattr(campaign, "id", campaign),
                "partner_id": getattr(partner, "id", partner),
                "touch_type": touch_type,
                "occurred_at": occurred_at or fields.Datetime.now(),
                "delivery_id": getattr(delivery, "id", delivery) or False,
                "response_id": getattr(response, "id", response) or False,
                "value_bdt": value_bdt or 0.0,
                "value_known": value_bdt is not None,
                "channel": channel or "",
                "source_key": key,
            }
        )

    @api.model
    def cron_harvest_from_delivery_log(self, days=7, limit=5000):
        """Turn S1 delivery rows into send touches.

        This is the join the estate could not previously make: before S1
        there was no record of an individual message, so there was nothing to
        build a touch ledger from. Only SENT and DELIVERED rows count — a
        suppressed message reached nobody and must not earn attribution
        credit.
        """
        Delivery = self.env["fix.notif.delivery"].sudo()
        since = fields.Datetime.subtract(fields.Datetime.now(), days=days)
        rows = Delivery.search(
            [
                ("state", "in", ("sent", "delivered")),
                ("purpose", "=", "marketing"),
                ("partner_id", "!=", False),
                ("sent_at", ">=", since),
                ("source_model", "in", ("fix.campaign", "fix.campaign.journey.member")),
            ],
            limit=limit,
        )
        created, failed = 0, 0
        for row in rows:
            # One row per savepoint (A03 audit §4.7 step 8, cron 52): a single
            # unrecordable row, such as one whose touch a concurrent run has
            # just inserted, used to fail the whole daily job.
            try:
                with self.env.cr.savepoint():
                    campaign = self._campaign_for_delivery(row)
                    if not campaign:
                        continue
                    touch = self.record(
                        campaign,
                        row.partner_id,
                        "send",
                        occurred_at=row.sent_at,
                        delivery=row,
                        channel=row.channel,
                        source_key="delivery:%d" % row.id,
                    )
            except Exception as exc:  # one row must not stop the harvest
                failed += 1
                _logger.warning("touch harvest skipped delivery %s: %s", row.id, exc)
                continue
            if touch.create_date and touch.create_date >= since:
                created += 1
        return {"delivery_rows": len(rows), "touches": created, "failed": failed}

    @api.model
    def _campaign_for_delivery(self, delivery):
        """Which campaign a delivery row belongs to."""
        if delivery.source_model == "fix.campaign":
            return self.env["fix.campaign"].sudo().browse(delivery.source_id).exists()
        if delivery.source_model == "fix.campaign.journey.member":
            member = (
                self.env["fix.campaign.journey.member"].sudo().browse(delivery.source_id).exists()
            )
            return member.journey_id.campaign_id if member else None
        return None

    # ------------------------------------------------------------------
    # Attribution
    # ------------------------------------------------------------------
    @api.model
    def _weights(self, touches, model):
        """Credit weights summing to 1.0 over an ordered touch list."""
        count = len(touches)
        if count == 0:
            return []
        if model == "last_touch":
            return [0.0] * (count - 1) + [1.0]
        if model == "first_touch":
            return [1.0] + [0.0] * (count - 1)
        if model == "linear":
            return [1.0 / count] * count
        if model == "time_decay":
            latest = touches[-1].occurred_at
            raw = []
            for touch in touches:
                age_days = max(0.0, (latest - touch.occurred_at).total_seconds() / 86400.0)
                raw.append(0.5 ** (age_days / TIME_DECAY_HALF_LIFE_DAYS))
            total = sum(raw) or 1.0
            return [value / total for value in raw]
        if model == "position":
            if count == 1:
                return [1.0]
            if count == 2:
                return [0.5, 0.5]
            middle = [0.20 / (count - 2)] * (count - 2)
            return [0.4, *middle, 0.4]
        raise ValidationError("Unknown attribution model %r." % model)

    @api.model
    def attribute(
        self, model="position", date_from=None, date_to=None, lookback_days=DEFAULT_LOOKBACK_DAYS
    ):
        """Credit conversions across the campaigns that touched each party.

        Returns one row per campaign with the attributed conversion count,
        the attributed revenue where value is known, and — separately — how
        many of its credited conversions had NO known value. That third
        number is the honesty of the first two: a campaign credited with 40
        conversions of which 38 have unknown value has not been shown to have
        produced revenue.
        """
        domain = [("touch_type", "=", "conversion")]
        if date_from:
            domain.append(("occurred_at", ">=", date_from))
        if date_to:
            domain.append(("occurred_at", "<=", date_to))
        conversions = self.sudo().search(domain, order="occurred_at")
        rows = {}
        unattributed = 0

        for conversion in conversions:
            window_start = conversion.occurred_at - timedelta(days=lookback_days)
            journey = self.sudo().search(
                [
                    ("partner_id", "=", conversion.partner_id.id),
                    ("touch_type", "in", ("send", "open", "click", "response")),
                    ("occurred_at", ">=", window_start),
                    ("occurred_at", "<=", conversion.occurred_at),
                ],
                order="occurred_at",
            )
            if not journey:
                # A conversion with no preceding touch is not attributable to
                # anything, and spreading it over all campaigns would be
                # inventing a cause.
                unattributed += 1
                continue
            weights = self._weights(journey, model)
            for touch, weight in zip(journey, weights, strict=False):
                bucket = rows.setdefault(
                    touch.campaign_id.id,
                    {
                        "campaign_id": touch.campaign_id.id,
                        "campaign": touch.campaign_id.name,
                        "channel": touch.campaign_id.channel,
                        "budget": touch.campaign_id.budget or 0.0,
                        "touches": 0,
                        "attributed_conversions": 0.0,
                        "attributed_revenue": 0.0,
                        "conversions_without_value": 0,
                    },
                )
                bucket["touches"] += 1
                bucket["attributed_conversions"] += weight
                if conversion.value_known:
                    bucket["attributed_revenue"] += weight * (conversion.value_bdt or 0.0)
                else:
                    bucket["conversions_without_value"] += 1

        out = []
        for bucket in rows.values():
            bucket["attributed_conversions"] = round(bucket["attributed_conversions"], 2)
            bucket["attributed_revenue"] = round(bucket["attributed_revenue"], 2)
            known = bucket["attributed_conversions"] and (bucket["conversions_without_value"] == 0)
            bucket["revenue_basis"] = (
                "complete" if known else "partial — some conversions have no value on file"
            )
            bucket["cost_per_attributed_conversion"] = (
                round(bucket["budget"] / bucket["attributed_conversions"], 2)
                if bucket["attributed_conversions"]
                else None
            )
            # ROAS is only reported when every credited conversion had a
            # value. A ratio over a partially-unknown numerator is not a
            # ratio anyone should plan with.
            bucket["roas"] = (
                round(bucket["attributed_revenue"] / bucket["budget"], 2)
                if known and bucket["budget"]
                else None
            )
            out.append(bucket)
        out.sort(key=lambda r: -r["attributed_conversions"])
        return {
            "model": model,
            "lookback_days": lookback_days,
            "conversions": len(conversions),
            "unattributed_conversions": unattributed,
            "rows": out,
        }

    @api.model
    def model_comparison(self, date_from=None, date_to=None):
        """The same conversions under all five models, side by side.

        Worth having because attribution model choice moves credit between
        campaigns substantially, and a single model presented alone reads as
        a fact rather than as a choice.
        """
        comparison = {}
        for model, _label in ATTRIBUTION_MODELS:
            result = self.attribute(model=model, date_from=date_from, date_to=date_to)
            for row in result["rows"]:
                entry = comparison.setdefault(
                    row["campaign_id"],
                    {"campaign": row["campaign"], "channel": row["channel"]},
                )
                entry[model] = row["attributed_conversions"]
        return sorted(comparison.values(), key=lambda r: r["campaign"] or "")
