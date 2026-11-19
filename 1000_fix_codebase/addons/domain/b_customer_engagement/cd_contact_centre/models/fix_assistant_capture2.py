# M32 capture audit, pass 2 (19 Nov 2026): what the spec gives a person to
# record on each sub-module page that pass 1 (14 Nov) did not build.
#
#   1 Intent Recognition  intent category and a per-intent confidence
#                         threshold (FR-CAI-002, T-05), honoured by the live
#                         bot, the playground and the benchmark; a shadow
#                         evaluation on live traffic before a bundle replaces
#                         the production one (T-11, BRU-CAI-14, AUT-CAI-11)
#   6 Guard Rails         a rule's stage (input / output) and severity (spec
#                         10.1 fix.guardrail.rule), and the review of a firing
#                         as correct, false positive or attempted injection
#                         (spec 14 "false-positive review", section 13 CDO)
#   8 Agent Assistance    the agent edits the AI answer before sending it
#                         (FR-CAI-038 "always editable"; the send lives on
#                         fix.assistant.ask in fix_assistant_llm.py)
#   9 Analytics           the unresolved queue (spec 10.1
#                         fix.unresolved.intent, AUT-CAI-06/08/10, KPI-184):
#                         every no-answer handoff is logged, reviewed with a
#                         disposition, and a knowledge gap is closed against
#                         its M61 reference
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_assistant_ops import _answers

_logger = logging.getLogger(__name__)

SUPERVISOR_GROUP = "cd_contact_centre.group_cc_supervisor"


def _is_reviewer(env) -> bool:
    """The Customer Service Manager's people: a Contact Centre Supervisor, or
    an administrator. Every employee can write fix.assistant.ask (its fields
    are guarded), so the role is checked here rather than left to the ACL."""
    return env.su or env.user.has_group(SUPERVISOR_GROUP) or env.user.has_group("base.group_system")


# --------------------------------------------------------------------------
# 1 Intent Recognition: the taxonomy fields the spec names
# --------------------------------------------------------------------------
INTENT_CATEGORIES = [
    ("status", "Status"),
    ("booking", "Booking"),
    ("pricing", "Pricing"),
    ("warranty", "Warranty"),
    ("complaint", "Complaint"),
    ("product", "Product"),
    ("location", "Location"),
    ("payment", "Payment"),
    ("account", "Account"),
    ("knowledge", "Knowledge / how-to"),
    ("other", "Other"),
]
# A calibrated threshold stays above the 0.50 disambiguation floor, so every
# intent keeps a band where the assistant asks rather than guesses
# (FR-CAI-005), and below 1.0, which only an exact match reaches.
THRESHOLD_MIN = 0.60
THRESHOLD_MAX = 0.99


class FixAssistantIntentTaxonomy(models.Model):
    _inherit = "fix.assistant.intent"

    category = fields.Selection(
        INTENT_CATEGORIES,
        tracking=True,
        help="FR-CAI-002: the taxonomy class (status, booking, pricing, ...).",
    )
    confidence_threshold = fields.Float(
        string="Confidence Threshold",
        digits=(3, 2),
        tracking=True,
        help="T-05: the confidence this intent must reach before the assistant "
        "acts on it, calibrated from the labelled evaluation set. Empty = the "
        "global 0.75. Read by the live bot, the playground and the benchmark.",
    )
    threshold_basis = fields.Char(
        string="Calibration Evidence",
        tracking=True,
        help="What the threshold was calibrated on, e.g. the golden set and its "
        "precision at this threshold.",
    )

    @api.constrains("confidence_threshold", "threshold_basis")
    def _check_threshold(self):
        for rec in self:
            if not rec.confidence_threshold:
                continue
            if not THRESHOLD_MIN <= rec.confidence_threshold <= THRESHOLD_MAX:
                raise ValidationError(
                    _(
                        "A calibrated threshold lies between %(lo).2f and %(hi).2f: below "
                        "it the assistant would act where it should ask (FR-CAI-005)."
                    )
                    % {"lo": THRESHOLD_MIN, "hi": THRESHOLD_MAX}
                )
            if not (rec.threshold_basis or "").strip():
                raise ValidationError(
                    _(
                        "T-05: a per-intent threshold is calibrated from a labelled "
                        "evaluation set. Say what it was calibrated on."
                    )
                )

    @api.model
    def confidence_thresholds(self) -> dict:
        """{intent code: threshold} for the active intents that set one."""
        rows = self.sudo().search(
            [("confidence_threshold", ">", 0), ("company_id", "in", self.env.companies.ids)]
        )
        return {r.code: r.confidence_threshold for r in rows if r.code}


