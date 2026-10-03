# fix_campaign — M35: campaigns, attribution, bilingual content (P08-M04-T08).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixCampaign(models.Model):
    _name = "fix.campaign"
    _description = "Marketing Campaign"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Campaign (Bengali)", help="DE-17")
    channel = fields.Selection(
        [("social", "Social"), ("search", "Search"), ("sms", "SMS"),
         ("email", "Email"), ("billboard", "Billboard")],
        required=True, default="social")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    budget = fields.Monetary(string="Budget", currency_field="currency_id")
    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("paused", "Paused"),
         ("completed", "Completed")],
        default="draft", required=True, tracking=True)
    audience_domain = fields.Char(
        string="Audience Segment",
        help="res.partner domain, e.g. [('city','=','Dhaka')]")
    response_ids = fields.One2many("fix.campaign.response", "campaign_id",
                                   string="Responses")
    response_count = fields.Integer(compute="_compute_response_count",
                                    string="Responses")
    cost_per_response = fields.Monetary(
        string="Cost per Response", currency_field="currency_id",
        compute="_compute_response_count")

    @api.depends("response_ids", "budget")
    def _compute_response_count(self):
        for rec in self:
            rec.response_count = len(rec.response_ids)
            rec.cost_per_response = (
                round(rec.budget / len(rec.response_ids), 2)
                if rec.response_ids else 0.0)

    def action_launch(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Launch from draft only")
            if not rec.start_date or not rec.end_date:
                raise UserError("A campaign runs between dates")
            if rec.end_date < rec.start_date:
                raise UserError("Campaign window is inverted")
            rec.state = "running"
            publish(self.env, "campaign.launched", "fix.campaign", rec.id,
                    {"campaign": rec.name, "channel": rec.channel})

    def action_pause(self):
        for rec in self:
            if rec.state != "running":
                raise UserError("Only a RUNNING campaign pauses")
            rec.state = "paused"

    def action_resume(self):
        for rec in self:
            if rec.state != "paused":
                raise UserError("Only a PAUSED campaign resumes")
            rec.state = "running"

    def action_complete(self):
        for rec in self:
            if rec.state not in ("running", "paused"):
                raise UserError("Complete an active campaign")
            rec.state = "completed"
            publish(self.env, "campaign.completed", "fix.campaign", rec.id,
                    {"campaign": rec.name,
                     "responses": rec.response_count})


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixCampaignResponse(models.Model):
    """The attribution ledger: demand generation is measurable per spend."""
    _name = "fix.campaign.response"
    _description = "Campaign Response"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    campaign_id = fields.Many2one("fix.campaign", required=True,
                                  ondelete="cascade", index=True)
    partner_id = fields.Many2one("res.partner", string="Lead",
                                 ondelete="set null")
    response_type = fields.Selection(
        [("click", "Click"), ("call", "Inbound Call"),
         ("form", "Form Submission"), ("visit", "Branch Visit")],
        required=True, default="click")
    responded_at = fields.Datetime(default=fields.Datetime.now, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            publish(self.env, "campaign.response", "fix.campaign.response",
                    rec.id, {"campaign": rec.campaign_id.name,
                             "type": rec.response_type})
        return recs

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")