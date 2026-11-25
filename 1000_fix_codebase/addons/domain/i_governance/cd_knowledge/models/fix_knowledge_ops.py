# fix_knowledge_ops — M61: troubleshooting trees, media assets and brand
# bulletins/recalls. Articles live in fix_knowledge.py.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

from .fix_knowledge import is_safety_content, require_publisher, require_reviewer

# A10 P1-7 (M61-4): a safety recall closes under the Quality Manager, not
# under whoever typed last.
QM_GROUP = "cd_qms_process.group_qms_quality_manager"


def _qm_gate(env, message):
    """The Quality Manager gate without a manifest dependency on
    cd_qms_process (a hard depends would create a dependency loop through
    the recall/billing consumers — see the manifest note). The group is
    resolved through ir.model.data; on a database without the QMS module
    the group cannot exist, so nobody passes: fail closed."""
    if env.su:
        return
    group = env.ref(QM_GROUP, raise_if_not_found=False)
    if group and env.user.has_group(QM_GROUP):
        return
    raise UserError(message)


class FixKnowledgeTree(models.Model):
    """A troubleshooting tree drives a technician's live decisions, so it is
    published under the same review gate as an article (A10 K1, M61-1)."""

    _name = "fix.knowledge.tree"
    _description = "Troubleshooting Tree"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    device_brand = fields.Char(string="Brand")
    device_model = fields.Char(string="Model / Chassis")
    fault_symptom = fields.Char(string="Entry Symptom")
    tags = fields.Char(
        string="Search Tags",
        help="Comma-separated keywords; electrical/battery/high-voltage tags make "
        "this tree safety-critical (review required before publishing, A10 K1).",
    )
    nodes_text = fields.Text(
        string="Decision Nodes",
        help="Ordered decision steps: question -> yes/no branch -> action.",
    )
    linked_article_id = fields.Many2one("fix.knowledge.article", string="Root Article")
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True)
    reviewed_on = fields.Date(string="Reviewed On", readonly=True)
    safety_critical = fields.Boolean(string="Safety-Critical", compute="_compute_safety_critical")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("archived", "Archived")],
        required=True,
        default="draft",
    )

    @api.depends("tags")
    def _compute_safety_critical(self):
        for rec in self:
            rec.safety_critical = is_safety_content(rec.tags)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "reviewed_by_id", "reviewed_on"}

    def action_publish(self, reviewer_id=None):
        require_publisher(self.env)
        for rec in self:
            if rec.state == "published":
                raise UserError("%s is already published." % rec.name)
            reviewer = rec._fix_publish_reviewer(reviewer_id)
            rec._guarded().write(
                {
                    "state": "published",
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
            rec.message_post(
                body="Tree published by %s%s."
                % (
                    self.env.user.name,
                    " — reviewed by %s" % reviewer.name if reviewer else "",
                )
            )
        return True

    def _fix_publish_reviewer(self, reviewer_id=None):
        """As the article's (A10 K1); extended by the review workflow."""
        self.ensure_one()
        rid = reviewer_id or self.reviewed_by_id.id
        reviewer = self.env["res.users"].browse(rid).exists() if rid else self.env["res.users"]
        if self.safety_critical or reviewer:
            require_reviewer(self, reviewer, self.create_uid.id)
        return reviewer

    def action_archive(self):
        require_publisher(self.env)
        for rec in self:
            if rec.state != "published":
                raise UserError(
                    "Only a published tree is archived — %s is %s." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "archived"})
        return True


class FixKnowledgeMedia(models.Model):
    _name = "fix.knowledge.media"
    _description = "Knowledge Media Asset"
    _inherit = ["fix.guarded.mixin"]
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
    _inherit = ["mail.thread", "fix.guarded.mixin"]
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
    affected_models = fields.Char(
        string="Affected Models",
        help="Comma-separated device model names in scope (A10 P1-7): a "
        "recall with no affected model is a rumour, not a recall.",
    )
    serial_scope = fields.Char(
        string="Serials in Scope",
        help="Exact serials or ranges in scope, e.g. 'SN-1001..SN-1050, SN-1099' "
        "(A10 P1-7); the branches check devices against this list.",
    )
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
        tracking=True,
    )
    recipient_ids = fields.One2many(
        "fix.knowledge.bulletin.recipient", "bulletin_id", string="Recipient Branches"
    )
    recipients_total = fields.Integer(
        string="Recipients", compute="_compute_recipients", store=True
    )
    recipients_acknowledged = fields.Integer(
        string="Acknowledged", compute="_compute_recipients", store=True
    )

    @api.depends("recipient_ids.acknowledged_on")
    def _compute_recipients(self):
        for rec in self:
            rec.recipients_total = len(rec.recipient_ids)
            rec.recipients_acknowledged = len(
                rec.recipient_ids.filtered(lambda r: r.acknowledged_on)
            )

    def _fix_guarded_fields(self) -> set:
        # R1: the state is the distribution record — received → distributed →
        # closed moves only through the actions (A10 P1-7 adds the recipient
        # acknowledgement lines and the Quality Manager's closure).
        return super()._fix_guarded_fields() | {"state"}

    def write(self, vals):
        # A10 P1-7 (M61-4): the audit closed a HIGH recall by downgrading it to
        # LOW with a plain write. Once a bulletin is distributed, its
        # classification (severity, type) is the thing the field acted on and
        # cannot be rewritten — a correction is a new bulletin. Superuser code
        # (the relay, crons) is trusted.
        if not self.env.su and ({"severity", "bulletin_type"} & set(vals or {})):
            for rec in self:
                if rec.state in ("distributed", "closed"):
                    raise UserError(
                        "The classification of %s is locked while %s — severity and "
                        "type cannot be rewritten after distribution. Issue a new "
                        "bulletin for a correction (A10 P1-7)." % (rec.name, rec.state)
                    )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.knowledge.bulletin") or "BUL/New"
                )
        return super().create(vals_list)

    def _recall_scope_linked(self) -> bool:
        self.ensure_one()
        return bool((self.affected_models or "").strip() or (self.serial_scope or "").strip())

    def action_distribute(self):
        require_publisher(self.env)
        for rec in self:
            if rec.state != "received":
                raise UserError(
                    "Only a received bulletin is distributed — %s is %s." % (rec.name, rec.state)
                )
            if rec.bulletin_type == "recall":
                # A10 P1-7 (M61-4): a recall is distributed only over what it
                # recalls and to branches that hold it.
                if not rec._recall_scope_linked():
                    raise UserError(
                        "Link %s to what it recalls — affected models or serials in "
                        "scope — before distributing it. A recall with no affected "
                        "model is a rumour, not a recall (A10 P1-7)." % rec.name
                    )
                if not rec.recipient_ids:
                    raise UserError(
                        "Name the recipient branch(es) of %s — a recall nobody holds "
                        "is not distributed (A10 P1-7)." % rec.name
                    )
            rec._guarded().write({"state": "distributed"})
            publish(
                self.env,
                "bulletin.distributed",
                "fix.knowledge.bulletin",
                rec.id,
                {
                    "name": rec.name,
                    "brand": rec.brand or "",
                    "bulletin_type": rec.bulletin_type,
                    "severity": rec.severity,
                    "affected_models": rec.affected_models or "",
                    "serial_scope": rec.serial_scope or "",
                    "summary": rec.summary or "",
                    "issued_on": str(rec.issued_on or ""),
                    "recipients": [
                        {
                            "operating_unit": r.branch_id.name or "",
                            "employee": r.employee_id.name or "",
                        }
                        for r in rec.recipient_ids
                    ],
                },
                metadata={"module": "cd_knowledge", "reason": "A10 P1-7 recall routing"},
            )
            rec.message_post(
                body="Distributed to %d recipient branch(es) by %s."
                % (len(rec.recipient_ids), self.env.user.name)
            )
        return True

    def action_acknowledge(self, recipient_id=None):
        """A recipient branch holds its bulletin: its duty officer (or, when
        the employee record carries the branch, any of that branch's staff)
        acknowledges it (A10 P1-7, M61-4)."""
        for rec in self:
            if rec.state != "distributed":
                raise UserError(
                    "%s is %s — a branch acknowledges a distributed bulletin."
                    % (rec.name, rec.state)
                )
            lines = rec.recipient_ids
            if recipient_id:
                lines = lines.filtered(lambda r, i=recipient_id: r.id == i)
            if not lines:
                raise UserError(
                    "Name the recipient branch of %s first — a bulletin nobody holds "
                    "cannot be acknowledged (A10 P1-7)." % rec.name
                )
            user = self.env.user
            employee = user.employee_id
            for line in lines:
                if line.acknowledged_on:
                    continue
                if not self.env.su and not line._ack_allowed(employee):
                    raise UserError(
                        "Only %s acknowledges '%s' for %s (A10 P1-7)."
                        % (
                            line.employee_id.name or "the branch's duty officer",
                            rec.name,
                            line.branch_id.name,
                        )
                    )
                line._guarded().write(
                    {
                        "acknowledged_on": fields.Date.context_today(line),
                        "acknowledged_by_id": user.id,
                    }
                )
                rec.message_post(
                    body="%s acknowledged %s for %s." % (user.name, rec.name, line.branch_id.name)
                )
        return True

    def action_close(self, note=""):
        for rec in self:
            if rec.state != "distributed":
                raise UserError("Distribute %s before closing it." % rec.name)
            if not (note or "").strip():
                raise UserError(
                    "State the closure note of %s — what the field did with it." % rec.name
                )
            if rec.bulletin_type == "recall":
                # A10 P1-7 (M61-4): the audit closed a HIGH recall as any user.
                # A recall closes under the Quality Manager, and only once every
                # recipient branch has acknowledged it.
                _qm_gate(
                    self.env,
                    "Only the Quality Manager closes a safety recall (A10 P1-7) — %s." % rec.name,
                )
                pending = rec.recipient_ids.filtered(lambda r: not r.acknowledged_on)
                if pending:
                    raise UserError(
                        "%d recipient branch(es) of %s have not acknowledged it: %s "
                        "(A10 P1-7)."
                        % (len(pending), rec.name, ", ".join(pending.mapped("branch_id.name")))
                    )
            else:
                require_publisher(self.env)
            rec._guarded().write({"state": "closed"})
            rec.message_post(body="Closed by %s: %s" % (self.env.user.name, note.strip()))
        return True


