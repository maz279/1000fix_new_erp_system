# fix_knowledge — M61: Technical library, knowledge management & P02 offline manuals (P09-M08 & R07-M05).
import datetime
import hashlib
import re

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

# A10 K1 (2026-11-05, M61-1): content a technician acts on live — anything
# tagged electrical, battery or high-voltage, and every safety bulletin —
# may not reach the field without a reviewer's named sign-off.
SAFETY_TAGS_RE = re.compile(r"electrical|battery|high[\s-]?voltage|\bhv\b", re.I)
PUBLISHER_GROUP = "cd_knowledge.group_knowledge_publisher"


def is_safety_content(tags, category=None) -> bool:
    """Safety-critical content: a safety tag, or a safety bulletin."""
    if category == "safety_bulletin":
        return True
    return bool(SAFETY_TAGS_RE.search(tags or ""))


def require_publisher(env):
    """Only a Knowledge Publisher publishes; superuser code (crons, relay)
    is trusted."""
    if env.su:
        return
    if not env.user.has_group(PUBLISHER_GROUP):
        raise UserError(
            "Only a Knowledge Publisher may publish technical content (A10 K1). "
            "Field technicians act on this content — it is reviewed, not posted."
        )


def require_reviewer(rec, reviewer, author_uid):
    """Safety content ships with a named reviewer who is a Knowledge
    Publisher and NOT the author (M61-1)."""
    if not reviewer:
        raise UserError(
            "'%s' is safety-critical technical content (tagged electrical, "
            "battery or high-voltage, or a safety bulletin). It cannot be "
            "published without a reviewer from the Knowledge Publisher group "
            "other than the author (A10 K1)." % rec.name
        )
    if not reviewer.has_group(PUBLISHER_GROUP):
        raise UserError(
            "The reviewer of '%s' must belong to the Knowledge Publisher group "
            "(A10 K1)." % rec.name
        )
    if author_uid and reviewer.id == author_uid:
        raise UserError(
            "The author of '%s' cannot be its reviewer — safety content needs "
            "a second pair of eyes (A10 K1, M61-1)." % rec.name
        )


