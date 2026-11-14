# S8 — Duplicate-Detection JOBS (A03 gap-plan Part IV, service S8).
#
# THE THREE-LAYER MODEL, reframed by the November 2026 re-audit because the
# estate was being scored against it as a single capability when it has two
# of the three layers:
#
#   (a) ALTERNATE KEYS  — hard uniqueness. Creates an index and BLOCKS the
#       write. Estate equivalent: the _check_* SQL constraints, including
#       M33's no-duplicate-masters rule.                        ALREADY BUILT
#   (b) DETECTION RULES — WARN at entry; a human decides. Estate equivalent:
#       fix.dedup.rule plus fix.party.duplicate candidates.     ALREADY BUILT
#   (c) DETECTION JOBS  — a batch sweep of data ALREADY STORED, feeding a
#       manual merge queue.                                     THIS FILE
#
# Saying it this way matters because "we have dedup" and "we have dedup jobs"
# are different claims, and one Microsoft caveat applies directly: creating a
# uniqueness key FAILS if the stored data already violates it. So the job
# layer must run, and its merges be worked, BEFORE any new constraint can be
# added to live data. That makes this the prerequisite for layer (a)
# expanding, not a nice-to-have after it.
#
# The matching itself reuses fix.dedup.rule — the rules that already warn at
# entry are the rules that sweep history. A second rule language would have
# meant the warning and the sweep could disagree about what a duplicate is.
import difflib
import json
import logging
import re

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

_logger = logging.getLogger(__name__)

# A sweep over a large party table is O(n^2) if done naively. Candidates are
# BLOCKED on a cheap normalised key first and compared only within a block,
# which is the standard record-linkage move and the difference between a job
# that finishes and one that does not.
MAX_BLOCK_SIZE = 400


def _normalise(value):
    """Lowercase, strip punctuation and collapse whitespace."""
    text = (value or "").strip().lower()
    text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text)


def _digits(value):
    return re.sub(r"\D", "", value or "")