# --------------------------------------------------------------------------
# 1 Intent Recognition: shadow evaluation before promotion
# --------------------------------------------------------------------------
SHADOW_STATES = [
    ("none", "Not run"),
    ("passed", "Passed"),
    ("failed", "Failed"),
    ("no_traffic", "No live traffic to measure"),
]
SHADOW_FIELDS = {
    "shadow_state",
    "shadow_turns",
    "shadow_baseline_confident",
    "shadow_candidate_confident",
    "shadow_agreement",
    "shadow_regressions",
    "shadow_run_at",
    "shadow_run_by",
    "shadow_sha256",
    "shadow_baseline_id",
    "shadow_window_days",
}


class FixAssistantDatasetShadow(models.Model):
    """T-11 / BRU-CAI-14: a candidate runs alongside production on live
    traffic without responding, and is promoted only on measured improvement.

    The run replays the PII-scrubbed customer turns of the window (SC-003: the
    same set intent mining may read) through the production engine and the
    candidate, at the per-intent thresholds, and stores only counts. It
    passes when the candidate answers at least as many turns as production
    and changes the answer of at most 2% of the turns production answered.
    """

    _inherit = "fix.assistant.dataset"

    MAX_SHADOW_REGRESSION_PCT = 2.0
    SHADOW_TURN_LIMIT = 5000

    shadow_state = fields.Selection(
        SHADOW_STATES, default="none", required=True, readonly=True, tracking=True, copy=False
    )
    shadow_window_days = fields.Integer(readonly=True, copy=False)
    shadow_turns = fields.Integer(string="Live Turns Replayed", readonly=True, copy=False)
    shadow_baseline_confident = fields.Integer(
        string="Answered by Production", readonly=True, copy=False
    )
    shadow_candidate_confident = fields.Integer(
        string="Answered by Candidate", readonly=True, copy=False
    )
    shadow_agreement = fields.Integer(string="Same Answer", readonly=True, copy=False)
    shadow_regressions = fields.Integer(
        string="Regressions",
        readonly=True,
        copy=False,
        help="Turns production answered that the candidate would not answer, or "
        "would answer with a different intent.",
    )
    shadow_baseline_id = fields.Many2one(
        "fix.assistant.dataset", string="Measured Against", readonly=True, copy=False
    )
    shadow_sha256 = fields.Char(readonly=True, copy=False)
    shadow_run_at = fields.Datetime(readonly=True, copy=False)
    shadow_run_by = fields.Many2one("res.users", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | SHADOW_FIELDS

    def _production_release(self):
        """The released intent corpus other than this one, if any."""
        self.ensure_one()
        return self.sudo().search(
            [
                ("state", "=", "released"),
                ("dataset_type", "=", "intent_corpus"),
                ("id", "!=", self.id),
            ],
            order="released_at desc, id desc",
            limit=1,
        )

    def action_run_shadow(self, days=30):
        days = max(1, min(int(days or 30), 90))
        Turn = self.env["fix.conversation.turn"].sudo()
        thresholds = self.env["fix.assistant.intent"].confidence_thresholds()
        for rec in self:
            if rec.dataset_type != "intent_corpus":
                raise UserError(_("Only an intent corpus (a release bundle) is shadow-evaluated."))
            if rec.state != "benchmarked":
                raise UserError(
                    _(
                        "BRU-CAI-14: a bundle is shadow-evaluated after it has passed the "
                        "Bengali evaluation set (this one is %s). Run Benchmark first."
                    )
                    % rec.state
                )
            if not rec.sha256_checksum or rec._file_digest() != rec.sha256_checksum:
                raise ValidationError(
                    _("The corpus file no longer matches its digest; recompute it first.")
                )
            baseline_engine, baseline = self.env["fix.assistant.dataset"].runtime_engine()
            candidate = rec._build_engine()
            since = fields.Datetime.subtract(fields.Datetime.now(), days=days)
            turns = Turn.search(
                [
                    ("speaker", "=", "customer"),
                    ("conversation_id.pii_masked", "=", True),
                    ("create_date", ">=", since),
                ],
                order="create_date desc, id desc",
                limit=self.SHADOW_TURN_LIMIT,
            )
            base_n = cand_n = agree = regress = 0
            for turn in turns:
                text = turn.text or ""
                b = baseline_engine.classify_intent(text, thresholds)
                c = candidate.classify_intent(text, thresholds)
                b_ok, c_ok = _answers(b, thresholds), _answers(c, thresholds)
                base_n += b_ok
                cand_n += c_ok
                if b_ok and c_ok and b.matched_intent == c.matched_intent:
                    agree += 1
                elif b_ok:
                    regress += 1
            total = len(turns)
            if not total:
                state = "no_traffic"
            elif cand_n >= base_n and regress * 100.0 / total <= self.MAX_SHADOW_REGRESSION_PCT:
                state = "passed"
            else:
                state = "failed"
            rec._guarded().write(
                {
                    "shadow_state": state,
                    "shadow_window_days": days,
                    "shadow_turns": total,
                    "shadow_baseline_confident": base_n,
                    "shadow_candidate_confident": cand_n,
                    "shadow_agreement": agree,
                    "shadow_regressions": regress,
                    "shadow_baseline_id": baseline.id if baseline else False,
                    "shadow_sha256": rec.sha256_checksum,
                    "shadow_run_at": fields.Datetime.now(),
                    "shadow_run_by": self.env.user.id,
                }
            )
            rec.message_post(
                body=_(
                    "Shadow evaluation over %(n)d live turns (%(d)d days) against %(base)s: "
                    "production answered %(b)d, the candidate %(c)d, %(r)d regressions. "
                    "Result: %(s)s."
                )
                % {
                    "n": total,
                    "d": days,
                    "base": baseline.name if baseline else _("the built-in intents"),
                    "b": base_n,
                    "c": cand_n,
                    "r": regress,
                    "s": dict(SHADOW_STATES)[state],
                }
            )
            publish(
                self.env,
                "model.evaluation_completed",
                "fix.assistant.dataset",
                rec.id,
                {
                    "kind": "shadow",
                    "turns": total,
                    "baseline_answered": base_n,
                    "candidate_answered": cand_n,
                    "regressions": regress,
                    "passed": state == "passed",
                },
            )
        return True

    def _assert_benchmark_evidence(self):
        """BRU-CAI-14: replacing a production bundle also needs a passing
        shadow run over THIS file against THAT production bundle. The first
        release has no production to shadow, so the benchmark alone gates it."""
        super()._assert_benchmark_evidence()
        production = self._production_release()
        if not production:
            return
        if not (
            self.shadow_state == "passed"
            and self.shadow_sha256 == self.sha256_checksum
            and self.shadow_baseline_id == production
        ):
            raise ValidationError(
                _(
                    "Promotion blocked (BRU-CAI-14): '%(p)s' is in production, so this "
                    "bundle needs a passing shadow evaluation against it on live traffic. "
                    "Run Shadow Evaluation (current result: %(s)s)."
                )
                % {"p": production.name, "s": dict(SHADOW_STATES)[self.shadow_state]}
            )


# --------------------------------------------------------------------------
# 6 Guard Rails: stage, severity, and the review of a firing
# --------------------------------------------------------------------------
GUARDRAIL_STAGES = [
    ("input", "Input: the customer's message"),
    ("output", "Output: the generated answer"),
    ("both", "Both"),
]
SEVERITIES = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")]
GUARDRAIL_REVIEWS = [
    ("confirmed", "Correct: the rail was right to fire"),
    ("false_positive", "False positive: it should not have fired"),
    ("attempted_injection", "Attempted injection or jailbreak"),
]


class FixAssistantGuardrailStage(models.Model):
    _inherit = "fix.assistant.guardrail"

    stage = fields.Selection(
        GUARDRAIL_STAGES,
        required=True,
        default="both",
        help="Spec 10.1: input rules screen the customer's message before "
        "inference; output rules screen the generated answer (FR-CAI-031/032).",
    )
    severity = fields.Selection(SEVERITIES, required=True, default="medium")


class FixAssistantAskReview(models.Model):
    _inherit = "fix.assistant.ask"

    guardrail_fired = fields.Boolean(
        compute="_compute_guardrail_fired",
        store=True,
        index=True,
        help="A guard rail blocked or flagged this answer.",
    )
    guardrail_review = fields.Selection(GUARDRAIL_REVIEWS, readonly=True, copy=False)
    guardrail_review_note = fields.Char(readonly=True, copy=False)
    guardrail_reviewed_by = fields.Many2one("res.users", readonly=True, copy=False)
    guardrail_reviewed_at = fields.Datetime(readonly=True, copy=False)
    # FR-CAI-038: what the agent sends may differ from what the AI drafted.
    draft_reply = fields.Text(
        string="Reply To Send",
        compute="_compute_draft_reply",
        help="The AI's answer in the conversation's language. Edit it before "
        "sending; an edited reply goes on the transcript as the agent's turn.",
    )
    sent_text = fields.Text(string="Text Sent", readonly=True, copy=False)
    edited_by_agent = fields.Boolean(readonly=True, copy=False)
    # The review form's inputs. Never stored: they only carry what the
    # supervisor enters to action_review_guardrail, which writes the guarded
    # outcome above (a guarded field is never a writable form input, R9 c).
    review_verdict = fields.Selection(
        GUARDRAIL_REVIEWS, string="Review", compute="_compute_review_inputs"
    )
    review_note_input = fields.Char(string="Note", compute="_compute_review_inputs")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "guardrail_review",
            "guardrail_review_note",
            "guardrail_reviewed_by",
            "guardrail_reviewed_at",
            "sent_text",
            "edited_by_agent",
        }

    @api.depends("guardrail_verdict", "guardrail_reason")
    def _compute_guardrail_fired(self):
        for rec in self:
            rec.guardrail_fired = rec.guardrail_verdict == "blocked" or (
                rec.guardrail_reason or ""
            ).startswith("Flagged by guardrail")

    def _compute_review_inputs(self):
        for rec in self:
            rec.review_verdict = rec.guardrail_review or False
            rec.review_note_input = rec.guardrail_review_note or False

    @api.depends("answer_bn", "answer_en", "language")
    def _compute_draft_reply(self):
        for rec in self:
            rec.draft_reply = rec._ai_reply_text() or False

    def action_review_guardrail(self, verdict=None, note=None):
        """Spec 14 "false-positive review": a supervisor says whether the rail
        was right. The verdict feeds the guard-rail firing report's precision."""
        if not _is_reviewer(self.env):
            raise UserError(
                _("Only a Contact Centre Supervisor reviews a guard-rail firing (spec 13).")
            )
        if verdict not in dict(GUARDRAIL_REVIEWS):
            raise UserError(_("Say whether the guard rail was right, wrong or met an attack."))
        note = (note or "").strip()
        if verdict == "false_positive" and not note:
            raise UserError(
                _("A false positive needs a note: it is what the rule's owner tunes from.")
            )
        for rec in self:
            if not rec.guardrail_fired:
                raise UserError(
                    _("No guard rail fired on this answer; there is nothing to review.")
                )
            if rec.guardrail_review:
                raise UserError(
                    _("This firing was already reviewed by %s.") % rec.guardrail_reviewed_by.name
                )
            rec._guarded().write(
                {
                    "guardrail_review": verdict,
                    "guardrail_review_note": note or False,
                    "guardrail_reviewed_by": self.env.user.id,
                    "guardrail_reviewed_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "guardrail.reviewed",
                "fix.assistant.ask",
                rec.id,
                {"verdict": verdict, "reason": rec.guardrail_reason or ""},
            )
        return True


# --------------------------------------------------------------------------
# 9 Analytics: the unresolved queue and the knowledge-gap loop
# --------------------------------------------------------------------------
# The handoffs where the assistant had no answer (AUT-CAI-06: "log as a
# knowledge gap"; AUT-CAI-08: "log to the unresolved queue for review").
UNRESOLVED_SIGNALS = frozenset({"low_confidence", "out_of_scope", "no_retrieval"})
DISPOSITIONS = [
    ("knowledge_gap", "Knowledge gap: needs an M61 article"),
    ("new_intent", "New intent needed"),
    ("add_utterance", "Existing intent: add this utterance"),
    ("out_of_scope", "Out of scope: the handoff was right"),
    ("no_action", "No action"),
]
UNRESOLVED_STATES = [("open", "Open"), ("reviewed", "Reviewed"), ("closed", "Gap Closed")]
KPI_184_DAYS = 30


class FixAssistantUnresolved(models.Model):
    """One conversation the assistant could not answer (spec 10.1
    fix.unresolved.intent). Logged by the assistant, reviewed by a person."""

    _name = "fix.assistant.unresolved"
    _description = "Assistant Unresolved Question"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "logged_at desc, id desc"
    _rec_name = "question"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    conversation_id = fields.Many2one(
        "fix.conversation", required=True, index=True, ondelete="cascade"
    )
    question = fields.Text(required=True, help="The customer's last message, PII-scrubbed.")
    language = fields.Selection([("bn", "Bengali"), ("en", "English")], default="bn")
    best_guess_intent = fields.Char(index=True)
    confidence = fields.Float(digits=(3, 2))
    handoff_reason = fields.Char()
    signal = fields.Char(help="The handoff trigger signal that logged it.")
    logged_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    state = fields.Selection(UNRESOLVED_STATES, required=True, default="open", tracking=True)
    disposition = fields.Selection(DISPOSITIONS, tracking=True)
    knowledge_gap_ref = fields.Char(
        string="M61 Reference",
        tracking=True,
        help="The M61 knowledge article (or article request) that answers it.",
    )
    review_note = fields.Char()
    reviewed_by = fields.Many2one("res.users", readonly=True)
    reviewed_at = fields.Datetime(readonly=True)
    gap_closed_at = fields.Datetime(readonly=True)
    gap_closed_by = fields.Many2one("res.users", readonly=True)
    # The review and close forms' inputs, never stored: the actions write the
    # guarded outcome (R9 c: a guarded field is never a writable form input).
    disposition_input = fields.Selection(
        DISPOSITIONS, string="Disposition", compute="_compute_inputs"
    )
    gap_ref_input = fields.Char(string="M61 Reference", compute="_compute_inputs")
    note_input = fields.Char(string="Reviewer Note", compute="_compute_inputs")
    gap_days = fields.Integer(
        string="Days to Close",
        compute="_compute_gap_days",
        store=True,
        help="KPI-184: days from logging to the gap being closed.",
    )

    def _fix_guarded_fields(self) -> set:
        # Logged by the assistant; reviewed and closed only through the actions.
        return super()._fix_guarded_fields() | {
            "conversation_id",
            "question",
            "language",
            "best_guess_intent",
            "confidence",
            "handoff_reason",
            "signal",
            "logged_at",
            "state",
            "disposition",
            "knowledge_gap_ref",
            "review_note",
            "reviewed_by",
            "reviewed_at",
            "gap_closed_at",
            "gap_closed_by",
        }

    def _compute_inputs(self):
        for rec in self:
            rec.disposition_input = rec.disposition or False
            rec.gap_ref_input = rec.knowledge_gap_ref or False
            rec.note_input = False

    @api.depends("logged_at", "gap_closed_at")
    def _compute_gap_days(self):
        for rec in self:
            rec.gap_days = (
                (rec.gap_closed_at - rec.logged_at).days
                if rec.gap_closed_at and rec.logged_at
                else 0
            )

    def _assert_reviewer(self):
        if not _is_reviewer(self.env):
            raise UserError(
                _("Only a Contact Centre Supervisor reviews the unresolved queue (spec 13).")
            )

    def action_review(self, disposition=None, note=None, gap_ref=None):
        """AUT-CAI-10: say what the unanswered question needs."""
        self._assert_reviewer()
        if disposition not in dict(DISPOSITIONS):
            raise UserError(_("Choose what this question needs (the disposition)."))
        note = (note or "").strip()
        if disposition in ("no_action", "out_of_scope") and not note:
            raise UserError(_("Say why nothing needs to change."))
        for rec in self:
            if rec.state != "open":
                raise UserError(_("This question was already reviewed."))
            rec._guarded().write(
                {
                    "state": "reviewed",
                    "disposition": disposition,
                    "review_note": note or False,
                    "knowledge_gap_ref": (gap_ref or "").strip() or False,
                    "reviewed_by": self.env.user.id,
                    "reviewed_at": fields.Datetime.now(),
                }
            )
            if disposition == "knowledge_gap":
                frequency = self.sudo().search_count(
                    [
                        ("best_guess_intent", "=", rec.best_guess_intent or False),
                        ("company_id", "=", rec.company_id.id),
                    ]
                )
                publish(
                    self.env,
                    "assistant.knowledge_gap",
                    "fix.assistant.unresolved",
                    rec.id,
                    {
                        "intent": rec.best_guess_intent or None,
                        "input": rec.question,
                        "frequency": frequency,
                        "reference": rec.knowledge_gap_ref or None,
                    },
                )
        return True

    def action_close_gap(self, gap_ref=None):
        """KPI-184: a knowledge gap is closed when M61 has the answer."""
        self._assert_reviewer()
        for rec in self:
            if rec.state != "reviewed" or rec.disposition != "knowledge_gap":
                raise UserError(_("Only a reviewed knowledge gap can be closed."))
            ref = (gap_ref or rec.knowledge_gap_ref or "").strip()
            if not ref:
                raise UserError(
                    _("Name the M61 article that now answers it: a gap closes against evidence.")
                )
            rec._guarded().write(
                {
                    "state": "closed",
                    "knowledge_gap_ref": ref,
                    "gap_closed_at": fields.Datetime.now(),
                    "gap_closed_by": self.env.user.id,
                }
            )
        return True


class FixConversationUnresolved(models.Model):
    _inherit = "fix.conversation"

    def action_handoff_to_agent(self, reason: str = ""):
        res = super().action_handoff_to_agent(reason=reason)
        for conv in self:
            if conv.handoff_signal in UNRESOLVED_SIGNALS:
                try:
                    conv._log_unresolved(reason)
                except Exception:  # the handoff itself must never fail on the log
                    _logger.exception("Could not log conversation %s as unresolved", conv.id)
        return res

    def _log_unresolved(self, reason, signal=None):
        self.ensure_one()
        Unresolved = self.env["fix.assistant.unresolved"].sudo()
        if Unresolved.search_count([("conversation_id", "=", self.id), ("state", "=", "open")]):
            return
        turns = self.turn_ids.filtered(lambda t: t.speaker == "customer").sorted("sequence")
        if not turns:
            return
        last = turns[-1]
        engine, _release = self.env["fix.assistant.dataset"].runtime_engine()
        res = engine.classify_intent(
            last.text or "", self.env["fix.assistant.intent"].confidence_thresholds()
        )
        row = Unresolved.create(
            {
                "company_id": self.company_id.id,
                "conversation_id": self.id,
                "question": last.text or "",
                "language": last.lang or "bn",
                "best_guess_intent": res.matched_intent or self.intent or False,
                "confidence": res.confidence,
                "handoff_reason": reason or False,
                "signal": signal or self.handoff_signal,
            }
        )
        publish(
            self.env,
            "assistant.unresolved",
            "fix.assistant.unresolved",
            row.id,
            {
                "conversation": self.id,
                "intent": row.best_guess_intent or None,
                "confidence": row.confidence,
                "reason": reason or None,
            },
        )