class FixKnowledgeArticle(models.Model):
    """M61: Technical library and knowledge base (M22 technical content moved here).
    Feeds M32 Conversational Assistant and P02 Technician Offline Manuals."""

    _name = "fix.knowledge.article"
    _description = "Knowledge Article & Technical Manual"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    # A10 K1 (M61-1): the named review behind a publication
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
        readonly=True,
        index=True,
        help="The author accountable for this content (stamped at creation).",
    )
    # A10 P1-2 (M61-6): the review cycle. Publishing (or revising) content
    # starts a 12-month review window; the daily cron announces content whose
    # window has closed — without a clock, published content never came due.
    review_due = fields.Date(
        string="Review Due",
        help="Set by publishing or revising: today + 12 months. The review "
        "cron announces published content past this date.",
    )
    review_notified_on = fields.Date()
    reviewed_by_id = fields.Many2one(
        "res.users",
        string="Reviewed By",
        readonly=True,
        help="The Knowledge Publisher who reviewed this content before it "
        "reached the field. For safety-critical content this is required and "
        "is never the author.",
    )
    reviewed_on = fields.Date(string="Reviewed On", readonly=True)
    safety_critical = fields.Boolean(
        string="Safety-Critical",
        compute="_compute_safety_critical",
        help="True when the tags name electrical, battery or high-voltage work "
        "(or the article is a safety bulletin): publishing then requires a "
        "reviewer other than the author (A10 K1).",
    )

    @api.depends("tags", "category")
    def _compute_safety_critical(self):
        for rec in self:
            rec.safety_critical = is_safety_content(rec.tags, rec.category)

    def _fix_guarded_fields(self) -> set:
        """The lifecycle, the version counter, the sync hash and the review
        record are the publication's evidence: they move only through the
        actions below (A10 K1 / R1)."""
        return super()._fix_guarded_fields() | {
            "state",
            "version",
            "content_hash",
            "views",
            "helpful_votes",
            "owner_id",
            "review_due",
            "review_notified_on",
            "reviewed_by_id",
            "reviewed_on",
        }

    # The fields an edit of a PUBLISHED article turns into a new version
    # (M61-3: the edit must reach the offline devices, not die on the server).
    # Everything the offline payload carries — titles, content, and the
    # brand/model/symptom/level the sync matches on.
    _REVISION_FIELDS = (
        "name",
        "title_bn",
        "content",
        "content_bn",
        "category",
        "device_brand",
        "device_model",
        "fault_symptom",
        "rework_level",
    )

    def write(self, vals):
        # K1 (M61-3): editing a published article is ALLOWED — the field is
        # the author's to improve — but it is a REVISION: the version rises
        # server-side and the event fires, so the offline sync (which reads
        # version_after + content_hash) delivers it to every device.
        revising = self.browse()
        if self and not self._fix_guard_open():
            touched = [n for n in self._REVISION_FIELDS if n in vals]
            if touched:
                for rec in self:
                    if rec.state == "published" and any(
                        rec._fix_guard_differs(n, vals[n], rec[n]) for n in touched
                    ):
                        revising |= rec
        result = super().write(vals)
        for rec in revising:
            # a revision is fresh content: the review window restarts (M61-6)
            rec._guarded().write(
                {
                    "version": (rec.version or 1) + 1,
                    "review_due": fields.Date.context_today(rec) + datetime.timedelta(days=365),
                }
            )
            publish(
                self.env,
                "knowledge.published",
                "fix.knowledge.article",
                rec.id,
                {
                    "title": rec.name,
                    "category": rec.category,
                    "code": rec.article_code,
                    "version": rec.version,
                    "content_hash": rec.content_hash,
                },
            )
            rec.message_post(
                body="Published content revised — version %d now syncing to the field "
                "(hash %s)." % (rec.version, (rec.content_hash or "")[:12])
            )
        return result

    @api.depends("content", "content_bn", "name", "category")
    def _compute_content_hash(self):
        for rec in self:
            payload = (
                f"{rec.name or ''}|{rec.category or ''}|{rec.content or ''}|{rec.content_bn or ''}"
            )
            rec.content_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def action_publish(self, reviewer_id=None):
        """Publishing is a Knowledge Publisher's act over reviewed content
        (A10 K1, M61-1/-2): safety-critical content additionally needs a
        named reviewer who is a publisher and NOT the author. The version
        rises server-side so offline clients can delta-sync."""
        require_publisher(self.env)
        for rec in self:
            if rec.state == "published":
                raise UserError("%s is already published." % rec.name)
            rid = reviewer_id or rec.reviewed_by_id.id
            reviewer = self.env["res.users"].browse(rid).exists() if rid else self.env["res.users"]
            if rec.safety_critical:
                require_reviewer(rec, reviewer, rec.create_uid.id)
            elif reviewer:
                # a named reviewer on ordinary content is still validated:
                # a reviewer who is not a publisher is a typo, not a review
                require_reviewer(rec, reviewer, rec.create_uid.id)
            rec._guarded().write(
                {
                    "state": "published",
                    "version": (rec.version or 1) + 1,
                    "review_due": fields.Date.context_today(rec) + datetime.timedelta(days=365),
                    **(
                        {
                            "reviewed_by_id": reviewer.id,
                            "reviewed_on": fields.Date.context_today(rec),
                        }
                        if reviewer
                        else {}
                    ),
                }
            )
            publish(
                self.env,
                "knowledge.published",
                "fix.knowledge.article",
                rec.id,
                {
                    "title": rec.name,
                    "category": rec.category,
                    "code": rec.article_code,
                    "version": rec.version,
                    "content_hash": rec.content_hash,
                },
            )
            rec.message_post(
                body="Published by %s%s."
                % (
                    self.env.user.name,
                    " — reviewed by %s" % reviewer.name
                    if reviewer
                    else " (no safety review required)",
                )
            )
        return True

    def action_archive(self):
        """A publisher retires an article from the field."""
        require_publisher(self.env)
        for rec in self:
            if rec.state != "published":
                raise UserError(
                    "Only a published article is archived — %s is %s." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "archived"})
            rec.message_post(body="Archived by %s." % self.env.user.name)
        return True

    # ------------------------------------------------------- the review clock
    @api.model
    def cron_article_review(self):
        """The daily knowledge review clock (A10 P1-2, M61-6): published
        content whose 12-month window closed is announced on the outbox — at
        most once a day each — until a revision (or archive) resolves it.
        Without the clock, published content never came due."""
        today = fields.Date.today()
        due = self.search(
            [
                ("state", "=", "published"),
                ("review_due", "!=", False),
                ("review_due", "<=", today),
            ]
        ).filtered(lambda a: not a.review_notified_on or a.review_notified_on < today)
        for rec in due:
            publish(
                self.env,
                "knowledge.review.due",
                "fix.knowledge.article",
                rec.id,
                {
                    "title": rec.name,
                    "code": rec.article_code or "",
                    "category": rec.category,
                    "version": rec.version,
                    "review_due": str(rec.review_due),
                },
            )
            rec._guarded().write({"review_notified_on": today})
            rec.message_post(
                body="Review due since %s (version %d) — technical content older "
                "than its window is re-reviewed, not trusted." % (rec.review_due, rec.version or 0)
            )
        return len(due)

    def consume_article_review_due(self, env_from_relay):
        """In-Odoo consumer for knowledge.review.due (relay-only): the
        article's own thread is the audit trail of the review call."""
        if not self.env.su:
            raise UserError("The review-clock consumer runs from the event relay only.")
        art = self.browse(int(env_from_relay.get("aggregate_id") or 0)).exists()
        if art:
            art.message_post(body="Review-due announcement relayed to the article thread.")
        return True

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
