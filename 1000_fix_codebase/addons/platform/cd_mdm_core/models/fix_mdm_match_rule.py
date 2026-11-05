# fix.mdm.match.rule — field-level match rules for dedup scoring (P03-M07).
# Defines which fields contribute to a duplicate match score and their weights.
#
# A12 audit M64 (2026-11-04) mr_01: weight had no bounds, so one field could
# alone push any pair over the duplicate threshold (or carry 0 and still be
# counted). A match weight is now strictly (0, 1].
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixMdmMatchRule(models.Model):
    """A field-level match rule used by M33's dedup engine.

    Each rule assigns a weight to a field: when two records match on that
    field, the weight is added to the overall match score. Above a threshold,
    records are flagged as potential duplicates.
    """

    _name = "fix.mdm.match.rule"
    _description = "MDM Match Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "model_name, sequence"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _model_field_unique = models.Constraint(
        "UNIQUE (model_name, field_name)", "One match rule per model+field"
    )

    sequence = fields.Integer(default=10)
    model_name = fields.Char(string="Target Model", required=True, index=True)
    field_name = fields.Char(string="Field", required=True, index=True)
    match_type = fields.Selection(
        [
            ("exact", "Exact Match"),
            ("fuzzy", "Fuzzy (normalised)"),
            ("phonetic", "Phonetic (Bengali-aware)"),
            ("numeric", "Numeric"),
        ],
        required=True,
        default="exact",
    )
    weight = fields.Float(
        default=1.0,
        required=True,
        help="Contribution to the match score when this field matches (0-1.0)",
    )
    normalize = fields.Boolean(
        default=True, help="Strip spaces, case-fold, normalise Bengali digits before matching"
    )
    description = fields.Text()
    active = fields.Boolean(default=True)

    @api.constrains("weight")
    def _check_weight_bounds(self):
        # mr_01: a match weight is a share of the score, not an arbitrary
        # multiplier: one field must not alone decide a duplicate pair.
        for rec in self:
            if not (0.0 < rec.weight <= 1.0):
                raise ValidationError(
                    "Match weight of %s on %s.%s must be within (0, 1] — got %s."
                    % (rec.match_type, rec.model_name, rec.field_name, rec.weight)
                )

    @api.constrains("model_name", "field_name")
    def _check_target_exists(self):
        for rec in self:
            if rec.model_name not in self.env:
                raise ValidationError(
                    "Match rule targets model %r, which does not exist." % rec.model_name
                )
            if rec.field_name not in self.env[rec.model_name]._fields:
                raise ValidationError(
                    "%s has no field %r: the match rule cannot score it."
                    % (rec.model_name, rec.field_name)
                )
