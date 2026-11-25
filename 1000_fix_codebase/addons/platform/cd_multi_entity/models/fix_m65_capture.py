# M65 capture audit (2026-11-18): the records M65's specification owns (§10.1)
# that no code had, so the sub-module pages that cover them could capture
# nothing (Translation offered "+ New Locale Pack"; Entity Structure and
# Jurisdiction had nothing past their own register).
#
#   fix.entity.jurisdiction          entity <-> country pack assignment
#                                    (FR-GLO-001/010): which active pack an
#                                    entity uses, at which version, with its
#                                    default locale and reporting currency. A
#                                    new assignment supersedes the old one,
#                                    which stays readable (BRU-GLO-14).
#   fix.jurisdiction.residency.rule  residency and cross-border transfer rules
#                                    per country and data class (FR-GLO-015,
#                                    BRU-GLO-13), verified by a second Platform
#                                    Admin. M29 does not read it yet: the
#                                    screens say so.
#   fix.country.onboarding           the governed onboarding of a new country
#                                    (FR-GLO-035): discovery -> pack authoring
#                                    -> translation -> integration ->
#                                    validation -> pilot -> active, each step
#                                    gated on the registers, the zero-core-
#                                    change gate (BRU-GLO-02) before the pilot,
#                                    activation by a second person, measured
#                                    against the 12-week target.
#   fix.translation.entry            a translation submitted for review
#                                    (FR-GLO-022/024, BRU-GLO-07): a second
#                                    person approves it; machine translation is
#                                    refused; an approved translation of a
#                                    record field is written into that record
#                                    in the locale's language.
#   fix.rendering.verification       Bengali rendering evidence per target
#                                    (FR-GLO-025): Android, iOS, Windows,
#                                    thermal, label, PDF.
#
# Deliberately NOT built (see the audit report): identifier formats, holiday
# sets with provisional moon-dependent dates, fiscal calendars (M19 owns the
# periods), exchange rates (Odoo's rates + M50), the tax and payroll rule
# registers (M51 and M56 compute from their own), statutory report definitions,
# the entity lifecycle and one-action entity provisioning.
from odoo import api, fields, models
from odoo.addons.cd_entity_config.models.fix_entity import audit_event, require_platform_admin
from odoo.exceptions import AccessError, UserError, ValidationError

PLATFORM_ADMIN_GROUP = "cd_entity_config.group_platform_admin"
STEWARD_GROUP = "cd_entity_config.group_mdm_domain_steward"
SYSTEM_GROUP = "base.group_system"
# FR-GLO-035 / KPI: a new jurisdiction is stood up in at most twelve weeks.
ONBOARDING_TARGET_WEEKS = 12
MIN_NOTE = 10

DATA_CLASSES = [
    ("personal", "Personal Data"),
    ("sensitive", "Sensitive Personal Data"),
    ("financial", "Financial / Payment Data"),
    ("health", "Health Data"),
    ("biometric", "Biometric Data"),
    ("device", "Device & Telemetry Data"),
    ("business", "Business Records"),
]

PHASES = [
    ("discovery", "1. Obligation Discovery"),
    ("pack_authoring", "2. Pack Authoring"),
    ("translation", "3. Translation"),
    ("integration", "4. Integration Selection"),
    ("validation", "5. Validation"),
    ("pilot", "6. Pilot"),
    ("active", "7. Active"),
    ("abandoned", "Abandoned"),
]
NEXT_PHASE = {
    "discovery": "pack_authoring",
    "pack_authoring": "translation",
    "translation": "integration",
    "integration": "validation",
    "validation": "pilot",
    "pilot": "active",
}

RENDER_TARGETS = [
    ("android", "Android"),
    ("ios", "iOS"),
    ("windows", "Windows"),
    ("thermal", "Thermal Printer"),
    ("label", "Label Printer"),
    ("pdf", "PDF / PDF-A"),
]


def _is_platform_admin(env):
    return env.su or env.user.has_group(PLATFORM_ADMIN_GROUP) or env.user.has_group(SYSTEM_GROUP)


