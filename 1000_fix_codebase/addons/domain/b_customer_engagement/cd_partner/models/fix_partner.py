# fix_partner — M40: partner, referral, franchise (P10-M04).
#
# A04 workflow audit (2026-11-03) M40-2/8/9/10: a partner was written straight
# to "onboarded" with no TIN, licence or documents; the document flags were
# Booleans the onboarder ticked; one user created and onboarded a partner
# alone, and a suspended partner was reinstated by the same call; the
# technical-audit score that gates rebates was typed by anyone and defaulted
# to a pass (85); the PII mask crashed for every ordinary user, which made
# the governed onboarding unusable; and a PDPA erasure could be typed as done,
# never persisted "blocked" and left the party's name, phone and address.
# Now the lifecycle, the KYC stamps, the audit score, the commission rate and
# the erasure state are guarded (fix.guarded.mixin) and move only through:
#   prospective --submit (channel officer)--> qualifying
#   --KYC verified (KYC officer, not the creator, not the uploader)-->
#   --onboard (channel manager, not the creator or the submitter)--> onboarded
#   --suspend (manager)--> suspended --reinstate (another manager)--> onboarded
# The audit score is the latest APPROVED fix.partner.audit (default 0).
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

GROUP_OFFICER = "cd_partner.group_fix_channel_officer"
GROUP_KYC = "cd_partner.group_fix_channel_kyc_officer"
GROUP_MANAGER = "cd_partner.group_fix_channel_manager"
GROUP_REBATE_APPROVER = "cd_partner.group_fix_rebate_approver"
GROUP_TIER3 = "cd_entity_config.group_dofa_tier_3"

# FLAW-40.1: the technical-audit pass mark that gates rebate payouts.
AUDIT_PASS_SCORE = 85.0
# A04 audit (2026-11-04): how long an approved technical audit stays current.
# A default the business must confirm (report §7.5).
AUDIT_VALIDITY_DAYS = 365

PARTNER_STATES = [
    ("prospective", "Prospective"),
    ("qualifying", "Qualifying (KYC under review)"),
    ("onboarded", "Onboarded"),
    ("suspended", "Suspended"),
]

PARTNER_GUARDED = frozenset(
    {
        "state",
        "technical_audit_score",
        "commission_rate",
        "has_trade_license_doc",
        "has_bank_solvency_doc",
        "kyc_verified",
        "kyc_verified_by_id",
        "kyc_verified_at",
        "submitted_by_id",
        "onboarded_by_id",
        "onboarded_at",
        "suspended_by_id",
        "suspension_reason",
        "pdpa_erasure_state",
        "pdpa_requested_on",
        "pdpa_requested_by_id",
        "pdpa_erased_on",
        "pdpa_blocked_reason",
    }
)


def fix_require(env, xmlids, what):
    """Refuse unless the acting user holds one of the roles. Superuser code
    (crons, seeds, the finance bridge) is trusted."""
    if env.su or any(env.user.has_group(x) for x in xmlids):
        return
    names = " or ".join(env.ref(x).name for x in xmlids)
    raise UserError("%s needs the %s role." % (what, names))


def fix_not_creator(env, record, what):
    """Segregation of duties: whoever raised a record does not approve it."""
    if not env.su and record.create_uid == env.user:
        raise UserError(
            "Segregation of duties: you raised %s, so %s must be done by someone else."
            % (record.display_name, what)
        )


