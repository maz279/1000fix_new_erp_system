# res.partner extension — the party kernel's projection (P03-M05, M33).
# THE design rule: a SINGLE res.partner holds MULTIPLE roles simultaneously
# (fix.party.role) — customer, seller, vendor, rider are roles, never separate
# masters. This extension carries the kernel's Bengali-first fields, the
# language default the dispatcher and reports read, and the party status
# lifecycle (spec §8.1) with its hard exits.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# States a party may be moved INTO by hand: they restrict what it can do.
# Moving a party to 'active' grants it the right to transact, so that goes
# through the registration approval or action_reactivate_party.
# 'pending_approval' is NOT here: only opening a registration approval sets
# it (A03 audit M33-3), so the status always has an approval behind it.
_RESTRICTIVE_STATUSES = {"dormant", "blocked", "credit_hold", "blacklisted"}

# Who may take the terminal step (blacklist) and who reactivates.
_STATUS_AUTHORITY_GROUP = "cd_entity_config.group_dofa_tier_2"

# BRU-CPM-02: these classes transact only after the two-step registration.
REGISTERED_CLASSES = ("dealer", "corporate", "government")

# A party in one of these is never usable downstream, whatever the policy.
_UNUSABLE_STATUSES = {
    "merged": "it was merged into another party; use the surviving record",
    "blacklisted": "it is blacklisted (BRU-CPM-13)",
    "blocked": "it is blocked",
    "pending_approval": "its registration approval is not complete (BRU-CPM-02)",
}

