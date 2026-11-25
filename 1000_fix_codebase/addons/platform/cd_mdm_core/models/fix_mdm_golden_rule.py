# fix.mdm.golden.rule — the golden-record rule engine (P03-M07-T07).
# Defines which field wins when M33's dedup engine finds duplicate records.
#
# A12 audit M64 (2026-11-04) gr_01: strategy=highest_priority_source silently
# behaved like "first candidate" — the priority order it was named for was
# never read, so the survivor was whichever record the search happened to
# return first. It now orders candidates by their source's position in
# priority_source_ids (unknown sources last, then most recent).
#
# A12 finish audit (E20): the priority order is each source's match-rule
# sequence (a many2many stores no order of its own), and fix.party.merge now
# calls resolve() per rule, storing each outcome in the merge audit.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixMdmGoldenRule(models.Model):
    """A golden-record survivorship rule.

    When the dedup engine (fix.dedup.rule in cd_party_master) identifies
    duplicates, these rules determine which record's value survives for each
    field. Example: "for phone, the most recently verified value wins".
    """

    _name = "fix.mdm.golden.rule"
    _description = "Golden Record Survivorship Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "model_name, field_name, sequence"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _model_field_unique = models.Constraint(
        "UNIQUE (model_name, field_name)", "One survivorship rule per model+field"
    )

    sequence = fields.Integer(default=10)
    model_name = fields.Char(
        string="Target Model",
        required=True,
        index=True,
        help="e.g. 'res.partner' — the model this rule governs",
    )
    field_name = fields.Char(
        string="Field", required=True, index=True, help="e.g. 'phone' — the field this rule decides"
    )
    strategy = fields.Selection(
        [
            ("most_recent", "Most Recent Non-Empty"),
            ("most_verified", "Most Verified (verification_status = verified)"),
            ("longest_value", "Longest Non-Empty Value"),
            ("highest_priority_source", "Highest-Priority Source"),
            ("manual_review", "Require Manual Review"),
        ],
        required=True,
        default="most_recent",
        help="How the winning value is chosen when duplicates conflict",
    )
    priority_source_ids = fields.Many2many(
        "fix.mdm.match.rule",
        string="Priority Sources",
        help="Only used with strategy=highest_priority_source. Ranked by each source's "
        "sequence, lowest first.",
    )
    description = fields.Text()
    active = fields.Boolean(default=True)

    @api.constrains("model_name", "field_name")
    def _check_target_exists(self):
        # gr_02: a survivorship rule for a model/field that is not there can
        # never fire — and silently makes resolve() fall back to no-rule.
        for rec in self:
            if rec.model_name not in self.env:
                raise ValidationError(
                    "Golden-record rule targets model %r, which does not exist." % rec.model_name
                )
            if rec.field_name not in self.env[rec.model_name]._fields:
                raise ValidationError(
                    "%s has no field %r: the survivorship rule cannot govern it."
                    % (rec.model_name, rec.field_name)
                )

    @api.model
    def resolve(self, model_name: str, field_name: str, candidates: list[dict]) -> dict | None:
        """Resolve a golden-record field value from duplicate candidates.

        Args:
            model_name: the target model (e.g. 'res.partner')
            field_name: the field to resolve (e.g. 'phone')
            candidates: list of dicts with 'value', 'write_date',
                        'verification_status' keys

        Returns:
            The winning candidate dict, or None if manual_review.
        """
        rule = self.search(
            [
                ("model_name", "=", model_name),
                ("field_name", "=", field_name),
                ("active", "=", True),
            ],
            limit=1,
        )
        if not rule:
            # No rule: default to most-recent non-empty
            non_empty = [c for c in candidates if c.get("value")]
            return max(non_empty, key=lambda c: c.get("write_date", "")) if non_empty else None

        non_empty = [c for c in candidates if c.get("value")]
        if not non_empty:
            return None

        if rule.strategy == "most_recent":
            return max(non_empty, key=lambda c: c.get("write_date", ""))
        if rule.strategy == "most_verified":
            verified = [c for c in non_empty if c.get("verification_status") == "verified"]
            return verified[0] if verified else non_empty[0]
        if rule.strategy == "longest_value":
            return max(non_empty, key=lambda c: len(str(c.get("value", ""))))
        if rule.strategy == "highest_priority_source":
            # gr_01: the rule's own priority order decides. A candidate names
            # its source by match-rule id ("source_rule_id") or its key
            # ("source"). With no order configured the documented fallback is
            # the first non-empty candidate.
            ranked = {
                r.id: pos
                for pos, r in enumerate(
                    rule.priority_source_ids.sorted(lambda s: (s.sequence, s.id))
                )
            }
            if not ranked:
                return non_empty[0]

            def _rank(cand):
                src = cand.get("source_rule_id") or cand.get("source")
                return ranked.get(src, ranked.get(str(src), len(ranked)))

            best = min(_rank(c) for c in non_empty)
            group = [c for c in non_empty if _rank(c) == best]
            if len(group) == 1:
                return group[0]
            # same priority: the most recent value wins (deterministic)
            return max(group, key=lambda c: str(c.get("write_date", "")))
        if rule.strategy == "manual_review":
            return None  # the dedup engine creates an MDM change request
        return non_empty[0]
