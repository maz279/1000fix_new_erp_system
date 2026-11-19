# M33 capture audit, pass 2 (2026-11-19). Each record here is one the M33
# spec names (section 10.1) that no screen, and no model, could capture:
#
#   fix.contact.point        FR-CPM-022, BRU-CPM-01, KPI-125: a phone or an
#                            email is a contact point with its own
#                            verification. Verification was an OTP log line
#                            tied to nothing.
#   fix.party.relationship   FR-CPM-006: employer, guardian, referrer, group
#                            member and authorised representative. The
#                            hierarchy holds households and corporate groups
#                            only.
#   fix.party.contact.role   FR-CPM-009/011: who at a corporate account may
#                            request, approve, pay or administer, inside a
#                            contact limit 1000FiX sets.
#   res.partner.consent_handling
#                            FR-CPM-052, BRU-CPM-16 (hard block): a minor or
#                            a party who needs assisted consent consents only
#                            through a verified guardian or representative.
#
# Imported last: it extends res.partner, fix.otp.log and fix.consent.
import re

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_party_security import DPO_GROUP, STEWARD_GROUP, require_group

# ir.config_parameter: BRU-CPM-01 ("a party cannot be activated without at
# least one verified contact point"). Off by default: on 19 Nov 2026 fix_real
# held no verified contact point at all, so switching it on stops every
# activation until contacts are verified. That is the owner's call.
REQUIRE_VERIFIED_CONTACT_PARAM = "cd_party_master.require_verified_contact"

# FR-CPM-022 verifies the mobile number and the email by one-time code.
_OTP_CHANNEL = {"mobile": "mobile", "email": "email"}

_BD_MOBILE = re.compile(r"^01[3-9]\d{8}$")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Relationships a minor's or an assisted party's consent may be given through.
_ASSISTING_RELATIONS = ("guardian", "authorised_rep")

# Corporate contact roles (FR-CPM-009).
CONTACT_ROLES = [
    ("authorised_requester", "Authorised Requester"),
    ("approver", "Approver"),
    ("billing", "Billing Contact"),
    ("technical", "Technical Contact"),
    ("administrator", "Corporate Administrator"),
]

# Who may set the delegated contact limit on a corporate (FR-CPM-011: "within
# limits set by 1000FiX"): the 1000FiX registration administrator.
_LIMIT_AUTHORITY_GROUP = "cd_party_master.group_party_registration_admin"