# ir.config_parameter: what a 'draft' (unverified) individual may do downstream.
# allow (default) | warn | refuse. A business ruling; it never relaxes the
# statuses above or an unregistered dealer / corporate / government party.
DRAFT_POLICY_PARAM = "cd_party_master.draft_party_policy"
DRAFT_POLICIES = ("allow", "warn", "refuse")


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "fix.guarded.mixin"]

    name_bn = fields.Char(
        string="Name (Bengali)",
        help="DE-17/TR-07: authoritative in the bn locale; empty falls back to "
        "the Latin name — never machine-translated",
    )
    preferred_language = fields.Selection(
        [("bn", "বাংলা (Bengali)"), ("en", "English")],
        string="Preferred Language",
        default="en",
        required=True,
        help="MD-013: the notification language — English is the business "
        "default (user directive 2026-11-08); Bengali is set per party when "
        "the customer chooses it",
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
    party_class = fields.Selection(
        [
            ("individual", "Individual / Retail"),
            ("dealer", "Dealer"),
            ("corporate", "Corporate"),
            ("government", "Government"),
        ],
        string="Party Class",
        default="individual",
        required=True,
        tracking=True,
        help="Dealer, corporate and government parties open a two-step registration "
        "approval automatically and transact only once it is complete (BRU-CPM-02).",
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

    @api.constrains("legacy_reference")
    def _check_legacy_reference_unique(self):
        """R-12 (2026-11-08 partner-ledger report): the legacy key is the
        idempotent migration/upsert key — it must be unique per value. The
        pre-uniqueness era left one tolerated exception: the constant tag
        'CORP-2023-23' stamped on 947 corporate parties by the first import
        (96% since re-stamped with unique keys); it stays exempt until that
        cleanup completes, and every other value — LEDGER-, CORP-2023-<slug>,
        anything — must belong to exactly one party."""
        for partner in self:
            ref = partner.legacy_reference
            if not ref or ref == "CORP-2023-23":
                continue
            clash = self.search([("legacy_reference", "=", ref), ("id", "!=", partner.id)], limit=1)
            if clash:
                raise UserError(
                    "Legacy reference '%s' already belongs to %s — the MIG-03 key is "
                    "unique per party (R-12, partner-ledger report 2026-11-08)."
                    % (ref, clash.display_name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        # The create path skipped the status rules: a party could be BORN
        # 'active' or 'pending_approval' with no decision behind it.
        if not self._fix_guard_has_token():
            for vals in vals_list:
                status = vals.get("party_status") or "draft"
                if status == "pending_approval":
                    self._fix_refuse_pending_approval()
                if status not in _RESTRICTIVE_STATUSES | {"draft"} and not self.env.su:
                    raise UserError(
                        "A new party starts as 'draft'. It becomes '%s' only through its "
                        "registration approval or 'Reactivate Party'." % status
                    )
        partners = super().create(vals_list)
        partners._fix_open_registration()
        return partners

    def _fix_refuse_pending_approval(self):
        raise UserError(
            "'Pending Approval' is set only by opening a registration approval. Set the "
            "party class to Dealer, Corporate or Government and the approval opens itself."
        )

    def write(self, vals):
        if self._fix_guard_has_token():
            # A transition (approval, merge, reversal) owns this write.
            return super().write(vals)
        if vals.get("party_status") == "pending_approval" and any(
            p.party_status != "pending_approval" for p in self
        ):
            # Binds the superuser too: the status must have an approval behind it.
            self._fix_refuse_pending_approval()
        class_changed = self.browse()
        if "party_class" in vals:
            class_changed = self.filtered(lambda p: p.party_class != vals["party_class"])
            for partner in class_changed:
                if partner._fix_open_registration_approval():
                    raise UserError(
                        "%s has a registration approval in progress. Have it decided "
                        "(approved or rejected) before changing the party class."
                        % partner.display_name
                    )
        result = self._fix_write_status_rules(vals)
        class_changed._fix_open_registration()
        return result

    def _fix_write_status_rules(self, vals):
        # BRU-CPM-13: blacklisted is terminal below CEO authority — the
        # system refuses the transition outright (the CEO path is a
        # governance action outside this model). fix.party.merge's reversal
        # restores its own tombstone through _guarded().
        # The hard exits below bind everyone, superuser included; only a
        # merge reversal (holding the transition token) restores a tombstone.
        # The activation rule binds people, not system code.
        if "party_status" in vals:
            new_status = vals["party_status"]
            for partner in self:
                if new_status == partner.party_status:
                    continue
                if new_status not in _RESTRICTIVE_STATUSES and not self.env.su:
                    # draft -> active and blocked -> active were plain writes
                    # (A03 audit). Activation is a decision with an owner.
                    raise UserError(
                        "A party becomes '%s' only through its registration approval "
                        "or 'Reactivate Party' (DOFA Tier 2 with a reason), not by "
                        "editing the status." % new_status
                    )
                if partner.party_status == "blacklisted" and new_status != "blacklisted":
                    raise ValidationError(
                        "A blacklisted party cannot be reactivated below CEO authority (BRU-CPM-13)"
                    )
                # M33 capture audit 2026-11-14: blacklisting is terminal
                # (nobody below the CEO can undo it), yet any clerk with
                # Contact write could do it with one edit. Restricting stays
                # a plain edit; the terminal step needs DOFA Tier 2.
                if (
                    new_status == "blacklisted"
                    and not self.env.su
                    and not self.env.user.has_group(_STATUS_AUTHORITY_GROUP)
                ):
                    raise UserError(
                        "Blacklisting is terminal (only the CEO can reinstate, BRU-CPM-13), "
                        "so it needs DOFA Tier 2 (Branch / Operations Manager) authority."
                    )
                if partner.party_status == "merged" and new_status != "merged":
                    raise ValidationError(
                        "A merged tombstone is restored only by reversing its "
                        "merge (fix.party.merge.action_reverse)"
                    )
        return super().write(vals)

    def action_set_party_status(self, status=None, reason=None):
        """Restrict a party: Dormant, Blocked, Credit Hold or Blacklisted,
        always with a written reason (FR-CPM-005: "with reasons, effective
        dates and controlled reactivation"). The workspace's "Change Party
        Status" form calls this; a plain status edit carried no reason.

        Activation is not here: that is the registration approval or
        action_reactivate_party."""
        if status not in _RESTRICTIVE_STATUSES:
            raise ValidationError(
                "Choose Dormant, Blocked, Credit Hold or Blacklisted. A party is made "
                "active only by its registration approval or 'Reactivate a Party'."
            )
        if not (reason or "").strip():
            raise ValidationError("Changing a party's status needs a written reason.")
        labels = dict(self._fields["party_status"].selection)
        for partner in self:
            if partner.party_status in ("merged", "blacklisted"):
                raise ValidationError(
                    "Party %s is %s; its status cannot be changed here."
                    % (partner.display_name, labels.get(partner.party_status))
                )
            if partner.party_status == status:
                raise ValidationError(
                    "Party %s is already %s." % (partner.display_name, labels.get(status))
                )
            prior = partner.party_status
            # the write applies the status rules (blacklisting needs Tier 2)
            partner.write(
                {
                    "party_status": status,
                    "status_reason": reason.strip(),
                    "status_since": fields.Date.context_today(partner),
                }
            )
            partner.message_post(
                body="Party status changed from '%s' to '%s' by %s. Reason: %s"
                % (labels.get(prior), labels.get(status), self.env.user.name, reason.strip())
            )
        return True

    def action_score_quality(self):
        """Score these parties now (FR-CPM-032).

        The quality register held a row only for parties the batch scorer had
        reached; a steward could not score the party in front of them."""
        Quality = self.env["fix.party.quality"]
        for partner in self:
            values = Quality._score_partner(partner)
            existing = Quality.search([("partner_id", "=", partner.id)], limit=1)
            if existing:
                existing.write(values)
            else:
                Quality.create(
                    {
                        "partner_id": partner.id,
                        "company_id": (partner.company_id or self.env.company).id,
                        **values,
                    }
                )
        return True

    def action_reactivate_party(self, reason=None):
        """Return a draft, dormant, blocked or credit-held party to 'active'.

        The governed alternative to editing party_status. Blacklisted and
        merged parties are refused by the hard exits above."""
        if not (reason or "").strip():
            raise ValidationError("Reactivating a party needs a written reason.")
        if not self.env.user.has_group("cd_entity_config.group_dofa_tier_2"):
            raise UserError(
                "Reactivating a party requires DOFA Tier 2 (Branch / Operations Manager) authority."
            )
        for partner in self:
            if partner.party_status in ("blacklisted", "merged", "active"):
                raise ValidationError(
                    "Party %s is %s and cannot be reactivated here."
                    % (partner.display_name, partner.party_status)
                )
            # A registration is decided by its two-step chain; reactivation
            # would otherwise be a one-person way round it (A03 audit M33-1).
            if partner.party_status == "pending_approval" or (
                partner.party_class in REGISTERED_CLASSES
                and partner.party_status == "draft"
                and not partner._fix_registration_approved()
            ):
                raise ValidationError(
                    "Party %s is a %s awaiting its registration approval. It is "
                    "activated by that approval, not by reactivation."
                    % (partner.display_name, partner.party_class)
                )
            prior = partner.party_status
            partner._guarded().write({"party_status": "active"})
            partner.message_post(
                body="Party reactivated from '%s' by %s. Reason: %s"
                % (prior, self.env.user.name, reason)
            )
        return True

    # --- registration approval (BRU-CPM-02, A03 audit M33-3) ----------------
    def _fix_open_registration_approval(self):
        """This party's registration approval still awaiting a decision."""
        self.ensure_one()
        return (
            self.env["fix.registration.approval"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", self.id),
                    ("lm_state", "!=", "rejected"),
                    ("admin_state", "=", "pending"),
                ],
                limit=1,
            )
        )

    def _fix_registration_approved(self) -> bool:
        """True when a completed approval covers this party's current class."""
        self.ensure_one()
        return bool(
            self.env["fix.registration.approval"]
            .sudo()
            .search_count(
                [
                    ("partner_id", "=", self.id),
                    ("party_class", "=", self.party_class),
                    ("lm_state", "=", "approved"),
                    ("admin_state", "=", "approved"),
                ]
            )
        )

    def _fix_open_registration(self):
        """Open the registration approval a dealer, corporate or government
        party needs. Nothing created these before; the 'two approvals before
        a dealer transacts' rule was a screen nobody had to use."""
        Approval = self.env["fix.registration.approval"].sudo()
        for partner in self:
            if partner.party_class not in REGISTERED_CLASSES:
                continue
            if partner.party_status in ("merged", "blacklisted"):
                continue
            if partner._fix_open_registration_approval() or partner._fix_registration_approved():
                continue
            # sudo() keeps the uid, so the approval's creator is the acting
            # user and the engine excludes them from deciding it.
            Approval.create(
                {
                    "partner_id": partner.id,
                    "party_class": partner.party_class,
                    "company_id": (partner.company_id or self.env.company).id,
                }
            )

    # --- downstream usability (A03 audit M33-3) -------------------------------
    @api.model
    def _fix_draft_party_policy(self) -> str:
        """allow | warn | refuse (see DRAFT_POLICY_PARAM). An unknown value
        fails closed to 'refuse' rather than silently allowing."""
        icp = self.env["ir.config_parameter"].sudo()
        value = (icp.get_param(DRAFT_POLICY_PARAM, "allow") or "allow").strip().lower()
        return value if value in DRAFT_POLICIES else "refuse"

    def _fix_assert_party_usable(self, purpose: str) -> str:
        """Refuse parties that may not be used for `purpose` (an order, an
        invoice, a role, a segment...). Returns a warning text, or "".

        Always refused: merged, blacklisted, blocked, pending approval, and a
        dealer / corporate / government party whose registration is not
        approved. A 'draft' individual follows the draft-party policy.
        Credit hold is not checked here: M20 enforces credit at order time."""
        warnings = []
        policy = None
        for partner in self:
            reason = _UNUSABLE_STATUSES.get(partner.party_status)
            if not reason and partner.party_status == "draft":
                if partner.party_class in REGISTERED_CLASSES:
                    reason = (
                        "it is a %s whose registration is not approved (BRU-CPM-02)"
                        % partner.party_class
                    )
                else:
                    policy = policy or self._fix_draft_party_policy()
                    if policy == "refuse":
                        reason = "it is still a draft (unverified) party"
                    elif policy == "warn":
                        text = "%s is a draft (unverified) party, used for %s." % (
                            partner.display_name,
                            purpose,
                        )
                        _logger.warning("draft party policy: %s", text)
                        warnings.append(text)
            if reason:
                raise UserError(
                    "%s cannot be used for %s: %s." % (partner.display_name, purpose, reason)
                )
        return " ".join(warnings)

    # --- party.merged consumers (R8) ------------------------------------------
    @api.model
    def _fix_merge_event_parties(self, event):
        """(survivor, victim) for a party.merged event, or None when the merge
        no longer stands (reversed before delivery). Every consumer checks
        this, so a late delivery never re-points onto a restored party.

        The pair is read from the executed fix.party.merge, not trusted from
        the payload (A03 audit W1): consumers are public methods, so a
        hand-made event could otherwise name any party as the survivor."""
        merge = self.env["fix.party.repoint.log"]._event_merge(event)
        if not merge:
            return None
        Partner = self.sudo().with_context(active_test=False)
        return Partner.browse(merge.survivor_id.id), Partner.browse(merge.victim_id.id)

    @api.model
    def consume_party_merged(self, event):
        """R8 consumer: the victim's child contacts move to the survivor.

        A company's contact people (res.partner.parent_id) stayed under the
        tombstone (A03 audit W1). The survivor itself is never made its own
        child. Logged, so a reversal moves them back. Idempotent: a second
        delivery finds no child left on the victim."""
        Log = self.env["fix.party.repoint.log"]
        merge = Log._event_merge(event)
        if not merge:
            return 0
        survivor, victim = merge.survivor_id, merge.victim_id
        children = (
            self.sudo()
            .with_context(active_test=False)
            .search([("parent_id", "=", victim.id), ("id", "!=", survivor.id)])
        )
        return len(Log.repoint(merge, children, "parent_id", victim, survivor))

    # --- the draft-party gate at downstream call sites (A03 audit W5) ---------
    def _fix_assert_party_usable_downstream(self, purpose: str) -> str:
        """The gate other modules call before using a party (an order, a won
        deal, an enrolment, an onboarding, an invoice).

        The policy (cd_party_master.draft_party_policy) rules on the DRAFT
        individual only: 'allow' lets it through. Merged, blocked, blacklisted
        and pending-approval parties and unregistered dealers are refused under
        every policy. 'allow' used to skip the whole gate, which left the
        registration approval a side register (2026-11-10 audit)."""
        return self._fix_assert_party_usable(purpose)

    def _get_notification_language(self) -> str:
        """The dispatcher's language lookup: preferred_language, defaulting
        en (user directive 2026-11-08 — English is the business default)."""
        self.ensure_one()
        return self.preferred_language or "en"

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
