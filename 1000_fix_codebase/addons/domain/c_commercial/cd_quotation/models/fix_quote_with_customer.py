# M36 customer approval loop (capture audit 2026-11-14).
#
# The workspace had no page that captured the customer side of a quotation:
#   * no quotation recorded the channel it reached the customer on, so
#     "Quote Conversion by Channel" could only group by state (FR-QTE-033/039);
#   * a counter-offer or a line-level partial acceptance had no record at all
#     (FR-QTE-035/036, BRU-QTE-11, AUT-QTE-08);
#   * a decline published an event nobody consumes, so the device return and
#     the diagnostic fee owed were nobody's task (FR-QTE-041, BRU-QTE-12).
#
# fix.quotation.delivery   one row per delivery / re-send of an issued version
# fix.quotation.counter    the customer's counter-offer or partial acceptance,
#                          decided by someone other than whoever took it down;
#                          "revise" makes the next version, which goes through
#                          the value-band approval like any other
# fix.quotation (extended) issue with a channel, the signed copy as an upload,
#                          a wrong acceptance code reported as a warning, and
#                          the decline follow-up on the service order
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.exceptions import UserError, ValidationError

# FR-QTE-033: the channels a quotation reaches the customer on.
CHANNELS = [
    ("portal", "Customer portal"),
    ("app", "Mobile app"),
    ("whatsapp", "WhatsApp"),
    ("sms", "SMS link"),
    ("email", "Email"),
    ("counter", "Printed counter copy"),
    ("onsite", "On-site technician device"),
    ("phone", "Phone call"),
]
PHONE_CHANNELS = ("whatsapp", "sms", "phone")

# What a delivery row lets you change after it was recorded: what happened to
# the message afterwards. What was sent, when, how and to whom is fixed.
DELIVERY_TRACKING = frozenset({"delivered_at", "first_viewed_at", "view_count", "note"})

COUNTER_KINDS = [
    ("counter", "Counter-offer (price or terms)"),
    ("partial", "Partial acceptance (some lines only)"),
]
COUNTER_STATES = [
    ("requested", "Awaiting decision"),
    ("revised", "Revised into a new version"),
    ("rejected", "Rejected: the quotation stands"),
]
COUNTER_DECISIONS = [
    ("revise", "Revise the quotation to these terms"),
    ("reject", "Reject: the quotation stands as issued"),
]
# Open to change while the counter awaits its decision.
COUNTER_EDITABLE = frozenset({"customer_request", "requested_value", "evidence_ref", "channel"})


def _changed(records, vals):
    """The fields of `vals` that would change one of `records`. The workspace
    form sends every field it shows on save; an unchanged value is no edit."""
    out = set()
    for name, value in vals.items():
        field = records._fields.get(name)
        if field is None:
            out.add(name)
            continue
        for rec in records:
            current = rec[name]
            if field.type == "many2one":
                new = value.get("id") if isinstance(value, dict) else value
                if (current.id or False) != (int(new) if new else False):
                    out.add(name)
            elif field.type in ("one2many", "many2many"):
                out.add(name)
            elif field.type == "datetime":
                # the form shows minutes: a re-sent value may lose its seconds
                new = fields.Datetime.to_datetime(value)
                if bool(new) != bool(current) or (
                    new and abs((new - current).total_seconds()) >= 60
                ):
                    out.add(name)
            elif field.type == "date":
                if fields.Date.to_date(value) != current:
                    out.add(name)
            elif field.type in ("float", "monetary"):
                if abs((current or 0.0) - float(value or 0.0)) > 0.005:
                    out.add(name)
            elif (current or False) != (value or False):
                out.add(name)
    return out


