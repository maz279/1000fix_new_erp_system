# fix_m61_capture — M61 sub-module capture audit (2026-11-18).
#
# Evaluated with the workspace engine's own fregCreate/fregPanels, the M61
# pages at HEAD 32e24dc9 captured little of what the spec says they hold:
#   * Authoring: no field capture (FR-KMS-023/024/027, BRU-KMS-08/09), no
#     review request (the "Review Workflow" list re-listed articles with a
#     Publish button that asked for a reviewer's numeric user ID; ordinary
#     content published with no reviewer at all, against BRU-KMS-02 H), no
#     version history (FR-KMS-007: a revision overwrote the text);
#   * Troubleshooting Trees: one free-text box for the nodes (FR-KMS-005);
#   * Technical Library: no "+ New"; manuals were articles, with no file, no
#     brand/model index and no licence terms (FR-KMS-004, BRU-KMS-16);
#   * Search & Surfacing: nothing; no operational link to fault codes,
#     models or brands (FR-KMS-006/015);
#   * Offline Distribution: nothing; no per-technician scope or storage
#     budget (FR-KMS-017/018, BRU-KMS-05);
#   * Feedback & Health: "+ New Article"; no usefulness feedback
#     (FR-KMS-030), so the usefulness tile read counters nothing increments.
#
# Each record below is captured on its page; every stamp, measured figure
# and decision is a guarded field that only its action moves.
import hashlib

from markupsafe import escape
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_knowledge import PUBLISHER_GROUP, require_publisher
from .fix_knowledge_ops import QM_GROUP

LEVELS = [
    ("L1", "L1: Modular Replacement"),
    ("L2", "L2: Subassembly Rework"),
    ("L3", "L3: Component-Level SMD / BGA Repair"),
    ("L4", "L4: Cleanroom Trace / Micro-Soldering"),
]
LEVEL_RANK = {key: n for n, (key, _label) in enumerate(LEVELS, start=1)}

# AUT-KMS-17: three "did not resolve" answers in a row on the current version
# flag the article; so does a low average once enough people have rated it.
FLAG_NO_RUN = 3
FLAG_MIN_RATINGS = 5
FLAG_LOW_AVG = 2.5


def _is_publisher(user) -> bool:
    return user.has_group(PUBLISHER_GROUP)


def _is_quality_manager(env, user) -> bool:
    """The Quality Manager without a manifest dependency on cd_qms_process
    (see the manifest note); no group on the database = nobody qualifies."""
    return bool(env.ref(QM_GROUP, raise_if_not_found=False)) and user.has_group(QM_GROUP)


def _next(env, code, fallback):
    return env["ir.sequence"].sudo().next_by_code(code) or fallback


def _only_by(env, user, message):
    if not env.su and env.user != user:
        raise UserError(message)


# ======================================================================
# The review gate shared by articles and trees (BRU-KMS-02/03)
# ======================================================================
def _approved_review(content, domain):
    return (
        content.env["fix.knowledge.review"]
        .sudo()
        .search(
            [
                *domain,
                ("state", "=", "approved"),
                ("content_hash", "=", content._fix_review_hash()),
            ],
            order="id desc",
            limit=1,
        )
    )


def _reviewed_publisher(content, reviewer_id, legacy):
    """M61 capture audit (BRU-KMS-02 H, BRU-KMS-03 H): content reaches the
    field reviewed. An approved review of the CURRENT content names the
    reviewer. Without one, ordinary content is published only by a Knowledge
    Publisher who did not write it (the publisher's own review), and
    safety-critical content only through a review that carries the Quality
    Manager's sign-off. Superuser code keeps the old path (`legacy`)."""
    review = content._fix_approved_review()
    if review:
        if reviewer_id and reviewer_id != review.reviewer_id.id:
            raise UserError(
                "'%s' was reviewed by %s under %s: publishing names that review, not "
                "another reviewer." % (content.name, review.reviewer_id.name, review.name)
            )
        return review.reviewer_id
    if content.env.su:
        return legacy(reviewer_id)
    if content.safety_critical:
        raise UserError(
            "'%s' is safety-critical (electrical, battery or high-voltage work, or a "
            "safety bulletin). It is published only through an approved review that "
            "carries the Quality Manager's safety sign-off (BRU-KMS-03). Request a "
            "review on the Review Workflow page." % content.name
        )
    if reviewer_id:
        raise UserError(
            "A reviewer is named by an approved review of '%s', not typed at "
            "publication (BRU-KMS-02). Request a review on the Review Workflow page." % content.name
        )
    if content.env.user in content._fix_authors():
        raise UserError(
            "You wrote '%s'. Content is published only after technical review by a "
            "qualified reviewer who is not its author (BRU-KMS-02): request a review, "
            "or let another Knowledge Publisher review and publish it." % content.name
        )
    # a Knowledge Publisher who did not write it reviews it by publishing
    return content.env.user


