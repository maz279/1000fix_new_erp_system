# M27/M32 — quality evaluation at scale, and intent mining from live traffic.
#
# QUALITY EVALUATION. fix.cc.qa.evaluation was a manual 0-100 scorecard with a
# free-text criteria JSON. D365 added bulk evaluation (GA 1 May 2026) and
# real-time coaching (GA 30 Jun 2026), and crucially it evaluates AI AND HUMAN
# interactions ON THE SAME SCALE. That last point is why this is not just a
# throughput improvement for 1000FiX: M32 resolves conversations
# autonomously and was measured by entirely different packs than agents
# were, so "is the bot as good as a person" had no answer. A rubric with a
# `handled_by` discriminator gives it one.
#
# What is scored automatically is restricted to what can be MEASURED from the
# record: wrap-up discipline, script adherence, recording integrity, handling
# time against the queue target, whether a survey went out. Tone, empathy and
# accuracy are not measurable from an Odoo row and are left to a human
# scorer — a rubric that pretended to score empathy from a transcript length
# would be worse than no rubric.
#
# INTENT MINING. M32's intent library is hand-authored (11 intents). The
# transcripts are already PII-scrubbed for mining by mask_pii_for_mining, so
# candidates can be proposed from real Bengali traffic. This is frequency
# analysis over normalised n-grams, and it says so: calling n-gram counting
# "AI" would misrepresent what the estate does. Candidates are PROPOSALS that
# a human promotes through the existing dataset gate.
import re
from collections import Counter

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .assistant_engine import normalize_text
from .fix_cc_workitem import assert_cc_supervisor

# Stop words in both languages, so mining surfaces INTENTS rather than
# grammar. Hand-listed because a runtime corpus download is not a dependency
# this estate should acquire.
STOP_WORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "my",
    "me",
    "i",
    "you",
    "to",
    "for",
    "of",
    "and",
    "or",
    "in",
    "on",
    "it",
    "this",
    "that",
    "please",
    "can",
    "do",
    "have",
    "has",
    "will",
    "would",
    "need",
    "want",
    "with",
    "at",
    "be",
    "not",
    "আমি",
    "আমার",
    "আপনি",
    "আপনার",
    "এই",
    "একটি",
    "এটা",
    "করে",
    "করা",
    "হবে",
    "হয়",
    "আছে",
    "নেই",
    "কি",
    "কী",
    "জন্য",
    "থেকে",
    "এবং",
    "বা",
    "না",
    "ও",
}

# Below this, a phrase is noise rather than an intent. Deliberately a
# constant with a stated reason rather than a setting: a configurable
# threshold invites tuning it until the output looks good.
MIN_CANDIDATE_FREQUENCY = 5


class FixCcQaRubric(models.Model):
    """A scoring rubric that can be applied in bulk and to AI or humans."""

    _name = "fix.cc.qa.rubric"
    _description = "QA Rubric"
    _inherit = ["mail.thread", "fix.guarded.mixin"]

    def _fix_guarded_fields(self) -> set:
        # An agent published a rubric by pressing Publish (A03 audit M27 Q3);
        # the state moves only through the supervisor's publish and retire.
        return super()._fix_guarded_fields() | {"state"}

    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    applies_to = fields.Selection(
        [
            ("both", "AI and human interactions"),
            ("human", "Human-handled only"),
            ("ai", "AI-handled only"),
        ],
        required=True,
        default="both",
        help="'Both' is the default deliberately: scoring the assistant on a "
        "different scale than agents is how an estate ends up unable to say "
        "whether automation improved service.",
    )
    criterion_ids = fields.One2many(
        "fix.cc.qa.criterion", "rubric_id", string="Criteria", copy=True
    )
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    _code_unique = models.Constraint("UNIQUE (code)", "Each rubric code exists once.")

    def _assert_weights_total_100(self):
        """Weights must total 100: a score out of an unknown denominator is
        not a score. Checked from BOTH sides -- see the note on the child."""
        for rec in self:
            if not rec.criterion_ids:
                continue
            total = sum(rec.criterion_ids.mapped("weight"))
            if abs(total - 100.0) > 0.01:
                raise ValidationError(
                    "Rubric '%s' criterion weights total %.2f, not 100. A "
                    "score out of an unknown denominator is not a score." % (rec.name, total)
                )

    @api.constrains("criterion_ids")
    def _check_weights(self):
        self._assert_weights_total_100()

    def action_publish(self):
        assert_cc_supervisor(self.env, "Publishing a QA rubric")
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft rubric can be published (this one is %s)." % rec.state
                )
            if not rec.criterion_ids:
                raise UserError("A rubric with no criteria scores nothing.")
            rec._guarded().write({"state": "published"})
        return True

    def action_retire(self):
        """Take a rubric out of use. It stays as the basis of its past scores."""
        assert_cc_supervisor(self.env, "Retiring a QA rubric")
        for rec in self:
            if rec.state != "published":
                raise UserError("Only a published rubric can be retired.")
            rec._guarded().write({"state": "retired"})
        return True

    @api.model
    def published_for(self, handled_by):
        return self.sudo().search(
            [
                ("state", "=", "published"),
                ("active", "=", True),
                ("applies_to", "in", ("both", handled_by)),
            ],
            limit=1,
        )