class FixDedupJob(models.Model):
    """One scheduled or manual sweep of stored data for duplicates."""

    _name = "fix.dedup.job"
    _description = "Duplicate Detection Job"
    _inherit = ["mail.thread"]
    _order = "started_at desc, id desc"
    _rec_name = "display_label"

    name = fields.Char(required=True)
    display_label = fields.Char(compute="_compute_display_label", store=True)
    rule_ids = fields.Many2many(
        "fix.dedup.rule",
        string="Rules To Run",
        help="Empty runs every active rule. These are the SAME rules that "
        "warn at data entry — one definition of 'duplicate', two moments it "
        "is applied.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("running", "Running"),
            ("done", "Completed"),
            ("failed", "Failed"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    scheduled = fields.Boolean(
        default=False, help="Created by the nightly cron rather than by hand."
    )
    started_at = fields.Datetime(readonly=True)
    finished_at = fields.Datetime(readonly=True)
    records_scanned = fields.Integer(readonly=True, default=0)
    blocks_compared = fields.Integer(readonly=True, default=0)
    candidates_found = fields.Integer(readonly=True, default=0)
    candidates_new = fields.Integer(readonly=True, default=0)
    error_text = fields.Text(readonly=True)
    summary = fields.Text(readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    @api.depends("name", "started_at")
    def _compute_display_label(self):
        for rec in self:
            rec.display_label = "%s · %s" % (
                rec.name or "Dedup job",
                rec.started_at or "not started",
            )

    # ------------------------------------------------------------------
    def action_run(self):
        """Run the sweep. Safe to re-run: candidates are idempotent."""
        for job in self:
            if job.state == "running":
                raise UserError("This job is already running.")
            job.write(
                {
                    "state": "running",
                    "started_at": fields.Datetime.now(),
                    "error_text": False,
                }
            )
            try:
                result = job._sweep()
            except Exception as exc:
                _logger.exception("dedup job %s failed", job.id)
                job.write(
                    {
                        "state": "failed",
                        "finished_at": fields.Datetime.now(),
                        "error_text": str(exc),
                    }
                )
                continue
            job.write(
                {
                    "state": "done",
                    "finished_at": fields.Datetime.now(),
                    "records_scanned": result["scanned"],
                    "blocks_compared": result["blocks"],
                    "candidates_found": result["found"],
                    "candidates_new": result["created"],
                    "summary": result["summary"],
                }
            )
            publish(
                self.env,
                "dedup.job_completed",
                "fix.dedup.job",
                job.id,
                {
                    "job": job.name,
                    "scanned": result["scanned"],
                    "candidates_found": result["found"],
                    "candidates_new": result["created"],
                    "rules": job._rules().mapped("name"),
                },
            )
        return True

    def _rules(self):
        self.ensure_one()
        if self.rule_ids:
            return self.rule_ids.filtered("active")
        return self.env["fix.dedup.rule"].sudo().search([("active", "=", True)])

    def _sweep(self):
        """Block, compare within blocks, record candidates."""
        self.ensure_one()
        Partner = self.env["res.partner"].sudo()
        Duplicate = self.env["fix.party.duplicate"].sudo()
        rules = self._rules()
        if not rules:
            return {
                "scanned": 0,
                "blocks": 0,
                "found": 0,
                "created": 0,
                "summary": "No active dedup rules, so nothing was swept. A job "
                "that finds nothing because it looked for nothing is not a "
                "clean estate.",
            }

        partners = Partner.search([("active", "=", True)])
        scanned = len(partners)
        found = created = blocks = 0
        lines = []

        for rule in rules:
            if rule.model_id.model != "res.partner":
                lines.append(
                    "Rule '%s' targets %s, which this sweep does not cover; "
                    "skipped." % (rule.name, rule.model_id.model)
                )
                continue
            match_fields = [f.strip() for f in (rule.match_fields or "").split(",") if f.strip()]
            usable = [f for f in match_fields if f in Partner._fields]
            if not usable:
                lines.append(
                    "Rule '%s' names no field that exists on res.partner (%s); "
                    "skipped rather than silently matching everything."
                    % (rule.name, rule.match_fields)
                )
                continue

            buckets = {}
            for partner in partners:
                key = self._blocking_key(partner, usable)
                if not key:
                    continue
                buckets.setdefault(key, []).append(partner)

            rule_found = rule_created = 0
            for key, members in buckets.items():
                if len(members) < 2:
                    continue
                if len(members) > MAX_BLOCK_SIZE:
                    lines.append(
                        "Rule '%s': block %r holds %d records, above the %d "
                        "comparison ceiling — reported, not compared, because "
                        "a block that large means the rule is too loose."
                        % (rule.name, key, len(members), MAX_BLOCK_SIZE)
                    )
                    continue
                blocks += 1
                for i, left in enumerate(members):
                    for right in members[i + 1 :]:
                        score = self._similarity(left, right, usable, rule)
                        if score is None:
                            continue
                        rule_found += 1
                        found += 1
                        if self._record_candidate(Duplicate, left, right, rule, score):
                            rule_created += 1
                            created += 1
            lines.append(
                "Rule '%s' (%s on %s): %d pair(s) matched, %d new candidate(s)."
                % (rule.name, rule.scope, ", ".join(usable), rule_found, rule_created)
            )

        return {
            "scanned": scanned,
            "blocks": blocks,
            "found": found,
            "created": created,
            "summary": "\n".join(lines),
        }

    @api.model
    def _blocking_key(self, partner, fields_list):
        """A cheap key that candidates must share before being compared."""
        parts = []
        for name in fields_list:
            value = partner[name]
            if hasattr(value, "display_name"):
                value = value.display_name if value else ""
            if name in ("phone", "mobile"):
                digits = _digits(value)
                parts.append(digits[-6:] if len(digits) >= 6 else digits)
            elif name in ("name", "street", "city"):
                text = _normalise(value)
                parts.append(text[:4])
            else:
                parts.append(_normalise(str(value or ""))[:8])
        # ALL, not any: _similarity() refuses a pair with a blank field, so a
        # record missing one of the rule's fields can never match. Blocking it
        # anyway put every phoneless party into name-only blocks - ~320k
        # comparisons on the dev estate, every one discarded.
        return "|".join(parts) if all(parts) else ""

    @api.model
    def _similarity(self, left, right, fields_list, rule):
        """Score a pair, or None when the rule says they do not match.

        Exact rules demand equality on every named field. Fuzzy rules use an
        edit-distance proxy bounded by the rule's own threshold, so the rule
        author's number is the number that decides.
        """
        values_left, values_right = [], []
        for name in fields_list:
            lv, rv = left[name], right[name]
            if hasattr(lv, "display_name"):
                lv = lv.display_name if lv else ""
            if hasattr(rv, "display_name"):
                rv = rv.display_name if rv else ""
            if name in ("phone", "mobile"):
                lv, rv = _digits(lv), _digits(rv)
            else:
                lv, rv = _normalise(str(lv or "")), _normalise(str(rv or ""))
            if not lv or not rv:
                return None  # a blank field is not evidence of sameness
            values_left.append(lv)
            values_right.append(rv)

        if rule.scope == "exact":
            return 100.0 if values_left == values_right else None

        ratios = [
            difflib.SequenceMatcher(None, a, b).ratio()
            for a, b in zip(values_left, values_right, strict=False)
        ]
        score = 100.0 * sum(ratios) / len(ratios)
        # The rule states a maximum edit distance; convert it to a floor on
        # similarity against the longer string, so threshold 2 on a 10-char
        # name means 80%.
        longest = max(len(v) for v in values_left + values_right) or 1
        floor = max(0.0, 100.0 * (1 - (rule.threshold or 2) / longest))
        return round(score, 1) if score >= floor else None

    @api.model
    def _score_raised_pair(self, left, right):
        """Score a pair a person raised against every active party rule: the
        best rule's score, with every rule's verdict as the explanation.

        A pair no rule matches scores 0 and says so; the steward can still
        review it, but the queue does not rank it above measured pairs."""
        Partner = self.env["res.partner"]
        rules = self.env["fix.dedup.rule"].sudo().search([("active", "=", True)])
        verdicts, best = [], 0.0
        for rule in rules:
            if rule.model_id.model != "res.partner":
                continue
            names = [f.strip() for f in (rule.match_fields or "").split(",") if f.strip()]
            usable = [f for f in names if f in Partner._fields]
            if not usable:
                continue
            score = self._similarity(left.sudo(), right.sudo(), usable, rule)
            verdicts.append(
                {
                    "rule": rule.name,
                    "rule_id": rule.id,
                    "scope": rule.scope,
                    "match_fields": ",".join(usable),
                    "score": score,
                }
            )
            best = max(best, score or 0.0)
        return {
            "score": best,
            "factors": json.dumps(
                {
                    "source": "raised_by_user",
                    "raised_by": self.env.user.name,
                    "rules": verdicts,
                    "matched": any(v["score"] is not None for v in verdicts),
                },
                ensure_ascii=False,
            ),
        }

    @api.model
    def _record_candidate(self, Duplicate, left, right, rule, score):
        """Create the candidate unless this pair is already known.

        Idempotence is per unordered pair: the same two parties must not
        accumulate a new candidate every night.
        """
        first, second = sorted([left.id, right.id])
        existing = Duplicate.search(
            [
                ("party_a", "in", [first, second]),
                ("party_b", "in", [first, second]),
            ],
            limit=1,
        )
        if existing:
            return False
        # fix.party.duplicate asks for EXPLAINABLE factors (T-03): a score
        # with no stated basis cannot be actioned by a steward, so the rule,
        # the fields compared and the sweep that found it all go in.
        Duplicate.create(
            {
                "party_a": first,
                "party_b": second,
                "score": score,
                "factors": json.dumps(
                    {
                        "source": "detection_job",
                        "rule": rule.name,
                        "rule_id": rule.id,
                        "scope": rule.scope,
                        "match_fields": rule.match_fields,
                        "threshold": rule.threshold,
                    },
                    ensure_ascii=False,
                ),
            }
        )
        return True

    @api.model
    def cron_run_nightly(self):
        """The nightly sweep the gap plan asks for.

        Creates its own job record each run so the history shows what was
        swept when — a sweep nobody can point at afterwards is not evidence.
        """
        job = self.sudo().create(
            {
                "name": "Nightly duplicate sweep %s" % fields.Date.context_today(self),
                "scheduled": True,
            }
        )
        job.action_run()
        return {
            "job_id": job.id,
            "candidates_new": job.candidates_new,
            "state": job.state,
        }
