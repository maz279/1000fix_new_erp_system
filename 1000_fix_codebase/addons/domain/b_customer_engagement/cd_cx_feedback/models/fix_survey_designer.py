# M34 — the survey designer (question bank, multi-question, branching, CES)
# and the detractor auto-spawn the 2 Nov audit found unwired.
#
# WHAT WAS HERE BEFORE. fix.survey held ONE rating selection and ONE comment
# box. Every instrument the business might want — a CES question, a
# multi-parameter rating across punctuality/technician/price, a branch that
# asks detractors a different follow-up — had nowhere to live. The registry's
# "Multi-Parameter Ratings" FR anticipated this and nothing implemented it.
#
# The design keeps fix.survey as the RESPONSE record (one per service order,
# as the UNIQUE constraint requires) and adds a TEMPLATE above it plus
# ANSWERS below it. That ordering matters: making the template the survey
# would have broken one-survey-per-order, and storing answers as JSON on the
# survey would have made "average punctuality score by branch" a text-parsing
# exercise instead of a query.
#
# The overall rating stays on fix.survey. It is what NPS is computed from and
# what every existing pack reads; moving it into the answer table would have
# been a rewrite of working measurement for no gain.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_cx_feedback import DETRACTOR_MAX_RATING

QUESTION_TYPES = [
    ("rating_5", "Rating 1-5"),
    ("nps_11", "NPS 0-10"),
    ("ces_7", "Customer Effort Score 1-7"),
    ("yes_no", "Yes / No"),
    ("choice", "Single choice"),
    ("text", "Free text"),
]

# Which question types produce a number that can be averaged. A free-text or
# single-choice answer cannot, and reporting a mean over them would be
# nonsense dressed as a metric.
NUMERIC_TYPES = {"rating_5", "nps_11", "ces_7"}

SCALE_BOUNDS = {
    "rating_5": (1, 5),
    "nps_11": (0, 10),
    "ces_7": (1, 7),
}