# ======================================================================
# Article: contributor, version history, feedback figures, the flag
# ======================================================================
class FixKnowledgeArticleCapture(models.Model):
    _inherit = "fix.knowledge.article"

    contributor_id = fields.Many2one(
        "res.users",
        string="Contributor (Field Capture)",
        readonly=True,
        index=True,
        help="The technician whose field capture this article was structured from "
        "(FR-KMS-029 contribution).",
    )
    capture_id = fields.Many2one(
        "fix.knowledge.capture", string="From Field Capture", readonly=True, index=True
    )
    original_capture_text = fields.Text(
        string="Contributor's Original Words",
        readonly=True,
        help="Kept beside the structured text, never overwritten (BRU-KMS-09).",
    )
    review_ids = fields.One2many("fix.knowledge.review", "article_id", string="Reviews")
    version_ids = fields.One2many(
        "fix.knowledge.article.version", "article_id", string="Version History"
    )
    link_ids = fields.One2many("fix.knowledge.link", "article_id", string="Operational Links")
    feedback_ids = fields.One2many("fix.knowledge.feedback", "article_id", string="Feedback")
    feedback_count = fields.Integer(
        string="Feedback Received", compute="_compute_feedback_stats", store=True
    )
    avg_rating = fields.Float(
        string="Average Rating (1-5)",
        compute="_compute_feedback_stats",
        store=True,
        digits=(3, 2),
    )
    resolution_rate = fields.Float(
        string="Resolved It (%)",
        compute="_compute_feedback_stats",
        store=True,
        digits=(5, 1),
        help="Share of 'did this resolve it?' answers that said yes.",
    )
    flagged_on = fields.Date(
        string="Flagged On",
        readonly=True,
        help="Set when users repeatedly say it did not resolve the fault or rate it "
        "low (AUT-KMS-17); cleared by the next publication or revision.",
    )
    flag_reason = fields.Char(string="Why Flagged", readonly=True)
    review_status = fields.Char(string="Review", compute="_compute_review_status")

    @api.depends("feedback_ids.rating", "feedback_ids.resolved")
    def _compute_feedback_stats(self):
        for rec in self:
            rows = rec.feedback_ids
            rec.feedback_count = len(rows)
            rec.avg_rating = sum(rows.mapped("rating")) / len(rows) if rows else 0.0
            yes = len(rows.filtered(lambda f: f.resolved == "yes"))
            rec.resolution_rate = round(yes / len(rows) * 100.0, 1) if rows else 0.0

    def _compute_review_status(self):
        labels = dict(self.env["fix.knowledge.review"]._fields["state"].selection)
        for rec in self:
            last = rec.review_ids.sorted("id")[-1:] if rec.review_ids else rec.review_ids
            rec.review_status = (
                "%s — %s" % (last.name, labels.get(last.state, last.state)) if last else "—"
            )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "contributor_id",
            "capture_id",
            "original_capture_text",
            "feedback_count",
            "avg_rating",
            "resolution_rate",
            "flagged_on",
            "flag_reason",
        }

    def _fix_authors(self):
        self.ensure_one()
        return self.create_uid | self.owner_id | self.contributor_id

    def _fix_review_hash(self) -> str:
        self.ensure_one()
        return self.content_hash or ""

    def _fix_review_domain(self):
        return [("article_id", "=", self.id)]

    def _fix_approved_review(self):
        self.ensure_one()
        return _approved_review(self, self._fix_review_domain())

    def _fix_publish_reviewer(self, reviewer_id=None):
        self.ensure_one()
        return _reviewed_publisher(self, reviewer_id, super()._fix_publish_reviewer)

    def _fix_after_publish(self, note):
        """FR-KMS-007: every published version is kept, with who and when; a
        new version clears the usefulness flag it answers."""
        res = super()._fix_after_publish(note)
        for rec in self:
            self.env["fix.knowledge.article.version"].sudo().create(
                {
                    "article_id": rec.id,
                    "version": rec.version,
                    "name": rec.name,
                    "title_bn": rec.title_bn,
                    "content": rec.content,
                    "content_bn": rec.content_bn,
                    "content_hash": rec.content_hash,
                    "change_note": note,
                    "changed_by_id": self.env.user.id,
                    "reviewed_by_id": rec.reviewed_by_id.id,
                }
            )
            if rec.flagged_on:
                rec._guarded().write({"flagged_on": False, "flag_reason": False})
        return res

    def action_archive(self):
        res = super().action_archive()
        # BRU-KMS-05 / AUT-KMS-06: retired content leaves every offline set
        sets = (
            self.env["fix.knowledge.offline.set"].sudo().search([("article_ids", "in", self.ids)])
        )
        for oset in sets:
            gone = oset.article_ids & self
            oset._guarded().write({"article_ids": [(3, a.id) for a in gone]})
            oset.message_post(
                body="Removed from the offline set: %s (archived)." % ", ".join(gone.mapped("name"))
            )
        return res

    def _fix_check_flag(self):
        """AUT-KMS-17: repeated 'did not resolve' or a low rating flags it."""
        self.ensure_one()
        current = self.feedback_ids.filtered(lambda f: f.version == self.version).sorted("id")
        reason = False
        last = current[-FLAG_NO_RUN:]
        if len(last) == FLAG_NO_RUN and all(f.resolved == "no" for f in last):
            reason = "%d users in a row said it did not resolve the fault" % FLAG_NO_RUN
        elif len(current) >= FLAG_MIN_RATINGS:
            avg = sum(current.mapped("rating")) / len(current)
            if avg < FLAG_LOW_AVG:
                reason = "average rating %.1f/5 over %d ratings" % (avg, len(current))
        if reason and not self.flagged_on:
            self._guarded().write(
                {"flagged_on": fields.Date.context_today(self), "flag_reason": reason}
            )
            self.message_post(body="Flagged for revision: %s (AUT-KMS-17)." % reason)
            owner = self.owner_id or self.create_uid
            if owner:
                self.sudo().activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=owner.id,
                    summary="Revise or retire: %s" % self.name,
                    note="Flagged by usefulness feedback: %s." % reason,
                )

    @api.model
    def surface_for(self, fault_code_id=None, device_model_id=None, brand_id=None, limit=10):
        """FR-KMS-015 context-aware surfacing: the published articles and trees
        for a job's fault code, model and brand, ranked by link relevance and
        then by how often they resolved the fault (FR-KMS-014)."""
        links = self.env["fix.knowledge.link"]
        domain = []
        for name, value in (
            ("fault_code_id", fault_code_id),
            ("device_model_id", device_model_id),
            ("brand_id", brand_id),
        ):
            if value:
                domain = (["|", *domain] if domain else []) + [(name, "=", value)]
        hits = {}
        for link in links.search(domain) if domain else links:
            target = link.article_id or link.tree_id
            if not target or target.state != "published":
                continue
            key = (target._name, target.id)
            hits.setdefault(key, [target, 0])[1] += link.relevance_weight
        model = self.env["fix.device.model"].browse(device_model_id) if device_model_id else None
        brand = self.env["fix.brand"].browse(brand_id) if brand_id else None
        brand_name = (brand.name if brand else (model.brand_id.name if model else "")) or ""
        if brand_name:
            text_domain = [("state", "=", "published"), ("device_brand", "=ilike", brand_name)]
            for art in self.search(text_domain):
                if model and art.device_model and art.device_model.lower() != model.name.lower():
                    continue
                hits.setdefault((art._name, art.id), [art, 0])[1] += 1
        rows = []
        for target, weight in hits.values():
            rate = getattr(target, "resolution_rate", 0.0) or 0.0
            rows.append(
                {
                    "kind": "article" if target._name == self._name else "tree",
                    "id": target.id,
                    "name": target.name,
                    "relevance": weight,
                    "resolution_rate": rate,
                    "review_overdue": bool(
                        getattr(target, "review_due", False)
                        and target.review_due <= fields.Date.context_today(self)
                    ),
                }
            )
        rows.sort(key=lambda r: (-r["relevance"], -r["resolution_rate"], r["name"]))
        return rows[:limit]


