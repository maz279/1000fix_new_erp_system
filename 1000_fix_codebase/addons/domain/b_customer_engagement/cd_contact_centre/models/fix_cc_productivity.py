# M27/M32 — agent scripts and macros, knowledge binding, quality evaluation
# at scale, and intent mining from live traffic.
#
# Four gap-plan rows, built together because they share the same raw
# material: the conversation transcript.
#
# 1. SCRIPTS AND MACROS. D365 separates them and the gap plan says so
#    explicitly: a SCRIPT is ordered step guidance for a scenario, a MACRO
#    automates the repeated steps and can invoke a flow. The estate had
#    neither, so every agent improvised the same call. Step completion is
#    captured, which turns a script into QA evidence rather than a wall
#    poster.
#
# 2. KNOWLEDGE BINDING. M61 knowledge articles exist; nothing connected an
#    intent to an article, so an agent searched by hand while the customer
#    waited. The binding is a record, not a search, so the surfaced article
#    is deliberate and reviewable.
#
# 3. QUALITY EVALUATION AT SCALE. fix.cc.qa.evaluation is a manual 0-100
#    scorecard. D365 added bulk evaluation (GA 1 May 2026) that scores AI AND
#    HUMAN interactions on the SAME scale -- which matters here more than in
#    most tenants, because M32 resolves conversations autonomously and was
#    measured by different packs than agents were. So the scorecard gains a
#    `handled_by` discriminator and a rubric that can be applied in bulk,
#    rather than a second AI-only metric.
#
# 4. INTENT MINING. M32's intent library is HAND-AUTHORED (11 intents). The
#    estate already scrubs transcripts for mining via mask_pii_for_mining,
#    so candidate intents can be proposed from real Bengali traffic instead
#    of waiting for an author. Candidates are PROPOSALS: they go through the
#    existing dataset release gate and a human, because an intent library
#    that writes itself is an intent library nobody reviewed.
#
# What is deliberately NOT here: a hosted LLM call. The grounding service
# seam is in fix_assistant_llm.py; the mining in this file is statistical
# (frequency over normalised, scrubbed utterances) and says so, because
# labelling n-gram counting as AI would misrepresent what the estate does.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class FixCcScript(models.Model):
    """Ordered step guidance for one scenario, bound to queue and intent."""

    _name = "fix.cc.script"
    _description = "Agent Script"
    _inherit = ["mail.thread"]
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")
    code = fields.Char(required=True, index=True)
    queue_id = fields.Many2one(
        "fix.cc.queue",
        string="Queue",
        help="Empty makes the script available on every queue.",
    )
    intent = fields.Char(
        index=True,
        help="The classified intent this script serves. Matched against "
        "fix.conversation.intent.",
    )
    support_type = fields.Char(
        help="D365 allows several scripts per support type; this is that "
        "grouping, e.g. 'warranty', 'escalation', 'billing dispute'."
    )
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    step_ids = fields.One2many("fix.cc.script.step", "script_id", string="Steps", copy=True)
    step_count = fields.Integer(compute="_compute_step_count")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    _code_unique = models.Constraint("UNIQUE (code)", "Each agent script code exists once.")

    @api.depends("step_ids")
    def _compute_step_count(self):
        for rec in self:
            rec.step_count = len(rec.step_ids)

    def action_publish(self):
        for rec in self:
            if not rec.step_ids:
                raise UserError(
                    "A script with no steps gives the agent nothing. Add at "
                    "least one step before publishing."
                )
            rec.state = "published"
        return True

    @api.model
    def for_conversation(self, conversation):
        """The scripts an agent should see for this conversation, best first.

        Ordered most specific first: a script bound to both this queue and
        this intent beats one bound to the intent alone, which beats a
        general one. An agent handed five equally-plausible scripts will use
        none of them.
        """
        domain = [("state", "=", "published"), ("active", "=", True)]
        scripts = self.sudo().search(domain)
        intent = (conversation.intent or "").strip().lower()
        queue = conversation.queue_id

        def specificity(script):
            score = 0
            if script.intent and script.intent.strip().lower() == intent:
                score += 2
            elif script.intent:
                return None  # bound to a different intent
            if script.queue_id and queue and script.queue_id == queue:
                score += 1
            elif script.queue_id:
                return None  # bound to a different queue
            return score

        scored = [(specificity(s), s) for s in scripts]
        usable = [(score, s) for score, s in scored if score is not None]
        usable.sort(key=lambda pair: (-pair[0], pair[1].sequence, pair[1].id))
        return self.browse([s.id for _score, s in usable])


