# fix.pipeline — multi-pipeline configuration (M07, FR-CRM-010, T-02).
# Adding a pipeline for a new revenue stream is CONFIGURATION, not code:
# stages_json carries the stage model with entry criteria and default
# probabilities; BRU-CRM-03 gates advancement on the criteria being confirmed.
import json

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixPipeline(models.Model):
    """A revenue-stream pipeline with its own stage model."""

    _name = "fix.pipeline"
    _description = "Sales Pipeline"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"
    # Odoo 19 constraint attribute form
    _code_unique = models.Constraint("UNIQUE (code)", "Each pipeline code exists once")

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    revenue_stream = fields.Selection(
        [
            ("msp", "Managed Services"),
            ("amc", "AMC / RAMC"),
            ("corporate_repair", "Corporate Repair"),
            ("rental", "Rental / EaaS"),
            ("refurb", "Refurbishment Sales"),
            ("data_services", "Data Services"),
            ("cross_sell", "Cross-Sell / Upsell"),
            ("renewal", "Renewal"),
            ("winback", "Win-Back"),
        ],
        string="Revenue Stream",
        required=True,
        tracking=True,
    )
    # T-02: [{stage, criteria, requires_confirmation, probability}] — the
    # stage name matches the crm.stage name used by this pipeline's team.
    stages_json = fields.Text(
        string="Stages (JSON)",
        help='JSON list, e.g. [{"stage": "Proposal", "criteria": "quotation '
        'requested (M36)", "requires_confirmation": true, "probability": 40}]',
    )
    default_probability = fields.Float(string="Default Probability %", default=10.0)
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.constrains("stages_json")
    def _check_stages_json(self):
        for pipeline in self:
            if not pipeline.stages_json:
                continue
            # Explicit checks, not `assert`: asserts vanish under `python -O`,
            # which would let a malformed pipeline through unvalidated.
            allowed = {"stage", "criteria", "requires_confirmation", "probability"}
            try:
                stages = json.loads(pipeline.stages_json)
                if not isinstance(stages, list):
                    raise ValueError("not a list")
                for entry in stages:
                    if not isinstance(entry, dict) or not set(entry) <= allowed:
                        raise ValueError("unexpected keys in %r" % (entry,))
                    if not entry.get("stage"):
                        raise ValueError("an entry has no stage")
            except Exception as exc:
                raise ValidationError(
                    "stages_json must be a JSON list of {stage, criteria, "
                    "requires_confirmation, probability} objects (%s)" % exc
                ) from exc

    def stage_rules(self):
        """The parsed stage rules: {stage_name: entry} for gating."""
        rules = {}
        for pipeline in self:
            for entry in json.loads(pipeline.stages_json or "[]"):
                rules[entry["stage"]] = entry
        return rules