# ======================================================================
# Troubleshooting tree: decision nodes and the review gate
# ======================================================================
class FixKnowledgeTreeCapture(models.Model):
    _inherit = "fix.knowledge.tree"

    node_ids = fields.One2many("fix.knowledge.tree.node", "tree_id", string="Decision Steps")
    review_ids = fields.One2many("fix.knowledge.review", "tree_id", string="Reviews")
    link_ids = fields.One2many("fix.knowledge.link", "tree_id", string="Operational Links")
    node_count = fields.Integer(string="Nodes", compute="_compute_node_count")

    @api.depends("node_ids")
    def _compute_node_count(self):
        for rec in self:
            rec.node_count = len(rec.node_ids)

    def _fix_review_hash(self) -> str:
        self.ensure_one()
        parts = [
            self.name or "",
            self.device_brand or "",
            self.device_model or "",
            self.fault_symptom or "",
            self.tags or "",
            self.nodes_text or "",
        ]
        for node in self.node_ids.sorted(lambda n: (n.sequence, n.id)):
            parts.append(
                "|".join(
                    str(x or "")
                    for x in (
                        node.sequence,
                        node.node_type,
                        node.text,
                        node.text_bn,
                        node.expected,
                        node.yes_next,
                        node.no_next,
                        node.article_id.id,
                        node.safety_note,
                    )
                )
            )
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()

    def _fix_review_domain(self):
        return [("tree_id", "=", self.id)]

    def _fix_authors(self):
        self.ensure_one()
        return self.create_uid

    def _fix_approved_review(self):
        self.ensure_one()
        return _approved_review(self, self._fix_review_domain())

    def _fix_publish_reviewer(self, reviewer_id=None):
        self.ensure_one()
        return _reviewed_publisher(self, reviewer_id, super()._fix_publish_reviewer)


