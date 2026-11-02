# M32 Conversational AI operations: dialogue flows, RAG knowledge sources and
# guard-rail rules. Intents already live in fix.assistant.intent; the engine
# (assistant_engine.py) is the real classifier the playground calls.
from odoo import fields, models
from odoo.exceptions import UserError, ValidationError


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
    """

    _name = "fix.assistant.dataset"
    _description = "Conversational AI Training Dataset"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

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
        tracking=True,
        help="Intent classification accuracy on the golden test set.",
    )
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
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    released_by = fields.Many2one("res.users", readonly=True, copy=False)
    released_at = fields.Datetime(readonly=True, copy=False)

    def action_compute_digest(self):
        """Digest the stored file itself, not its name or its path."""
        import base64
        import hashlib

        for rec in self:
            if not rec.attachment_id:
                raise ValidationError(
                    "Attach the dataset file before computing its digest (REQ-32.5)."
                )
            payload = base64.b64decode(rec.attachment_id.datas or b"")
            if not payload:
                raise ValidationError("The attached dataset file is empty.")
            rec.sha256_checksum = hashlib.sha256(payload).hexdigest()
            rec.file_name = rec.file_name or rec.attachment_id.name

    def action_release(self):
        """REQ-32.5: production release needs a digest and >= 92% accuracy."""
        for rec in self:
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
            if not self.env.user.has_group("cd_entity_config.group_dofa_tier_3"):
                raise UserError(
                    "Production deployment of a retrained Bengali NLU model "
                    "requires DOFA Tier 3 (AI Engineering Director) authority."
                )
            rec.write(
                {
                    "state": "released",
                    "released_by": self.env.user.id,
                    "released_at": fields.Datetime.now(),
                }
            )