class FixCcQaCriterion(models.Model):
    """One weighted criterion. Auto-scorable ones name what they measure."""

    _name = "fix.cc.qa.criterion"
    _description = "QA Criterion"
    _order = "rubric_id, sequence, id"

    rubric_id = fields.Many2one("fix.cc.qa.rubric", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(required=True, default=10)
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    weight = fields.Float(required=True, default=20.0, help="Percentage of the total.")
    measure = fields.Selection(
        [
            ("manual", "Scored by a human"),
            ("wrapup_quality", "Wrap-up notes present and substantive"),
            ("disposition_set", "Disposition recorded"),
            ("script_adherence", "Script steps followed"),
            ("recording_integrity", "Recording digest present when required"),
            ("handling_time", "Handled within the queue target"),
            ("csat_dispatched", "Satisfaction survey dispatched"),
            ("fcr", "Resolved at first contact"),
        ],
        required=True,
        default="manual",
        help="Only measurable criteria are auto-scored. Tone, empathy and "
        "accuracy are not readable from a database row and stay manual — a "
        "rubric that scored empathy from transcript length would be worse "
        "than no rubric.",
    )
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "UNIQUE (rubric_id, code)", "A criterion code is used once per rubric."
    )

    @api.constrains("weight", "rubric_id")
    def _check_parent_weights(self):
        """The same rule, enforced where the write actually happens.

        A constrains on the PARENT keyed to criterion_ids does not fire when
        a criterion is created directly with rubric_id set, which is how a
        criterion is normally created. Having it only there meant the rule
        was enforced through the form and not through the ORM.
        """
        self.mapped("rubric_id")._assert_weights_total_100()

    def score_for(self, conversation):
        """Score this criterion out of 100, or None when not auto-scorable."""
        self.ensure_one()
        if self.measure == "manual":
            return None
        if self.measure == "wrapup_quality":
            notes = (conversation.wrapup_notes or "").strip()
            if not notes:
                return 0.0
            return 100.0 if len(notes) >= 20 else 50.0
        if self.measure == "disposition_set":
            return 100.0 if conversation.disposition_id else 0.0
        if self.measure == "script_adherence":
            result = self.env["fix.cc.script.completion"].script_adherence(conversation)
            if not result.get("applicable"):
                return None  # nothing to adhere to is not a failure
            return float(result["adherence_pct"])
        if self.measure == "recording_integrity":
            if conversation.channel != "voice":
                return None
            if conversation.recording_consent_state == "refused":
                # Not recording because consent was refused is CORRECT
                # behaviour. Scoring it as a failure would punish the agent
                # for the compliance gate working.
                return 100.0
            if not conversation.recording_url:
                return None
            return 100.0 if (conversation.recording_sha256 or "") else 0.0
        if self.measure == "handling_time":
            if not (conversation.answered_at and conversation.ended_at):
                return None
            target = conversation.queue_id.target_answer_seconds or 0
            if not target:
                return None
            handled = (conversation.ended_at - conversation.answered_at).total_seconds()
            # Handling time is scored against a generous multiple of the
            # ANSWER target because they measure different things; this is a
            # proxy and is labelled as one.
            allowed = target * 10
            return 100.0 if handled <= allowed else max(0.0, 100.0 * allowed / handled)
        if self.measure == "csat_dispatched":
            return 100.0 if conversation.csat_dispatched_at else 0.0
        if self.measure == "fcr":
            return 100.0 if conversation.fcr else 0.0
        return None