class FixSurveyTemplate(models.Model):
    """A reusable instrument: a named, versioned set of questions."""

    _name = "fix.survey.template"
    _description = "Survey Template"
    _inherit = ["mail.thread"]
    _order = "name, version desc"

    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")
    code = fields.Char(required=True, index=True)
    version = fields.Integer(required=True, default=1)
    purpose = fields.Selection(
        [
            ("post_service", "Post-service CSAT"),
            ("nps", "Relationship NPS"),
            ("ces", "Customer Effort"),
            ("post_complaint", "Post-complaint recovery"),
            ("in_conversation", "In-conversation (M27 CSAT)"),
        ],
        required=True,
        default="post_service",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    intro_text = fields.Text()
    intro_text_bn = fields.Text(string="Introduction (Bengali)", help="DE-17")
    question_ids = fields.One2many(
        "fix.survey.question", "template_id", string="Questions", copy=True
    )
    question_count = fields.Integer(compute="_compute_counts")
    response_count = fields.Integer(compute="_compute_counts")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    _code_version_unique = models.Constraint(
        "UNIQUE (code, version)",
        "That survey template code and version already exist. Publish a new "
        "version rather than editing a published one.",
    )

    @api.depends("question_ids")
    def _compute_counts(self):
        Survey = self.env["fix.survey"]
        for rec in self:
            rec.question_count = len(rec.question_ids)
            rec.response_count = Survey.sudo().search_count([("template_id", "=", rec.id)])

    def action_publish(self):
        """Publish, with the same discipline the notice versions use.

        A published template is frozen because its answers are only
        comparable if the question did not change underneath them. Changing a
        question's wording after responses exist would silently merge two
        different questions into one trend line.
        """
        for rec in self:
            if rec.state == "published":
                raise UserError("This template is already published.")
            if not rec.question_ids:
                raise UserError(
                    "A template with no questions asks nothing. Add at least "
                    "one question before publishing."
                )
            missing_bn = rec.question_ids.filtered(lambda q: not (q.text_bn or "").strip())
            if missing_bn:
                raise UserError(
                    "DE-17 bilingual mandate: %d question(s) have no Bengali "
                    "text. A survey sent to a Bengali-speaking customer in "
                    "English only is not a survey they can answer: %s"
                    % (len(missing_bn), ", ".join(missing_bn.mapped("code")))
                )
            rec.state = "published"
            publish(
                self.env,
                "survey.template_published",
                "fix.survey.template",
                rec.id,
                {
                    "code": rec.code,
                    "version": rec.version,
                    "purpose": rec.purpose,
                    "questions": len(rec.question_ids),
                },
            )
        return True

    def action_new_version(self):
        """Clone to a new draft version. The only way to change a published
        instrument without corrupting its history."""
        copies = self.browse()
        for rec in self:
            existing = self.sudo().search([("code", "=", rec.code)], order="version desc", limit=1)
            copies |= rec.copy(
                {"version": (existing.version if existing else rec.version) + 1, "state": "draft"}
            )
        return copies

    def action_retire(self):
        for rec in self:
            rec.state = "retired"
        return True

    @api.model
    def published_for(self, purpose):
        """The live template for a purpose, highest version, or empty."""
        return self.sudo().search(
            [("purpose", "=", purpose), ("state", "=", "published"), ("active", "=", True)],
            order="version desc",
            limit=1,
        )


class FixSurveyQuestion(models.Model):
    """One question on a template, with its scale and its branch."""

    _name = "fix.survey.question"
    _description = "Survey Question"
    _order = "template_id, sequence, id"

    template_id = fields.Many2one(
        "fix.survey.template", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(required=True, default=10)
    code = fields.Char(
        required=True,
        help="Stable key for reporting, e.g. 'punctuality'. Reporting joins "
        "on this, so it must not change between versions that mean to be "
        "comparable.",
    )
    text = fields.Char(required=True, string="Question (English)")
    text_bn = fields.Char(string="Question (Bengali)", help="DE-17")
    question_type = fields.Selection(QUESTION_TYPES, required=True, default="rating_5")
    required = fields.Boolean(default=False)
    choice_values = fields.Char(help="Comma-separated options for a single-choice question.")
    # --- branching ---
    ask_if_question_id = fields.Many2one(
        "fix.survey.question",
        string="Only Ask If",
        ondelete="set null",
        help="Ask this question only when an earlier answer meets the "
        "condition below. Empty always asks.",
    )
    ask_if_operator = fields.Selection(
        [("<=", "at most"), (">=", "at least"), ("=", "equals")],
        default="<=",
    )
    ask_if_value = fields.Char()
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "UNIQUE (template_id, code)",
        "A question code is used once per template — reporting keys on it.",
    )
    _sequence_unique = models.Constraint(
        "UNIQUE (template_id, sequence)",
        "Two questions on one template cannot share a sequence number.",
    )

    @api.constrains("question_type", "choice_values")
    def _check_choice_has_options(self):
        for rec in self:
            if rec.question_type == "choice" and not (rec.choice_values or "").strip():
                raise ValidationError("Single-choice question '%s' offers no options." % rec.code)

    @api.constrains("ask_if_question_id", "template_id", "sequence")
    def _check_branch_points_backwards(self):
        """A question may only depend on one asked EARLIER.

        A forward dependency cannot be evaluated — the answer it needs does
        not exist yet — and it is the easy mistake to make in a designer.
        """
        for rec in self:
            source = rec.ask_if_question_id
            if not source:
                continue
            if source.template_id != rec.template_id:
                raise ValidationError(
                    "Question '%s' branches on a question from another " "template." % rec.code
                )
            if source.sequence >= rec.sequence:
                raise ValidationError(
                    "Question '%s' branches on '%s', which is asked at the same "
                    "point or later. A branch can only read an answer already "
                    "given." % (rec.code, source.code)
                )

    def should_ask(self, answers_by_code):
        """Given the answers so far, is this question asked?"""
        self.ensure_one()
        source = self.ask_if_question_id
        if not source:
            return True
        given = answers_by_code.get(source.code)
        if given is None:
            return False
        try:
            given_value = float(given)
            expected = float(self.ask_if_value or 0)
        except (TypeError, ValueError):
            return str(given) == (self.ask_if_value or "")
        operator = self.ask_if_operator or "<="
        if operator == "<=":
            return given_value <= expected
        if operator == ">=":
            return given_value >= expected
        return given_value == expected

    def validate_answer(self, value):
        """Range-check an answer. Returns the normalised value or raises."""
        self.ensure_one()
        if value in (None, "", False):
            if self.required:
                raise ValidationError("Question '%s' is required." % self.code)
            return None
        if self.question_type in NUMERIC_TYPES:
            try:
                numeric = int(value)
            except (TypeError, ValueError) as exc:
                raise ValidationError(
                    "Question '%s' expects a number, got %r." % (self.code, value)
                ) from exc
            low, high = SCALE_BOUNDS[self.question_type]
            if not (low <= numeric <= high):
                raise ValidationError(
                    "Question '%s' is scored %d-%d; %d is outside it."
                    % (self.code, low, high, numeric)
                )
            return numeric
        if self.question_type == "yes_no":
            text = str(value).strip().lower()
            if text not in ("yes", "no", "true", "false", "1", "0"):
                raise ValidationError("Question '%s' expects yes or no." % self.code)
            return "yes" if text in ("yes", "true", "1") else "no"
        if self.question_type == "choice":
            options = [o.strip() for o in (self.choice_values or "").split(",") if o.strip()]
            if str(value).strip() not in options:
                raise ValidationError(
                    "Question '%s' expects one of: %s." % (self.code, ", ".join(options))
                )
            return str(value).strip()
        return str(value)


class FixSurveyAnswer(models.Model):
    """One answer to one question on one response.

    A row per answer rather than a JSON blob, so that "average punctuality by
    branch this quarter" is a query and not a parsing job.
    """

    _name = "fix.survey.answer"
    _description = "Survey Answer"
    _order = "survey_id, sequence, id"
    _rec_name = "question_code"

    survey_id = fields.Many2one("fix.survey", required=True, ondelete="cascade", index=True)
    question_id = fields.Many2one(
        "fix.survey.question", required=True, ondelete="restrict", index=True
    )
    question_code = fields.Char(
        related="question_id.code",
        store=True,
        index=True,
        help="Denormalised so trend reporting survives a template version "
        "change without a join through two tables.",
    )
    question_type = fields.Selection(related="question_id.question_type", store=True)
    sequence = fields.Integer(related="question_id.sequence", store=True)
    value_numeric = fields.Integer(
        help="Set for rating, NPS and CES answers. Only these are averaged."
    )
    value_text = fields.Char(help="Set for yes/no, choice and free-text answers.")
    answered_at = fields.Datetime(required=True, default=fields.Datetime.now)

    _answer_unique = models.Constraint(
        "UNIQUE (survey_id, question_id)",
        "One answer per question per response.",
    )


class FixSurveyWithTemplate(models.Model):
    """Attach the template, the answers and the detractor loop to fix.survey."""

    _inherit = "fix.survey"

    template_id = fields.Many2one(
        "fix.survey.template",
        string="Instrument",
        ondelete="restrict",
        help="The template this response was collected against. Empty means "
        "the legacy single-rating form, which is still a valid response.",
    )
    answer_ids = fields.One2many("fix.survey.answer", "survey_id", string="Answers")
    answer_count = fields.Integer(compute="_compute_answer_count")
    ces_score = fields.Integer(
        compute="_compute_derived_scores",
        store=True,
        help="Customer Effort Score from the CES question, if the instrument "
        "asked one. 0 means not asked — not 'no effort'.",
    )
    followup_id = fields.Many2one(
        "fix.cx.followup", string="Recovery Task", readonly=True, copy=False
    )

    @api.depends("answer_ids")
    def _compute_answer_count(self):
        for rec in self:
            rec.answer_count = len(rec.answer_ids)

    @api.depends("answer_ids.value_numeric", "answer_ids.question_type")
    def _compute_derived_scores(self):
        for rec in self:
            ces = rec.answer_ids.filtered(lambda a: a.question_type == "ces_7")
            rec.ces_score = ces[0].value_numeric if ces else 0

    def record_answers(self, answers):
        """Store a set of answers, validating each against its question.

        `answers` is {question_code: value}. Questions whose branch condition
        is not met are skipped rather than stored empty, so "not asked" and
        "asked and declined" stay distinguishable — they mean different
        things and a blank row would merge them.
        """
        self.ensure_one()
        if not self.template_id:
            raise UserError(
                "This response has no instrument attached, so there are no "
                "questions to answer against."
            )
        Answer = self.env["fix.survey.answer"]
        stored = Answer.browse()
        progressive = {}
        for question in self.template_id.question_ids.filtered("active").sorted(
            lambda q: (q.sequence, q.id)
        ):
            if not question.should_ask(progressive):
                continue
            raw = answers.get(question.code)
            value = question.validate_answer(raw)
            if value is None:
                continue
            progressive[question.code] = value
            existing = Answer.search(
                [("survey_id", "=", self.id), ("question_id", "=", question.id)],
                limit=1,
            )
            vals = {
                "survey_id": self.id,
                "question_id": question.id,
                "value_numeric": value if question.question_type in NUMERIC_TYPES else 0,
                "value_text": "" if question.question_type in NUMERIC_TYPES else str(value),
            }
            if existing:
                existing.write(vals)
                stored |= existing
            else:
                stored |= Answer.create(vals)
        self.write({"state": "responded"})
        self._spawn_detractor_followup()
        return stored

    # ------------------------------------------------------------------
    # Detractor auto-spawn (the 2 Nov audit found the worklist unwired)
    # ------------------------------------------------------------------
    def _is_detractor(self):
        """Low overall rating, or a low NPS answer on the instrument.

        The rating threshold is the one _compute_nps uses (A03 audit M34-10):
        a 3 scored -100 there but stopped at 2 here, so the customers who
        dragged NPS down most often got no recovery call."""
        self.ensure_one()
        if self.rating and int(self.rating) <= DETRACTOR_MAX_RATING:
            return True, "low_rating"
        nps_answers = self.answer_ids.filtered(lambda a: a.question_type == "nps_11")
        if nps_answers and nps_answers[0].value_numeric <= 6:
            return True, "detractor_nps"
        return False, ""

    def _spawn_detractor_followup(self):
        """Raise the recovery task automatically.

        fix.cx.followup existed as a worklist a human had to populate, which
        means recovery happened when somebody remembered. The loop is closed
        here: a detractor response raises its own task, idempotently.
        """
        Followup = self.env["fix.cx.followup"]
        for survey in self:
            if survey.followup_id:
                continue
            detractor, reason = survey._is_detractor()
            if not detractor:
                continue
            followup = Followup.sudo().create(
                {
                    "survey_id": survey.id,
                    "reason": reason,
                    "due_date": fields.Date.add(fields.Date.context_today(survey), days=2),
                    "owner_id": survey.service_order_id.branch_id.manager_id.id
                    if survey.service_order_id.branch_id
                    and getattr(survey.service_order_id.branch_id, "manager_id", False)
                    else False,
                    "company_id": survey.company_id.id,
                    "notes": "Raised automatically from survey %s (%s)." % (survey.id, reason),
                }
            )
            survey.write({"followup_id": followup.id})
            # A03 audit M34-8: a detractor whose order already has an open
            # complaint is the same grievance; link it rather than run two
            # recoveries that do not know about each other.
            followup._link_open_complaint()
            publish(
                self.env,
                "survey.detractor_flagged",
                "fix.survey",
                survey.id,
                {
                    "partner_id": survey.customer_id.id or None,
                    "service_order_id": survey.service_order_id.id,
                    "reason": reason,
                    "rating": survey.rating or None,
                    "nps_score": survey.nps_score,
                    "followup_id": followup.id,
                },
            )
        return True

    def write(self, vals):
        """A rating written directly still closes the loop.

        Most responses arrive through record_answers(), but the legacy
        single-rating path writes `rating` straight onto the survey. Hooking
        write() means the recovery task is raised either way — otherwise half
        the detractors would still be invisible, which is the bug this is
        fixing.
        """
        result = super().write(vals)
        if "rating" in vals:
            self._spawn_detractor_followup()
        return result