class FixPartner(models.Model):
    """M40: a partner is a PARTY ROLE on M33."""

    _name = "fix.partner"
    _description = "Channel Partner"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    partner_id = fields.Many2one(
        "res.partner", string="Party (M33)", required=True, ondelete="restrict"
    )
    partner_type = fields.Selection(
        [
            ("referral", "Referral Partner"),
            ("reseller", "Reseller"),
            ("franchise", "Franchise"),
            ("alliance", "Strategic Alliance"),
        ],
        required=True,
        default="referral",
    )
    commission_rate = fields.Float(string="Commission Rate", default=0.05)
    territory = fields.Char(string="Territory")
    # Technical Quality & ESD Compliance Score (FLAW-40.1). A04 audit M40-2:
    # the score is the latest APPROVED technical audit, never typed; no audit
    # (or an expired one) scores 0, which fails the rebate gate.
    audit_ids = fields.One2many("fix.partner.audit", "partner_id", string="Technical Audits")
    technical_audit_score = fields.Float(
        string="Technical Audit Score (%)",
        compute="_compute_technical_audit",
        help="Technical quality, workshop ESD compliance, and tooling audit score "
        "(minimum 85% for rebate payouts): the latest approved technical audit "
        "still inside its validity.",
    )
    technical_audit_id = fields.Many2one(
        "fix.partner.audit", string="Current Technical Audit", compute="_compute_technical_audit"
    )
    contract_id = fields.Many2one("fix.contract", string="Agreement (M08)", ondelete="set null")
    state = fields.Selection(
        PARTNER_STATES,
        default="prospective",
        required=True,
        tracking=True,
    )

    # Statutory identification & KYC fields (FLAW-33.1)
    nid_number = fields.Char(
        string="NID Number",
        tracking=True,
        groups="cd_entity_config.group_pii_unmasked",
        help="Raw National ID. Restricted: ordinary operators see masked_nid. "
        "Every unmasked read is written to fix.pii.access.log (REQ-33.3).",
    )
    tin_number = fields.Char(string="e-TIN Number", tracking=True)
    trade_license_no = fields.Char(string="Trade License Number", tracking=True)
    trade_license_expiry = fields.Date(string="Trade License Expiry Date")
    bank_solvency_ref = fields.Char(string="Bank Solvency Ref")

    # Document evidence (FLAW-33.2). A04 audit M40-8: the flags were Booleans
    # the onboarder ticked; they now say whether the document is attached.
    trade_license_attachment_id = fields.Many2one(
        "ir.attachment", string="Trade Licence Document", copy=False, ondelete="restrict"
    )
    bank_solvency_attachment_id = fields.Many2one(
        "ir.attachment", string="Bank Solvency Certificate", copy=False, ondelete="restrict"
    )
    has_trade_license_doc = fields.Boolean(
        string="Trade License Attached", compute="_compute_doc_flags", store=True
    )
    has_bank_solvency_doc = fields.Boolean(
        string="Bank Solvency Attached", compute="_compute_doc_flags", store=True
    )
    kyc_verified = fields.Boolean(string="KYC Verified", readonly=True, copy=False, tracking=True)
    kyc_verified_by_id = fields.Many2one(
        "res.users", string="KYC Verified By", readonly=True, copy=False
    )
    kyc_verified_at = fields.Datetime(string="KYC Verified At", readonly=True, copy=False)
    submitted_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True, copy=False)
    onboarded_by_id = fields.Many2one("res.users", string="Onboarded By", readonly=True, copy=False)
    onboarded_at = fields.Datetime(readonly=True, copy=False)
    suspended_by_id = fields.Many2one("res.users", string="Suspended By", readonly=True, copy=False)
    suspension_reason = fields.Char(readonly=True, copy=False)

    # Role-based PII Masking fields (FLAW-33.3)
    masked_phone = fields.Char(string="Masked Phone", compute="_compute_masked_pii")
    masked_nid = fields.Char(string="Masked NID", compute="_compute_masked_pii")
    masked_address = fields.Char(string="Masked Address", compute="_compute_masked_pii")

    # ------------------------------------------------------------ guard
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | PARTNER_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state != "prospective":
            # what was verified is what was onboarded
            locked |= {
                "partner_id",
                "partner_type",
                "tin_number",
                "trade_license_no",
                "trade_license_attachment_id",
                "bank_solvency_attachment_id",
            }
        if rec and rec.pdpa_erasure_state == "erased":
            locked |= set(rec._fields) - {"id", "display_name"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                frozen = rec._fix_form_locked_fields() - rec._fix_guarded_fields()
                changed = [
                    n
                    for n in frozen & set(vals)
                    if n in rec._fields and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "%s cannot be changed on partner %s once it is %s (A04 audit M40-8)."
                        % (
                            ", ".join(sorted(rec._fields[n].string or n for n in changed)),
                            rec.name,
                            "erased" if rec.pdpa_erasure_state == "erased" else rec.state,
                        )
                    )
        return super().write(vals)

    # ------------------------------------------------------------ computes
    @api.depends("trade_license_attachment_id", "bank_solvency_attachment_id")
    def _compute_doc_flags(self):
        for rec in self:
            rec.has_trade_license_doc = bool(rec.trade_license_attachment_id)
            rec.has_bank_solvency_doc = bool(rec.bank_solvency_attachment_id)

    def _fix_current_audit(self):
        """The latest approved technical audit still inside its validity."""
        self.ensure_one()
        cutoff = fields.Date.context_today(self) - timedelta(days=AUDIT_VALIDITY_DAYS)
        audits = self.sudo().audit_ids.filtered(
            lambda a: a.state == "approved" and a.audit_date and a.audit_date >= cutoff
        )
        return audits.sorted(lambda a: (a.audit_date, a.id), reverse=True)[:1]

    @api.depends("audit_ids.state", "audit_ids.score", "audit_ids.audit_date")
    def _compute_technical_audit(self):
        for rec in self:
            audit = rec._fix_current_audit() if rec.id else rec.env["fix.partner.audit"]
            rec.technical_audit_id = audit
            rec.technical_audit_score = audit.score if audit else 0.0

    @api.depends("partner_id", "nid_number")
    def _compute_masked_pii(self):
        # A04 audit M40-9: the mask is computed from the raw values under
        # sudo. The masked value is what ordinary operators are meant to see;
        # reading the restricted nid_number as them raised AccessError and
        # broke onboarding for everyone without group_pii_unmasked.
        for rec in self:
            src = rec.sudo()
            # Phone masking: 01711-***890
            phone = (src.partner_id.phone or src.partner_id.mobile or "").strip()
            if phone and len(phone) >= 7:
                rec.masked_phone = phone[:5] + "***" + phone[-3:]
            elif phone:
                rec.masked_phone = "***"
            else:
                rec.masked_phone = ""

            # NID masking. The old rule was nid[:4] + stars + nid[-4:], which
            # on a 10-digit Smart NID revealed 8 of 10 digits (audit
            # 2026-10-31). A 17-digit legacy card can spare a 4-digit prefix;
            # a 10-digit Smart card cannot, so only the last 4 survive.
            nid = (src.nid_number or "").strip()
            if not nid:
                rec.masked_nid = ""
            elif len(nid) <= 8:
                rec.masked_nid = "*" * len(nid)
            elif len(nid) <= 12:
                rec.masked_nid = ("*" * (len(nid) - 4)) + nid[-4:]
            else:
                rec.masked_nid = nid[:4] + ("*" * (len(nid) - 8)) + nid[-4:]

            # Address masking: House ***, Road ***, City
            street = (src.partner_id.street or "").strip()
            city = (src.partner_id.city or "").strip()
            if street:
                rec.masked_address = "House ***, Road ***, " + (city or "Bangladesh")
            else:
                rec.masked_address = city or ""

    # ------------------------------------------------------------ KYC
    @api.constrains("trade_license_attachment_id", "bank_solvency_attachment_id")
    def _check_documents_are_this_partners(self):
        for rec in self:
            for att in rec.trade_license_attachment_id | rec.bank_solvency_attachment_id:
                att = att.sudo()
                if att.res_model != "fix.partner" or att.res_id != rec.id:
                    raise ValidationError(
                        "Document %s is not attached to partner %s." % (att.name, rec.name)
                    )

    def _fix_kyc_check(self):
        """FLAW-33.1/33.2: the statutory identifiers and, for a franchise, the
        two documents. Raises a ValidationError naming what is missing."""
        self.ensure_one()
        rec = self.sudo()
        if rec.partner_type in ("reseller", "franchise", "alliance"):
            if rec.tin_number:
                if not re.match(r"^\d{12}$", rec.tin_number.strip()):
                    raise ValidationError(
                        "e-TIN must be exactly 12 numeric digits (NBR statutory format)."
                    )
            else:
                raise ValidationError(
                    "A valid 12-digit e-TIN is mandatory to onboard a %s partner (FLAW-33.1)."
                    % rec.partner_type
                )
            if rec.nid_number:
                nid = rec.nid_number.strip()
                if not (re.match(r"^\d{10}$", nid) or re.match(r"^\d{17}$", nid)):
                    raise ValidationError(
                        "NID must be either a 10-digit Smart NID or a 17-digit National ID (FLAW-33.1)."
                    )
            if not rec.trade_license_no or not rec.trade_license_no.strip():
                raise ValidationError(
                    "Municipal Trade License number is required for partner onboarding (FLAW-33.1)."
                )
        if rec.partner_type == "franchise" and (
            not rec.trade_license_attachment_id or not rec.bank_solvency_attachment_id
        ):
            raise ValidationError(
                "Franchise onboarding requires the Trade License and the Bank Solvency "
                "Certificate attached as documents (FLAW-33.2)."
            )

    def _fix_needs_kyc_verification(self) -> bool:
        return self.partner_type == "franchise"

    def action_submit_onboarding(self):
        """The channel officer puts the application up for KYC review and
        onboarding, once the identifiers and documents are in."""
        fix_require(self.env, [GROUP_OFFICER], "Submitting a partner for onboarding")
        for rec in self:
            if rec.state != "prospective":
                raise UserError("Only a prospective partner can be submitted for onboarding.")
            rec._fix_kyc_check()
            rec._guarded().write({"state": "qualifying", "submitted_by_id": self.env.uid})
        return True

    def action_verify_kyc(self):
        """A KYC officer who neither created the partner nor uploaded its
        documents confirms the identifiers and documents are genuine."""
        fix_require(self.env, [GROUP_KYC], "Verifying partner KYC")
        for rec in self:
            if rec.state not in ("prospective", "qualifying"):
                raise UserError("KYC is verified before onboarding.")
            fix_not_creator(self.env, rec, "verifying its KYC")
            rec._fix_kyc_check()
            uploaders = (
                rec.sudo().trade_license_attachment_id | rec.sudo().bank_solvency_attachment_id
            ).mapped("create_uid")
            if not self.env.su and self.env.user in uploaders:
                raise UserError(
                    "Segregation of duties: you uploaded a KYC document of %s; another "
                    "KYC officer verifies it." % rec.name
                )
            rec._guarded().write(
                {
                    "kyc_verified": True,
                    "kyc_verified_by_id": self.env.uid,
                    "kyc_verified_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="KYC verified by %s." % self.env.user.name)
        return True

    def action_onboard(self):
        """Approve the partner: a channel manager who did not create or submit
        it, on valid statutory identifiers (and verified documents for a
        franchise). A suspended partner is reinstated, not re-onboarded."""
        for rec in self:
            # A03 audit W5 (M33-3): the draft-party switch (no-op under 'allow').
            if hasattr(rec.partner_id, "_fix_assert_party_usable_downstream"):
                rec.partner_id._fix_assert_party_usable_downstream("partner onboarding")
        fix_require(self.env, [GROUP_MANAGER], "Onboarding a partner")
        for rec in self:
            if rec.state == "onboarded":
                raise UserError("Partner %s is already onboarded." % rec.name)
            if rec.state == "suspended":
                raise UserError(
                    "Partner %s is suspended: a manager reinstates it (Reinstate), it is "
                    "not onboarded again (A04 audit M40-8)." % rec.name
                )
            fix_not_creator(self.env, rec, "onboarding it")
            if not self.env.su and rec.submitted_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you submitted %s for onboarding; another "
                    "channel manager approves it." % rec.name
                )
            rec._fix_kyc_check()
            if rec._fix_needs_kyc_verification() and not rec.kyc_verified:
                raise ValidationError(
                    "Franchise onboarding requires the Trade License and Bank Solvency "
                    "documents verified by a KYC officer first (FLAW-33.2)."
                )
            rec._guarded().write(
                {
                    "state": "onboarded",
                    "onboarded_by_id": self.env.uid,
                    "onboarded_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "partner.onboarded",
                "fix.partner",
                rec.id,
                {
                    "partner": rec.name,
                    "type": rec.partner_type,
                    "tin": rec.tin_number,
                    "trade_license": rec.trade_license_no,
                },
            )
        return True

    def action_return_to_prospect(self, reason=None):
        """The onboarding review sends an application back for more evidence."""
        fix_require(self.env, [GROUP_MANAGER, GROUP_KYC], "Returning a partner application")
        for rec in self:
            if rec.state != "qualifying":
                raise UserError("Only an application under review can be returned.")
            rec._guarded().write(
                {"state": "prospective", "kyc_verified": False, "submitted_by_id": False}
            )
            rec.message_post(body="Application returned: %s" % (reason or "no reason given"))
        return True

    def action_suspend(self, reason=None):
        fix_require(self.env, [GROUP_MANAGER], "Suspending a partner")
        reason = (str(reason).strip() if reason else "") or False
        if not reason:
            raise UserError("State why the partner is suspended.")
        for rec in self:
            if rec.state != "onboarded":
                raise UserError("Only an onboarded partner can be suspended.")
            rec._guarded().write(
                {
                    "state": "suspended",
                    "suspended_by_id": self.env.uid,
                    "suspension_reason": reason,
                }
            )
        return True

    def action_reinstate(self, reason=None):
        """A04 audit M40-8: reinstatement is a decision of its own, by a
        manager other than the one who suspended."""
        fix_require(self.env, [GROUP_MANAGER], "Reinstating a partner")
        for rec in self:
            if rec.state != "suspended":
                raise UserError("Only a suspended partner can be reinstated.")
            if not self.env.su and rec.suspended_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you suspended %s; another channel manager "
                    "reinstates it." % rec.name
                )
            rec._guarded().write(
                {"state": "onboarded", "suspended_by_id": False, "suspension_reason": False}
            )
            rec.message_post(body="Reinstated: %s" % (reason or "no reason given"))
        return True

    def action_set_commission_rate(self, rate=None):
        """A04 audit (report §7.5): the referral commission rate is the
        company's decision, set by a channel manager, between 0 and 100%."""
        fix_require(self.env, [GROUP_MANAGER], "Changing a partner's commission rate")
        try:
            value = float(rate)
        except (TypeError, ValueError):
            raise UserError("The commission rate must be a fraction, e.g. 0.05 for 5%.") from None
        if not 0 < value <= 1:
            raise UserError("The commission rate must be above 0 and at most 1 (100%).")
        for rec in self:
            old = rec.commission_rate
            rec._guarded().write({"commission_rate": value})
            rec.message_post(
                body="Commission rate %.4f -> %.4f by %s." % (old, value, self.env.user.name)
            )
        return True

    # --- REQ-33.6 PDPA right to erasure ----------------------------------
    # Erasure is not unconditional: the Income Tax Act and the Companies Act
    # oblige 1000 FiX to retain transaction records, so a request cannot be
    # executed while any linked service order is inside the 3-year statutory
    # audit window.
    _PDPA_RETENTION_DAYS = 1095

    pdpa_erasure_state = fields.Selection(
        [
            ("none", "No Request"),
            ("requested", "Erasure Requested"),
            ("blocked", "Blocked — Statutory Retention"),
            ("erased", "Anonymised"),
        ],
        string="PDPA Erasure Status",
        default="none",
        required=True,
        tracking=True,
    )
    pdpa_requested_on = fields.Date(string="Erasure Requested On", readonly=True, copy=False)
    pdpa_requested_by_id = fields.Many2one(
        "res.users", string="Erasure Requested By", readonly=True, copy=False
    )
    pdpa_erased_on = fields.Date(string="Anonymised On", readonly=True, copy=False)
    pdpa_blocked_reason = fields.Char(string="Retention Block", readonly=True, copy=False)

    def action_request_erasure(self):
        """Register a data-subject erasure request (PDPA)."""
        fix_require(self.env, [GROUP_OFFICER], "Registering a PDPA erasure request")
        for rec in self:
            if rec.pdpa_erasure_state == "erased":
                raise UserError("This party has already been anonymised.")
            rec._guarded().write(
                {
                    "pdpa_erasure_state": "requested",
                    "pdpa_requested_on": fields.Date.context_today(rec),
                    "pdpa_requested_by_id": self.env.uid,
                    "pdpa_blocked_reason": False,
                }
            )
            rec.message_post(body="PDPA erasure requested by the data subject.")
        return True

    def _erasure_blocker(self):
        """'' when erasure may proceed, else why it may not. The retention
        clock runs from the order's CLOSURE (closed_at), not its last edit."""
        self.ensure_one()
        if not self.partner_id:
            return ""
        orders = (
            self.env["fix.service.order"].sudo().search([("customer_id", "=", self.partner_id.id)])
        )
        cutoff = fields.Date.context_today(self) - timedelta(days=self._PDPA_RETENTION_DAYS)
        for order in orders:
            if order.state not in ("closed", "cancelled"):
                return "service order %s is still open" % order.name
            stamp = order.closed_at if "closed_at" in order._fields and order.closed_at else None
            closed_on = fields.Date.to_date(stamp or order.write_date)
            if closed_on and closed_on > cutoff:
                return (
                    "service order %s closed on %s, inside the %d-day statutory "
                    "retention window" % (order.name, closed_on, self._PDPA_RETENTION_DAYS)
                )
        return ""

    def _fix_anonymise(self):
        """REQ-33.6: remove the personal identifiers of the partner AND of its
        M33 party (name, phone, e-mail, address), and the KYC documents."""
        self.ensure_one()
        rec = self.sudo()
        label = "Erased party #%d" % rec.partner_id.id
        docs = rec.trade_license_attachment_id | rec.bank_solvency_attachment_id
        rec._guarded().write(
            {
                "name": "Erased partner #%d" % rec.id,
                "nid_number": False,
                "tin_number": False,
                "trade_license_no": False,
                "trade_license_expiry": False,
                "bank_solvency_ref": False,
                "territory": False,
                "trade_license_attachment_id": False,
                "bank_solvency_attachment_id": False,
            }
        )
        docs.unlink()
        party = rec.partner_id
        vals = {"name": label}
        for name in (
            "phone",
            "mobile",
            "email",
            "street",
            "street2",
            "city",
            "zip",
            "vat",
            "website",
            "comment",
        ):
            if name in party._fields:
                vals[name] = False
        party.write(vals)

    def action_execute_erasure(self):
        """REQ-33.6: anonymise personal identifiers once retention has lapsed.

        Tier 3 (Compliance / CX Director), not the person who registered the
        request. A04 audit M40-10: a retention block is recorded and kept
        (the call returns it instead of raising, which rolled it back); an
        erasure anonymises the party, and cannot be undone."""
        for rec in self:
            if rec.pdpa_erasure_state not in ("requested", "blocked"):
                raise UserError("Record a PDPA erasure request before anonymising this party.")
            # Tier 3 for everyone, the superuser included: erasure is a
            # compliance officer's act, never a background one.
            if not self.env.user.has_group(GROUP_TIER3):
                raise UserError(
                    "PDPA erasure requires DOFA Tier 3 (Compliance / CX Director) " "sign-off."
                )
            if not self.env.su and rec.pdpa_requested_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you registered this erasure request; another "
                    "Tier 3 officer executes it."
                )
        blocked = {}
        for rec in self:
            blocker = rec._erasure_blocker()
            # sudo: the Tier 3 check above is the authority gate; the restricted
            # identifiers are cleared by the privileged compliance act.
            if blocker:
                rec.sudo()._guarded().write(
                    {"pdpa_erasure_state": "blocked", "pdpa_blocked_reason": blocker[:250]}
                )
                rec.sudo().message_post(
                    body="Erasure blocked under the 3-year statutory audit limitation: %s "
                    "(REQ-33.6)." % blocker
                )
                blocked[rec.id] = blocker
                continue
            rec._fix_anonymise()
            rec.sudo()._guarded().write(
                {
                    "pdpa_erasure_state": "erased",
                    "pdpa_erased_on": fields.Date.context_today(rec),
                    "pdpa_blocked_reason": False,
                }
            )
            rec.sudo().message_post(body="Personal identifiers anonymised under PDPA erasure.")
        if blocked:
            return {
                "blocked": blocked,
                "message": "Erasure blocked under the 3-year statutory audit limitation: %s"
                % "; ".join(blocked.values()),
            }
        return True


class FixReferral(models.Model):
    """M40: referral with commission through M53's event engine."""

    _name = "fix.referral"
    _description = "Referral"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    partner_id = fields.Many2one(
        "fix.partner", string="Referring Partner", required=True, ondelete="cascade"
    )
    referred_partner_id = fields.Many2one(
        "res.partner", string="Referred Customer", ondelete="set null"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    base_amount = fields.Monetary(
        string="Referred Revenue (Gross)",
        currency_field="currency_id",
        tracking=True,
        help="The gross value of the converted business the commission is earned on",
    )
    commission_amount = fields.Monetary(
        string="Commission Earned", currency_field="currency_id", readonly=True
    )
    state = fields.Selection(
        [("submitted", "Submitted"), ("converted", "Converted"), ("commissioned", "Commissioned")],
        default="submitted",
        required=True,
        tracking=True,
    )

    # A04 audit C1 (M40-7): what a portal partner may say when submitting a
    # referral. The state, the referred revenue and the commission are the
    # company's to establish, because M53's accrual posts the GL entry from
    # them; a P12 partner set its own referral to commissioned on a BDT
    # 5,000,000 base.
    _PORTAL_REFERRAL_FIELDS = frozenset({"name", "partner_id", "referred_partner_id"})

    # A04 hand-off closure, ref_02 (2026-11-05): the model now really gates
    # duplicate and self-referrals server-side, as partner_api's AS-09 note
    # always claimed. BUSINESS DEFAULT to confirm (§7.5): a referred customer
    # may hold ONE open (submitted/converted) referral estate-wide — first in
    # wins, like a deal registration — and one partner earns on a customer at
    # most once (a second referral of the same customer by the same partner
    # is refused whatever the state of the first).
    def _referral_reject_dup_and_self(self, vals, skip_id=0):
        referred_id = vals.get("referred_partner_id") or 0
        partner_id = vals.get("partner_id") or 0
        if not referred_id or not partner_id:
            return
        own = self.env["fix.partner"].browse(partner_id)
        referred = self.env["res.partner"].browse(referred_id)
        if own.partner_id and own.partner_id.id == referred_id:
            raise UserError(
                "%s cannot refer themselves: a referral names a different customer."
                % (own.name or "A partner")
            )
        open_dup = self.sudo().search_count(
            [
                ("referred_partner_id", "=", referred_id),
                ("state", "in", ("submitted", "converted")),
                ("id", "!=", skip_id),
            ]
        )
        if open_dup:
            raise UserError(
                "%s already has an open referral — convert or close it before raising another."
                % (referred.name or "That customer")
            )
        own_dup = self.sudo().search_count(
            [
                ("partner_id", "=", partner_id),
                ("referred_partner_id", "=", referred_id),
                ("id", "!=", skip_id),
            ]
        )
        if own_dup:
            raise UserError(
                "%s has already referred %s: one commission per customer."
                % (own.name or "That partner", referred.name or "that customer")
            )

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.share and not self.env.su:
            for vals in vals_list:
                extra = set(vals) - self._PORTAL_REFERRAL_FIELDS
                if extra:
                    raise UserError(
                        "A partner submits who was referred; %s are set by the company."
                        % ", ".join(sorted(extra))
                    )
        for vals in vals_list:
            self._referral_reject_dup_and_self(vals)
        return super().create(vals_list)

    def write(self, vals):
        # re-pointing an existing referral's attribution runs the same gate
        if self and ("partner_id" in vals or "referred_partner_id" in vals):
            for rec in self:
                check = {
                    "partner_id": vals.get("partner_id", rec.partner_id.id),
                    "referred_partner_id": vals.get(
                        "referred_partner_id", rec.referred_partner_id.id
                    ),
                }
                self._referral_reject_dup_and_self(check, skip_id=rec.id)
        return super().write(vals)

    def _fix_require_internal(self, what):
        if self.env.user.share and not self.env.su:
            raise UserError("%s is the company's decision, not the partner's." % what)

    def action_convert(self, base_amount=None):
        self._fix_require_internal("Converting a referral")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted referral can be converted")
            if base_amount is not None:
                rec.base_amount = base_amount
            rec.state = "converted"
            publish(
                self.env,
                "referral.converted",
                "fix.referral",
                rec.id,
                {"partner": rec.partner_id.name},
            )

    def action_earn_commission(self):
        """Publishes commission.earned — M53's engine consumes it."""
        self._fix_require_internal("Earning a referral commission")
        for rec in self:
            if rec.state != "converted":
                raise UserError("Convert before commissioning")
            if rec.base_amount <= 0:
                raise UserError(
                    "Referral %s has no referred revenue: the commission base is required"
                    % rec.name
                )
            rate = rec.partner_id.commission_rate
            if not 0 < rate <= 1:
                raise UserError(
                    "Partner %s has no valid commission rate (%s)" % (rec.partner_id.name, rate)
                )
            # the partner's agreed rate on the real base - never a flat amount
            commission = rec.currency_id.round(rec.base_amount * rate)
            rec.write({"state": "commissioned", "commission_amount": commission})
            publish(
                self.env,
                "commission.earned",
                "fix.referral",
                rec.id,
                {
                    "partner_id": rec.partner_id.partner_id.id,
                    "gross": float(rec.base_amount),
                    "rate": rate,
                    "commission": float(commission),
                },
            )
