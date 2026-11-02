# res.partner extension — the party kernel's projection (P03-M05, M33).
# THE design rule: a SINGLE res.partner holds MULTIPLE roles simultaneously
# (fix.party.role) — customer, seller, vendor, rider are roles, never separate
# masters. This extension carries the kernel's Bengali-first fields, the
# language default the dispatcher and reports read, and the party status
# lifecycle (spec §8.1) with its hard exits.
from odoo import fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    name_bn = fields.Char(
        string="Name (Bengali)",
        help="DE-17/TR-07: authoritative in the bn locale; empty falls back to "
        "the Latin name — never machine-translated",
    )
    preferred_language = fields.Selection(
        [("bn", "বাংলা (Bengali)"), ("en", "English")],
        string="Preferred Language",
        default="bn",
        required=True,
        help="MD-013: the notification language — Bengali is the default (PS-03)",
    )
    # --- Party status lifecycle (spec §8.1) --------------------------------
    party_status = fields.Selection(
        [
            ("draft", "Draft (unverified)"),
            ("pending_approval", "Pending Approval"),
            ("active", "Active"),
            ("dormant", "Dormant"),
            ("blocked", "Blocked"),
            ("credit_hold", "Credit Hold"),
            ("blacklisted", "Blacklisted (terminal)"),
            ("merged", "Merged (tombstone)"),
        ],
        string="Party Status",
        default="draft",
        required=True,
        tracking=True,
        index=True,
        help="The party lifecycle. BLACKLISTED is terminal: reinstatement "
        "requires CEO authority (BRU-CPM-13) and is refused by the system.",
    )
    status_reason = fields.Char(string="Status Reason")
    status_since = fields.Date(string="Status Since", default=fields.Date.today)
    # --- kernel one-to-many surfaces ----------------------------------------
    role_ids = fields.One2many("fix.party.role", "partner_id", string="Party Roles")
    consent_ids = fields.One2many("fix.consent", "partner_id", string="Consent Records")
    identity_document_ids = fields.One2many(
        "fix.identity.document", "partner_id", string="Identity Documents"
    )
    approval_ids = fields.One2many(
        "fix.registration.approval", "partner_id", string="Registration Approvals"
    )
    quality_ids = fields.One2many("fix.party.quality", "partner_id", string="Quality Scores")
    segment_membership_ids = fields.One2many(
        "fix.segment.membership", "partner_id", string="Segment Memberships"
    )
    hierarchy_parent_ids = fields.One2many(
        "fix.party.hierarchy", "child_id", string="Related Parties (as child)"
    )
    hierarchy_child_ids = fields.One2many(
        "fix.party.hierarchy", "parent_id", string="Related Parties (as parent)"
    )
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        copy=False,
        help="MIG-03: permanent source system reference (FR-SRM-088)",
    )

    def write(self, vals):
        # BRU-CPM-13: blacklisted is terminal below CEO authority — the
        # system refuses the transition outright (the CEO path is a
        # governance action outside this model). fix.party.merge's reversal
        # passes skip_party_status_guard to restore its own tombstone.
        if "party_status" in vals and not self.env.context.get("skip_party_status_guard"):
            new_status = vals["party_status"]
            for partner in self:
                if partner.party_status == "blacklisted" and new_status != "blacklisted":
                    raise ValidationError(
                        "A blacklisted party cannot be reactivated below CEO "
                        "authority (BRU-CPM-13)"
                    )
                if partner.party_status == "merged" and new_status != "merged":
                    raise ValidationError(
                        "A merged tombstone is restored only by reversing its "
                        "merge (fix.party.merge.action_reverse)"
                    )
        return super().write(vals)

    def _get_notification_language(self) -> str:
        """The dispatcher's language lookup: preferred_language, defaulting bn."""
        self.ensure_one()
        return self.preferred_language or "bn"

    def get_masked_phone(self) -> str:
        """Return masked phone (e.g. 01711-***890) for non-privileged privacy displays (PDPA)."""
        self.ensure_one()
        # getattr: this line raised AttributeError on an Odoo build where
        # res.partner has no `mobile` field - a latent crash in the masked
        # PII getter, found while wiring S1 (A03 gap-closure build).
        phone = (self.phone or getattr(self, "mobile", False) or "").strip()
        if phone and len(phone) >= 7:
            return phone[:5] + "***" + phone[-3:]
        return phone

    def get_masked_nid(self) -> str:
        """Return masked NID for non-privileged privacy displays (PDPA)."""
        self.ensure_one()
        doc = self.identity_document_ids.filtered(lambda d: d.document_type in ("nid_10", "nid_17"))
        if doc and doc[:1].residency_ref:
            return "NID-***" + doc[:1].residency_ref[-4:]
        return ""
