# fix.mdm.match.rule — field-level match rules for dedup scoring (P03-M07).
# Defines which fields contribute to a duplicate match score and their weights.
#
# A12 audit M64 (2026-11-04) mr_01: weight had no bounds, so one field could
# alone push any pair over the duplicate threshold (or carry 0 and still be
# counted). A match weight is now strictly (0, 1].
#
# A12 finish audit (E21): match rules had no consumer and nothing raised a
# candidate. cron_detect_duplicates scores pairs from these rules, in SQL and
# bounded per run, so it stays cheap on 15k partners. Every pair already in the
# register, whatever its decision, is left out: a dismissed pair stays dismissed.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import SQL

logger = logging.getLogger(__name__)

# Tunables, read per run (ir.config_parameter).
PARAM_MIN_SCORE = "fix_mdm.dup_candidate_min_score"
PARAM_MAX_PAIRS = "fix_mdm.dup_detect_max_pairs"
PARAM_MAX_BLOCK = "fix_mdm.dup_detect_max_block"
DEFAULT_MIN_SCORE = 40.0
DEFAULT_MAX_PAIRS = 200
# A key shared by more records than this identifies nobody (a common name): it
# raises no pairs, which also keeps the pair count of one run bounded.
DEFAULT_MAX_BLOCK = 50
# Bengali digits compare as ASCII digits.
_BN_DIGITS, _ASCII_DIGITS = "০১২৩৪৫৬৭৮৯", "0123456789"


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

    # ---- detection (E21) ---------------------------------------------------
    @api.model
    def _key_sql(self, alias, rule):
        """The comparison key of one rule's field on one table alias. A numeric
        rule keeps the last 10 digits (a phone with or without +880); otherwise
        case, spaces and punctuation go, unless the rule asks for exact text.
        Bengali digits always compare as ASCII digits."""
        column = SQL("%s.%s", SQL.identifier(alias), SQL.identifier(rule.field_name))
        text = SQL("translate(%s::text, %s, %s)", column, _BN_DIGITS, _ASCII_DIGITS)
        if rule.match_type == "numeric":
            return SQL("right(regexp_replace(%s, '[^0-9]', '', 'g'), 10)", text)
        if rule.normalize or rule.match_type in ("fuzzy", "phonetic"):
            return SQL("regexp_replace(lower(%s), '[[:space:][:punct:]]', '', 'g')", text)
        return text

    @api.model
    def _detectable_rules(self, model_name):
        """Active rules this run can compare in SQL: stored scalar columns."""
        model = self.env[model_name]
        kept = self.browse()
        for rule in self.sudo().search([("model_name", "=", model_name), ("active", "=", True)]):
            field = model._fields.get(rule.field_name)
            if field and field.store and field.column_type and field.type != "binary":
                kept |= rule
            else:
                logger.info("Match rule %s.%s is not comparable", model_name, rule.field_name)
        return kept

    @api.model
    def _detect_pairs(self, model_name, limit, min_score, max_block):
        """(a_id, b_id, score, matched field names) for new pairs at or above
        the score.

        Each rule blocks on its own key: only records sharing a key that at most
        `max_block` records carry are compared, so the work stays bounded whatever
        the size of the master. The score is the share of rule weight that matches."""
        model = self.env[model_name]
        rules = self._detectable_rules(model_name)
        total_weight = sum(rules.mapped("weight"))
        if not rules or not total_weight:
            return []
        self.env.flush_all()
        table = SQL.identifier(model._table)
        weights, names = [], []
        for rule in rules:
            same = SQL(
                "%s = %s AND %s <> ''",
                self._key_sql("a", rule),
                self._key_sql("b", rule),
                self._key_sql("a", rule),
            )
            weights.append(SQL("CASE WHEN %s THEN %s ELSE 0 END", same, rule.weight))
            names.append(SQL("CASE WHEN %s THEN %s END", same, rule.field_name))
        score = SQL("(100.0 * (%s) / %s)", SQL(" + ").join(weights), total_weight)
        active = SQL("a.active AND") if "active" in model._fields else SQL()
        found, seen = [], set()
        for rule in rules:
            if len(found) >= limit:
                break
            self.env.cr.execute(
                SQL(
                    """
                    WITH keyed AS (
                        SELECT a.id, %(key)s AS k FROM %(table)s a
                         WHERE %(active)s %(key)s <> ''
                    ), blocks AS (
                        SELECT k FROM keyed GROUP BY k
                        HAVING count(*) BETWEEN 2 AND %(max_block)s
                    ), candidates AS (
                        SELECT ka.id AS a_id, kb.id AS b_id
                          FROM blocks
                          JOIN keyed ka ON ka.k = blocks.k
                          JOIN keyed kb ON kb.k = blocks.k AND ka.id < kb.id
                    )
                    SELECT a.id, b.id, %(score)s,
                           array_remove(ARRAY[%(names)s]::text[], NULL)
                      FROM candidates c
                      JOIN %(table)s a ON a.id = c.a_id
                      JOIN %(table)s b ON b.id = c.b_id
                     WHERE %(score)s >= %(min_score)s
                       AND NOT EXISTS (
                           SELECT 1 FROM fix_mdm_duplicate d
                            WHERE d.res_model = %(model)s
                              AND d.record_a_ref = a.id::text AND d.record_b_ref = b.id::text)
                       AND NOT EXISTS (
                           SELECT 1 FROM fix_mdm_duplicate d
                            WHERE d.res_model = %(model)s
                              AND d.record_a_ref = b.id::text AND d.record_b_ref = a.id::text)
                     LIMIT %(limit)s
                    """,
                    key=self._key_sql("a", rule),
                    table=table,
                    active=active,
                    max_block=max_block,
                    score=score,
                    names=SQL(", ").join(names),
                    min_score=min_score,
                    model=model_name,
                    limit=limit - len(found),
                )
            )
            for a_id, b_id, pair_score, matched in self.env.cr.fetchall():
                if (a_id, b_id) not in seen:
                    seen.add((a_id, b_id))
                    found.append((a_id, b_id, float(pair_score), matched))
        return found

    @api.model
    def cron_detect_duplicates(self):
        """E21 (daily): raise candidate pairs for a steward to decide. Nothing
        merges here: a merge stays a supervised, routed M33 decision."""
        if not self.env.su:
            raise UserError("Duplicate detection runs as the system only.")
        icp = self.env["ir.config_parameter"].sudo()
        min_score = float(icp.get_param(PARAM_MIN_SCORE, DEFAULT_MIN_SCORE))
        budget = int(icp.get_param(PARAM_MAX_PAIRS, DEFAULT_MAX_PAIRS))
        max_block = int(icp.get_param(PARAM_MAX_BLOCK, DEFAULT_MAX_BLOCK))
        Duplicate = self.env["fix.mdm.duplicate"].sudo()
        raised = 0
        models_with_rules = set(self.sudo().search([("active", "=", True)]).mapped("model_name"))
        for model_name in sorted(models_with_rules):
            if budget - raised <= 0 or model_name not in self.env:
                continue
            pairs = self._detect_pairs(model_name, budget - raised, min_score, max_block)
            if pairs:
                Duplicate.create(
                    [
                        {
                            "res_model": model_name,
                            "record_a_ref": str(a_id),
                            "record_b_ref": str(b_id),
                            "score": round(score, 2),
                            "match_factors": ", ".join(matched)[:250],
                        }
                        for a_id, b_id, score, matched in pairs
                    ]
                )
                raised += len(pairs)
        logger.info("Duplicate detection raised %d candidate pair(s)", raised)
        return raised