class FixKnowledgeTreeNode(models.Model):
    """FR-KMS-005: one step of a troubleshooting tree — a question, a check, a
    measurement or an outcome, with where each answer leads. A published
    tree's steps are what technicians follow: they change only while the tree
    is a draft."""

    _name = "fix.knowledge.tree.node"
    _description = "Troubleshooting Tree Node"
    _order = "tree_id, sequence, id"
    _rec_name = "text"

    tree_id = fields.Many2one(
        "fix.knowledge.tree", string="Tree", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="tree_id.company_id", store=True, index=True)
    sequence = fields.Integer(string="Step", default=10)
    node_type = fields.Selection(
        [
            ("question", "Question"),
            ("check", "Check"),
            ("measurement", "Measurement"),
            ("outcome", "Outcome"),
        ],
        string="Step Type",
        required=True,
        default="question",
    )
    text = fields.Char(string="Step (English)", required=True)
    text_bn = fields.Char(string="Step (Bengali)")
    expected = fields.Char(string="Expected Reading / Pass Condition")
    yes_next = fields.Char(string="If Yes / Pass → Go To")
    no_next = fields.Char(string="If No / Fail → Go To")
    article_id = fields.Many2one("fix.knowledge.article", string="Procedure Article")
    safety_note = fields.Char(string="Safety Note")

    def _refuse_unless_draft(self, trees):
        if self.env.su:
            return
        live = trees.filtered(lambda t: t.state != "draft")
        if live:
            raise UserError(
                "The steps of %s change only while the tree is a draft: a published tree "
                "is what technicians follow (FR-KMS-005). Archive it and publish a new "
                "tree for a change." % ", ".join(live.mapped("name"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        trees = self.env["fix.knowledge.tree"].browse(
            [v["tree_id"] for v in vals_list if v.get("tree_id")]
        )
        self._refuse_unless_draft(trees)
        return super().create(vals_list)

    def write(self, vals):
        trees = self.mapped("tree_id")
        if vals.get("tree_id"):
            trees |= self.env["fix.knowledge.tree"].browse(vals["tree_id"])
        self._refuse_unless_draft(trees)
        return super().write(vals)

    def unlink(self):
        self._refuse_unless_draft(self.mapped("tree_id"))
        return super().unlink()


# ======================================================================
# Page 1 — Review Request (Review Workflow)
# ======================================================================
class FixKnowledgeReview(models.Model):
    """BRU-KMS-02/03, §8.1 IN REVIEW: an author asks a named, qualified
    reviewer to review the content as it stands. The reviewer approves or
    returns it with comments; safety-critical content also needs the Quality
    Manager's sign-off. An approval covers the exact content reviewed: an
    edit after it needs a new review."""

    _name = "fix.knowledge.review"
    _description = "Knowledge Review Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Review No.", default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    article_id = fields.Many2one("fix.knowledge.article", string="Article", index=True)
    tree_id = fields.Many2one("fix.knowledge.tree", string="Troubleshooting Tree", index=True)
    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer",
        required=True,
        index=True,
        help="A Knowledge Publisher who did not write the content.",
    )
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    requested_on = fields.Datetime(
        string="Requested On", default=fields.Datetime.now, readonly=True
    )
    request_note = fields.Text(string="What to Look At")
    content_hash = fields.Char(string="Content Reviewed (hash)", readonly=True)
    safety_required = fields.Boolean(string="Safety Sign-off Required", readonly=True)
    state = fields.Selection(
        [
            ("requested", "Awaiting Review"),
            ("reviewed", "Reviewed — Awaiting Safety Sign-off"),
            ("approved", "Approved"),
            ("returned", "Returned to Author"),
            ("cancelled", "Cancelled"),
        ],
        default="requested",
        required=True,
        tracking=True,
    )
    comments = fields.Text(string="Reviewer's Comments", readonly=True)
    decided_on = fields.Datetime(string="Reviewed On", readonly=True)
    safety_approved_by_id = fields.Many2one(
        "res.users", string="Safety Sign-off By (Quality Manager)", readonly=True
    )
    safety_approved_on = fields.Datetime(string="Safety Sign-off On", readonly=True)
    content_changed = fields.Boolean(
        string="Content Changed Since Request", compute="_compute_content_changed"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "requested_by_id",
            "requested_on",
            "content_hash",
            "safety_required",
            "state",
            "comments",
            "decided_on",
            "safety_approved_by_id",
            "safety_approved_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"article_id", "tree_id", "reviewer_id", "request_note", "company_id"}
        return locked

    def _subject(self):
        self.ensure_one()
        return self.article_id or self.tree_id

    def _compute_content_changed(self):
        for rec in self:
            subject = rec.article_id or rec.tree_id
            rec.content_changed = bool(
                subject and rec.content_hash and subject._fix_review_hash() != rec.content_hash
            )

    @api.constrains("article_id", "tree_id")
    def _check_one_subject(self):
        for rec in self:
            if bool(rec.article_id) == bool(rec.tree_id):
                raise ValidationError("A review covers one article or one tree.")

    def _check_request(self, vals):
        """Refuse a bad request before any row exists (BRU-KMS-02)."""
        article = self.env["fix.knowledge.article"].browse(vals.get("article_id") or [])
        tree = self.env["fix.knowledge.tree"].browse(vals.get("tree_id") or [])
        if bool(article) == bool(tree):
            raise ValidationError("A review covers one article or one tree.")
        subject = (article or tree).sudo()
        reviewer = self.env["res.users"].sudo().browse(vals.get("reviewer_id") or [])
        open_other = self.sudo().search(
            [
                ("state", "in", ("requested", "reviewed")),
                ("article_id", "=", article.id or False),
                ("tree_id", "=", tree.id or False),
            ],
            limit=1,
        )
        if open_other:
            raise UserError("%s already has an open review (%s)." % (subject.name, open_other.name))
        if self.env.su:
            return
        if subject.state != "draft":
            raise UserError(
                "%s is %s: a review is requested for draft content, before it "
                "reaches the field." % (subject.name, subject.state)
            )
        if not reviewer or not _is_publisher(reviewer):
            raise UserError(
                "The reviewer of '%s' must be a Knowledge Publisher (BRU-KMS-02)." % subject.name
            )
        if reviewer in subject._fix_authors():
            raise UserError(
                "The reviewer of '%s' cannot be its author (BRU-KMS-02)." % subject.name
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_request(vals)
        records = super().create(vals_list)
        for rec in records:
            subject = rec._subject()
            rec._guarded().write(
                {
                    "name": _next(self.env, "fix.knowledge.review", "KREV/New"),
                    "content_hash": subject._fix_review_hash(),
                    "safety_required": bool(subject.safety_critical),
                }
            )
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=rec.reviewer_id.id,
                summary="Review: %s" % subject.name,
            )
        return records

    def write(self, vals):
        if not self.env.su and {"article_id", "tree_id", "reviewer_id"} & set(vals):
            for rec in self:
                for name in ("article_id", "tree_id", "reviewer_id"):
                    if name in vals and rec._fix_guard_differs(name, vals[name], rec[name]):
                        raise UserError(
                            "%s names its content and reviewer when it is requested; "
                            "cancel it and request a new one to change them." % rec.name
                        )
        return super().write(vals)

    def _require_unchanged(self):
        self.ensure_one()
        if self.content_changed:
            raise UserError(
                "%s has changed since %s was requested: return it, and request a new "
                "review of the content as it now stands." % (self._subject().name, self.name)
            )

    def action_approve(self, note=""):
        """The named reviewer passes the content (technical review)."""
        for rec in self:
            if rec.state != "requested":
                raise UserError("%s is not awaiting review." % rec.name)
            _only_by(
                self.env, rec.reviewer_id, "Only %s reviews %s." % (rec.reviewer_id.name, rec.name)
            )
            rec._require_unchanged()
            nxt = "reviewed" if rec.safety_required else "approved"
            rec._guarded().write(
                {"state": nxt, "decided_on": fields.Datetime.now(), "comments": note or False}
            )
            rec.message_post(
                body="Technical review passed by %s%s."
                % (
                    self.env.user.name,
                    " — awaiting the Quality Manager's safety sign-off (BRU-KMS-03)"
                    if nxt == "reviewed"
                    else "",
                )
            )
        return True

    def action_return(self, note=""):
        """Back to the author with the reviewer's comments (kept)."""
        for rec in self:
            if rec.state not in ("requested", "reviewed"):
                raise UserError("%s is not open." % rec.name)
            if not (note or "").strip():
                raise UserError("Say what the author should change in %s." % rec.name)
            if not self.env.su:
                allowed = self.env.user == rec.reviewer_id or (
                    rec.state == "reviewed" and _is_quality_manager(self.env, self.env.user)
                )
                if not allowed:
                    raise UserError(
                        "Only the reviewer (or the Quality Manager at sign-off) returns %s."
                        % rec.name
                    )
            rec._guarded().write(
                {"state": "returned", "decided_on": fields.Datetime.now(), "comments": note.strip()}
            )
            author = rec._subject().create_uid
            if author:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=author.id,
                    summary="Returned: %s" % rec._subject().name,
                    note=note.strip(),
                )
        return True

    def action_safety_approve(self, note=""):
        """BRU-KMS-03: the Quality Manager's additional approval of
        safety-critical content — never its author or its reviewer."""
        for rec in self:
            if rec.state != "reviewed":
                raise UserError("%s is not awaiting a safety sign-off." % rec.name)
            if not self.env.su:
                if not _is_quality_manager(self.env, self.env.user):
                    raise UserError(
                        "Only the Quality Manager signs off safety content (BRU-KMS-03)."
                    )
                if self.env.user in rec._subject()._fix_authors() | rec.reviewer_id:
                    raise UserError(
                        "The safety sign-off of %s is given by someone who neither wrote nor "
                        "reviewed it." % rec.name
                    )
            rec._require_unchanged()
            rec._guarded().write(
                {
                    "state": "approved",
                    "safety_approved_by_id": self.env.user.id,
                    "safety_approved_on": fields.Datetime.now(),
                    "comments": "\n".join(x for x in (rec.comments, note) if x) or False,
                }
            )
            rec.message_post(body="Safety sign-off by %s (BRU-KMS-03)." % self.env.user.name)
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("requested", "reviewed"):
                raise UserError("%s is not open." % rec.name)
            if not (
                self.env.su or self.env.user == rec.requested_by_id or _is_publisher(self.env.user)
            ):
                raise UserError("Only who requested %s, or a publisher, cancels it." % rec.name)
            rec._guarded().write({"state": "cancelled"})
        return True


# ======================================================================
# Page 1 — Version history (written by publication, never typed)
# ======================================================================
class FixKnowledgeArticleVersion(models.Model):
    """FR-KMS-007: each published version of an article, kept as published."""

    _name = "fix.knowledge.article.version"
    _description = "Knowledge Article Version"
    _inherit = ["fix.guarded.mixin"]
    _order = "article_id, version desc, id desc"

    article_id = fields.Many2one(
        "fix.knowledge.article", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="article_id.company_id", store=True, index=True)
    version = fields.Integer(required=True)
    name = fields.Char(string="Title (English)")
    title_bn = fields.Char(string="Title (Bengali)")
    content = fields.Html(string="Content (English)", sanitize=True)
    content_bn = fields.Html(string="Content (Bengali)", sanitize=True)
    content_hash = fields.Char()
    change_note = fields.Selection(
        [("published", "Published"), ("revised", "Revised While Published")], required=True
    )
    changed_by_id = fields.Many2one("res.users", string="By")
    changed_on = fields.Datetime(string="On", default=fields.Datetime.now)
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._fields) - {
            "id",
            "display_name",
            "create_uid",
            "create_date",
            "write_uid",
            "write_date",
        }


# ======================================================================
# Page 1 — Field Capture (the improvement queue)
# ======================================================================
class FixKnowledgeCapture(models.Model):
    """FR-KMS-023/024/027, BRU-KMS-08/09: a technician records how they fixed
    something hard, in their own words (Bengali is fine), with a photo or a
    voice note. It is never discarded: a Knowledge Publisher takes it into
    the improvement queue and structures it into a draft article, or merges
    it into the article that already covers it. The original words are kept."""

    _name = "fix.knowledge.capture"
    _description = "Knowledge Field Capture"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Capture No.", default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    captured_by_id = fields.Many2one(
        "res.users",
        string="Captured By",
        default=lambda self: self.env.user,
        readonly=True,
        index=True,
    )
    captured_on = fields.Datetime(string="Captured On", default=fields.Datetime.now, readonly=True)
    service_order_id = fields.Many2one(
        "fix.service.order",
        string="Job (Service Order)",
        index=True,
        help="The job this was solved on: its device's brand and model and its first "
        "fault code are filled in when left blank (FR-KMS-023).",
    )
    device_brand = fields.Char(string="Brand")
    device_model = fields.Char(string="Model")
    fault_code_id = fields.Many2one("fix.fault.code", string="Fault Code")
    fault_symptom = fields.Char(string="Symptom")
    rework_level = fields.Selection(LEVELS, string="Repair Level")
    raw_text = fields.Text(
        string="What You Did (Your Own Words)",
        required=True,
        help="Rough, Bengali or English: a reviewer structures it later and the "
        "original is kept (BRU-KMS-08/09).",
    )
    photo_attachment_id = fields.Many2one("ir.attachment", string="Photo")
    voice_attachment_id = fields.Many2one("ir.attachment", string="Voice Note")
    state = fields.Selection(
        [
            ("queued", "In Improvement Queue"),
            ("taken", "Being Structured"),
            ("drafted", "Draft Article Created"),
            ("merged", "Merged into Existing Article"),
        ],
        default="queued",
        required=True,
        tracking=True,
    )
    reviewer_id = fields.Many2one(
        "res.users", string="Reviewer / Technical Writer", readonly=True, index=True
    )
    taken_on = fields.Datetime(readonly=True)
    article_id = fields.Many2one("fix.knowledge.article", string="Resulting Article", readonly=True)
    handled_on = fields.Datetime(string="Structured On", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "captured_by_id",
            "captured_on",
            "state",
            "reviewer_id",
            "taken_on",
            "article_id",
            "handled_on",
        }

    _FROZEN = (
        "raw_text",
        "service_order_id",
        "device_brand",
        "device_model",
        "fault_code_id",
        "fault_symptom",
        "rework_level",
        "photo_attachment_id",
        "voice_attachment_id",
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and (self.state != "queued" or self.env.user != self.captured_by_id):
            locked |= set(self._FROZEN)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"name": _next(self.env, "fix.knowledge.capture", "KCAP/New")})
            rec._prefill_from_job()
        return records

    def _prefill_from_job(self):
        order = self.service_order_id.sudo()
        if not order:
            return
        vals = {}
        device = getattr(order, "device_id", False)
        dmodel = device.device_model_id if device else False
        if dmodel and not self.device_model:
            vals["device_model"] = dmodel.name
        if dmodel and dmodel.brand_id and not self.device_brand:
            vals["device_brand"] = dmodel.brand_id.name
        if not self.fault_code_id:
            codes = [c for c in order.fault_line_ids.mapped("fault_code") if c]
            if codes:
                code = (
                    self.env["fix.fault.code"]
                    .sudo()
                    .search([("code", "=ilike", codes[0].strip())], limit=1)
                )
                if code:
                    vals["fault_code_id"] = code.id
        if vals:
            self.sudo().write(vals)

    def write(self, vals):
        if not self.env.su and set(self._FROZEN) & set(vals):
            for rec in self:
                changed = [
                    n
                    for n in self._FROZEN
                    if n in vals and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed and (rec.state != "queued" or self.env.user != rec.captured_by_id):
                    raise UserError(
                        "%s keeps the contributor's own words as captured: only %s changes "
                        "them, and only while it waits in the queue (BRU-KMS-09)."
                        % (rec.name, rec.captured_by_id.name)
                    )
        return super().write(vals)

    def action_take(self):
        """A Knowledge Publisher takes the capture to structure it."""
        require_publisher(self.env)
        for rec in self:
            if rec.state != "queued":
                raise UserError("%s is not waiting in the queue." % rec.name)
            if not self.env.su and self.env.user == rec.captured_by_id:
                raise UserError(
                    "%s is your own capture: another publisher structures it, so the "
                    "article is reviewed by someone other than its contributor." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "taken",
                    "reviewer_id": self.env.user.id,
                    "taken_on": fields.Datetime.now(),
                }
            )
        return True

    def _require_taker(self):
        self.ensure_one()
        if self.state != "taken":
            raise UserError("Take %s into the queue first." % self.name)
        _only_by(
            self.env,
            self.reviewer_id,
            "%s is being structured by %s." % (self.name, self.reviewer_id.name),
        )

    def action_draft_article(self):
        """Structure the capture into a draft article, pre-filled from it,
        carrying the contributor's original words (FR-KMS-023, BRU-KMS-09)."""
        for rec in self:
            rec._require_taker()
            first = (
                (rec.raw_text or "").strip().splitlines()[0] if (rec.raw_text or "").strip() else ""
            )
            title = (first[:80] or rec.name).strip()
            body = "<p>%s</p>" % "<br/>".join(
                str(escape(line)) for line in rec.raw_text.splitlines()
            )
            article = (
                self.env["fix.knowledge.article"]
                ._guarded()
                .create(
                    {
                        "name": title,
                        "category": "troubleshooting",
                        "content": body,
                        "device_brand": rec.device_brand,
                        "device_model": rec.device_model,
                        "fault_symptom": rec.fault_symptom
                        or (rec.fault_code_id.name if rec.fault_code_id else False),
                        "rework_level": rec.rework_level or "L2",
                        "contributor_id": rec.captured_by_id.id,
                        "capture_id": rec.id,
                        "original_capture_text": rec.raw_text,
                    }
                )
            )
            if rec.fault_code_id:
                self.env["fix.knowledge.link"].create(
                    {"article_id": article.id, "fault_code_id": rec.fault_code_id.id}
                )
            for att in rec.photo_attachment_id | rec.voice_attachment_id:
                att.sudo().copy({"res_model": article._name, "res_id": article.id})
            rec._guarded().write(
                {"state": "drafted", "article_id": article.id, "handled_on": fields.Datetime.now()}
            )
            rec.message_post(body="Structured into draft article %s." % article.name)
        return True

    def action_merge(self, article_ref=""):
        """The knowledge already exists: the capture is merged into that
        article (its words are posted on the article; nothing is discarded)."""
        for rec in self:
            rec._require_taker()
            ref = (article_ref or "").strip()
            if not ref:
                raise UserError(
                    "Name the article (its reference code or number) %s merges into." % rec.name
                )
            Article = self.env["fix.knowledge.article"]
            article = Article.search([("article_code", "=ilike", ref)], limit=1)
            if not article and ref.isdigit():
                article = Article.browse(int(ref)).exists()
            if not article:
                raise UserError("No article %s." % ref)
            article.message_post(
                body="Field capture %s by %s merged here. Original words: %s"
                % (rec.name, rec.captured_by_id.name, escape(rec.raw_text))
            )
            rec._guarded().write(
                {"state": "merged", "article_id": article.id, "handled_on": fields.Datetime.now()}
            )
        return True