def _is_language_steward(env):
    return _is_platform_admin(env) or env.user.has_group(STEWARD_GROUP)


def _require_language_steward(env, what):
    if not _is_language_steward(env):
        raise AccessError(
            "%s needs the 'Platform Admin' or 'MDM Domain Steward' role, which %s does "
            "not hold." % (what, env.user.name)
        )


def _note(note, what):
    note = (note or "").strip()
    if len(note) < MIN_NOTE:
        raise UserError(
            "%s needs a note of at least %d characters saying what you checked." % (what, MIN_NOTE)
        )
    return note


def _changed(records, vals, keep=()):
    """The fields of `vals` that really change a value on `records`. A workspace
    form re-sends every field it shows, so an unchanged value is not an edit."""
    return {
        name
        for name in vals
        if name not in keep
        and not name.startswith("message_")
        and name in records._fields
        and any(rec._fix_guard_differs(name, vals[name], rec[name]) for rec in records)
    }


def _label(record, field):
    return dict(record._fields[field].selection).get(record[field], record[field] or "")


# ---------------------------------------------------------------------------
# Entity <-> country pack assignment (FR-GLO-001, FR-GLO-010, BRU-GLO-14)
# ---------------------------------------------------------------------------
class FixEntityJurisdiction(models.Model):
    _name = "fix.entity.jurisdiction"
    _description = "Entity Country Pack Assignment"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "entity_id, pack_kind, assigned_on desc, id desc"

    entity_id = fields.Many2one(
        "fix.entity", string="Legal Entity", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(
        related="entity_id.company_id", store=True, index=True, string="Company"
    )
    country_pack_id = fields.Many2one(
        "fix.country.pack",
        string="Country Pack",
        required=True,
        ondelete="restrict",
        domain=[("state", "=", "active")],
    )
    pack_kind = fields.Selection(related="country_pack_id.kind", store=True, string="Pack Kind")
    pack_version = fields.Char(string="Pack Version (at assignment)", readonly=True, copy=False)
    locale_pack_id = fields.Many2one(
        "fix.locale.pack",
        string="Default Locale",
        ondelete="restrict",
        domain=[("state", "=", "active")],
    )
    base_currency_id = fields.Many2one(
        related="entity_id.currency_id", string="Base Currency", readonly=True
    )
    reporting_currency_id = fields.Many2one("res.currency", string="Group Reporting Currency")
    note = fields.Char(string="Note")
    state = fields.Selection(
        [("current", "Current"), ("superseded", "Superseded")],
        required=True,
        default="current",
        tracking=True,
    )
    assigned_by_id = fields.Many2one("res.users", string="Assigned By", readonly=True, copy=False)
    assigned_on = fields.Datetime(string="Assigned On", readonly=True, copy=False)
    superseded_by_id = fields.Many2one(
        "fix.entity.jurisdiction", string="Superseded By", readonly=True, copy=False
    )
    superseded_on = fields.Datetime(string="Superseded On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "pack_version",
            "assigned_by_id",
            "assigned_on",
            "superseded_by_id",
            "superseded_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            # an assignment is history: a change is a new assignment
            locked |= {
                "entity_id",
                "country_pack_id",
                "locale_pack_id",
                "reporting_currency_id",
            }
        return locked

    @api.depends("entity_id", "country_pack_id", "pack_version")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s · %s v%s" % (
                rec.entity_id.code or rec.entity_id.legal_name or "?",
                rec.country_pack_id.code or "?",
                rec.pack_version or rec.country_pack_id.version or "?",
            )

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "Assigning a country pack to an entity")
        records = super().create(vals_list)
        for rec in records:
            pack = rec.country_pack_id
            if pack.state != "active":
                raise UserError(
                    "Only an active country pack can be assigned to an entity (%s is %s). "
                    "Validate, certify and activate it first." % (pack.code, _label(pack, "state"))
                )
            if rec.locale_pack_id and rec.locale_pack_id.state != "active":
                raise UserError(
                    "The default locale must be an active locale pack (%s is %s)."
                    % (rec.locale_pack_id.code, _label(rec.locale_pack_id, "state"))
                )
            previous = self.search(
                [
                    ("id", "!=", rec.id),
                    ("entity_id", "=", rec.entity_id.id),
                    ("pack_kind", "=", rec.pack_kind),
                    ("state", "=", "current"),
                ]
            )
            now = fields.Datetime.now()
            rec._guarded().write(
                {
                    "pack_version": pack.version,
                    "assigned_by_id": rec.env.uid,
                    "assigned_on": now,
                }
            )
            previous._guarded().write(
                {"state": "superseded", "superseded_by_id": rec.id, "superseded_on": now}
            )
            audit_event(
                rec.env,
                "entity.pack_assigned",
                "fix.entity.jurisdiction,%d" % rec.id,
                "%s -> %s v%s (superseding %d)"
                % (rec.entity_id.code, pack.code, pack.version, len(previous)),
            )
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            require_platform_admin(self.env, "An entity's country pack assignment")
            frozen = _changed(self, vals, keep=("note",))
            if frozen:
                raise UserError(
                    "An assignment is history and cannot be changed (%s). Assign the "
                    "entity again: the new assignment supersedes this one."
                    % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError(
                "An entity's pack assignment is history and is never deleted: assign "
                "again to supersede it."
            )
        return super().unlink()


# ---------------------------------------------------------------------------
# Residency and cross-border transfer rules (FR-GLO-015, BRU-GLO-13)
# ---------------------------------------------------------------------------
class FixJurisdictionResidencyRule(models.Model):
    _name = "fix.jurisdiction.residency.rule"
    _description = "Data Residency Rule"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "country_id, data_class, effective_from desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    country_id = fields.Many2one("res.country", string="Country", required=True, tracking=True)
    data_class = fields.Selection(DATA_CLASSES, string="Data Class", required=True, tracking=True)
    residency_required = fields.Boolean(
        string="Must Stay In Country",
        tracking=True,
        help="The data must be stored and processed inside the country.",
    )
    cross_border_permitted = fields.Boolean(
        string="Cross-Border Transfer Permitted",
        tracking=True,
        help="The data may leave the country under the safeguard stated.",
    )
    notification_required = fields.Boolean(
        string="Transfer Must Be Notified",
        tracking=True,
        help="A permitted transfer must be notified to the authority.",
    )
    safeguard_required = fields.Char(
        string="Safeguard Required",
        tracking=True,
        help="e.g. explicit consent, standard contractual clauses, authority approval",
    )
    authority_name = fields.Char(string="Authority", required=True, tracking=True)
    statute_reference = fields.Char(
        string="Statute / Clause", required=True, tracking=True, help="Act, section and year"
    )
    effective_from = fields.Date(string="Effective From", required=True, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("verified", "Verified"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_on = fields.Datetime(string="Verified On", readonly=True, copy=False)
    verification_note = fields.Char(string="Verified Against", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "verified_by_id",
            "verified_on",
            "verification_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._fields) - {"message_ids", "message_follower_ids"}
        return locked

    @api.depends("country_id", "data_class")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s · %s" % (
                rec.country_id.code or "?",
                _label(rec, "data_class") if rec.data_class else "?",
            )

    @api.constrains("residency_required", "cross_border_permitted", "notification_required")
    def _check_consistent(self):
        for rec in self:
            if rec.residency_required and rec.cross_border_permitted:
                raise ValidationError(
                    "Data that must stay in the country cannot also be permitted to "
                    "cross the border: choose one."
                )
            if rec.notification_required and not rec.cross_border_permitted:
                raise ValidationError(
                    "A transfer can only need notifying when cross-border transfer is permitted."
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The data residency rule register")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            require_platform_admin(self.env, "The data residency rule register")
            if self.filtered(lambda r: r.state != "draft") and _changed(self, vals):
                raise UserError(
                    "A verified or retired residency rule is frozen. Record a new rule: "
                    "verifying it retires this one."
                )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda r: r.state != "draft") and not self.env.su:
            raise UserError("A verified residency rule is kept; retire it instead.")
        return super().unlink()

    def action_verify(self, note=None):
        """A second Platform Admin checks the rule against the statute. Verifying
        it retires the verified rule it replaces (same country and data class)."""
        if not _is_platform_admin(self.env):
            raise AccessError(
                "Verifying a residency rule needs the 'Platform Admin' role, which %s "
                "does not hold." % self.env.user.name
            )
        note = _note(note, "Verifying a residency rule")
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft rule is verified (%s is %s)." % (rec.display_name, rec.state)
                )
            if not rec.env.su and rec.env.user == rec.create_uid:
                raise UserError(
                    "A second person verifies a residency rule: you recorded %s." % rec.display_name
                )
            replaced = self.search(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("country_id", "=", rec.country_id.id),
                    ("data_class", "=", rec.data_class),
                    ("state", "=", "verified"),
                ]
            )
            replaced._guarded().write({"state": "retired"})
            rec._guarded().write(
                {
                    "state": "verified",
                    "verified_by_id": rec.env.uid,
                    "verified_on": fields.Datetime.now(),
                    "verification_note": note,
                }
            )
            audit_event(
                rec.env,
                "jurisdiction.residency_verified",
                "fix.jurisdiction.residency.rule,%d" % rec.id,
                "%s against %s (retired %d)" % (rec.display_name, note, len(replaced)),
            )
        return True

    def action_retire(self):
        if not _is_platform_admin(self.env):
            raise AccessError(
                "Retiring a residency rule needs the 'Platform Admin' role, which %s does "
                "not hold." % self.env.user.name
            )
        for rec in self:
            if rec.state != "verified":
                raise UserError(
                    "Retire a verified rule (%s is %s)." % (rec.display_name, rec.state)
                )
            rec._guarded().write({"state": "retired"})
            rec.message_post(body="Retired by %s." % self.env.user.name)
        return True


# ---------------------------------------------------------------------------
# Country onboarding (FR-GLO-035, BRU-GLO-02, BRU-GLO-05)
# ---------------------------------------------------------------------------
class FixCountryOnboarding(models.Model):
    _name = "fix.country.onboarding"
    _description = "Country Onboarding"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "initiated_on desc, id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    country_id = fields.Many2one("res.country", string="Country", required=True, tracking=True)
    lead_id = fields.Many2one(
        "res.users", string="Country Lead", required=True, default=lambda self: self.env.user
    )
    phase = fields.Selection(PHASES, required=True, default="discovery", tracking=True)
    initiated_on = fields.Date(string="Initiated On", readonly=True, copy=False)
    piloted_on = fields.Date(string="Pilot Started On", readonly=True, copy=False)
    activated_on = fields.Date(string="Activated On", readonly=True, copy=False)
    activated_by_id = fields.Many2one("res.users", string="Activated By", readonly=True, copy=False)
    abandoned_reason = fields.Char(string="Why Abandoned", readonly=True, copy=False)
    pack_ids = fields.Many2many("fix.country.pack", string="Country Packs")
    locale_pack_id = fields.Many2one("fix.locale.pack", string="Locale Pack")
    gateway_ids = fields.Many2many("fix.payment.gateway", string="Payment Gateways")
    core_changes_required = fields.Boolean(
        string="Needs A Core Code Change",
        tracking=True,
        help="BRU-GLO-02: tick if standing the country up needs any change to core "
        "module code. The pilot is refused while it is ticked.",
    )
    core_change_note = fields.Text(string="Core Changes Found")
    obligations_discovered = fields.Integer(
        string="Obligations Recorded", compute="_compute_registers"
    )
    residency_assessed = fields.Boolean(string="Residency Assessed", compute="_compute_registers")
    elapsed_weeks = fields.Float(
        string="Elapsed Weeks", compute="_compute_registers", digits=(16, 1)
    )
    on_target = fields.Boolean(string="Within 12 Weeks", compute="_compute_registers")
    gate_result = fields.Selection(
        [("open", "Open"), ("passed", "Passed"), ("failed", "Failed")],
        string="Zero-Core-Change Gate",
        compute="_compute_registers",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "phase",
            "initiated_on",
            "piloted_on",
            "activated_on",
            "activated_by_id",
            "abandoned_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.phase in ("active", "abandoned"):
            locked |= set(self._fields) - {"message_ids", "message_follower_ids"}
        if self and self.phase != "discovery":
            locked |= {"country_id"}
        return locked

    def _country_code(self):
        return (self.country_id.code or "").upper()

    @api.depends("country_id", "phase", "initiated_on", "activated_on", "core_changes_required")
    def _compute_registers(self):
        Rule = self.env["fix.jurisdiction.rule"]
        Residency = self.env["fix.jurisdiction.residency.rule"]
        today = fields.Date.context_today(self)
        for rec in self:
            code = rec._country_code()
            rec.obligations_discovered = (
                Rule.search_count([("active", "=", True), ("jurisdiction", "=ilike", code + "%")])
                if code
                else 0
            )
            rec.residency_assessed = bool(
                rec.country_id
                and Residency.search_count(
                    [("country_id", "=", rec.country_id.id), ("state", "=", "verified")]
                )
            )
            start = rec.initiated_on
            end = rec.activated_on or today
            rec.elapsed_weeks = round((end - start).days / 7.0, 1) if start else 0.0
            rec.on_target = rec.elapsed_weeks <= ONBOARDING_TARGET_WEEKS
            if rec.core_changes_required:
                rec.gate_result = "failed"
            elif rec.phase in ("pilot", "active"):
                rec.gate_result = "passed"
            else:
                rec.gate_result = "open"

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "Country onboarding")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.country.onboarding") or "New"
                )
        records = super().create(vals_list)
        records._guarded().write({"initiated_on": fields.Date.context_today(records)})
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            require_platform_admin(self.env, "Country onboarding")
            if self.filtered(lambda r: r.phase in ("active", "abandoned")) and _changed(self, vals):
                raise UserError("A finished onboarding is a record: it is not edited.")
            if self.filtered(lambda r: r.phase != "discovery") and _changed(
                self, {k: v for k, v in vals.items() if k == "country_id"}
            ):
                raise UserError("The country is fixed once discovery is over.")
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda r: r.phase != "discovery") and not self.env.su:
            raise UserError("An onboarding past discovery is kept; abandon it instead.")
        return super().unlink()

    def _gate(self, target):
        """What stops this onboarding entering `target`, or ''."""
        self.ensure_one()
        code = self._country_code()
        if target == "pack_authoring" and not self.obligations_discovered:
            return (
                "Record the country's statutory obligations first: add them as jurisdiction "
                "rules whose jurisdiction starts with %s (e.g. %s-TAX)." % (code, code)
            )
        if target == "translation" and not self.pack_ids:
            return "Name the country packs being authored for %s." % code
        if target == "integration":
            if not self.locale_pack_id:
                return "Name the locale pack for %s." % code
            if self.locale_pack_id.state != "active":
                return (
                    "The locale pack %s is %s: it activates only at full translation "
                    "coverage (BRU-GLO-06)." % (self.locale_pack_id.code, self.locale_pack_id.state)
                )
        if target == "validation" and not self.gateway_ids:
            return "Select the payment gateways %s will use (FR-GLO-016)." % code
        if target == "pilot":
            if self.core_changes_required:
                return (
                    "Zero-core-change gate FAILED (BRU-GLO-02): standing %s up needs a core "
                    "code change. That is a design defect to escalate, not a step to skip." % code
                )
            unready = self.pack_ids.filtered(lambda p: p.state not in ("certified", "active"))
            if unready:
                return "Certify every pack before the pilot (BRU-GLO-05): %s." % ", ".join(
                    unready.mapped("code")
                )
            if not self.residency_assessed:
                return (
                    "Verify at least one data residency rule for %s before the pilot "
                    "(FR-GLO-015)." % code
                )
        if target == "active":
            inactive = self.pack_ids.filtered(lambda p: p.state != "active")
            if inactive:
                return "Activate every pack first: %s." % ", ".join(inactive.mapped("code"))
            if not self.gateway_ids.filtered(lambda g: g.state == "active"):
                return "At least one of the selected payment gateways must be active."
        return ""

    def action_advance(self):
        if not _is_platform_admin(self.env):
            raise AccessError(
                "Advancing an onboarding needs the 'Platform Admin' role, which %s does not "
                "hold." % self.env.user.name
            )
        for rec in self:
            target = NEXT_PHASE.get(rec.phase)
            if not target:
                raise UserError(
                    "%s is %s: there is no next step." % (rec.name, _label(rec, "phase"))
                )
            blocker = rec._gate(target)
            if blocker:
                raise UserError(blocker)
            vals = {"phase": target}
            if target == "pilot":
                vals["piloted_on"] = fields.Date.context_today(rec)
            if target == "active":
                if not rec.env.su and rec.env.user in (rec.create_uid, rec.lead_id):
                    raise UserError(
                        "A second person approves activation: you started or lead %s." % rec.name
                    )
                vals["activated_on"] = fields.Date.context_today(rec)
                vals["activated_by_id"] = rec.env.uid
            rec._guarded().write(vals)
            rec.message_post(body="%s by %s." % (_label(rec, "phase"), self.env.user.name))
            audit_event(
                rec.env,
                "country.onboarding_advanced",
                "fix.country.onboarding,%d" % rec.id,
                "%s %s -> %s" % (rec.name, rec._country_code(), target),
            )
        return True

    def action_abandon(self, reason=None):
        if not _is_platform_admin(self.env):
            raise AccessError(
                "Abandoning an onboarding needs the 'Platform Admin' role, which %s does not "
                "hold." % self.env.user.name
            )
        reason = _note(reason, "Abandoning an onboarding")
        for rec in self:
            if rec.phase in ("active", "abandoned"):
                raise UserError("%s is already %s." % (rec.name, _label(rec, "phase")))
            rec._guarded().write({"phase": "abandoned", "abandoned_reason": reason})
            rec.message_post(body="Abandoned by %s: %s" % (self.env.user.name, reason))
        return True