class FixQuotationDelivery(models.Model):
    _name = "fix.quotation.delivery"
    _description = "Quotation Delivery (channel, delivery and view tracking)"
    _order = "sent_at desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    quotation_id = fields.Many2one(
        "fix.quotation",
        required=True,
        ondelete="cascade",
        index=True,
        domain=[("state", "=", "sent")],
    )
    company_id = fields.Many2one(related="quotation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="quotation_id.operating_unit_id", store=True, index=True
    )
    customer_id = fields.Many2one(
        "res.partner", related="quotation_id.customer_id", store=True, string="Customer"
    )
    version = fields.Integer(readonly=True)
    channel = fields.Selection(CHANNELS, required=True)
    recipient = fields.Char(help="The number, address or person it went to.")
    delivery_ref = fields.Char(string="Message / Delivery Ref")
    sent_at = fields.Datetime(required=True, default=fields.Datetime.now)
    delivered_at = fields.Datetime()
    first_viewed_at = fields.Datetime(string="First Viewed At")
    view_count = fields.Integer(string="Views")
    note = fields.Char()
    recorded_by_id = fields.Many2one(
        "res.users", string="Recorded By", readonly=True, default=lambda self: self.env.user
    )

    @api.depends("quotation_id.name", "version", "channel")
    def _compute_name(self):
        labels = dict(CHANNELS)
        for rec in self:
            rec.name = "%s v%s · %s" % (
                rec.quotation_id.name or "",
                rec.version or rec.quotation_id.version or 1,
                labels.get(rec.channel, ""),
            )

    @api.model
    def _default_recipient(self, quote, channel):
        partner = quote.customer_id
        if not partner:
            return False
        if channel in PHONE_CHANNELS:
            return fix_otp_util.bd_mobile(partner) or partner.phone or False
        if channel == "email":
            return partner.email or False
        return False

    @api.model_create_multi
    def create(self, vals_list):
        Quote = self.env["fix.quotation"]
        now = fields.Datetime.now()
        for vals in vals_list:
            quote = Quote.browse(vals.get("quotation_id")).exists()
            if not quote:
                raise UserError(_("Name the quotation that was delivered."))
            if quote.state != "sent":
                raise UserError(
                    _(
                        "Quotation %(q)s is %(s)s: a delivery is recorded for a quotation "
                        "issued to the customer (issue it first).",
                        q=quote.name,
                        s=quote.state,
                    )
                )
            vals["version"] = quote.version
            if not self.env.su:
                vals["recorded_by_id"] = self.env.user.id
            sent = fields.Datetime.to_datetime(vals.get("sent_at")) or now
            if sent > now + timedelta(minutes=10):
                raise ValidationError(_("A delivery cannot be recorded as sent in the future."))
            if not vals.get("recipient"):
                vals["recipient"] = self._default_recipient(quote, vals.get("channel"))
        records = super().create(vals_list)
        records._check_tracking()
        for rec in records:
            rec.quotation_id.message_post(
                body=_("Delivered to the customer by %s.") % dict(CHANNELS).get(rec.channel)
            )
        return records

    def write(self, vals):
        if not self.env.su:
            fixed = _changed(self, {k: v for k, v in vals.items() if k not in DELIVERY_TRACKING})
            if fixed:
                raise UserError(
                    _(
                        "What was sent, when, how and to whom is fixed once recorded; record "
                        "a new delivery instead (refused: %s)."
                    )
                    % ", ".join(sorted(fixed))
                )
            if "view_count" in vals and any((vals["view_count"] or 0) < r.view_count for r in self):
                raise ValidationError(_("The view count of a delivery never goes down."))
        res = super().write(vals)
        self._check_tracking()
        return res

    def _check_tracking(self):
        for rec in self:
            for stamp in ("delivered_at", "first_viewed_at"):
                if rec[stamp] and rec.sent_at and rec[stamp] < rec.sent_at:
                    raise ValidationError(
                        _("A delivery cannot be delivered or viewed before it was sent.")
                    )
            if (rec.view_count or 0) < 0:
                raise ValidationError(_("The view count cannot be negative."))
            if rec.view_count and not rec.first_viewed_at:
                raise ValidationError(_("Record when the customer first viewed it."))