# ======================================================================
# Page 3 — Technical Library entry
# ======================================================================
class FixKnowledgeLibrary(models.Model):
    """FR-KMS-004, BRU-KMS-16: a manual, service manual, wiring or board
    diagram, schematic, exploded view or parts diagram, indexed by brand and
    model, with its file and the terms it may be used under. Only an entry
    whose terms allow it reaches the technicians' offline sets."""

    _name = "fix.knowledge.library"
    _description = "Technical Library Entry"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "brand_id, name"

    name = fields.Char(string="Title", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    entry_type = fields.Selection(
        [
            ("repair_manual", "Repair Manual"),
            ("service_manual", "Service Manual"),
            ("wiring_diagram", "Wiring Diagram"),
            ("board_diagram", "Board Diagram / Boardview"),
            ("schematic", "Schematic"),
            ("exploded_view", "Exploded View"),
            ("parts_diagram", "Parts Diagram"),
        ],
        string="Entry Type",
        required=True,
        default="service_manual",
    )
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True, index=True)
    device_model_ids = fields.Many2many(
        "fix.device.model",
        "fix_knowledge_library_model_rel",
        "library_id",
        "model_id",
        string="Models Covered",
    )
    model_text = fields.Char(string="Other Models (not in the catalogue)")
    document_attachment_id = fields.Many2one("ir.attachment", string="Manual / Diagram File")
    document_ref = fields.Char(string="M24 Document Reference")
    page_count = fields.Integer(string="Pages")
    source = fields.Selection(
        [
            ("brand_portal", "Brand Documentation Portal"),
            ("brand_partner", "Brand Partner (sent to us)"),
            ("internal", "Internal (our own)"),
            ("third_party", "Third Party"),
        ],
        string="Source",
        required=True,
        default="brand_portal",
    )
    licence_terms = fields.Text(string="Licence / Usage Terms")
    redistribution = fields.Selection(
        [
            ("internal_desk", "Internal — workstations only"),
            ("technicians", "Technicians — including offline devices"),
            ("brand_authorised", "Brand-authorised technicians only — no offline copy"),
        ],
        string="Who May Use It",
        required=True,
        default="internal_desk",
    )
    offline_allowed = fields.Boolean(
        string="May Go Offline", compute="_compute_offline_allowed", store=True
    )
    state = fields.Selection(
        [("draft", "Draft"), ("available", "Available"), ("withdrawn", "Withdrawn")],
        default="draft",
        required=True,
        tracking=True,
    )
    made_available_by_id = fields.Many2one("res.users", string="Made Available By", readonly=True)
    made_available_on = fields.Date(string="Available Since", readonly=True)
    withdrawn_reason = fields.Char(string="Why Withdrawn", readonly=True)

    _TERMS = (
        "brand_id",
        "device_model_ids",
        "model_text",
        "document_attachment_id",
        "document_ref",
        "licence_terms",
        "redistribution",
        "entry_type",
    )

    @api.depends("redistribution")
    def _compute_offline_allowed(self):
        for rec in self:
            rec.offline_allowed = rec.redistribution == "technicians"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "made_available_by_id",
            "made_available_on",
            "withdrawn_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS)
        return locked

    def write(self, vals):
        if not self.env.su and set(self._TERMS) & set(vals):
            for rec in self:
                if rec.state == "draft":
                    continue
                if any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in self._TERMS if n in vals
                ):
                    raise UserError(
                        "%s is %s: its file, index and terms are fixed. Withdraw it and "
                        "register a new entry for a new edition." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def action_make_available(self):
        require_publisher(self.env)
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft." % rec.name)
            missing = []
            if not (rec.document_attachment_id or (rec.document_ref or "").strip()):
                missing.append("the file (upload it, or give its M24 document reference)")
            if not (rec.device_model_ids or (rec.model_text or "").strip()):
                missing.append("the models it covers (FR-KMS-004)")
            if not (rec.licence_terms or "").strip():
                missing.append("the licence or usage terms (BRU-KMS-16)")
            if missing:
                raise UserError(
                    "Before %s is made available, record %s." % (rec.name, "; ".join(missing))
                )
            rec._guarded().write(
                {
                    "state": "available",
                    "made_available_by_id": self.env.user.id,
                    "made_available_on": fields.Date.context_today(rec),
                }
            )
        return True

    def action_withdraw(self, reason=""):
        require_publisher(self.env)
        for rec in self:
            if rec.state != "available":
                raise UserError(
                    "Only an available entry is withdrawn — %s is %s." % (rec.name, rec.state)
                )
            if not (reason or "").strip():
                raise UserError("Say why %s is withdrawn." % rec.name)
            rec._guarded().write({"state": "withdrawn", "withdrawn_reason": reason.strip()})
        return True


# ======================================================================
# Page 4 — Operational link (what context surfaces the content)
# ======================================================================
class FixKnowledgeLink(models.Model):
    """FR-KMS-006: an article or tree bound to a fault code, a device model or
    a brand of the catalogue, with a relevance weight. Context-aware
    surfacing (FR-KMS-015) reads these links."""

    _name = "fix.knowledge.link"
    _description = "Knowledge Operational Link"
    _inherit = ["fix.guarded.mixin"]
    _order = "relevance_weight desc, id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    article_id = fields.Many2one("fix.knowledge.article", string="Article", index=True)
    tree_id = fields.Many2one("fix.knowledge.tree", string="Troubleshooting Tree", index=True)
    fault_code_id = fields.Many2one("fix.fault.code", string="Fault Code", index=True)
    device_model_id = fields.Many2one("fix.device.model", string="Device Model", index=True)
    brand_id = fields.Many2one("fix.brand", string="Brand", index=True)
    link_type = fields.Selection(
        [("fault", "Fault Code"), ("model", "Device Model"), ("brand", "Brand")],
        string="Linked To",
        compute="_compute_link_type",
        store=True,
    )
    relevance_weight = fields.Integer(
        string="Relevance (1-10)", default=5, help="Higher surfaces first on a job."
    )
    linked_by_id = fields.Many2one(
        "res.users", string="Linked By", default=lambda self: self.env.user, readonly=True
    )

    @api.depends("fault_code_id", "device_model_id", "brand_id")
    def _compute_link_type(self):
        for rec in self:
            rec.link_type = (
                "fault"
                if rec.fault_code_id
                else "model"
                if rec.device_model_id
                else "brand"
                if rec.brand_id
                else False
            )

    @api.depends("article_id", "tree_id", "link_type")
    def _compute_display_name(self):
        for rec in self:
            target = rec.article_id or rec.tree_id
            subject = rec.fault_code_id or rec.device_model_id or rec.brand_id
            rec.display_name = "%s → %s" % (target.display_name or "?", subject.display_name or "?")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"linked_by_id"}

    @api.constrains(
        "article_id", "tree_id", "fault_code_id", "device_model_id", "brand_id", "relevance_weight"
    )
    def _check_link(self):
        for rec in self:
            if bool(rec.article_id) == bool(rec.tree_id):
                raise ValidationError("A link binds one article or one tree.")
            subjects = [x for x in (rec.fault_code_id, rec.device_model_id, rec.brand_id) if x]
            if len(subjects) != 1:
                raise ValidationError(
                    "A link names exactly one of: a fault code, a device model or a brand "
                    "(add one link per subject)."
                )
            if not 1 <= rec.relevance_weight <= 10:
                raise ValidationError("Relevance is between 1 and 10.")
            target = rec.article_id or rec.tree_id
            if target.state == "archived":
                raise ValidationError(
                    "%s is archived: it no longer surfaces on jobs." % target.name
                )
            twin = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("article_id", "=", rec.article_id.id or False),
                    ("tree_id", "=", rec.tree_id.id or False),
                    ("fault_code_id", "=", rec.fault_code_id.id or False),
                    ("device_model_id", "=", rec.device_model_id.id or False),
                    ("brand_id", "=", rec.brand_id.id or False),
                ]
            )
            if twin:
                raise ValidationError("%s is already linked to that." % target.name)