class FixKnowledgeBulletinRecipient(models.Model):
    """One branch's copy of a bulletin: who must hold it, and when they said
    so (A10 P1-7, M61-4). The acknowledgement is never typed — it is stamped
    by the branch's own acknowledgement."""

    _name = "fix.knowledge.bulletin.recipient"
    _description = "Bulletin Recipient Branch"
    _inherit = ["fix.guarded.mixin"]
    _order = "bulletin_id desc, id desc"

    bulletin_id = fields.Many2one(
        "fix.knowledge.bulletin", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    # NOTE: addressing, not ownership (AS-03): the line belongs to the
    # bulletin (company-isolated) and points AT the branch that must
    # acknowledge it — so it is `branch_id`, not the ownership-shaped
    # `operating_unit_id` the isolation generator would lock to the writer's
    # own units (a central publisher must reach every branch).
    branch_id = fields.Many2one(
        "operating.unit", string="Recipient Branch / Hub", required=True, index=True
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Duty Officer",
        help="Who holds this bulletin at the branch (optional): they, and any "
        "colleague whose employee record carries this branch, may acknowledge it.",
    )
    acknowledged_on = fields.Date(readonly=True)
    acknowledged_by_id = fields.Many2one("res.users", string="Acknowledged By", readonly=True)
    note = fields.Char(string="Instruction to the Branch")

    _one_branch_per_bulletin = models.Constraint(
        "UNIQUE (bulletin_id, branch_id)",
        "Each branch appears once per bulletin (A10 P1-7).",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"acknowledged_on", "acknowledged_by_id"}

    def _ack_allowed(self, employee) -> bool:
        self.ensure_one()
        if self.employee_id and employee and self.employee_id == employee:
            return True  # the named duty officer
        if not self.employee_id and employee:
            unit = getattr(employee, "operating_unit_id", False)
            if unit and unit == self.branch_id:
                return True  # the branch's own staff (hr.employee.operating_unit_id)
        return False
