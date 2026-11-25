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
#
# A12 finish E6/E10: the lifecycle gated nothing. The author certified his own
# pack with note "x", an active pack stayed editable, draft lines moved the VAT
# date, and "load" only stamped a date. Now the certifier differs from the
# creator, a validated pack is frozen, consumers read only active and loaded
# packs, and action_load really copies the lines per kind and says what it did.
from odoo import api, fields, models
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
    load_summary = fields.Char(string="What The Load Did", readonly=True, copy=False)
    line_ids = fields.One2many("fix.country.pack.line", "pack_id", string="Lines")
    active = fields.Boolean(default=True)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "state",
            "certified_by_id",
            "certified_on",
            "loaded_at",
            "load_summary",
        }
        # Past draft the pack is what was checked: a correction goes back to
        # draft before certification, and is a new version after it.
        if self and any(rec.state != "draft" for rec in self):
            guarded |= {"name", "code", "kind", "version", "active", "certification_note"}
        return guarded

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

    def action_back_to_draft(self):
        """A person checking a validated pack found an error: back for correction.
        A certified pack is not reopened; a correction there is a new version."""
        for rec in self:
            if rec.state != "validated":
                raise UserError(
                    "Only a validated pack goes back to draft (%s is %s). After "
                    "certification a correction is a new version." % (rec.code, rec.state)
                )
            rec._guarded().write({"state": "draft"})
            rec.message_post(body="Returned to draft by %s." % self.env.user.name)
        return True

    def action_certify(self, note=None):
        """P1-4: certification is a platform-admin decision, recorded (who,
        when, on what basis) and audited. Only a validated pack qualifies.

        A12 finish E10: and not by whoever created the pack. What the certifier
        signs is their own check against the source; this system cannot and does
        not assert the statutory content is correct."""
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
            if not self.env.su and self.env.user == rec.create_uid:
                raise UserError(
                    "A second person certifies: you created pack %s. Another Platform "
                    "Admin must check it against the source and certify it." % rec.code
                )
            if not (note or rec.certification_note or "").strip():
                raise UserError(
                    "Certify a pack against something: give the certification "
                    "basis (gazette, NBR circular…)."
                )
            if not self.env.su and len((note or rec.certification_note or "").strip()) < 8:
                raise UserError(
                    "'%s' does not say what the pack was checked against. Name the "
                    "gazette or circular and its date." % (note or rec.certification_note)
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

    def _load_divisions(self):
        """Division and district lines become address hierarchy rows (fix.bd.address
        holds a division and a district on each row; a division line is not a row)."""
        Address = self.env["fix.bd.address"].sudo()
        by_code = {line.code: line for line in self.line_ids}
        added = kept = 0
        for line in self.line_ids.filtered("parent_code"):
            division = by_code.get(line.parent_code)
            if not division:
                continue
            domain = [("division", "=", division.name), ("district", "=", line.name)]
            if Address.search_count(domain, limit=1):
                kept += 1
                continue
            Address.create(
                {
                    "division": division.name,
                    "division_bn": division.name_bn,
                    "district": line.name,
                    "district_bn": line.name_bn,
                }
            )
            added += 1
        return "%d address rows added, %d already present" % (added, kept)

    def _load_holidays(self):
        """Holiday lines become holidays on every active national calendar (no
        template and no branch); retiring the pack removes them. The VAT calendar
        reads the active pack directly."""
        calendars = (
            self.env["fix.working.calendar"]
            .sudo()
            .search([("template_id", "=", False), ("branch_id", "=", False)])
        )
        Holiday = self.env["fix.working.calendar.holiday"].sudo()
        added = 0
        for calendar in calendars:
            for line in self.line_ids.filtered("date_value"):
                if Holiday.search_count(
                    [("calendar_id", "=", calendar.id), ("pack_line_id", "=", line.id)], limit=1
                ):
                    continue
                Holiday.create(
                    {
                        "calendar_id": calendar.id,
                        "name": line.name,
                        "name_bn": line.name_bn,
                        "date_from": line.date_value,
                        "date_to": line.date_value,
                        "pack_line_id": line.id,
                    }
                )
                added += 1
        return "%d holidays added to %d national calendar(s)" % (added, len(calendars))

    def _load_postcodes(self):
        """There is no postcode register to copy into: fix.bd.address holds a
        postcode per address. Say so, rather than pretend."""
        return "%d postcode lines made available; nothing was copied" % len(self.line_ids)

    def action_load(self):
        """Load the pack into use. P1-4: only an ACTIVE (certified) pack may load.

        A12 finish E10: it copies per kind (divisions into fix.bd.address, holidays
        into the national calendars, postcodes nowhere) and returns what it did.
        Sudo after the check: the targets are registers a Platform Admin does not
        all hold, and the pack itself is already certified by a second person."""
        summary = ""
        for rec in self:
            if rec.state != "active":
                raise UserError(
                    "Only a certified, active pack can be loaded (%s is %s). Ask a "
                    "platform admin to validate, certify and activate it." % (rec.code, rec.state)
                )
            summary = {
                "divisions": rec._load_divisions,
                "holidays": rec._load_holidays,
                "postcodes": rec._load_postcodes,
            }[rec.kind]()
            rec._guarded().write({"loaded_at": fields.Datetime.now(), "load_summary": summary})
            rec._audit_log("country.pack_loaded", summary)
            rec.message_post(body="Loaded by %s: %s." % (self.env.user.name, summary))
        return {"note": summary} if len(self) == 1 else True

    def action_retire(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Retire an active pack (%s is %s)." % (rec.code, rec.state))
            removed = (
                self.env["fix.working.calendar.holiday"]
                .sudo()
                .search([("pack_line_id", "in", rec.line_ids.ids)])
            )
            count = len(removed)
            removed.unlink()
            rec._guarded().write({"state": "retired"})
            rec._audit_log("country.pack_retired", "%d calendar holidays removed" % count)
            rec.message_post(
                body="Retired by %s; %d calendar holidays removed. Address rows stay: "
                "places do not retire with a pack." % (self.env.user.name, count)
            )


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

    # A12 finish E10: past draft the lines are what the certifier checked.
    def _assert_pack_draft(self, packs):
        frozen = packs.filtered(lambda pack: pack.state != "draft")
        if frozen and not frozen._fix_guard_open():
            raise UserError(
                "Pack %s is %s, so its lines are frozen. Return a validated pack to "
                "draft, or issue a new version of a certified one."
                % (frozen[0].code, frozen[0].state)
            )

    @api.model_create_multi
    def create(self, vals_list):
        packs = self.env["fix.country.pack"].browse(
            {vals["pack_id"] for vals in vals_list if vals.get("pack_id")}
        )
        self._assert_pack_draft(packs)
        return super().create(vals_list)

    def write(self, vals):
        self._assert_pack_draft(self.mapped("pack_id"))
        return super().write(vals)

    def unlink(self):
        self._assert_pack_draft(self.mapped("pack_id"))
        return super().unlink()
