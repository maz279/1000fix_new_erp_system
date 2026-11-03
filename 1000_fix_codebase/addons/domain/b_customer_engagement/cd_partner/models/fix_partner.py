# fix_partner — M40: partner, referral, franchise (P10-M04).
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish


class FixPartner(models.Model):
    """M40: a partner is a PARTY ROLE on M33."""

    _name = "fix.partner"
    _description = "Channel Partner"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
    # Technical Quality & ESD Compliance Score (FLAW-40.1)
    technical_audit_score = fields.Float(
        string="Technical Audit Score (%)",
        default=85.0,
        tracking=True,
        help="Technical quality, workshop ESD compliance, and tooling audit score (minimum 85% for rebate payouts)",
    )
    contract_id = fields.Many2one("fix.contract", string="Agreement (M08)", ondelete="set null")
    state = fields.Selection(
        [("prospective", "Prospective"), ("onboarded", "Onboarded"), ("suspended", "Suspended")],
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

    # Document attachment flags (FLAW-33.2)
    has_trade_license_doc = fields.Boolean(string="Trade License Attached", default=False)
    has_bank_solvency_doc = fields.Boolean(string="Bank Solvency Attached", default=False)

    # Role-based PII Masking fields (FLAW-33.3)
    masked_phone = fields.Char(string="Masked Phone", compute="_compute_masked_pii")
    masked_nid = fields.Char(string="Masked NID", compute="_compute_masked_pii")
    masked_address = fields.Char(string="Masked Address", compute="_compute_masked_pii")

    @api.depends("partner_id", "nid_number")
    def _compute_masked_pii(self):
        for rec in self:
            # Phone masking: 01711-***890
            phone = (rec.partner_id.phone or rec.partner_id.mobile or "").strip()
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
            nid = (rec.nid_number or "").strip()
            if not nid:
                rec.masked_nid = ""
            elif len(nid) <= 8:
                rec.masked_nid = "*" * len(nid)
            elif len(nid) <= 12:
                rec.masked_nid = ("*" * (len(nid) - 4)) + nid[-4:]
            else:
                rec.masked_nid = nid[:4] + ("*" * (len(nid) - 8)) + nid[-4:]

            # Address masking: House ***, Road ***, City
            street = (rec.partner_id.street or "").strip()
            city = (rec.partner_id.city or "").strip()
            if street:
                rec.masked_address = "House ***, Road ***, " + (city or "Bangladesh")
            else:
                rec.masked_address = city or ""

    def action_onboard(self):
        for rec in self:
            # FLAW-33.1: Validate statutory credentials for business partners
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

            # FLAW-33.2: Verify mandatory document attachments for franchise onboarding
            if rec.partner_type == "franchise" and (
                not rec.has_trade_license_doc or not rec.has_bank_solvency_doc
            ):
                raise ValidationError(
                    "Franchise onboarding requires verified Trade License and Bank Solvency Certificate in the Documents tab (FLAW-33.2)."
                )

            rec.state = "onboarded"
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
    pdpa_erased_on = fields.Date(string="Anonymised On", readonly=True, copy=False)

    def action_request_erasure(self):
        """Register a data-subject erasure request (PDPA)."""
        for rec in self:
            if rec.pdpa_erasure_state == "erased":
                raise UserError("This party has already been anonymised.")
            rec.write(
                {
                    "pdpa_erasure_state": "requested",
                    "pdpa_requested_on": fields.Date.today(),
                }
            )
            rec.message_post(body="PDPA erasure requested by the data subject.")

    def _erasure_blocker(self):
        """'' when erasure may proceed, else why it may not."""
        self.ensure_one()
        if not self.partner_id:
            return ""
        orders = (
            self.env["fix.service.order"].sudo().search([("customer_id", "=", self.partner_id.id)])
        )
        cutoff = fields.Date.today() - timedelta(days=self._PDPA_RETENTION_DAYS)
        for order in orders:
            if order.state not in ("closed", "cancelled"):
                return "service order %s is still open" % order.name
            closed_on = fields.Date.to_date(order.write_date)
            if closed_on and closed_on > cutoff:
                return (
                    "service order %s closed on %s, inside the %d-day statutory "
                    "retention window" % (order.name, closed_on, self._PDPA_RETENTION_DAYS)
                )
        return ""

    def action_execute_erasure(self):
        """REQ-33.6: anonymise personal identifiers once retention has lapsed."""
        for rec in self:
            if rec.pdpa_erasure_state != "requested":
                raise UserError("Record a PDPA erasure request before anonymising this party.")
            if not self.env.user.has_group("cd_entity_config.group_dofa_tier_3"):
                raise UserError(
                    "PDPA erasure requires DOFA Tier 3 (Compliance / CX Director) " "sign-off."
                )
            blocker = rec._erasure_blocker()
            if blocker:
                rec.pdpa_erasure_state = "blocked"
                raise ValidationError(
                    "Erasure blocked under the 3-year statutory audit limitation: %s "
                    "(REQ-33.6)." % blocker
                )
            # sudo: nid_number is group-restricted for READING, but erasure is
            # precisely the privileged compliance act that must clear it. The
            # Tier 3 check above is the authority gate.
            rec.sudo().write(
                {
                    "nid_number": False,
                    "tin_number": False,
                    "pdpa_erasure_state": "erased",
                    "pdpa_erased_on": fields.Date.today(),
                }
            )
            rec.message_post(body="Personal identifiers anonymised under PDPA erasure.")


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
    # them; a P12 partner set its own referral to commissioned on a
    # BDT 5,000,000 base.
    _PORTAL_REFERRAL_FIELDS = frozenset({"name", "partner_id", "referred_partner_id"})

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
        return super().create(vals_list)

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
