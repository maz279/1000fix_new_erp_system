# fix_knowledge_ops — M61: troubleshooting trees, media assets and brand
# bulletins/recalls. Articles live in fix_knowledge.py.
from odoo import api, fields, models


class FixKnowledgeTree(models.Model):
    _name = "fix.knowledge.tree"
    _description = "Troubleshooting Tree"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    device_brand = fields.Char(string="Brand")
    device_model = fields.Char(string="Model / Chassis")
    fault_symptom = fields.Char(string="Entry Symptom")
    nodes_text = fields.Text(
        string="Decision Nodes",
        help="Ordered decision steps: question -> yes/no branch -> action.",
    )
    linked_article_id = fields.Many2one("fix.knowledge.article", string="Root Article")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("archived", "Archived")],
        required=True,
        default="draft",
    )

    def action_publish(self):
        for rec in self:
            rec.state = "published"


class FixKnowledgeMedia(models.Model):
    _name = "fix.knowledge.media"
    _description = "Knowledge Media Asset"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    media_type = fields.Selection(
        [("video", "Video"), ("image", "Image"), ("diagram", "Diagram"), ("audio", "Audio")],
        required=True,
        default="video",
    )
    article_id = fields.Many2one("fix.knowledge.article", string="Attached Article")
    url = fields.Char(string="Asset URL")
    duration_min = fields.Float(string="Duration (minutes)")
    size_mb = fields.Float(string="Size (MB)")
    offline_available = fields.Boolean(string="Available Offline", default=False)
    active = fields.Boolean(default=True)


class FixKnowledgeBulletin(models.Model):
    _name = "fix.knowledge.bulletin"
    _description = "Brand Bulletin / Recall"
    _order = "issued_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    brand = fields.Char(required=True)
    bulletin_type = fields.Selection(
        [
            ("recall", "Safety Recall"),
            ("technical", "Technical Bulletin"),
            ("advisory", "Service Advisory"),
            ("parts", "Parts Change Notice"),
        ],
        required=True,
        default="technical",
    )
    issued_on = fields.Date(required=True, default=fields.Date.context_today)
    affected_models = fields.Char(string="Affected Models")
    summary = fields.Text()
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    state = fields.Selection(
        [("received", "Received"), ("distributed", "Distributed"), ("closed", "Closed")],
        required=True,
        default="received",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.knowledge.bulletin") or "BUL/New"
                )
        return super().create(vals_list)

    def action_distribute(self):
        for rec in self:
            rec.state = "distributed"
