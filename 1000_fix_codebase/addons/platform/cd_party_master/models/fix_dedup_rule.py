# fix.dedup.rule — duplicate-identity prevention rules (P03-M05, M33/M64).
# THE failure mode this kernel exists to prevent: the same human as three
# res.partner rows (walk-in, phone-in, web) each carrying a slice of history.
# Rules declared here feed the M64 golden-record engine in Phase 4+; the
# party kernel enforces the blocking keys at write time.
from odoo import fields, models


class FixDedupRule(models.Model):
    """A deduplication rule: which fields identify the same human."""

    _name = "fix.dedup.rule"
    _description = "Deduplication Rule"

    name = fields.Char(string="Rule Name", required=True)
    # Odoo 19: ondelete='restrict' is rejected for ir.model comodels (module
    # uninstalls delete ir.model rows) - cascade is the required mode.
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
        default=lambda self: self.env.ref("base.model_res_partner").id,
    )
    match_fields = fields.Char(
        string="Match Fields",
        required=True,
        help="Comma-separated field names, e.g. 'phone,name_normalized'",
    )
    scope = fields.Selection(
        [("exact", "Exact Match"), ("fuzzy", "Fuzzy (Levenshtein <= threshold)")],
        string="Scope",
        required=True,
        default="exact",
    )
    threshold = fields.Integer(
        string="Fuzzy Threshold", default=2, help="Maximum edit distance for a fuzzy match"
    )
    action = fields.Selection(
        [("block", "Block Creation (hard fail)"), ("flag", "Flag for Steward Review (M64)")],
        string="Action",
        required=True,
        default="flag",
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    # A rules engine, not transactional data — no OU on purpose (dedup rules
    # are estate-wide: a customer duplicated across two OUs is still one human).