class FixQuotationCounter(models.Model):
    _name = "fix.quotation.counter"
    _description = "Quotation Counter-Offer / Partial Acceptance"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(compute="_compute_name", store=True)
    quotation_id = fields.Many2one(
        "fix.quotation",
        required=True,
        ondelete="cascade",
        index=True,
        domain=[("state", "=", "sent")],
    )
    company_id = fields.Many2one(related="quotation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="quotation_id.operating_unit_id", store=True, index=True
    )
    customer_id = fields.Many2one(
        "res.partner", related="quotation_id.customer_id", store=True, string="Customer"
    )
    currency_id = fields.Many2one(related="quotation_id.currency_id")
    version = fields.Integer(string="Quotation Version", readonly=True)
    quoted_value = fields.Monetary(
        related="quotation_id.value",
        string="Quoted Value (excl. VAT)",
        currency_field="currency_id",
    )
    kind = fields.Selection(COUNTER_KINDS, required=True, default="counter")
    channel = fields.Selection(CHANNELS, required=True, string="Received By")
    customer_request = fields.Text(string="What the Customer Asked For", required=True)
    requested_value = fields.Monetary(
        string="Customer's Proposed Price (excl. VAT)",
        currency_field="currency_id",
        help="Empty: the customer did not name a price.",
    )
    evidence_ref = fields.Char(
        string="Evidence (call recording / message ref)",
        help="FR-QTE-036/042: the recorded call or message the counter came in on.",
    )
    line_ids = fields.One2many("fix.quotation.counter.line", "counter_id", string="Line Decisions")
    accepted_value = fields.Monetary(
        string="Accepted Lines (excl. VAT)",
        currency_field="currency_id",
        compute="_compute_accepted_value",
    )
    state = fields.Selection(COUNTER_STATES, required=True, default="requested", readonly=True)
    recorded_by_id = fields.Many2one("res.users", string="Taken Down By", readonly=True)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(readonly=True)
    decision_note = fields.Char(readonly=True)
    revised_quotation_id = fields.Many2one("fix.quotation", string="Revised Version", readonly=True)
    # the decision form's input (never stored: the decision is the state)
    decision_choice = fields.Selection(
        COUNTER_DECISIONS, string="Decision", compute="_compute_decision_choice"
    )

    @api.depends("quotation_id.name", "version", "kind")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s v%s · %s" % (
                rec.quotation_id.name or "",
                rec.version or rec.quotation_id.version or 1,
                "Partial" if rec.kind == "partial" else "Counter",
            )

    @api.depends("line_ids.decision", "line_ids.subtotal")
    def _compute_accepted_value(self):
        for rec in self:
            rec.accepted_value = round(
                sum(rec.line_ids.filtered(lambda r: r.decision == "accept").mapped("subtotal")), 2
            )

    def _compute_decision_choice(self):
        for rec in self:
            rec.decision_choice = False

    # ---- create / write ------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        Quote = self.env["fix.quotation"]
        for vals in vals_list:
            quote = Quote.browse(vals.get("quotation_id")).exists()
            if not quote:
                raise UserError(_("Name the quotation the customer answered."))
            if quote.state != "sent":
                raise UserError(
                    _(
                        "Quotation %(q)s is %(s)s: only a quotation with the customer can be "
                        "countered or partly accepted.",
                        q=quote.name,
                        s=quote.state,
                    )
                )
            if quote.estimate_id:
                raise UserError(
                    _(
                        "Quotation %s prices M01 estimate %s: the customer's change goes to the "
                        "estimate (Customer Counter on Internal Estimates), and the quotation "
                        "follows it."
                    )
                    % (quote.name, quote.estimate_id.display_name)
                )
            if self.sudo().search_count(
                [("quotation_id", "=", quote.id), ("state", "=", "requested")]
            ):
                raise UserError(
                    _("Quotation %s already has a counter awaiting its decision.") % quote.name
                )
            vals["version"] = quote.version
            vals["recorded_by_id"] = False if self.env.su else self.env.user.id
            vals.pop("state", None)
        records = super().create(vals_list)
        for rec in records:
            rec._check_request()
            if rec.kind == "partial" and not rec.line_ids:
                priced = rec.quotation_id._scope_lines()
                self.env["fix.quotation.counter.line"].create(
                    [{"counter_id": rec.id, "quotation_line_id": ln.id} for ln in priced]
                )
            rec.quotation_id.message_post(
                body=_("Customer %(k)s recorded (%(c)s): %(r)s")
                % {
                    "k": dict(COUNTER_KINDS).get(rec.kind),
                    "c": dict(CHANNELS).get(rec.channel),
                    "r": rec.customer_request,
                }
            )
        return records

    def write(self, vals):
        if not self.env.su:
            if self.filtered(lambda r: r.state != "requested"):
                raise UserError(_("A decided counter-offer is a record: it is not edited."))
            fixed = _changed(
                self, {k: v for k, v in vals.items() if k not in COUNTER_EDITABLE | {"line_ids"}}
            )
            if fixed:
                raise UserError(
                    _(
                        "Only the request, the price, the channel and the evidence change "
                        "before the decision (refused: %s)."
                    )
                    % ", ".join(sorted(fixed))
                )
        res = super().write(vals)
        for rec in self:
            rec._check_request()
        return res

    def unlink(self):
        if not self.env.su and self.filtered(lambda r: r.state != "requested"):
            raise UserError(_("A decided counter-offer is kept with its quotation."))
        return super().unlink()

    def _check_request(self):
        self.ensure_one()
        if not (self.customer_request or "").strip():
            raise ValidationError(_("Write down what the customer asked for."))
        if self.requested_value:
            quote = self.quotation_id
            if self.requested_value < 0:
                raise ValidationError(_("A proposed price cannot be negative."))
            if self.requested_value > (quote.lines_total or quote.value or 0.0) + 0.005:
                raise ValidationError(
                    _(
                        "The customer's price (%.2f) is above the quoted lines (%.2f): that is "
                        "no counter-offer."
                    )
                    % (self.requested_value, quote.lines_total or quote.value)
                )

    # ---- the decision ----------------------------------------------------------
    def action_decide(self, decision=None, note=None):
        """FR-QTE-036: the counter routes to someone other than the person who
        took it down. Revise makes the next draft version on the customer's
        terms (declined lines out, the proposed price as an overall discount);
        that version takes the value-band approval like any other, is issued
        and accepted with its own evidence (T-03: a derived version)."""
        note = (note or "").strip()
        decisions = dict(COUNTER_DECISIONS)
        for rec in self:
            if rec.state != "requested":
                raise UserError(_("Counter %s is already decided.") % rec.name)
            if decision not in decisions:
                raise UserError(_("Choose the decision: revise or reject."))
            if not self.env.su and rec.recorded_by_id == self.env.user:
                raise UserError(
                    _(
                        "Segregation of duties: whoever took the counter-offer down does not "
                        "decide it."
                    )
                )
            if decision == "reject":
                if not note:
                    raise UserError(_("Say why the counter-offer is rejected."))
                rec.sudo().write(
                    {
                        "state": "rejected",
                        "decided_by_id": self.env.user.id,
                        "decided_at": fields.Datetime.now(),
                        "decision_note": note,
                    }
                )
                rec.quotation_id.message_post(
                    body=_("Counter %(n)s rejected: %(w)s") % {"n": rec.name, "w": note}
                )
                continue
            new = rec._revise()
            rec.sudo().write(
                {
                    "state": "revised",
                    "decided_by_id": self.env.user.id,
                    "decided_at": fields.Datetime.now(),
                    "decision_note": note or False,
                    "revised_quotation_id": new.id,
                }
            )
        return True

    def _revise(self):
        self.ensure_one()
        quote = self.quotation_id
        if quote.state != "sent":
            raise UserError(
                _(
                    "Quotation %(q)s is %(s)s: it can no longer be revised from this counter; "
                    "reject the counter to close it.",
                    q=quote.name,
                    s=quote.state,
                )
            )
        declined = self.line_ids.filtered(lambda r: r.decision == "decline")
        if self.kind == "partial":
            accepted = self.line_ids - declined
            if not declined:
                raise UserError(_("Mark the lines the customer declined."))
            if not accepted:
                raise UserError(
                    _(
                        "The customer declined every line: record a decline, not a partial "
                        "acceptance."
                    )
                )
        action = quote.action_revise()
        new = self.env["fix.quotation"].browse(action["res_id"])
        if declined:
            # copy=True carried the lines over in order: drop the copies of the
            # declined ones (matched on what makes a line, never on position)
            def key(line):
                return (
                    line.sequence,
                    line.display_type or "",
                    line.product_id.id or 0,
                    line.description or "",
                    round(line.quantity or 0.0, 4),
                    round(line.unit_price or 0.0, 2),
                    round(line.discount_pct or 0.0, 4),
                    bool(line.is_optional),
                )

            pool = {}
            for line in new.line_ids:
                pool.setdefault(key(line), []).append(line)
            drop = self.env["fix.quotation.line"]
            for dec in declined:
                bucket = pool.get(key(dec.quotation_line_id)) or []
                if bucket:
                    drop |= bucket.pop(0)
            drop.unlink()
        if self.requested_value:
            base = new.lines_total or 0.0
            discount = round(max(0.0, base - self.requested_value), 2)
            if discount > base + 0.005:
                discount = base
            new.write({"discount_amount": discount})
        new.message_post(
            body=_("Version %(v)s made from the customer's %(k)s %(n)s: %(r)s")
            % {
                "v": new.version,
                "k": dict(COUNTER_KINDS).get(self.kind).lower(),
                "n": self.name,
                "r": self.customer_request,
            }
        )
        return new