class FixCcScriptStep(models.Model):
    """One step of a script. Completion is captured for QA evidence."""

    _name = "fix.cc.script.step"
    _description = "Agent Script Step"
    _order = "script_id, sequence, id"

    script_id = fields.Many2one("fix.cc.script", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(required=True, default=10)
    name = fields.Char(required=True)
    instruction = fields.Text(required=True, string="What To Do Or Say")
    instruction_bn = fields.Text(string="Instruction (Bengali)", help="DE-17")
    is_mandatory = fields.Boolean(
        default=False,
        help="A mandatory step that was skipped is a QA finding, not a " "preference.",
    )
    macro_id = fields.Many2one(
        "fix.cc.macro",
        string="Macro",
        help="The automation this step offers, if any. This is the D365 "
        "script/macro distinction: the step says what, the macro does it.",
    )
    knowledge_binding_id = fields.Many2one(
        "fix.cc.knowledge.binding",
        string="Surface Article",
        help="The knowledge article to put in front of the agent at this step.",
    )
    active = fields.Boolean(default=True)

    _sequence_unique = models.Constraint(
        "UNIQUE (script_id, sequence)",
        "Two steps of one script cannot share a sequence number.",
    )


class FixCcMacro(models.Model):
    """An automation an agent can trigger from a script step.

    Bounded by design: a macro names an ACTION FROM A WHITELIST on a target
    the conversation already relates to. Letting a macro name an arbitrary
    model and method would make the macro table a remote-execution surface
    for anyone who can edit configuration.
    """

    _name = "fix.cc.macro"
    _description = "Agent Macro"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    macro_action = fields.Selection(
        [
            ("create_field_order", "Dispatch a field work order"),
            ("handoff_agent", "Hand off to another agent"),
            ("send_template", "Send a notification template"),
            ("dispatch_csat", "Dispatch the CSAT survey"),
            ("raise_complaint", "Raise a complaint record"),
        ],
        required=True,
        help="A whitelist. A macro that could name any model and method "
        "would turn configuration access into code execution.",
    )
    template_id = fields.Many2one(
        "fix.cc.notif.template", string="Template", help="For the send action."
    )
    confirm_required = fields.Boolean(
        default=True,
        help="Ask the agent to confirm before running. Off only for actions "
        "that cannot surprise the customer.",
    )
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("UNIQUE (code)", "Each macro code exists once.")

    @api.constrains("macro_action", "template_id")
    def _check_template_present(self):
        for rec in self:
            if rec.macro_action == "send_template" and not rec.template_id:
                raise ValidationError("Macro '%s' sends a template but names none." % rec.name)

    def run_for(self, conversation):
        """Execute this macro against a conversation. Returns a result dict."""
        self.ensure_one()
        if self.macro_action == "create_field_order":
            conversation.action_create_field_work_order()
            return {"ok": True, "note": "Field work order dispatched."}
        if self.macro_action == "handoff_agent":
            conversation.action_handoff_to_agent(reason="macro:%s" % self.code)
            return {"ok": True, "note": "Handed off to an agent."}
        if self.macro_action == "dispatch_csat":
            conversation._dispatch_csat_survey()
            return {"ok": True, "note": "CSAT survey dispatched."}
        if self.macro_action == "send_template":
            delivery = self.env["fix.notif.delivery"].queue(
                channel=self.template_id.channel,
                purpose="service_updates"
                if self.template_id.consent_class == "transactional"
                else "marketing",
                partner=conversation.customer_id or None,
                to_address=conversation.contact_identity or None,
                template=self.template_id,
                lawful_basis="contract"
                if self.template_id.consent_class == "transactional"
                else "consent",
                source_model="fix.conversation",
                source_id=conversation.id,
                company=conversation.company_id,
            )
            return {
                "ok": delivery.state != "suppressed",
                "delivery_id": delivery.id,
                "note": delivery.consent_reason or "Queued for delivery.",
            }
        if self.macro_action == "raise_complaint":
            # A03 audit M27 G6: the macro was a stub that always refused. M34
            # (cd_cx_feedback, which depends on this module) adds
            # fix.conversation.action_create_complaint; call it when present.
            if not hasattr(conversation, "action_create_complaint"):
                return {
                    "ok": False,
                    "note": "The complaints module (M34) is not installed, so no "
                    "complaint can be raised from a conversation.",
                }
            result = conversation.action_create_complaint()
            complaint_id = None
            if isinstance(result, models.BaseModel):
                complaint_id = result[:1].id or None
            elif isinstance(result, dict):
                complaint_id = result.get("res_id") or result.get("complaint_id")
            return {
                "ok": True,
                "complaint_id": complaint_id,
                "note": "Complaint raised from this conversation.",
            }
        return {"ok": False, "note": "Unknown macro action."}


class FixCcKnowledgeBinding(models.Model):
    """Intent (or queue) to knowledge article. The M61 embed the plan asks for."""

    _name = "fix.cc.knowledge.binding"
    _description = "Knowledge Binding"
    _order = "sequence, id"
    _rec_name = "display_label"

    sequence = fields.Integer(default=10)
    intent = fields.Char(index=True, help="The intent this article answers.")
    queue_id = fields.Many2one("fix.cc.queue", string="Queue")
    article_ref = fields.Char(
        required=True,
        help="The M61 knowledge article reference. A Char rather than a "
        "Many2one because M27 must not hard-depend on the governance stack "
        "to put a link in front of an agent; resolve_article() resolves it "
        "when M61 is installed and says so when it is not.",
    )
    display_label = fields.Char(compute="_compute_display_label", store=True)
    note = fields.Char(help="Why this article, for the reviewer.")
    active = fields.Boolean(default=True)

    @api.depends("intent", "article_ref", "queue_id")
    def _compute_display_label(self):
        for rec in self:
            rec.display_label = "%s -> %s" % (
                rec.intent or (rec.queue_id.code if rec.queue_id else "any"),
                rec.article_ref or "?",
            )

    def resolve_article(self):
        """The article record, when M61 is installed."""
        self.ensure_one()
        Article = self.env.get("fix.knowledge.article")
        if Article is None:
            return {
                "found": False,
                "note": "The knowledge module is not installed in this database.",
            }
        article = Article.sudo().search(
            ["|", ("name", "=", self.article_ref), ("id", "=", self._safe_int(self.article_ref))],
            limit=1,
        )
        if not article:
            return {
                "found": False,
                "note": "No knowledge article matches reference %r." % self.article_ref,
            }
        return {"found": True, "article_id": article.id, "name": article.name}

    @api.model
    def _safe_int(self, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @api.model
    def for_conversation(self, conversation):
        """Articles to surface for this conversation, most specific first."""
        intent = (conversation.intent or "").strip().lower()
        bindings = self.sudo().search([("active", "=", True)])
        matched = bindings.filtered(
            lambda b: (not b.intent or b.intent.strip().lower() == intent)
            and (not b.queue_id or b.queue_id == conversation.queue_id)
        )
        return matched.sorted(lambda b: (0 if b.intent else 1, b.sequence, b.id))


class FixCcScriptCompletion(models.Model):
    """Which script steps an agent actually completed on a conversation.

    This is what makes a script QA evidence. Without it "did the agent follow
    the escalation script" is answered by asking them.
    """

    _name = "fix.cc.script.completion"
    _description = "Script Step Completion"
    _order = "conversation_id, completed_at"
    _rec_name = "step_id"

    conversation_id = fields.Many2one(
        "fix.conversation", required=True, ondelete="cascade", index=True
    )
    script_id = fields.Many2one("fix.cc.script", required=True, ondelete="cascade")
    step_id = fields.Many2one("fix.cc.script.step", required=True, ondelete="cascade", index=True)
    agent_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user)
    completed_at = fields.Datetime(required=True, default=fields.Datetime.now)
    skipped = fields.Boolean(default=False)
    skip_reason = fields.Char()

    _step_unique = models.Constraint(
        "UNIQUE (conversation_id, step_id)",
        "A script step is recorded once per conversation.",
    )

    @api.constrains("skipped", "skip_reason", "step_id")
    def _check_mandatory_skip_has_reason(self):
        for rec in self:
            if rec.skipped and rec.step_id.is_mandatory and not (rec.skip_reason or "").strip():
                raise ValidationError(
                    "Step '%s' is mandatory. Skipping it requires a stated "
                    "reason — that reason is the QA record." % rec.step_id.name
                )

    @api.model
    def script_adherence(self, conversation):
        """How much of the applicable script was followed."""
        scripts = self.env["fix.cc.script"].for_conversation(conversation)
        if not scripts:
            return {"applicable": False, "note": "No published script matches this conversation."}
        script = scripts[0]
        steps = script.step_ids.filtered("active")
        done = self.sudo().search(
            [("conversation_id", "=", conversation.id), ("script_id", "=", script.id)]
        )
        completed = done.filtered(lambda d: not d.skipped)
        mandatory = steps.filtered("is_mandatory")
        mandatory_missed = mandatory - completed.mapped("step_id")
        return {
            "applicable": True,
            "script": script.code,
            "steps": len(steps),
            "completed": len(completed),
            "skipped": len(done) - len(completed),
            "adherence_pct": round(100.0 * len(completed) / len(steps), 1) if steps else 0.0,
            "mandatory_missed": mandatory_missed.mapped("name"),
        }
