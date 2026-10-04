# fix_knowledge — M61: knowledge management (P09-M08).
from odoo import fields, models

from libs.py.fix_events import publish


class FixKnowledgeArticle(models.Model):
    """M61: the technical library (M22's technical content moved here)."""
    _name = "fix.knowledge.article"
    _description = "Knowledge Article"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    title_bn = fields.Char(string="Title (Bengali)", help="DE-17")
    category = fields.Selection(
        [("troubleshooting", "Troubleshooting Guide"),
         ("repair_procedure", "Repair Procedure"),
         ("device_guide", "Device Guide"), ("policy", "Policy"),
         ("training", "Training Material")],
        required=True, default="troubleshooting")
    content = fields.Html(required=True)
    tags = fields.Char(help="Comma-separated search tags")
    views = fields.Integer(default=0, readonly=True)
    helpful_votes = fields.Integer(default=0, readonly=True)
    state = fields.Selection([("draft", "Draft"), ("published", "Published"),
                              ("archived", "Archived")],
                             default="draft", required=True, tracking=True)

    def action_publish(self):
        for rec in self:
            rec.state = "published"
            publish(self.env, "knowledge.published", "fix.knowledge.article",
                    rec.id, {"title": rec.name, "category": rec.category})