# ======================================================================
# Page 5 — Offline set (a technician's scope and storage budget)
# ======================================================================
class FixKnowledgeOfflineSet(models.Model):
    """FR-KMS-017/018, BRU-KMS-05: the published articles a technician's
    device holds offline, scoped by brand, model and repair level within a
    storage budget. Computing it takes only published, offline-flagged
    content; archiving an article removes it from every set."""

    _name = "fix.knowledge.offline.set"
    _description = "Technician Offline Knowledge Set"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Set No.", default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    user_id = fields.Many2one("res.users", string="Technician", required=True, index=True)
    brand_ids = fields.Many2many(
        "fix.brand", "fix_knowledge_offline_set_brand_rel", "set_id", "brand_id", string="Brands"
    )
    device_model_ids = fields.Many2many(
        "fix.device.model",
        "fix_knowledge_offline_set_model_rel",
        "set_id",
        "model_id",
        string="Models",
    )
    max_level = fields.Selection(LEVELS, string="Up to Repair Level", required=True, default="L2")
    budget_mb = fields.Float(string="Storage Budget (MB)", required=True, default=200.0)
    active = fields.Boolean(default=True)
    article_ids = fields.Many2many(
        "fix.knowledge.article",
        "fix_knowledge_offline_set_article_rel",
        "set_id",
        "article_id",
        string="Articles in the Set",
        readonly=True,
    )
    article_count = fields.Integer(string="Articles", compute="_compute_counts")
    stale_count = fields.Integer(
        string="No Longer Published",
        compute="_compute_counts",
        help="Articles in the set that are no longer published: recompute removes them.",
    )
    total_mb = fields.Float(string="Size (MB)", readonly=True, digits=(12, 6))
    over_budget_count = fields.Integer(string="Left Out (Over Budget)", readonly=True)
    computed_on = fields.Datetime(string="Computed On", readonly=True)
    computed_by_id = fields.Many2one("res.users", string="Computed By", readonly=True)
    last_synced_on = fields.Datetime(string="Last Synced On", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "article_ids",
            "total_mb",
            "over_budget_count",
            "computed_on",
            "computed_by_id",
            "last_synced_on",
        }

    @api.depends("article_ids", "article_ids.state")
    def _compute_counts(self):
        for rec in self:
            rec.article_count = len(rec.article_ids)
            rec.stale_count = len(rec.article_ids.filtered(lambda a: a.state != "published"))

    @api.constrains("user_id", "active", "budget_mb")
    def _check_set(self):
        for rec in self:
            if rec.budget_mb <= 0:
                raise ValidationError("The storage budget is more than 0 MB.")
            if rec.active and self.sudo().search_count(
                [("id", "!=", rec.id), ("user_id", "=", rec.user_id.id), ("active", "=", True)]
            ):
                raise ValidationError("%s already has an offline set." % rec.user_id.name)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"name": _next(self.env, "fix.knowledge.offline.set", "OFS/New")})
        return records

    @staticmethod
    def _article_mb(article):
        text = (article.content or "") + (article.content_bn or "")
        media = (
            article.env["fix.knowledge.media"]
            .sudo()
            .search([("article_id", "=", article.id), ("offline_available", "=", True)])
        )
        return len(text.encode("utf-8")) / (1024.0 * 1024.0) + sum(media.mapped("size_mb"))

    def action_compute(self):
        """Recompute the set within its budget (AUT-KMS-10): published,
        offline-flagged articles of its brands/models up to its level, the
        ones linked to its models first."""
        for rec in self:
            if not self.env.su and not (
                _is_publisher(self.env.user) or self.env.user == rec.user_id
            ):
                raise UserError(
                    "A Knowledge Publisher or %s recomputes %s." % (rec.user_id.name, rec.name)
                )
            if not (rec.brand_ids or rec.device_model_ids):
                raise UserError(
                    "Give %s its scope: the brands or models the technician works on." % rec.name
                )
            brands = {
                b.name.lower() for b in rec.brand_ids | rec.device_model_ids.mapped("brand_id")
            }
            models_ = {m.name.lower() for m in rec.device_model_ids}
            Article = self.env["fix.knowledge.article"].sudo()
            linked = (
                self.env["fix.knowledge.link"]
                .sudo()
                .search(
                    [
                        "|",
                        ("brand_id", "in", rec.brand_ids.ids),
                        ("device_model_id", "in", rec.device_model_ids.ids),
                    ]
                )
            )
            linked_ids = set(linked.mapped("article_id").ids)
            model_linked = set(
                linked.filtered(lambda link: link.device_model_id).mapped("article_id").ids
            )
            limit_rank = LEVEL_RANK.get(rec.max_level, 2)
            chosen = []
            for art in Article.search(
                [("state", "=", "published"), ("offline_available", "=", True)]
            ):
                if LEVEL_RANK.get(art.rework_level or "L2", 2) > limit_rank:
                    continue
                brand_ok = (art.device_brand or "").lower() in brands
                model_ok = (
                    not models_ or not art.device_model or art.device_model.lower() in models_
                )
                if art.id in linked_ids or (brand_ok and model_ok):
                    chosen.append(art)
            chosen.sort(
                key=lambda a: (
                    0 if a.id in model_linked else 1,
                    0 if (a.device_model or "").lower() in models_ else 1,
                    -(a.resolution_rate or 0.0),
                    a.id,
                )
            )
            kept, size, left = [], 0.0, 0
            for art in chosen:
                mb = self._article_mb(art)
                if size + mb > rec.budget_mb:
                    left += 1
                    continue
                kept.append(art.id)
                size += mb
            # authorised above (a publisher, or the technician for their own
            # set, who holds no write right on sets)
            rec.sudo()._guarded().write(
                {
                    "article_ids": [(6, 0, kept)],
                    "total_mb": round(size, 6),
                    "over_budget_count": left,
                    "computed_on": fields.Datetime.now(),
                    "computed_by_id": self.env.user.id,
                }
            )
            rec.sudo().message_post(
                body="Computed: %d article(s), %.3f MB of %.0f MB; %d left out over budget."
                % (len(kept), size, rec.budget_mb, left)
            )
        return True

    def offline_manifest(self):
        """What the technician app syncs: each article's version and hash, so
        a stale copy is replaced and a retired one deleted (FR-KMS-018)."""
        self.ensure_one()
        return [
            {
                "id": a.id,
                "code": a.article_code or "KB-%04d" % a.id,
                "version": a.version,
                "content_hash": a.content_hash,
                "review_overdue": bool(
                    a.review_due and a.review_due <= fields.Date.context_today(a)
                ),
            }
            for a in self.article_ids.filtered(lambda x: x.state == "published")
        ]

    def action_mark_synced(self):
        """The technician's device reports a completed sync."""
        for rec in self:
            _only_by(
                self.env, rec.user_id, "Only %s's device syncs %s." % (rec.user_id.name, rec.name)
            )
            rec.sudo()._guarded().write({"last_synced_on": fields.Datetime.now()})
        return True


