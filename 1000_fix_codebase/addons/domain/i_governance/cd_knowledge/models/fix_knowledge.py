# fix_knowledge — M61: Technical Library, Knowledge Management & P02 Offline Manuals (P09-M08 & R07-M05).
import hashlib

from odoo import api, fields, models

from libs.py.fix_events import publish


class FixKnowledgeArticle(models.Model):
    """M61: Technical library and knowledge base (M22 technical content moved here).
    Feeds M32 Conversational Assistant and P02 Technician Offline Manuals."""

    _name = "fix.knowledge.article"
    _description = "Knowledge Article & Technical Manual"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Article Title (English)", required=True)
    title_bn = fields.Char(
        string="Article Title (Bengali)", help="Bengali-first localization (DE-17)"
    )
    article_code = fields.Char(string="Reference Code (e.g. KB-HW-001)")
    category = fields.Selection(
        [
            ("troubleshooting", "Troubleshooting Guide"),
            ("repair_procedure", "Repair Procedure (SOP)"),
            ("schematic", "Circuit Schematic & Boardview"),
            ("device_guide", "Device Disassembly Guide"),
            ("policy", "Quality & Warranty Policy"),
            ("training", "Technical Training Material"),
            ("safety_bulletin", "Technical Safety Bulletin"),
        ],
        required=True,
        default="troubleshooting",
    )
    content = fields.Html(string="Content (English)", required=True)
    content_bn = fields.Html(string="Content (Bengali)")
    tags = fields.Char(string="Search Tags", help="Comma-separated search keywords for M32 NLU")

    # Technical metadata for repair operations
    device_brand = fields.Char(string="Target Brand (e.g. Dell, HP, Samsung, Walton)")
    device_model = fields.Char(string="Target Model / Chassis")
    fault_symptom = fields.Char(string="Fault Symptom (e.g. No Power, Display Artifact, Bootloop)")
    rework_level = fields.Selection(
        [
            ("L1", "L1: Modular Replacement"),
            ("L2", "L2: Subassembly Rework"),
            ("L3", "L3: Component-Level SMD / BGA Repair"),
            ("L4", "L4: Cleanroom Trace / Micro-Soldering"),
        ],
        default="L2",
        string="Technical Repair Level",
    )

    # P02 Offline Manual & Sync Metadata
    offline_available = fields.Boolean(
        string="Available for Offline Sync",
        default=True,
        help="Synced to P02 Technician mobile app SQLite store for offline cleanroom access",
    )
    version = fields.Integer(string="Manual Version", default=1, readonly=True)
    content_hash = fields.Char(
        string="Content SHA-256 Hash",
        compute="_compute_content_hash",
        store=True,
        help="Cryptographic checksum for bandwidth-efficient delta sync to mobile clients",
    )
    views = fields.Integer(default=0, readonly=True)
    helpful_votes = fields.Integer(default=0, readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("archived", "Archived")],
        default="draft",
        required=True,
        tracking=True,
    )

    @api.depends("content", "content_bn", "name", "category")
    def _compute_content_hash(self):
        for rec in self:
            payload = (
                f"{rec.name or ''}|{rec.category or ''}|{rec.content or ''}|{rec.content_bn or ''}"
            )
            rec.content_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def action_publish(self):
        for rec in self:
            rec.state = "published"
            rec.version += 1
            publish(
                self.env,
                "knowledge.published",
                "fix.knowledge.article",
                rec.id,
                {"title": rec.name, "category": rec.category, "code": rec.article_code},
            )

    @api.model
    def get_offline_manuals(self, brand=None, model=None, version_after=0):
        """API consumed by P02 Technician mobile app offline sync engine."""
        domain = [("state", "=", "published"), ("offline_available", "=", True)]
        if brand:
            domain.append(("device_brand", "=ilike", brand))
        if model:
            domain.append(("device_model", "=ilike", model))
        if version_after:
            domain.append(("version", ">", version_after))

        articles = self.search(domain)
        return [
            {
                "id": a.id,
                "code": a.article_code or f"KB-{a.id:04d}",
                "title_en": a.name,
                "title_bn": a.title_bn or a.name,
                "category": a.category,
                "brand": a.device_brand or "",
                "model": a.device_model or "",
                "fault_symptom": a.fault_symptom or "",
                "rework_level": a.rework_level or "L2",
                "content_en": a.content,
                "content_bn": a.content_bn or a.content,
                "content_hash": a.content_hash,
                "version": a.version,
            }
            for a in articles
        ]
