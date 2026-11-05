# fix.country.pack — Bangladesh reference data pack (P03-M04-T06, AF-09).
# The 8 divisions, 64 districts and moon-dependent public holidays are DATA,
# not code (05-06 §9): they load as pack lines so a new district or a revised
# holiday date is a data change, never a deployment. The W1 subset ships the
# structure; the full 64-district pack is MD-005 master data (AF-09-funded).
#
# A12 audit (2026-11-04) P1-4: action_load stamped loaded_at from ANY state,
# so an unreviewed pack could mark itself loaded into statutory calculations.
# A pack now walks a certification lifecycle:
#   draft --action_validate--> validated --action_certify--> certified
#   --action_activate--> active --action_load--> (loaded into use) --retire-->
# Only a CERTIFIED-ACTIVE pack loads, and certification is recorded (who,
# when, on what basis) and audited.
from odoo import fields, models
from odoo.exceptions import UserError

PLATFORM_ADMIN_GROUP = "cd_entity_config.group_platform_admin"


class FixCountryPack(models.Model):
    """The Bangladesh reference-data pack: divisions, districts, holidays."""

    _name = "fix.country.pack"
    _description = "Country Data Pack"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint("UNIQUE (code)", "Pack code must be unique")

    name = fields.Char(string="Pack Name", required=True, tracking=True)
    code = fields.Char(
        string="Pack Code", required=True, size=16, help="e.g. BD-DIV-2026, BD-HOL-2026"
    )
    kind = fields.Selection(
        [
            ("divisions", "Divisions & Districts"),
            ("holidays", "Public Holidays"),
            ("postcodes", "Postcodes"),
        ],
        string="Kind",
        required=True,
        default="divisions",
    )
    version = fields.Char(string="Version", required=True, default="2026.1")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("validated", "Validated"),
            ("certified", "Certified"),
            ("active", "Active"),
            ("retired", "Retired"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    certified_by_id = fields.Many2one("res.users", string="Certified By", readonly=True, copy=False)
    certified_on = fields.Date(string="Certified On", readonly=True, copy=False)
    certification_note = fields.Char(
        string="Certification Basis",
        help="What the pack was checked against (gazette, NBR circular…)",
    )
    loaded_at = fields.Datetime(string="Loaded At", readonly=True)
    line_ids = fields.One2many("fix.country.pack.line", "pack_id", string="Lines")
    active = fields.Boolean(default=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "certified_by_id",
            "certified_on",
            "loaded_at",
        }

    def _audit_log(self, event, detail):
        for rec in self:
            rec.env["fix.security.audit"].sudo().log_event(
                event,
                "fix.country.pack,%d" % rec.id,
                "%s (%s v%s) by %s" % (detail, rec.code, rec.version, rec.env.user.name),
            )

    def action_validate(self):
        """Structural check: a pack with no lines validates nothing."""
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft pack can be validated (%s is %s)." % (rec.code, rec.state)
                )
            if not rec.line_ids:
                raise UserError("Validate a pack with at least one line (%s is empty)." % rec.code)
            rec._guarded().write({"state": "validated"})
            rec.message_post(body="Validated: %d lines." % len(rec.line_ids))

    def action_certify(self, note=None):
        """P1-4: certification is a platform-admin decision, recorded (who,
        when, on what basis) and audited. Only a validated pack qualifies."""
        for rec in self:
            if rec.state != "validated":
                raise UserError(
                    "Only a validated pack can be certified (%s is %s)." % (rec.code, rec.state)
                )
            if not self.env.su and not self.env.user.has_group(PLATFORM_ADMIN_GROUP):
                raise UserError(
                    "Certifying a country pack requires the 'Platform Admin' role, "
                    "which %s does not hold." % self.env.user.name
                )
            if not (note or rec.certification_note or "").strip():
                raise UserError(
                    "Certify a pack against something: give the certification "
                    "basis (gazette, NBR circular…)."
                )
            rec._guarded().write(
                {
                    "state": "certified",
                    "certified_by_id": self.env.uid,
                    "certified_on": fields.Date.context_today(rec),
                    "certification_note": (note or rec.certification_note or "").strip()[:250],
                }
            )
            rec._audit_log(
                "country.pack_certified",
                "certified against %s" % (note or rec.certification_note),
            )
            rec.message_post(
                body="Certified by %s against %s."
                % (self.env.user.name, note or rec.certification_note)
            )

    def action_activate(self):
        for rec in self:
            if rec.state != "certified":
                raise UserError(
                    "Only a certified pack can be activated (%s is %s)." % (rec.code, rec.state)
                )
            rec._guarded().write({"state": "active"})
            rec._audit_log("country.pack_activated", "certified pack activated")
            rec.message_post(body="Activated by %s." % self.env.user.name)

    def action_load(self):
        """Load the pack into use. P1-4: only an ACTIVE (certified) pack may
        load - the actual rows are master data (AF-09), loaded by the data
        pipeline, never hard-coded in this module."""
        for rec in self:
            if rec.state != "active":
                raise UserError(
                    "Only a certified, active pack can be loaded (%s is %s). Ask a "
                    "platform admin to validate, certify and activate it." % (rec.code, rec.state)
                )
            rec._guarded().write({"loaded_at": fields.Datetime.now()})
            rec.message_post(body="Loaded by %s." % self.env.user.name)
        return True

    def action_retire(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Retire an active pack (%s is %s)." % (rec.code, rec.state))
            rec._guarded().write({"state": "retired"})
            rec.message_post(body="Retired by %s." % self.env.user.name)


class FixCountryPackLine(models.Model):
    """One entry of a data pack — a division, district, holiday or postcode."""

    _name = "fix.country.pack.line"
    _description = "Country Data Pack Line"

    pack_id = fields.Many2one("fix.country.pack", required=True, ondelete="cascade")
    parent_code = fields.Char(
        string="Parent Code", help="District lines point at their division code"
    )
    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name (English)", required=True)
    name_bn = fields.Char(
        string="Name (Bengali)",
        required=True,
        help="DE-17: Bengali is not optional for place names",
    )
    date_value = fields.Date(string="Date (holiday packs)")
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _pack_code_unique = models.Constraint("UNIQUE (pack_id, code)", "Code appears once per pack")