class FixCcQaEvaluationAtScale(models.Model):
    """Extend the existing scorecard: who handled it, and auto-scoring.

    A03 audit M27 G11: there was no dispute or calibration flow, and an agent
    edited their own score from 40 to 100 and then deleted the row. A score is
    now scored -> (disputed by the agent) -> in calibration -> final, the
    scored agent can neither change nor delete it, and only a supervisor who
    is not the scored agent calibrates or finalises it.
    """

    _name = "fix.cc.qa.evaluation"
    _inherit = ["fix.cc.qa.evaluation", "fix.guarded.mixin"]

    # What the score is. The scored agent never changes these; once the score
    # is disputed or final only a transition does.
    _SCORE_FIELDS = frozenset(
        {"score", "criteria_json", "notes", "agent_id", "conversation_id", "rubric_id"}
    )

    state = fields.Selection(
        [
            ("scored", "Scored"),
            ("disputed", "Disputed by the agent"),
            ("in_calibration", "In calibration"),
            ("final", "Final"),
        ],
        required=True,
        default="scored",
        index=True,
    )
    dispute_reason = fields.Text(readonly=True, copy=False)
    disputed_at = fields.Datetime(readonly=True, copy=False)
    original_score = fields.Integer(
        readonly=True, copy=False, help="The score as it stood when it was disputed."
    )
    calibration_note = fields.Text(readonly=True, copy=False)
    calibrated_by = fields.Many2one("res.users", readonly=True, copy=False)
    finalised_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "dispute_reason",
            "disputed_at",
            "original_score",
            "calibration_note",
            "calibrated_by",
            "finalised_at",
            "auto_scored",
            "auto_score",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(
            rec.agent_id == self.env.user or rec.state in ("disputed", "final") for rec in self
        ):
            locked |= self._SCORE_FIELDS
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            for vals in vals_list:
                if vals.get("agent_id") == self.env.user.id:
                    raise UserError("An agent cannot score their own interaction.")
        return super().create(vals_list)

    def write(self, vals):
        touched = self._SCORE_FIELDS & set(vals)
        if touched and self and not self._fix_guard_open():
            supervisor = self.env.user.has_group("cd_contact_centre.group_cc_supervisor")
            for rec in self:
                changed = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
                if not changed:
                    continue
                if rec.agent_id == self.env.user:
                    raise UserError(
                        "You cannot change your own QA score. Dispute it instead; a "
                        "supervisor calibrates disputed scores."
                    )
                if rec.state in ("disputed", "final"):
                    raise UserError("A %s QA score changes only through calibration." % rec.state)
                if rec.state == "in_calibration" and not supervisor:
                    raise UserError("Only a supervisor adjusts a score in calibration.")
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open():
            for rec in self:
                if rec.agent_id == self.env.user:
                    raise UserError("You cannot delete your own QA evaluation.")
                if rec.state != "scored":
                    raise UserError("A disputed or calibrated QA evaluation is kept as evidence.")
        return super().unlink()

    def action_dispute(self, reason=""):
        """The scored agent contests the score, with a reason."""
        for rec in self:
            if rec.agent_id != self.env.user:
                raise UserError("Only the agent who was scored can dispute the score.")
            if rec.state != "scored":
                raise UserError(
                    "Only a scored evaluation can be disputed (this one is %s)." % rec.state
                )
            if not (reason or "").strip():
                raise UserError("A dispute needs the reason the score is wrong.")
            rec._guarded().write(
                {
                    "state": "disputed",
                    "dispute_reason": reason.strip(),
                    "disputed_at": fields.Datetime.now(),
                    "original_score": rec.score,
                }
            )
        return True

    def _assert_calibrator(self):
        assert_cc_supervisor(self.env, "Calibrating a QA score")
        for rec in self:
            if rec.agent_id == self.env.user and not self.env.su:
                raise AccessError("A supervisor cannot calibrate their own QA score.")

    def action_send_to_calibration(self, note=""):
        """A supervisor opens the score for calibration."""
        self._assert_calibrator()
        for rec in self:
            if rec.state not in ("scored", "disputed"):
                raise UserError("Only a scored or disputed evaluation goes to calibration.")
            rec._guarded().write(
                {
                    "state": "in_calibration",
                    "calibration_note": (note or "").strip() or rec.calibration_note,
                    "original_score": rec.original_score or rec.score,
                }
            )
        return True

    def action_finalise(self, note=""):
        """A supervisor closes the score: upheld, or as calibrated."""
        self._assert_calibrator()
        for rec in self:
            if rec.state == "final":
                raise UserError("This QA evaluation is already final.")
            if rec.state == "disputed" and not (note or "").strip():
                raise UserError("Finalising a disputed score needs the supervisor's ruling.")
            rec._guarded().write(
                {
                    "state": "final",
                    "calibration_note": (note or "").strip() or rec.calibration_note,
                    "calibrated_by": self.env.user.id,
                    "finalised_at": fields.Datetime.now(),
                }
            )
        return True

    handled_by = fields.Selection(
        [("human", "Human agent"), ("ai", "AI assistant"), ("hybrid", "AI then human")],
        compute="_compute_handled_by",
        store=True,
        help="Derived from the conversation, not asserted. This is what lets "
        "AI and human service be compared on one scale.",
    )
    rubric_id = fields.Many2one("fix.cc.qa.rubric", string="Rubric")
    auto_scored = fields.Boolean(
        readonly=True,
        help="True when this score came from measurable criteria rather than "
        "a human scorer. Mixing the two silently would make the average "
        "meaningless.",
    )
    auto_score = fields.Float(readonly=True, help="The measurable portion of the score.")
    manual_criteria_pending = fields.Char(
        readonly=True,
        help="Criteria a human still has to score. An auto-score that ignores "
        "them is partial and says so.",
    )
    coverage_pct = fields.Float(
        readonly=True,
        help="What share of the rubric weight the auto-score actually covered.",
    )

    @api.depends(
        "conversation_id.ai_resolved", "conversation_id.handoff_reason", "conversation_id.state"
    )
    def _compute_handled_by(self):
        for rec in self:
            conv = rec.conversation_id
            if not conv:
                rec.handled_by = "human"
            elif conv.ai_resolved:
                rec.handled_by = "ai"
            elif conv.handoff_reason:
                rec.handled_by = "hybrid"
            else:
                rec.handled_by = "human"

    @api.model
    def evaluate_conversation(self, conversation, rubric=None):
        """Score one conversation against a rubric, measurable parts only.

        Idempotent per (conversation, rubric): re-running updates the row
        rather than adding a second opinion from the same rubric.
        """
        handled_by = (
            "ai"
            if conversation.ai_resolved
            else ("hybrid" if conversation.handoff_reason else "human")
        )
        rubric_rec = rubric or self.env["fix.cc.qa.rubric"].published_for(handled_by)
        if not rubric_rec:
            return self.browse()

        weighted_total = 0.0
        covered_weight = 0.0
        pending = []
        breakdown = {}
        for criterion in rubric_rec.criterion_ids.filtered("active"):
            score = criterion.score_for(conversation)
            if score is None:
                pending.append(criterion.code)
                continue
            weighted_total += score * criterion.weight / 100.0
            covered_weight += criterion.weight
            breakdown[criterion.code] = round(score, 1)

        if covered_weight <= 0:
            return self.browse()

        # Normalise over the weight actually covered, so a rubric that is
        # half manual does not report every conversation at 50%.
        normalised = weighted_total * 100.0 / covered_weight

        existing = self.sudo().search(
            [
                ("conversation_id", "=", conversation.id),
                ("rubric_id", "=", rubric_rec.id),
                ("auto_scored", "=", True),
            ],
            limit=1,
        )
        if existing and existing.state != "scored":
            # A disputed or calibrated score is not overwritten by a re-run.
            return existing
        vals = {
            "conversation_id": conversation.id,
            "agent_id": (conversation.agent_id or self.env.user).id,
            "rubric_id": rubric_rec.id,
            "score": int(round(normalised)),
            "auto_scored": True,
            "auto_score": round(normalised, 2),
            "coverage_pct": round(covered_weight, 1),
            "manual_criteria_pending": ", ".join(pending),
            "criteria_json": repr(breakdown),
            "notes": "Auto-scored over %.0f%% of rubric weight; %d criterion/criteria "
            "await a human scorer." % (covered_weight, len(pending)),
        }
        if existing:
            existing.write(vals)
            return existing
        return self.sudo().create(vals)

    @api.model
    def cron_bulk_evaluate(self, limit=500, days=1):
        """Score recently closed conversations in bulk.

        The point of bulk scoring is coverage: a manual QA programme samples
        a few percent of calls, so a systematic failure in the other
        ninety-odd percent is invisible.
        """
        since = fields.Datetime.subtract(fields.Datetime.now(), days=days)
        conversations = (
            self.env["fix.conversation"]
            .sudo()
            .search(
                [
                    ("state", "in", ("resolved_ai", "resolved_agent")),
                    ("ended_at", ">=", since),
                ],
                limit=limit,
            )
        )
        scored = 0
        for conversation in conversations:
            if self.evaluate_conversation(conversation):
                scored += 1
        result = {"considered": len(conversations), "scored": scored}
        if scored:
            publish(
                self.env,
                "qa.bulk_evaluated",
                "fix.cc.qa.evaluation",
                0,
                dict(result, days=days),
            )
        return result

    @api.model
    def ai_vs_human_comparison(self, days=30):
        """The comparison the single scale exists to make possible."""
        since = fields.Datetime.subtract(fields.Datetime.now(), days=days)
        rows = self.sudo().search([("evaluated_at", ">=", since)])
        buckets = {}
        for row in rows:
            bucket = buckets.setdefault(
                row.handled_by or "human",
                {"handled_by": row.handled_by or "human", "evaluations": 0, "total": 0.0},
            )
            bucket["evaluations"] += 1
            bucket["total"] += row.score
        out = []
        for bucket in buckets.values():
            bucket["mean_score"] = (
                round(bucket["total"] / bucket["evaluations"], 1) if bucket["evaluations"] else None
            )
            bucket.pop("total")
            out.append(bucket)
        return sorted(out, key=lambda r: r["handled_by"])


