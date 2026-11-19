# M32 Conversational AI operations: dialogue flows, RAG knowledge sources and
# guard-rail rules. Intents already live in fix.assistant.intent; the engine
# (assistant_engine.py) is the real classifier the playground calls.
import base64
import dataclasses
import hashlib
import json
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .assistant_engine import (
    CONFIDENT_THRESHOLD,
    INTENT_REGISTRY,
    AssistantEngine,
    default_assistant_engine,
)

_logger = logging.getLogger(__name__)

# Built engines, keyed by (database, release id, corpus digest). A released
# corpus is immutable once released, so the key never goes stale.
_ENGINE_CACHE: dict = {}
# Databases already told, once per process, that nothing is released.
_FALLBACK_LOGGED: set = set()

TIER_3 = "cd_entity_config.group_dofa_tier_3"


def _answers(result, thresholds) -> bool:
    """Whether a classification is at the tier the live bot acts on."""
    code = result.matched_intent
    if not code:
        return False
    return result.confidence >= ((thresholds or {}).get(code) or CONFIDENT_THRESHOLD)


class FixAssistantDialogue(models.Model):
    _name = "fix.assistant.dialogue"
    _description = "Assistant Dialogue Flow"
    _order = "name"

    name = fields.Char(required=True)
    channel = fields.Selection(
        [("chat", "Web Chat"), ("whatsapp", "WhatsApp"), ("voice", "Voice"), ("in_app", "In-App")],
        required=True,
        default="chat",
    )
    version = fields.Integer(required=True, default=1)
    flow_json = fields.Text(help="State machine as JSON (the dialogue engine's contract).")
    active = fields.Boolean(default=True)


class FixAssistantRagSource(models.Model):
    _name = "fix.assistant.rag.source"
    _description = "Assistant RAG Knowledge Source"
    _order = "name"

    name = fields.Char(required=True)
    source_type = fields.Selection(
        [
            ("article", "Knowledge Article (M61)"),
            ("faq", "FAQ"),
            ("policy", "Policy Document"),
            ("dataset", "Dataset"),
        ],
        required=True,
        default="faq",
    )
    reference = fields.Char(help="Exact reference of the indexed source.")
    chunk_count = fields.Integer(readonly=True, default=0)
    last_indexed_at = fields.Datetime(readonly=True)
    active = fields.Boolean(default=True)


class FixAssistantGuardrail(models.Model):
    _name = "fix.assistant.guardrail"
    _description = "Assistant Guard-Rail Rule"
    _order = "name"

    name = fields.Char(required=True)
    rule = fields.Char(
        required=True, help="The precise condition, e.g. 'advice on legal liability'."
    )
    action = fields.Selection(
        [
            ("block", "Block the reply"),
            ("flag", "Flag for review"),
            ("handoff", "Force human handoff"),
        ],
        required=True,
        default="handoff",
    )
    active = fields.Boolean(default=True)
    note = fields.Char()


