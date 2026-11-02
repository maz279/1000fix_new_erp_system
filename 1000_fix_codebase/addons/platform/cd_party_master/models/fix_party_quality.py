# fix.party.quality — deterministic data-quality scoring (M33, FR-CPM-032,
# KPI-120). The score is COMPUTED from the party record — completeness,
# validity, recency — with the deficiencies listed, so a steward acts on
# causes, not a number.
from odoo import api, fields, models


class FixPartyQuality(models.Model):
    """One scored party record; recomputed on demand (action_recompute)."""

    _name = "fix.party.quality"
    _description = "Party Data Quality"
    _order = "composite desc, id desc"
    # Odoo 19 constraint attribute form
    _partner_unique = models.Constraint("UNIQUE (partner_id)", "One quality record per party")

    partner_id = fields.Many2one(
        "res.partner", string="Party", required=True, ondelete="cascade", index=True
    )
    completeness = fields.Float(string="Completeness %", readonly=True)
    validity = fields.Float(string="Validity %", readonly=True)
    recency = fields.Float(string="Recency %", readonly=True)
    composite = fields.Float(
        string="Composite %",
        readonly=True,
        help="50% completeness + 30% validity + 20% recency (KPI-120 weights)",
    )
    deficiencies = fields.Text(string="Deficiencies (JSON)", readonly=True)
    evaluated_at = fields.Datetime(string="Evaluated At", readonly=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    # The checklist every party is scored against — deterministic, no config.
    _CHECKLIST = ("name", "name_bn", "phone", "email", "preferred_language", "role_ids")

    def _score_partner(self, partner):
        import json

        deficiencies = [
            field_name for field_name in self._CHECKLIST if not getattr(partner, field_name, False)
        ]
        completeness = round(
            100.0 * (len(self._CHECKLIST) - len(deficiencies)) / len(self._CHECKLIST), 1
        )

        # Validity judges the QUALITY of what is filled; a missing value is a
        # completeness deficiency, not a validity failure.
        email_ok = bool(partner.email) and "@" in partner.email
        phone_digits = "".join(c for c in (partner.phone or "") if c.isdigit())
        validity_checks = [
            email_ok or not bool(partner.email),
            bool(len(phone_digits) >= 11) or not bool(partner.phone),
            bool(partner.identity_document_ids),  # identity presence is a validity signal
        ]
        validity = round(100.0 * sum(validity_checks) / len(validity_checks), 1)

        last_write = partner.write_date or partner.create_date
        age_days = (fields.Datetime.now() - last_write).days if last_write else 9999
        recency = 100.0 if age_days <= 365 else max(0.0, 100.0 - (age_days - 365) / 10.0)
        recency = round(recency, 1)

        composite = round(0.5 * completeness + 0.3 * validity + 0.2 * recency, 1)
        return {
            "completeness": completeness,
            "validity": validity,
            "recency": recency,
            "composite": composite,
            "deficiencies": json.dumps(deficiencies),
            "evaluated_at": fields.Datetime.now(),
        }

    def action_recompute(self):
        for quality in self:
            quality.write(quality._score_partner(quality.partner_id))
        return True

    @api.model
    def action_recompute_all(self, limit=500):
        """Upsert quality for parties holding roles (the governed base)."""
        partners = self.env["fix.party.role"].search([]).mapped("partner_id")[:limit]
        for partner in partners:
            existing = self.search([("partner_id", "=", partner.id)], limit=1)
            if existing:
                existing.action_recompute()
            else:
                self.create({"partner_id": partner.id, **self._score_partner(partner)})
        return True