class FixAssistantIntentCandidate(models.Model):
    """A candidate intent mined from real traffic, awaiting a human.

    M32's library is hand-authored, which caps intent coverage at whatever
    somebody thought to write down. This proposes additions from what
    customers actually said — and proposes only, because an intent library
    that promotes itself is one nobody reviewed.
    """

    _name = "fix.assistant.intent.candidate"
    _description = "Candidate Intent"
    _inherit = ["mail.thread"]
    _order = "frequency desc, id desc"
    _rec_name = "phrase"

    phrase = fields.Char(required=True, index=True)
    normalised = fields.Char(required=True, index=True)
    language = fields.Selection(
        [("bn", "Bengali"), ("en", "English"), ("mixed", "Mixed")],
        required=True,
        default="bn",
    )
    frequency = fields.Integer(required=True, default=0)
    distinct_conversations = fields.Integer(required=True, default=0)
    first_seen = fields.Datetime()
    last_seen = fields.Datetime()
    sample_utterances = fields.Text(
        help="Scrubbed examples, for the reviewer. These come from "
        "mask_pii_for_mining output only."
    )
    state = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("accepted", "Accepted — intent authored"),
            ("rejected", "Rejected"),
            ("duplicate", "Already covered"),
        ],
        required=True,
        default="proposed",
        tracking=True,
    )
    covered_by_intent = fields.Char(help="The existing intent that already handles this, if any.")
    review_note = fields.Char()
    mined_at = fields.Datetime(required=True, default=fields.Datetime.now)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    _phrase_unique = models.Constraint(
        "UNIQUE (normalised)", "That candidate phrase is already proposed."
    )

    def action_reject(self, note=""):
        for rec in self:
            rec.write({"state": "rejected", "review_note": note})
        return True

    def action_mark_duplicate(self, intent_name=""):
        for rec in self:
            rec.write({"state": "duplicate", "covered_by_intent": intent_name})
        return True

    def action_accept(self, note=""):
        """Mark accepted. Authoring the intent itself stays a human act.

        Deliberately does NOT create a fix.assistant.intent: an intent needs
        authored Bengali utterances and a grounding function, and T08 forbids
        machine-translated utterances. Generating either from a mined n-gram
        would put unreviewed text in front of customers.
        """
        for rec in self:
            rec.write({"state": "accepted", "review_note": note})
            publish(
                self.env,
                "assistant.intent_candidate_accepted",
                "fix.assistant.intent.candidate",
                rec.id,
                {
                    "phrase": rec.phrase,
                    "language": rec.language,
                    "frequency": rec.frequency,
                    "note": "Accepted for authoring; the intent itself is "
                    "written by a native speaker (T08).",
                },
            )
        return True

    # ------------------------------------------------------------------
    @api.model
    def mine_from_traffic(self, days=30, ngram_sizes=(2, 3), limit_turns=20000):
        """Propose candidate intents from scrubbed customer turns.

        ONLY reads turns on conversations whose transcript has been scrubbed
        (`pii_masked`). SC-003 makes mining conditional on that flag, and
        mining the unscrubbed set would breach it — so an estate that has not
        scrubbed gets an empty result and a reason, not a silent sample of
        raw PII.
        """
        Turn = self.env["fix.conversation.turn"].sudo()
        since = fields.Datetime.subtract(fields.Datetime.now(), days=days)
        turns = Turn.search(
            [
                ("speaker", "=", "customer"),
                ("conversation_id.pii_masked", "=", True),
                ("create_date", ">=", since),
            ],
            limit=limit_turns,
        )
        if not turns:
            return {
                "mined": 0,
                "created": 0,
                "note": "No PII-scrubbed customer turns in the window. Mining "
                "unscrubbed transcripts is forbidden (SC-003), so nothing was "
                "read.",
            }

        existing_intents = {
            (i.name or "").strip().lower()
            for i in self.env["fix.assistant.intent"].sudo().search([])
        }
        counter = Counter()
        conversations = {}
        samples = {}
        first_seen = {}
        last_seen = {}

        for turn in turns:
            text = normalize_text(turn.text or "")
            words = [w for w in re.split(r"\s+", text) if w and w not in STOP_WORDS]
            for size in ngram_sizes:
                for i in range(len(words) - size + 1):
                    phrase = " ".join(words[i : i + size])
                    counter[phrase] += 1
                    conversations.setdefault(phrase, set()).add(turn.conversation_id.id)
                    samples.setdefault(phrase, [])
                    if len(samples[phrase]) < 3:
                        samples[phrase].append((turn.text or "")[:160])
                    stamp = turn.create_date
                    if phrase not in first_seen or stamp < first_seen[phrase]:
                        first_seen[phrase] = stamp
                    if phrase not in last_seen or stamp > last_seen[phrase]:
                        last_seen[phrase] = stamp

        created = 0
        for phrase, frequency in counter.most_common():
            if frequency < MIN_CANDIDATE_FREQUENCY:
                break  # most_common is descending, so nothing after this qualifies
            if len(conversations.get(phrase, ())) < 2:
                # A phrase one caller repeated is not an intent.
                continue
            if phrase in existing_intents:
                continue
            if self.sudo().search_count([("normalised", "=", phrase)]):
                continue
            self.sudo().create(
                {
                    "phrase": phrase,
                    "normalised": phrase,
                    "language": self._guess_language(phrase),
                    "frequency": frequency,
                    "distinct_conversations": len(conversations[phrase]),
                    "first_seen": first_seen.get(phrase),
                    "last_seen": last_seen.get(phrase),
                    "sample_utterances": "\n".join(samples.get(phrase, [])),
                }
            )
            created += 1

        return {
            "mined": len(turns),
            "phrases_considered": len(counter),
            "created": created,
            "note": "Frequency analysis over scrubbed turns. This is n-gram "
            "counting, not a language model; candidates are proposals for a "
            "native speaker to author (T08).",
        }

    @api.model
    def _guess_language(self, phrase):
        """Bengali if it contains Bengali script, English if none, else mixed."""
        has_bengali = bool(re.search(r"[ঀ-৿]", phrase))
        has_latin = bool(re.search(r"[A-Za-z]", phrase))
        if has_bengali and has_latin:
            return "mixed"
        return "bn" if has_bengali else "en"

    @api.model
    def cron_mine_intents(self):
        return self.mine_from_traffic()
