# fix_tradein — M14: trade-in, refurbishment, resale (P09-M04).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

TRADEIN_STATES = [
    ("draft", "Draft"), ("offered", "Offer Sent"), ("accepted", "Accepted"),
    ("collected", "Collected"), ("wiped", "Data Wiped"),
    ("refurbished", "Refurbished"), ("graded", "Graded"),
    ("resale_ready", "Resale Ready"), ("closed", "Closed"),
    ("rejected", "Rejected"),
]


class FixTradeinRequest(models.Model):
    """Journey 9: trade-in -> offer -> intake -> data wipe -> refurbishment
    -> grading -> resale. The circular business's money path."""
    _name = "fix.tradein.request"
    _description = "Trade-In Request"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M14",
        "form": "Trade-In Request",
        "fields": ["customer_id", "device_id", "offered_value", "grade"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True,
                       default=lambda self: "New")
    customer_id = fields.Many2one("res.partner", string="Customer",
                                  required=True, index=True)
    device_id = fields.Many2one("fix.device", string="Device",
                                ondelete="set null")
    device_model_id = fields.Many2one("fix.device.model",
                                      string="Device Model",
                                      related="device_id.device_model_id",
                                      store=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    offered_value = fields.Monetary(string="Offered Value",
                                    currency_field="currency_id",
                                    help="The trade-in offer (valuation)")
    payout_amount = fields.Monetary(string="Payout Amount",
                                    currency_field="currency_id",
                                    readonly=True,
                                    help="The actual payout (M50 treasury)")
    grade = fields.Selection(
        [("a", "Grade A (Like New)"), ("b", "Grade B (Good)"),
         ("c", "Grade C (Fair)"), ("d", "Grade D (Poor)"),
         ("e", "Grade E (Parts Only)")],
        string="Refurbishment Grade")
    state = fields.Selection(TRADEIN_STATES, default="draft",
                             required=True, tracking=True)
    wipe_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate", string="Data Wipe Certificate",
        ondelete="set null",
        help="M06's secure wipe; required before refurbishment")
    resale_value = fields.Monetary(string="Resale Value",
                                   currency_field="currency_id",
                                   help="The graded resale valuation")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fix.tradein.request") or "TRD/New"
        return super().create(vals_list)

    def action_send_offer(self):
        for rec in self:
            if rec.offered_value <= 0:
                raise UserError("An offer requires a positive valuation")
            rec.state = "offered"
            publish(self.env, "tradein.offered", "fix.tradein.request",
                    rec.id, {"customer": rec.customer_id.name,
                             "value": float(rec.offered_value)})

    def action_accept(self):
        for rec in self:
            if rec.state != "offered":
                raise UserError("Accept from offered")
            rec.state = "accepted"

    def action_collect(self):
        """Collection through M03 logistics (the custody chain starts)."""
        for rec in self:
            if rec.state != "accepted":
                raise UserError("Collect from accepted")
            rec.state = "collected"
            publish(self.env, "tradein.collected", "fix.tradein.request",
                    rec.id, {"device": rec.device_id.name or ""})

    def action_wipe(self):
        """The secure data wipe — M06's certificate must exist before the
        refurbishment can begin (journey 9's gate)."""
        for rec in self:
            if rec.state != "collected":
                raise UserError("Wipe from collected")
            if not rec.wipe_certificate_id:
                wipe = self.env["fix.data.wipe.certificate"].create({
                    "device_id": rec.device_id.id,
                    "method": "nist_800_88",
                })
                rec.write({"wipe_certificate_id": wipe.id,
                           "state": "wiped"})
            else:
                rec.state = "wiped"
            publish(self.env, "tradein.wiped", "fix.tradein.request",
                    rec.id, {"certificate": rec.wipe_certificate_id.name or ""})

    def action_refurbish(self):
        """Refurbishment on M31's workshop model (composes the estate)."""
        for rec in self:
            if rec.state != "wiped":
                raise UserError("Refurbish from data-wiped (the wipe gate)")
            rec.state = "refurbished"
            publish(self.env, "tradein.refurbished", "fix.tradein.request",
                    rec.id, {})

    def action_grade(self):
        """Grading against M37's refurbishment grades."""
        for rec in self:
            if rec.state != "refurbished":
                raise UserError("Grade from refurbished")
            if not rec.grade:
                raise UserError("A grade is required before resale")
            rec.state = "graded"
            publish(self.env, "tradein.graded", "fix.tradein.request",
                    rec.id, {"grade": rec.grade})

    def action_resale_ready(self):
        """The resale seam: M12 marketplace and M38 storefront land in W7;
        the trade-in is ready now (the seam, not the channel)."""
        for rec in self:
            if rec.state != "graded":
                raise UserError("Resale from graded")
            rec.state = "resale_ready"
            publish(self.env, "tradein.resale_ready", "fix.tradein.request",
                    rec.id, {"grade": rec.grade,
                             "resale_value": float(rec.resale_value)})

    def action_pay(self):
        """Trade-in payout through M50 treasury."""
        for rec in self:
            if rec.state not in ("resale_ready", "graded"):
                raise UserError("Payout from graded or resale-ready")
            rec.write({"state": "closed", "payout_amount": rec.offered_value})
            publish(self.env, "tradein.paid", "fix.tradein.request",
                    rec.id, {"payout": float(rec.payout_amount)})


class FixRefurbishment(models.Model):
    """A refurbishment step within a trade-in (composes the workshop)."""
    _name = "fix.refurbishment"
    _description = "Refurbishment"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M14",
        "form": "Refurb Work Order",
        "fields": ["name", "step", "tradein_id", "notes"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    tradein_id = fields.Many2one("fix.tradein.request", string="Trade-In",
                                 ondelete="cascade")
    step = fields.Selection(
        [("intake", "Intake Inspection"), ("repair", "Repair"),
         ("cosmetic", "Cosmetic Restoration"), ("testing", "Testing"),
         ("final_qa", "Final QA")],
        required=True, default="intake")
    state = fields.Selection([("pending", "Pending"), ("done", "Done")],
                             default="pending", required=True)
    notes = fields.Text()