def _normalise_mobile(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if digits.startswith("880"):
        digits = digits[2:]
    return digits


def _mask(contact_type: str, value: str) -> str:
    value = value or ""
    if contact_type == "email" and "@" in value:
        local, _, domain = value.partition("@")
        return "%s***@%s" % (local[:1], domain)
    return value[:2] + "***" + value[-4:] if len(value) > 6 else "***"


class FixContactPoint(models.Model):
    """A phone number, email or messaging handle of a party, and whether and
    how it was verified (spec 10.1 fix.contact.point)."""

    _name = "fix.contact.point"
    _description = "Party Contact Point"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "partner_id, contact_type, is_primary desc, id"
    _rec_name = "value"

    def _fix_guarded_fields(self) -> set:
        # Verification is stamped by the verified OTP, never typed.
        return super()._fix_guarded_fields() | {
            "state",
            "verified_at",
            "verification_method",
            "otp_log_id",
        }

    partner_id = fields.Many2one(
        "res.partner", string="Party", required=True, index=True, ondelete="cascade"
    )
    contact_type = fields.Selection(
        [
            ("mobile", "Mobile"),
            ("email", "Email"),
            ("whatsapp", "WhatsApp"),
            ("landline", "Landline"),
        ],
        string="Type",
        required=True,
        default="mobile",
    )
    value = fields.Char(string="Number / Address", required=True, tracking=True)
    is_primary = fields.Boolean(string="Primary for this Type", default=False)
    state = fields.Selection(
        [
            ("unverified", "Unverified"),
            ("pending", "Code Sent"),
            ("verified", "Verified"),
        ],
        string="Verification",
        default="unverified",
        required=True,
        tracking=True,
    )
    verified_at = fields.Datetime(string="Verified At", readonly=True)
    verification_method = fields.Selection(
        [("otp", "One-Time Code")], string="Verified By", readonly=True
    )
    otp_log_id = fields.Many2one(
        "fix.otp.log", string="Verifying Code", readonly=True, ondelete="set null"
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.model
    def _normalise_vals(self, vals, contact_type):
        if vals.get("value"):
            raw = vals["value"].strip()
            if contact_type in ("mobile", "whatsapp"):
                raw = _normalise_mobile(raw)
            elif contact_type == "email":
                raw = raw.lower()
            vals["value"] = raw
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._normalise_vals(vals, vals.get("contact_type") or "mobile")
        return super().create(vals_list)

    def write(self, vals):
        if {"value", "contact_type"} & set(vals):
            for point in self:
                ctype = vals.get("contact_type") or point.contact_type
                one = point._normalise_vals(dict(vals), ctype)
                moved = one.get("value", point.value) != point.value or ctype != point.contact_type
                if moved and point.state != "unverified":
                    # FR-CPM-022: a changed contact is verified again
                    one.update(
                        state="unverified",
                        verified_at=False,
                        verification_method=False,
                        otp_log_id=False,
                    )
                    super(FixContactPoint, point._guarded()).write(one)
                    point.message_post(body="Contact changed: it must be verified again.")
                else:
                    super(FixContactPoint, point).write(one)
            return True
        return super().write(vals)

    @api.constrains("contact_type", "value")
    def _check_format(self):
        for point in self:
            if point.contact_type in ("mobile", "whatsapp") and not _BD_MOBILE.match(
                point.value or ""
            ):
                raise ValidationError(
                    "%s is not a Bangladesh mobile number (11 digits starting 013-019)."
                    % point.value
                )
            if point.contact_type == "email" and not _EMAIL.match(point.value or ""):
                raise ValidationError("%s is not an email address." % point.value)

    @api.constrains("partner_id", "contact_type", "value", "is_primary")
    def _check_unique(self):
        for point in self:
            same = self.search_count(
                [
                    ("id", "!=", point.id),
                    ("partner_id", "=", point.partner_id.id),
                    ("contact_type", "=", point.contact_type),
                    ("value", "=", point.value),
                ]
            )
            if same:
                raise ValidationError(
                    "%s already holds this %s." % (point.partner_id.display_name, point.value)
                )
            if point.is_primary and self.search_count(
                [
                    ("id", "!=", point.id),
                    ("partner_id", "=", point.partner_id.id),
                    ("contact_type", "=", point.contact_type),
                    ("is_primary", "=", True),
                ]
            ):
                raise ValidationError(
                    "%s already has a primary %s. Clear that one first."
                    % (point.partner_id.display_name, point.contact_type)
                )

    def action_request_verification(self):
        """Ask for a one-time code: the OTP log line is opened here, the code
        itself is issued and checked by the channel (M27 / portal), which
        marks the log verified (fix.otp.log.action_mark_verified)."""
        Log = self.env["fix.otp.log"]
        for point in self:
            channel = _OTP_CHANNEL.get(point.contact_type)
            if not channel:
                raise UserError(
                    "Only a mobile number or an email is verified by one-time code " "(FR-CPM-022)."
                )
            if point.state == "verified":
                raise UserError("%s is already verified." % point.value)
            log = Log.create(
                {
                    "partner_id": point.partner_id.id,
                    "channel": channel,
                    "destination_masked": _mask(point.contact_type, point.value),
                    "contact_point_id": point.id,
                    "company_id": point.company_id.id,
                }
            )
            point._guarded().write({"state": "pending", "otp_log_id": log.id})
        return True

    def _fix_mark_verified(self, log):
        for point in self:
            point._guarded().write(
                {
                    "state": "verified",
                    "verified_at": log.verified_at or fields.Datetime.now(),
                    "verification_method": "otp",
                    "otp_log_id": log.id,
                }
            )


class FixOtpLog(models.Model):
    _inherit = "fix.otp.log"

    contact_point_id = fields.Many2one(
        "fix.contact.point", string="Contact Point", index=True, ondelete="set null"
    )

    def action_mark_verified(self, channel_ref=None):
        result = super().action_mark_verified(channel_ref=channel_ref)
        for log in self.filtered("contact_point_id"):
            log.contact_point_id.sudo()._fix_mark_verified(log)
        return result


class FixPartyRelationship(models.Model):
    """A named, dated link between two parties (FR-CPM-006): who employs,
    guards, referred, groups or represents whom."""

    _name = "fix.party.relationship"
    _description = "Party Relationship"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "date_from desc, id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"verified", "verified_by", "verified_at"}

    party_a_id = fields.Many2one(
        "res.partner", string="Party A", required=True, index=True, ondelete="cascade"
    )
    relation_type = fields.Selection(
        [
            ("employer", "is the employer of"),
            ("guardian", "is the guardian of"),
            ("referrer", "referred"),
            ("group_member", "has as a group member"),
            ("authorised_rep", "is the authorised representative of"),
        ],
        string="Relation",
        required=True,
    )
    party_b_id = fields.Many2one(
        "res.partner", string="Party B", required=True, index=True, ondelete="cascade"
    )
    date_from = fields.Date(string="Since", required=True, default=fields.Date.context_today)
    date_to = fields.Date(string="Ended", readonly=True)
    evidence = fields.Char(
        string="Evidence",
        help="What shows the relationship: a guardianship document, a power of "
        "attorney, an employment letter. The steward reads it before verifying.",
    )
    verified = fields.Boolean(string="Verified", readonly=True, tracking=True)
    verified_by = fields.Many2one("res.users", string="Verified By", readonly=True)
    verified_at = fields.Datetime(string="Verified At", readonly=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.constrains("party_a_id", "party_b_id", "relation_type", "date_to")
    def _check_pair(self):
        for rel in self:
            if rel.party_a_id == rel.party_b_id:
                raise ValidationError("A party cannot be related to itself.")
            if not rel.date_to and self.search_count(
                [
                    ("id", "!=", rel.id),
                    ("party_a_id", "=", rel.party_a_id.id),
                    ("party_b_id", "=", rel.party_b_id.id),
                    ("relation_type", "=", rel.relation_type),
                    ("date_to", "=", False),
                ]
            ):
                raise ValidationError("This relationship is already recorded and open.")

    def write(self, vals):
        moving = {"party_a_id", "party_b_id", "relation_type"} & set(vals)
        if moving and not self._fix_guard_open() and any(r.verified for r in self):
            raise UserError(
                "A verified relationship cannot be re-pointed. End it and record a new one."
            )
        return super().write(vals)

    def action_verify(self):
        """A data steward who did not record it verifies it (four eyes)."""
        require_group(self.env, STEWARD_GROUP, "Verifying a party relationship")
        for rel in self:
            if rel.verified:
                raise UserError("This relationship is already verified.")
            if rel.date_to:
                raise UserError("An ended relationship is not verified.")
            if not (rel.evidence or "").strip():
                raise UserError("Record the evidence before the relationship is verified.")
            if not self.env.su and rel.create_uid == self.env.user:
                raise UserError("You recorded this relationship; another data steward verifies it.")
            rel._guarded().write(
                {
                    "verified": True,
                    "verified_by": self.env.user.id,
                    "verified_at": fields.Datetime.now(),
                }
            )
        return True

    def action_end(self, reason=None):
        """Close the relationship; it is kept, never deleted."""
        if not (reason or "").strip():
            raise ValidationError("Ending a relationship needs a reason.")
        for rel in self:
            if rel.date_to:
                raise UserError("This relationship has already ended.")
            rel._guarded().write({"date_to": fields.Date.context_today(rel)})
            rel.message_post(body="Ended by %s: %s" % (self.env.user.name, reason.strip()))
        return True


class FixPartyContactRole(models.Model):
    """A person's role at a corporate, dealer or government account
    (FR-CPM-009), suspended or removed with a reason (FR-CPM-011)."""

    _name = "fix.party.contact.role"
    _description = "Corporate Contact Role"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "corporate_id, role, id"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "date_to", "status_note"}

    corporate_id = fields.Many2one(
        "res.partner", string="Corporate Account", required=True, index=True, ondelete="cascade"
    )
    contact_id = fields.Many2one(
        "res.partner", string="Contact Person", required=True, index=True, ondelete="cascade"
    )
    role = fields.Selection(CONTACT_ROLES, string="Role", required=True)
    approval_limit = fields.Monetary(
        string="Approval Limit (BDT)",
        currency_field="currency_id",
        help="Approvers only: the most this person may approve for the account. Empty = no limit.",
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.ref("base.BDT"), required=True
    )
    state = fields.Selection(
        [("active", "Active"), ("suspended", "Suspended"), ("removed", "Removed")],
        string="State",
        default="active",
        required=True,
        tracking=True,
    )
    date_from = fields.Date(string="From", required=True, default=fields.Date.context_today)
    date_to = fields.Date(string="Removed On", readonly=True)
    status_note = fields.Char(string="Last Status Reason", readonly=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.constrains("corporate_id", "contact_id", "role", "state")
    def _check_role(self):
        for rec in self:
            corp = rec.corporate_id
            if not (corp.is_company or corp.party_class in ("dealer", "corporate", "government")):
                raise ValidationError(
                    "%s is not a corporate, dealer or government account." % corp.display_name
                )
            if rec.contact_id == corp or rec.contact_id.is_company:
                raise ValidationError("The contact is a person, not the account itself.")
            if rec.state != "removed" and self.search_count(
                [
                    ("id", "!=", rec.id),
                    ("corporate_id", "=", corp.id),
                    ("contact_id", "=", rec.contact_id.id),
                    ("role", "=", rec.role),
                    ("state", "!=", "removed"),
                ]
            ):
                raise ValidationError(
                    "%s already holds this role at %s."
                    % (rec.contact_id.display_name, corp.display_name)
                )
            if rec.approval_limit and rec.role != "approver":
                raise ValidationError("Only an approver carries an approval limit.")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.mapped("corporate_id")._fix_check_contact_limit()
        return records

    def write(self, vals):
        if not self._fix_guard_open() and {"corporate_id", "contact_id", "role"} & set(vals):
            raise UserError("A contact role is not re-pointed. Remove it and grant the new one.")
        return super().write(vals)

    def _set_state(self, state, reason, allowed_from):
        if not (reason or "").strip():
            raise ValidationError("A reason is required.")
        for rec in self:
            if rec.state not in allowed_from:
                raise UserError("This role is %s." % rec.state)
            vals = {"state": state, "status_note": reason.strip()}
            if state == "removed":
                vals["date_to"] = fields.Date.context_today(rec)
            rec._guarded().write(vals)
            rec.message_post(
                body="%s by %s: %s" % (state.capitalize(), self.env.user.name, reason.strip())
            )

    def action_suspend(self, reason=None):
        self._set_state("suspended", reason, ("active",))
        return True

    def action_reinstate(self, reason=None):
        self._set_state("active", reason, ("suspended",))
        self.mapped("corporate_id")._fix_check_contact_limit()
        return True

    def action_remove(self, reason=None):
        self._set_state("removed", reason, ("active", "suspended"))
        return True


class ResPartner(models.Model):
    _inherit = "res.partner"

    # --- FR-CPM-052 / BRU-CPM-16 ----------------------------------------------
    consent_handling = fields.Selection(
        [
            ("standard", "Standard"),
            ("minor", "Minor (under 18)"),
            ("assisted", "Needs Assisted Consent"),
        ],
        string="Consent Handling",
        default="standard",
        required=True,
        tracking=True,
        help="A minor or a party needing assistance consents only through a verified "
        "guardian or authorised representative (BRU-CPM-16).",
    )
    consent_handling_reason = fields.Char(string="Consent Handling Reason", tracking=True)
    # --- FR-CPM-011 -------------------------------------------------------------
    delegated_contact_limit = fields.Integer(
        string="Contact Limit",
        default=0,
        tracking=True,
        help="Most people who may hold an active role at this account. 0 = no limit. "
        "Set by a 1000FiX registration administrator (FR-CPM-011).",
    )
    contact_point_ids = fields.One2many("fix.contact.point", "partner_id", string="Contact Points")
    contact_role_ids = fields.One2many(
        "fix.party.contact.role", "corporate_id", string="Corporate Contact Roles"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"consent_handling", "consent_handling_reason"}

    def write(self, vals):
        if (
            "delegated_contact_limit" in vals
            and not self.env.su
            and any(p.delegated_contact_limit != vals["delegated_contact_limit"] for p in self)
            and not self.env.user.has_group(_LIMIT_AUTHORITY_GROUP)
        ):
            raise UserError(
                "The contact limit is set by a 1000FiX registration administrator (FR-CPM-011)."
            )
        result = super().write(vals)
        if "delegated_contact_limit" in vals:
            self._fix_check_contact_limit()
        return result

    def _fix_check_contact_limit(self):
        Role = self.env["fix.party.contact.role"].sudo()
        for corp in self:
            limit = corp.delegated_contact_limit
            if not limit:
                continue
            people = Role.search([("corporate_id", "=", corp.id), ("state", "=", "active")]).mapped(
                "contact_id"
            )
            if len(people) > limit:
                raise UserError(
                    "%s may have at most %d active contacts (set by 1000FiX); it would have %d."
                    % (corp.display_name, limit, len(people))
                )

    def action_set_consent_handling(self, handling=None, reason=None):
        """Flag a minor or a party who needs assisted consent; anyone serving
        the party may do so. Clearing the flag is the Data Protection
        Officer's decision."""
        labels = dict(self._fields["consent_handling"].selection)
        if handling not in labels:
            raise ValidationError("Choose Standard, Minor or Needs Assisted Consent.")
        if not (reason or "").strip():
            raise ValidationError("Say why: the handling decides who may consent.")
        for partner in self:
            if partner.consent_handling == handling:
                raise ValidationError(
                    "%s is already %s." % (partner.display_name, labels[handling])
                )
            if handling == "standard":
                require_group(self.env, DPO_GROUP, "Clearing heightened consent handling")
            partner._guarded().write(
                {"consent_handling": handling, "consent_handling_reason": reason.strip()}
            )
            partner.message_post(
                body="Consent handling set to %s by %s: %s"
                % (labels[handling], self.env.user.name, reason.strip())
            )
        return True

    # --- BRU-CPM-01 -------------------------------------------------------------
    def _fix_has_verified_contact(self) -> bool:
        self.ensure_one()
        if (
            self.env["fix.contact.point"]
            .sudo()
            .search_count([("partner_id", "=", self.id), ("state", "=", "verified")])
        ):
            return True
        return bool(
            self.env["fix.otp.log"]
            .sudo()
            .search_count([("partner_id", "=", self.id), ("state", "=", "verified")])
        )

    def _fix_assert_verified_contact(self):
        icp = self.env["ir.config_parameter"].sudo()
        if (icp.get_param(REQUIRE_VERIFIED_CONTACT_PARAM, "0") or "0").strip() not in (
            "1",
            "true",
            "True",
        ):
            return
        for partner in self:
            if not partner._fix_has_verified_contact():
                raise UserError(
                    "%s has no verified contact point; a party is activated only once "
                    "one is verified (BRU-CPM-01)." % partner.display_name
                )

    def action_reactivate_party(self, reason=None):
        self.filtered(lambda p: p.party_status == "draft")._fix_assert_verified_contact()
        return super().action_reactivate_party(reason=reason)


class FixConsent(models.Model):
    _inherit = "fix.consent"

    assisted_by_id = fields.Many2one(
        "res.partner",
        string="Consent Given By (guardian / representative)",
        ondelete="restrict",
        help="For a minor or an assisted party: the verified guardian or authorised "
        "representative who gave the consent (BRU-CPM-16).",
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        return locked | {"assisted_by_id"} if self else locked

    def write(self, vals):
        if (
            "assisted_by_id" in vals
            and not self._fix_guard_open()
            and any(
                c._fix_guard_differs("assisted_by_id", vals["assisted_by_id"], c.assisted_by_id)
                for c in self
            )
        ):
            raise UserError(
                "A consent record cannot be edited once captured (assisted by). Record "
                "a new consent, or withdraw this one."
            )
        return super().write(vals)

    @api.constrains("state", "partner_id", "assisted_by_id")
    def _check_assisted_consent(self):
        Rel = self.env["fix.party.relationship"].sudo()
        for consent in self:
            if consent.state != "granted":
                continue
            party = consent.partner_id
            if party.consent_handling == "standard":
                continue
            helper = consent.assisted_by_id
            if not helper:
                raise ValidationError(
                    "%s needs assisted consent (%s): record who gave it on the "
                    "party's behalf (BRU-CPM-16)." % (party.display_name, party.consent_handling)
                )
            if not Rel.search_count(
                [
                    ("party_a_id", "=", helper.id),
                    ("party_b_id", "=", party.id),
                    ("relation_type", "in", _ASSISTING_RELATIONS),
                    ("verified", "=", True),
                    ("date_to", "=", False),
                ]
            ):
                raise ValidationError(
                    "%s is not a verified guardian or authorised representative of %s. "
                    "Record the relationship and have a data steward verify it first."
                    % (helper.display_name, party.display_name)
                )

    def action_withdraw(self):
        # the withdrawal row copies the grant; carry who consented with it
        result = super().action_withdraw()
        for consent in self.filtered("assisted_by_id"):
            withdrawal = consent.superseded_by_id
            if withdrawal and not withdrawal.assisted_by_id:
                withdrawal._guarded().write({"assisted_by_id": consent.assisted_by_id.id})
        return result