# ======================================================================
# Page 6 — Usefulness feedback
# ======================================================================
class FixKnowledgeFeedback(models.Model):
    """FR-KMS-030: "did this resolve it?", a 1-5 rating and a comment from the
    person who used the article, on its current version. Given once and kept
    as given; it drives the article's usefulness figures and its flag."""

    _name = "fix.knowledge.feedback"
    _description = "Knowledge Usefulness Feedback"
    _inherit = ["fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Feedback", compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    article_id = fields.Many2one(
        "fix.knowledge.article", string="Article", required=True, index=True, ondelete="cascade"
    )
    version = fields.Integer(string="Version Rated", readonly=True)
    user_id = fields.Many2one(
        "res.users",
        string="Given By",
        default=lambda self: self.env.user,
        readonly=True,
        index=True,
    )
    service_order_id = fields.Many2one(
        "fix.service.order", string="Job (Service Order)", index=True
    )
    resolved = fields.Selection(
        [("yes", "Yes — it resolved the fault"), ("partial", "Partly"), ("no", "No")],
        string="Did This Resolve It?",
        required=True,
    )
    rating = fields.Integer(string="Rating (1-5)", required=True)
    comment = fields.Text(string="Comment / Suggested Improvement")
    captured_offline = fields.Boolean(string="Given Offline")
    captured_on = fields.Datetime(string="Given On", default=fields.Datetime.now, readonly=True)

    @api.depends("article_id", "user_id", "resolved")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s — %s" % (rec.article_id.name or "?", rec.user_id.name or "?")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"version", "user_id", "captured_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {
                "article_id",
                "service_order_id",
                "resolved",
                "rating",
                "comment",
                "captured_offline",
                "company_id",
            }
        return locked

    @api.constrains("rating")
    def _check_rating(self):
        for rec in self:
            if not 1 <= rec.rating <= 5:
                raise ValidationError("The rating is from 1 to 5.")

    def _check_given(self, vals):
        """Refuse before any row exists: published content, once per person,
        version and job."""
        art = self.env["fix.knowledge.article"].sudo().browse(vals.get("article_id") or [])
        if not art:
            return  # the required-field check names it
        if not self.env.su and art.state != "published":
            raise UserError(
                "%s is %s: feedback is given on published content in use." % (art.name, art.state)
            )
        user = self.env["res.users"].browse(vals.get("user_id") or self.env.user.id)
        order = self.env["fix.service.order"].sudo().browse(vals.get("service_order_id") or [])
        twin = self.sudo().search_count(
            [
                ("article_id", "=", art.id),
                ("user_id", "=", user.id),
                ("version", "=", art.version),
                ("service_order_id", "=", order.id or False),
            ]
        )
        if twin:
            raise UserError(
                "%s has already rated version %d of %s%s."
                % (user.name, art.version, art.name, " on %s" % order.name if order else "")
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_given(vals)
        records = super().create(vals_list)
        for rec in records:
            art = rec.article_id.sudo()
            # the stamps are the system's: the giver holds no write right on
            # feedback (it is kept as given)
            rec.sudo()._guarded().write({"version": art.version})
            if rec.resolved == "yes":
                art._guarded().write({"helpful_votes": (art.helpful_votes or 0) + 1})
            art._fix_check_flag()
        return records

    def write(self, vals):
        if not self.env.su and not self._fix_guard_has_token():
            # the stamps answer to the guard (its own message); the answer itself
            # is kept as given
            editable = set(vals) - {"name"} - self._fix_guarded_fields()
            for rec in self:
                if any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in editable if n in rec._fields
                ):
                    raise UserError("Feedback is kept as given (FR-KMS-030).")
        return super().write(vals)