# ---------------------------------------------------------------------------
# Translation review (FR-GLO-022/024, BRU-GLO-07)
# ---------------------------------------------------------------------------
class FixTranslationEntry(models.Model):
    _name = "fix.translation.entry"
    _description = "Translation Review"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Key", compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    locale_pack_id = fields.Many2one(
        "fix.locale.pack", string="Locale", required=True, ondelete="restrict"
    )
    lang_code = fields.Char(related="locale_pack_id.code", string="Language Code")
    module_code = fields.Char(string="Module", help="e.g. M01, M65, P03 portal")
    target_model = fields.Char(
        string="Record Type",
        help="Technical model of the record whose text is translated, e.g. fix.zone. "
        "Leave empty for an interface string.",
    )
    target_id = fields.Integer(string="Record ID")
    target_field = fields.Char(string="Field", help="A translatable field, e.g. name")
    source_string = fields.Text(
        string="Source (English)",
        help="Filled from the record for a record field; typed for an interface string.",
    )
    translated_string = fields.Text(string="Translation", required=True)
    machine_translated = fields.Boolean(
        string="Machine Translated",
        help="Tick if any part came from machine translation. BRU-GLO-07: it cannot be "
        "approved for release.",
    )
    state = fields.Selection(
        [("submitted", "Submitted"), ("approved", "Approved"), ("rejected", "Rejected")],
        required=True,
        default="submitted",
        tracking=True,
    )
    translated_by_id = fields.Many2one(
        "res.users", string="Translated By", readonly=True, copy=False
    )
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True, copy=False)
    reviewed_on = fields.Datetime(string="Reviewed On", readonly=True, copy=False)
    review_note = fields.Char(string="Review Note", readonly=True, copy=False)
    applied = fields.Boolean(string="Written To The Record", readonly=True, copy=False)
    is_stale = fields.Boolean(
        string="Source Changed Since",
        compute="_compute_is_stale",
        help="The record's English text no longer matches the text this translation was made from.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "translated_by_id",
            "reviewed_by_id",
            "reviewed_on",
            "review_note",
            "applied",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "submitted":
            locked |= set(self._fields) - {"message_ids", "message_follower_ids"}
        if self and self.target_model:
            locked |= {"source_string"}
        return locked

    @api.depends("module_code", "target_model", "target_id", "target_field", "source_string")
    def _compute_name(self):
        for rec in self:
            if rec.target_model:
                rec.name = "%s,%s.%s" % (rec.target_model, rec.target_id, rec.target_field)
            else:
                rec.name = "%s: %s" % (rec.module_code or "UI", (rec.source_string or "")[:60])

    def _target(self):
        """The record and field this entry translates, checked; or (None, None)."""
        self.ensure_one()
        if not (self.target_model or self.target_id or self.target_field):
            return None, None
        if not (self.target_model and self.target_id and self.target_field):
            raise ValidationError(
                "A record translation names the record type, the record ID and the field together."
            )
        if self.target_model not in self.env:
            raise ValidationError("There is no record type %s." % self.target_model)
        Model = self.env[self.target_model]
        field = Model._fields.get(self.target_field)
        if not field or not getattr(field, "translate", False):
            raise ValidationError(
                "%s on %s is not a translatable field." % (self.target_field, self.target_model)
            )
        record = Model.browse(self.target_id).exists()
        if not record:
            raise ValidationError("%s %s does not exist." % (self.target_model, self.target_id))
        return record, field

    def _english(self, record):
        return record.with_context(lang="en_US")[self.target_field] or ""

    @api.depends("target_model", "target_id", "target_field", "source_string")
    def _compute_is_stale(self):
        for rec in self:
            stale = False
            if rec.target_model and rec.target_id and rec.target_field:
                try:
                    record, _field = rec._target()
                    stale = rec._english(record) != (rec.source_string or "")
                except (ValidationError, AccessError):
                    stale = False
            rec.is_stale = stale

    @api.model_create_multi
    def create(self, vals_list):
        _require_language_steward(self.env, "Submitting a translation")
        records = super().create(vals_list)
        for rec in records:
            if rec.locale_pack_id.state == "retired":
                raise UserError("%s is a retired locale." % rec.locale_pack_id.code)
            if rec.locale_pack_id.code == "en_US":
                raise UserError("English is the source language: translate into another locale.")
            record, _field = rec._target()
            stamps = {"translated_by_id": rec.env.uid}
            if record is not None:
                stamps["source_string"] = rec._english(record)
            elif not (rec.source_string or "").strip():
                raise ValidationError("An interface string needs its English source text.")
            rec._guarded().write(stamps)
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            _require_language_steward(self.env, "Changing a translation")
            if self.filtered(lambda r: r.state != "submitted") and _changed(self, vals):
                raise UserError(
                    "A reviewed translation is frozen. Submit a new translation instead."
                )
            if self.filtered("target_model") and "source_string" in _changed(self, vals):
                raise UserError("The source of a record translation is read from the record.")
        res = super().write(vals)
        if (
            self
            and not self._fix_guard_open()
            and {"target_model", "target_id", "target_field"} & set(vals)
        ):
            for rec in self:
                record, _field = rec._target()
                if record is not None:
                    rec._guarded().write({"source_string": rec._english(record)})
        return res

    def unlink(self):
        if self.filtered(lambda r: r.state != "submitted") and not self.env.su:
            raise UserError("A reviewed translation is kept as evidence.")
        return super().unlink()

    def action_approve(self, note=None):
        """Native-speaker review by a second person (BRU-GLO-07). Approving a
        record translation writes it into the record in the locale's language,
        as the reviewer: someone who may not edit the record cannot approve it."""
        _require_language_steward(self.env, "Approving a translation")
        note = _note(note, "Approving a translation")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            if not rec.env.su and rec.env.user == rec.translated_by_id:
                raise UserError(
                    "A second person reviews a translation: you submitted %s." % rec.name
                )
            if rec.machine_translated:
                raise UserError(
                    "Machine translation is not accepted for release (BRU-GLO-07). Have it "
                    "translated professionally and submit it again, then reject this one."
                )
            if rec.is_stale:
                raise UserError(
                    "The English text changed after this translation was made: reject it and "
                    "translate the new text."
                )
            record, _field = rec._target()
            applied = False
            if record is not None:
                lang = rec.locale_pack_id.code
                if not self.env["res.lang"].search_count(
                    [("code", "=", lang), ("active", "=", True)]
                ):
                    raise UserError(
                        "%s is not an installed language: activate its locale pack first." % lang
                    )
                record.with_context(lang=lang).write({rec.target_field: rec.translated_string})
                applied = True
            rec._guarded().write(
                {
                    "state": "approved",
                    "reviewed_by_id": rec.env.uid,
                    "reviewed_on": fields.Datetime.now(),
                    "review_note": note,
                    "applied": applied,
                }
            )
            rec.message_post(
                body="Approved by %s%s."
                % (self.env.user.name, " and written to the record" if applied else "")
            )
        return True

    def action_reject(self, note=None):
        _require_language_steward(self.env, "Rejecting a translation")
        note = _note(note, "Rejecting a translation")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            rec._guarded().write(
                {
                    "state": "rejected",
                    "reviewed_by_id": rec.env.uid,
                    "reviewed_on": fields.Datetime.now(),
                    "review_note": note,
                }
            )
        return True


# ---------------------------------------------------------------------------
# Bengali rendering verification (FR-GLO-025)
# ---------------------------------------------------------------------------
class FixRenderingVerification(models.Model):
    _name = "fix.rendering.verification"
    _description = "Rendering Verification"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "verified_on desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    locale_pack_id = fields.Many2one(
        "fix.locale.pack", string="Locale", required=True, ondelete="restrict"
    )
    target = fields.Selection(RENDER_TARGETS, string="Target", required=True)
    device = fields.Char(string="Device / Printer / Viewer", required=True)
    test_set_ref = fields.Char(
        string="Test Set",
        required=True,
        help="The sample checked: conjuncts, numerals, ৳ amounts, long names…",
    )
    verified_on = fields.Date(
        string="Verified On", required=True, default=fields.Date.context_today
    )
    result = fields.Selection([("pass", "Pass"), ("fail", "Fail")], string="Result", required=True)
    issues = fields.Text(string="Issues Found")
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Evidence (photo / print scan / PDF)", ondelete="restrict"
    )
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"verified_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= set(self._fields) - {"message_ids", "message_follower_ids"}
        return locked

    @api.depends("locale_pack_id", "target", "verified_on")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s · %s · %s" % (
                rec.locale_pack_id.code or "?",
                _label(rec, "target") if rec.target else "?",
                rec.verified_on or "",
            )

    @api.constrains("result", "issues", "verified_on")
    def _check_result(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.result == "fail" and not (rec.issues or "").strip():
                raise ValidationError("A failed verification names the issues found.")
            if rec.verified_on and rec.verified_on > today:
                raise ValidationError("A verification cannot be dated in the future.")

    @api.model_create_multi
    def create(self, vals_list):
        _require_language_steward(self.env, "Recording a rendering verification")
        records = super().create(vals_list)
        records._guarded().write({"verified_by_id": self.env.uid})
        for rec in records:
            if rec.evidence_attachment_id:
                rec.evidence_attachment_id.sudo().write({"res_model": rec._name, "res_id": rec.id})
        return records

    def write(self, vals):
        if self and not self._fix_guard_open() and _changed(self, vals):
            raise UserError(
                "A rendering verification is evidence and is not edited: record a new one."
            )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A rendering verification is evidence and is never deleted.")
        return super().unlink()

    @api.model
    def latest_by_target(self, locale_pack):
        """{target: record} - the latest verification per target for a locale."""
        out = {}
        for rec in self.search([("locale_pack_id", "=", locale_pack.id)]):
            out.setdefault(rec.target, rec)
        return out