class FixAssistantDataset(models.Model):
    """REQ-32.5: a training artifact with a digest and a release gate.

    The A03 zero-trust audit (2026-10-31) found Bengali NLU model promotion
    entirely ungoverned: no dataset record, no SHA-256, and no benchmark
    threshold, so any retrained intent library could reach production.

    A03 workflow audit M32 G4 then found the gate decorative: accuracy was a
    number the author typed, a Tier-3 user released their own rejected
    dataset, and nothing at run time read a released record anyway. So:

    * an intent corpus is the RELEASE BUNDLE: the corpus file, plus the model
      tag and system prompt (with its version) the live assistant runs on;
    * the accuracy is measured by action_run_benchmark against an independent
      golden set, never typed;
    * release is a four-eyes decision routed through the M63 engine
      (domain dataset_release) to a Tier-3 holder who is neither the author
      nor the requester;
    * the live bot and the generator read the released bundle at run time
      (runtime_release / runtime_engine).
    """

    _name = "fix.assistant.dataset"
    _description = "Conversational AI Training Dataset"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "create_date desc, id desc"

    _approval_domain = "dataset_release"
    _approval_apply_method = "action_release"
    _approval_group = TIER_3
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        # An agent wrote state='released' with a director as released_by
        # (A03 audit). The digest is computed from the file and the accuracy
        # from a benchmark run, never typed (M32 G4).
        return super()._fix_guarded_fields() | {
            "state",
            "released_by",
            "released_at",
            "sha256_checksum",
            "benchmark_accuracy_pct",
            "benchmark_cases",
            "benchmark_correct",
            "benchmark_run_at",
            "benchmark_run_by",
            "benchmark_training_sha256",
            "benchmark_set_sha256",
        }

    # What the benchmark and the approver saw. Frozen once the bundle leaves
    # draft, so the released bundle is the one that was measured and approved.
    _CONTENT_FIELDS = frozenset(
        {
            "attachment_id",
            "dataset_type",
            "language",
            "authored_by_native_speaker",
            "benchmark_dataset_id",
            "model_name",
            "system_prompt",
            "prompt_version",
        }
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked |= self._CONTENT_FIELDS
        return locked

    MIN_BENCHMARK_ACCURACY = 92.0

    name = fields.Char(required=True, tracking=True)
    dataset_type = fields.Selection(
        [
            ("intent_corpus", "Intent Utterance Corpus"),
            ("golden_benchmark", "Golden Benchmark Test Set"),
            ("rag_corpus", "RAG Knowledge Corpus"),
            ("model_artifact", "Trained Model Artifact"),
        ],
        required=True,
        default="intent_corpus",
        tracking=True,
    )
    file_name = fields.Char(string="File Name")
    attachment_id = fields.Many2one("ir.attachment", string="Stored File")
    sha256_checksum = fields.Char(string="SHA-256 Digest", readonly=True, tracking=True)
    benchmark_accuracy_pct = fields.Float(
        string="Golden Benchmark Accuracy (%)",
        readonly=True,
        tracking=True,
        help="Intent classification accuracy on the golden test set, measured "
        "by Run Benchmark. It cannot be typed.",
    )
    benchmark_dataset_id = fields.Many2one(
        "fix.assistant.dataset",
        string="Golden Benchmark Set",
        domain=[("dataset_type", "=", "golden_benchmark")],
        tracking=True,
        help="The independent test set this corpus is measured against. It must "
        "be prepared by someone other than the corpus author.",
    )
    benchmark_cases = fields.Integer(readonly=True)
    benchmark_correct = fields.Integer(readonly=True)
    benchmark_run_at = fields.Datetime(readonly=True, copy=False)
    benchmark_run_by = fields.Many2one("res.users", readonly=True, copy=False)
    benchmark_training_sha256 = fields.Char(
        readonly=True, copy=False, help="Digest of the corpus file the benchmark measured."
    )
    benchmark_set_sha256 = fields.Char(
        readonly=True, copy=False, help="Digest of the golden set the benchmark used."
    )
    # --- the run-time bundle -------------------------------------------
    model_name = fields.Char(
        string="Model Tag",
        tracking=True,
        help="The self-hosted model the assistant generates with once this "
        "bundle is released (e.g. a local Ollama tag).",
    )
    system_prompt = fields.Text(
        tracking=True,
        help="The system prompt the generator runs with once released.",
    )
    prompt_version = fields.Char(tracking=True)
    language = fields.Selection(
        [("bn", "Bengali"), ("en", "English"), ("mixed", "Mixed")],
        default="bn",
        required=True,
    )
    authored_by_native_speaker = fields.Boolean(
        string="Native-Speaker Authored",
        default=False,
        tracking=True,
        help="REQ-32.2: Bengali utterances must be authored by native speakers; "
        "machine translation from English must not reach production.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("benchmarked", "Benchmarked"),
            ("released", "Released to Production"),
            ("superseded", "Superseded"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    released_by = fields.Many2one("res.users", readonly=True, copy=False)
    released_at = fields.Datetime(readonly=True, copy=False)

    def write(self, vals):
        touched = self._CONTENT_FIELDS & set(vals)
        if touched and not self._fix_guard_open():
            for rec in self:
                if rec.state == "draft":
                    continue
                changed = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed:
                    raise UserError(
                        "Cannot change %s on a %s dataset: the benchmark and the "
                        "approval covered what is there now. Create a new version."
                        % (", ".join(sorted(changed)), rec.state)
                    )
        return super().write(vals)

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------
    def _file_payload(self) -> bytes:
        self.ensure_one()
        if not self.attachment_id:
            return b""
        return base64.b64decode(self.attachment_id.sudo().datas or b"")

    def _file_digest(self) -> str:
        payload = self._file_payload()
        return hashlib.sha256(payload).hexdigest() if payload else ""

    def _load_json(self) -> dict:
        try:
            data = json.loads(self._file_payload().decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValidationError(
                "Dataset '%s' is not a readable JSON file: %s" % (self.name, exc)
            ) from exc
        if not isinstance(data, dict):
            raise ValidationError("Dataset '%s' must be a JSON object." % self.name)
        return data

    def action_compute_digest(self):
        """Digest the stored file itself, not its name or its path."""
        for rec in self:
            if not rec.attachment_id:
                raise ValidationError(
                    "Attach the dataset file before computing its digest (REQ-32.5)."
                )
            if rec.state != "draft" and not rec._fix_guard_open():
                raise UserError("Only a draft dataset's digest can be recomputed.")
            payload = rec._file_payload()
            if not payload:
                raise ValidationError("The attached dataset file is empty.")
            rec._guarded().write(
                {
                    "sha256_checksum": hashlib.sha256(payload).hexdigest(),
                    "file_name": rec.file_name or rec.attachment_id.name,
                }
            )

    def _build_engine(self) -> AssistantEngine:
        """An engine over the built-in intents plus this corpus's utterances.

        Corpus format: {"intents": {"<code>": {"sample_bn": [...],
        "sample_en": [...]}}}. Only intents the estate can answer exist in the
        code registry (each needs a grounder or an authored answer), so the
        corpus adds utterances to those and may not invent new codes.
        """
        self.ensure_one()
        data = self._load_json()
        intents = dict(INTENT_REGISTRY)
        for code, samples in (data.get("intents") or {}).items():
            if code not in intents:
                raise ValidationError(
                    "Corpus '%s' names intent %r, which has no grounder or authored "
                    "answer in the assistant. Author the intent first." % (self.name, code)
                )
            defn = intents[code]
            samples = samples or {}
            extra_bn = list(samples.get("sample_bn") or [])
            extra_en = list(samples.get("sample_en") or [])
            intents[code] = dataclasses.replace(
                defn,
                sample_bn=list(dict.fromkeys(defn.sample_bn + extra_bn)),
                sample_en=list(dict.fromkeys(defn.sample_en + extra_en)),
            )
        return AssistantEngine(intents)

    def action_run_benchmark(self):
        """Measure the corpus against its golden set. The ONLY way to an accuracy.

        Golden set format: {"cases": [{"text": "...", "intent": "<code>"}]};
        an intent of null means the assistant should hand off. A prediction
        counts only at the confident tier (>= 0.75), the tier the live bot acts
        on.
        """
        for rec in self:
            if rec.state not in ("draft", "benchmarked"):
                raise UserError("A %s dataset cannot be benchmarked." % rec.state)
            if rec.dataset_type != "intent_corpus":
                raise UserError(
                    "Only an intent corpus (the release bundle) is benchmarked; "
                    "this dataset is a %s." % rec.dataset_type
                )
            digest = rec._file_digest()
            if not rec.sha256_checksum or digest != rec.sha256_checksum:
                raise ValidationError(
                    "Compute the digest of the corpus file first: the benchmark must "
                    "measure the exact file that will be released."
                )
            golden = rec.benchmark_dataset_id
            if not golden or golden.dataset_type != "golden_benchmark":
                raise ValidationError("Choose the golden benchmark set to measure against.")
            if not golden.sha256_checksum or golden._file_digest() != golden.sha256_checksum:
                raise ValidationError(
                    "The golden set '%s' has no digest, or its file changed since "
                    "the digest was taken." % golden.name
                )
            if golden.create_uid == rec.create_uid:
                raise ValidationError(
                    "Independent benchmark evidence: the golden set must be prepared "
                    "by someone other than the corpus author (A03 audit M32 G4)."
                )
            cases = golden._load_json().get("cases") or []
            if not cases:
                raise ValidationError("The golden set '%s' holds no cases." % golden.name)
            engine = rec._build_engine()
            # T-05: each intent is judged at its own calibrated threshold, the
            # one the live bot applies (M32 capture pass 2).
            thresholds = self.env["fix.assistant.intent"].confidence_thresholds()
            correct = 0
            for case in cases:
                result = engine.classify_intent(str(case.get("text") or ""), thresholds)
                predicted = result.matched_intent if _answers(result, thresholds) else None
                correct += int(predicted == (case.get("intent") or None))
            accuracy = round(100.0 * correct / len(cases), 2)
            passed = accuracy >= self.MIN_BENCHMARK_ACCURACY
            rec._guarded().write(
                {
                    "benchmark_accuracy_pct": accuracy,
                    "benchmark_cases": len(cases),
                    "benchmark_correct": correct,
                    "benchmark_run_at": fields.Datetime.now(),
                    "benchmark_run_by": self.env.user.id,
                    "benchmark_training_sha256": digest,
                    "benchmark_set_sha256": golden.sha256_checksum,
                    "state": "benchmarked" if passed else "draft",
                }
            )
            rec.message_post(
                body="Benchmark run: %d of %d golden cases correct (%.2f%%), %s the "
                "%.0f%% release minimum."
                % (
                    correct,
                    len(cases),
                    accuracy,
                    "meeting" if passed else "below",
                    self.MIN_BENCHMARK_ACCURACY,
                )
            )
        return True

    def _assert_benchmark_evidence(self):
        """The accuracy must come from a run over THIS file and that golden set."""
        self.ensure_one()
        if not (
            self.benchmark_run_at
            and self.benchmark_training_sha256
            and self.benchmark_training_sha256 == self.sha256_checksum
            and self.benchmark_dataset_id
            and self.benchmark_set_sha256 == self.benchmark_dataset_id.sha256_checksum
        ):
            raise ValidationError(
                "Release blocked: there is no benchmark run over this exact corpus "
                "and golden set. Run Benchmark; an accuracy typed by hand is not "
                "evidence (A03 audit M32 G4)."
            )
        if self.attachment_id and self._file_digest() != self.sha256_checksum:
            raise ValidationError(
                "Release blocked: the corpus file no longer matches the digest the "
                "benchmark measured."
            )

    # ------------------------------------------------------------------
    # Four-eyes release through the M63 engine
    # ------------------------------------------------------------------
    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "benchmarked":
                raise UserError(
                    "Only a benchmarked dataset can be sent for release approval (this "
                    "one is %s)." % rec.state
                )
            rec._assert_benchmark_evidence()
        return super().action_request_approval(justification=justification)

    def _approval_on_rejected(self, comment):
        self._guarded().write({"state": "rejected"})

    def action_release(self):
        """REQ-32.5: production release needs a digest and >= 92% accuracy.

        Runs only as the approval engine's apply step, in the approver's
        environment (four-eyes, A03 audit M32 G4)."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state not in ("draft", "benchmarked"):
                # It had no state check: a REJECTED dataset was released.
                raise ValidationError(
                    "Release blocked: a %s dataset cannot be released." % rec.state
                )
            if not rec.sha256_checksum:
                raise ValidationError(
                    "Release blocked: the dataset has no SHA-256 digest. Compute "
                    "it from the stored file first (REQ-32.5)."
                )
            if rec.benchmark_accuracy_pct < self.MIN_BENCHMARK_ACCURACY:
                raise ValidationError(
                    "Release blocked: golden-benchmark accuracy is %.1f%%, below "
                    "the %.0f%% minimum required for production (REQ-32.5)."
                    % (rec.benchmark_accuracy_pct, self.MIN_BENCHMARK_ACCURACY)
                )
            if rec.language in ("bn", "mixed") and not rec.authored_by_native_speaker:
                raise ValidationError(
                    "Release blocked: Bengali training data must be authored and "
                    "verified by native speakers; machine-translated phrases must "
                    "not be deployed (REQ-32.2)."
                )
            rec._assert_benchmark_evidence()
            authority = rec._approval_authority_user()
            if not authority.has_group(TIER_3):
                raise UserError(
                    "Production deployment of a retrained Bengali NLU model "
                    "requires DOFA Tier 3 (AI Engineering Director) authority."
                )
            preparers = rec.create_uid | rec.approval_request_id.requested_by_id
            if rec._approval_acting_users() & preparers:
                raise UserError(
                    "Segregation of duties: the person who prepared a dataset or "
                    "asked for its release cannot release it to production (REQ-32.5)."
                )
            previous = self.sudo().search(
                [
                    ("state", "=", "released"),
                    ("dataset_type", "=", rec.dataset_type),
                    ("id", "!=", rec.id),
                ]
            )
            previous._guarded().write({"state": "superseded"})
            rec._guarded().write(
                {
                    "state": "released",
                    "released_by": self.env.user.id,
                    "released_at": fields.Datetime.now(),
                }
            )

    # ------------------------------------------------------------------
    # Run time: the released bundle drives the live assistant
    # ------------------------------------------------------------------
    @api.model
    def runtime_release(self):
        """The released intent-corpus bundle, or empty when none may be used.

        A bundle whose file no longer matches its released digest is NOT used:
        running on bytes nobody approved would defeat the release gate."""
        release = self.sudo().search(
            [("state", "=", "released"), ("dataset_type", "=", "intent_corpus")],
            order="released_at desc, id desc",
            limit=1,
        )
        if release and release.attachment_id and release._file_digest() != release.sha256_checksum:
            _logger.error(
                "Released NLU bundle %s (id %s) no longer matches its digest; the "
                "assistant falls back to the built-in intents.",
                release.name,
                release.id,
            )
            return self.browse()
        if not release and self.env.cr.dbname not in _FALLBACK_LOGGED:
            _FALLBACK_LOGGED.add(self.env.cr.dbname)
            _logger.warning(
                "No NLU bundle is released in %s: the assistant runs on the built-in "
                "intent registry, the FIX_OLLAMA_MODEL environment model and the "
                "code system prompt (explicit fallback).",
                self.env.cr.dbname,
            )
        return release

    @api.model
    def runtime_engine(self):
        """(engine, release): the classifier the live bot uses now."""
        release = self.runtime_release()
        if not release or not release.attachment_id:
            return default_assistant_engine, release
        key = (self.env.cr.dbname, release.id, release.sha256_checksum)
        engine = _ENGINE_CACHE.get(key)
        if engine is None:
            try:
                engine = release._build_engine()
            except ValidationError as exc:
                _logger.error("Released NLU bundle %s is unusable: %s", release.name, exc)
                return default_assistant_engine, self.browse()
            _ENGINE_CACHE[key] = engine
        return engine, release