class FixQuotationCounterLine(models.Model):
    _name = "fix.quotation.counter.line"
    _description = "Quotation Counter-Offer Line Decision"
    _order = "counter_id, sequence, id"

    counter_id = fields.Many2one(
        "fix.quotation.counter", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="counter_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="counter_id.operating_unit_id", store=True, index=True
    )
    quotation_line_id = fields.Many2one(
        "fix.quotation.line", string="Quoted Line", required=True, ondelete="cascade"
    )
    sequence = fields.Integer(related="quotation_line_id.sequence", store=True)
    description = fields.Char(related="quotation_line_id.description")
    quantity = fields.Float(related="quotation_line_id.quantity")
    currency_id = fields.Many2one(related="quotation_line_id.currency_id")
    subtotal = fields.Monetary(
        related="quotation_line_id.subtotal",
        string="Amount excl. VAT",
        currency_field="currency_id",
    )
    decision = fields.Selection(
        [("accept", "Accepted"), ("decline", "Declined")], required=True, default="accept"
    )

    _counter_line_unique = models.Constraint(
        "unique(counter_id, quotation_line_id)", "Each quoted line is decided once."
    )

    @api.constrains("counter_id", "quotation_line_id")
    def _check_line(self):
        for rec in self:
            if rec.quotation_line_id.quotation_id != rec.counter_id.quotation_id:
                raise ValidationError(_("A line decision is about a line of the same quotation."))
            if rec.counter_id.kind != "partial":
                raise ValidationError(_("Line decisions belong to a partial acceptance."))

    def _assert_open(self, counters):
        if not self.env.su and counters.filtered(lambda c: c.state != "requested"):
            raise UserError(_("A decided counter-offer is a record: it is not edited."))

    @api.model_create_multi
    def create(self, vals_list):
        ids = {v.get("counter_id") for v in vals_list} - {None, False}
        self._assert_open(self.env["fix.quotation.counter"].browse(list(ids)).exists())
        return super().create(vals_list)

    def write(self, vals):
        self._assert_open(self.counter_id)
        if not self.env.su and set(vals) - {"decision"}:
            raise UserError(_("Only the customer's decision on a line changes."))
        return super().write(vals)

    def unlink(self):
        self._assert_open(self.counter_id)
        return super().unlink()


class FixQuotationLineName(models.Model):
    # A quoted line is named by what it quotes ("fix.quotation.line,440"
    # showed on the counter's line decisions).
    _inherit = "fix.quotation.line"
    _rec_name = "description"


class FixQuotationLoop(models.Model):
    _inherit = "fix.quotation"

    delivery_ids = fields.One2many("fix.quotation.delivery", "quotation_id", string="Deliveries")
    counter_ids = fields.One2many("fix.quotation.counter", "quotation_id", string="Counter-Offers")
    # Derived, never stored: the deliveries are the record.
    delivery_channel = fields.Selection(
        CHANNELS, string="First Delivered By", compute="_compute_delivery"
    )
    delivery_count = fields.Integer(string="Delivery Count", compute="_compute_delivery")
    first_viewed_at = fields.Datetime(string="First Viewed At", compute="_compute_delivery")
    diagnostic_fee_due = fields.Monetary(
        string="Diagnostic Fee Due on Decline",
        currency_field="currency_id",
        compute="_compute_diagnostic_fee_due",
        help="BRU-QTE-12: the M01 estimate's diagnostic charge, owed when the repair is declined.",
    )
    # The pick forms' inputs (never stored: each goes to its workflow method).
    issue_channel = fields.Selection(CHANNELS, string="Deliver By", compute="_compute_inputs")
    issue_recipient = fields.Char(string="Delivered To", compute="_compute_inputs")
    issue_ref = fields.Char(string="Message / Delivery Ref", compute="_compute_inputs")
    acceptance_code_entry = fields.Char(
        string="Code the Customer Read Out", compute="_compute_inputs"
    )

    @api.depends("delivery_ids.channel", "delivery_ids.sent_at", "delivery_ids.first_viewed_at")
    def _compute_delivery(self):
        for rec in self:
            rows = rec.delivery_ids.sorted(lambda d: (d.sent_at, d.id))
            rec.delivery_channel = rows[:1].channel or False
            rec.delivery_count = len(rows)
            viewed = [d.first_viewed_at for d in rows if d.first_viewed_at]
            rec.first_viewed_at = min(viewed) if viewed else False

    @api.depends("state", "estimate_id")
    def _compute_diagnostic_fee_due(self):
        for rec in self:
            est = rec.estimate_id.sudo()
            rec.diagnostic_fee_due = (
                est.diagnostic_total if rec.state == "declined" and est else 0.0
            )

    def _compute_inputs(self):
        for rec in self:
            rec.issue_channel = False
            rec.issue_recipient = False
            rec.issue_ref = False
            rec.acceptance_code_entry = False

    # ---- issue on a channel -----------------------------------------------------
    def action_issue_on_channel(self, channel=None, recipient=None, delivery_ref=None):
        """Issue (approved -> sent) on a channel and record the delivery
        (FR-QTE-033; the spec's guard "delivery channel confirmed"). A method
        of its own: action_send is overridden elsewhere (the tender lock)."""
        if channel not in dict(CHANNELS):
            raise UserError(_("Choose the channel the customer receives it on."))
        self.action_send()
        Delivery = self.env["fix.quotation.delivery"]
        for rec in self:
            Delivery.create(
                {
                    "quotation_id": rec.id,
                    "channel": channel,
                    "recipient": (recipient or "").strip() or False,
                    "delivery_ref": (delivery_ref or "").strip() or False,
                }
            )
        return True

    # ---- acceptance -------------------------------------------------------------------
    def action_record_signed_acceptance(self, attachment_id=None):
        """The signed copy may arrive with the request (the workspace uploads
        it and passes its id); the acceptance rules are the base method's."""
        if attachment_id:
            att = self.env["ir.attachment"].browse(int(attachment_id)).exists()
            if not att:
                raise UserError(_("The signed quotation upload was not stored."))
            if not self.env.su and att.create_uid != self.env.user:
                raise UserError(_("Attach the signed quotation you uploaded yourself."))
            for rec in self:
                if rec.state != "sent":
                    raise UserError(_("Issue the quotation to the customer first."))
                rec.write({"signed_attachment_id": att.id})
        return super().action_record_signed_acceptance()

    def action_verify_acceptance_otp(self, otp=None, code=None):
        """A wrong code is counted, not raised (a raise would roll the counter
        back); the workspace shows it as a warning, not "Saved"."""
        res = super().action_verify_acceptance_otp(otp=otp, code=code)
        if isinstance(res, dict) and not res.get("verified"):
            res = dict(res, warning=res.get("error") or _("That acceptance code is not correct."))
        return res

    # ---- decline follow-up ---------------------------------------------------------
    def action_decline(self, reason=None, code=None):
        res = super().action_decline(reason=reason, code=code)
        self._decline_followup()
        return res

    def _decline_followup(self):
        """BRU-QTE-12 / AUT-QTE-09: a declined repair quote gives the service
        order a task to return or collect the device, with the diagnostic fee
        owed. Raising the fee as an invoice follows the M20 fee policy."""
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        for rec in self.filtered(lambda q: q.state == "declined"):
            order = (rec.service_order_id or rec.estimate_id.order_id).sudo()
            if not order or not hasattr(order, "activity_schedule"):
                continue
            fee = rec.diagnostic_fee_due or 0.0
            note = _("Quotation %(q)s v%(v)s declined (%(r)s). Return or collect the device.") % {
                "q": rec.name,
                "v": rec.version,
                "r": rec.decline_reason or "",
            }
            if fee:
                note += " " + _("Diagnostic fee owed: BDT %.2f.") % fee
            order.activity_schedule(
                activity_type_id=todo.id if todo else False,
                summary=_("Quotation declined: return or collect the device"),
                note=note,
                user_id=(order.create_uid or self.env.user).id,
            )
