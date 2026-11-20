# cd_vendor_ext — M42 Supplier Relationship & Performance: the supplier
# profile over the party, segmentation, the compliance document register and
# the controlled bank-detail change (CD-M42-01).
#
# Spec: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/
#       M42_Supplier_Relationship_and_Performance.md §5.1-§5.3, §10.1.
#
# Every model that backs a P03 workspace data-entry form declares
# `_p03_capture`: the P03 portal (platform layer) discovers capture forms
# through the registry and never imports this domain module (AR-007).
import hashlib
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

# FR-SRM2-002 — the twelve supplier classes (BR-SCM-001).
SUPPLIER_CLASSES = [
    ("oem", "OEM"),
    ("authorised_distributor", "Authorised Distributor"),
    ("local_distributor", "Local Distributor"),
    ("local_trader", "Local Trader"),
    ("importer", "Importer"),
    ("service_provider", "Service Provider"),
    ("courier_partner", "Courier Partner"),
    ("recycling_partner", "Recycling Partner"),
    ("freight_forwarder", "Freight Forwarder"),
    ("cnf_agent", "C&F Agent"),
    ("cargo_insurer", "Cargo Insurer"),
    ("brand_partner", "Brand Partner"),
]

# FR-SRM2-003 — segments, reviewed on a defined cycle.
SEGMENTS = [
    ("strategic", "Strategic"),
    ("preferred", "Preferred"),
    ("approved", "Approved"),
    ("transactional", "Transactional"),
    ("restricted", "Restricted"),
]

# FR-SRM2-004 — the risk tier drives qualification depth and review cadence.
RISK_TIERS = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("critical", "Critical"),
]

INCOTERMS = [
    ("exw", "EXW"), ("fca", "FCA"), ("fob", "FOB"), ("cfr", "CFR"),
    ("cif", "CIF"), ("cpt", "CPT"), ("cip", "CIP"), ("dap", "DAP"),
    ("ddp", "DDP"),
]

# FR-SRM2-016 — the compliance document register.
DOC_TYPES = [
    ("trade_licence", "Trade Licence"),
    ("vat_bin", "VAT / BIN Registration"),
    ("tin", "TIN Certificate"),
    ("bank_verification", "Bank Account Verification"),
    ("iso_cert", "ISO / Other Certification"),
    ("brand_authorisation", "Brand Authorisation"),
    ("insurance", "Insurance"),
]

# Documents expiring inside this window count as "expiring" (KPI
# "Docs Expiring (60d)") and trigger the FR-SRM2-017 warning.
EXPIRY_WARNING_DAYS = 60


def check_sod(record, actor_field, approver, message):
    """SoD helper (§13): the user named in `actor_field` may not approve."""
    actor = record[actor_field]
    if actor and approver and actor.id == approver.id:
        raise UserError(message)


class FixSupplierProfile(models.Model):
    """FR-SRM2-001/002/005/006: the supplier role over an M33 party."""

    _name = "fix.supplier.profile"
    _description = "Supplier Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"
    _p03_capture = {
        "module": "M42",
        "form": "Supplier Profile",
        "fields": ["partner_id", "classification", "segment", "risk_tier",
                   "category_ids", "capabilities", "capacity_note",
                   "geography", "currency_id", "incoterm",
                   "payment_terms_days", "owner_user_id"],
    }
    _partner_company_unique = models.Constraint(
        "UNIQUE (partner_id, company_id)",
        "A party has one supplier profile per legal entity (T-12)")

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    partner_id = fields.Many2one("res.partner", string="Supplier Party",
                                 required=True, index=True, ondelete="restrict",
                                 tracking=True)
    name = fields.Char(related="partner_id.name", store=True, string="Supplier")
    classification = fields.Selection(SUPPLIER_CLASSES, string="Classification",
                                      required=True, tracking=True)
    segment = fields.Selection(SEGMENTS, string="Segment", required=True,
                               default="approved", tracking=True)
    risk_tier = fields.Selection(RISK_TIERS, string="Risk Tier", required=True,
                                 default="medium", tracking=True)
    category_ids = fields.Many2many("product.category", string="Supplied Categories",
                                    help="Spend categories this supplier is qualified "
                                         "to supply (FR-SRM2-005)")
    capabilities = fields.Text(string="Capabilities")
    capacity_note = fields.Text(string="Capacity")
    geography = fields.Char(string="Geography")
    currency_id = fields.Many2one("res.currency", string="Trading Currency",
                                  default=lambda self: self.env.company.currency_id)
    incoterm = fields.Selection(INCOTERMS, string="Default Incoterm")
    payment_terms_days = fields.Integer(string="Payment Terms (days)", default=30)
    owner_user_id = fields.Many2one("res.users", string="Relationship Owner",
                                    default=lambda self: self.env.user)
    state = fields.Selection(
        [("prospect", "Prospect"), ("under_qualification", "Under Qualification"),
         ("active", "Active"), ("suspended", "Suspended"), ("blocked", "Blocked")],
        string="Status", default="prospect", required=True, tracking=True)
    status_reason = fields.Text(string="Status Reason", tracking=True)
    document_ids = fields.One2many("fix.supplier.document", "profile_id",
                                   string="Documents")
    agreement_ids = fields.One2many("fix.supplier.agreement", "profile_id",
                                    string="Agreements")
    document_expiring_count = fields.Integer(
        string="Documents Expiring", compute="_compute_document_expiring_count")
    next_segment_review = fields.Date(string="Next Segment Review", tracking=True)

    @api.depends("document_ids.expires_on", "document_ids.state")
    def _compute_document_expiring_count(self):
        horizon = fields.Date.today() + timedelta(days=EXPIRY_WARNING_DAYS)
        for profile in self:
            profile.document_expiring_count = len(profile.document_ids.filtered(
                lambda d: d.state == "verified" and d.expires_on
                and d.expires_on <= horizon))

    @api.constrains("payment_terms_days")
    def _check_payment_terms(self):
        for profile in self:
            if profile.payment_terms_days < 0:
                raise ValidationError("Payment terms cannot be negative")

    def _publish_state(self, event_type):
        for profile in self:
            publish(self.env, event_type, "fix.supplier.profile", profile.id, {
                "partner_id": profile.partner_id.id,
                "company_id": profile.company_id.id,
                "state": profile.state,
                "segment": profile.segment,
                "risk_tier": profile.risk_tier,
            })

    def action_start_qualification(self):
        self.filtered(lambda p: p.state == "prospect").write(
            {"state": "under_qualification"})

    def action_activate(self):
        """Activation follows an approved qualification (cd_supplier_
        qualification calls this); a blocked supplier is never re-activated
        here — un-blocking is a CFO decision outside this flow."""
        for profile in self:
            if profile.state == "blocked":
                raise UserError("A permanently blocked supplier cannot be activated")
        self.write({"state": "active", "status_reason": False})
        self._publish_state("supplier.activated")

    def _require_reason(self, reason):
        if not (reason or "").strip():
            raise UserError("A recorded reason is required (FR-SRM2-014)")

    def action_suspend(self, reason=None):
        """FR-SRM2-014: immediately prevents new orders; open orders stay
        visible in M16."""
        self._require_reason(reason)
        self.write({"state": "suspended", "status_reason": reason})
        self._publish_state("supplier.deactivated")

    def action_block(self, reason=None):
        self._require_reason(reason)
        self.write({"state": "blocked", "status_reason": reason})
        self._publish_state("supplier.deactivated")


class FixSupplierSegmentReview(models.Model):
    """FR-SRM2-003/004: a governed change of segment and risk tier. The
    profile only moves when the review is approved by someone other than
    the proposer."""

    _name = "fix.supplier.segment.review"
    _description = "Supplier Segment & Risk-Tier Review"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"
    _p03_capture = {
        "module": "M42",
        "form": "Segment & Risk-Tier Review",
        "fields": ["profile_id", "proposed_segment", "proposed_risk_tier",
                   "annual_spend", "criticality", "rationale", "next_review_due"],
    }

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    profile_id = fields.Many2one("fix.supplier.profile", string="Supplier",
                                 required=True, index=True, ondelete="cascade")
    current_segment = fields.Selection(SEGMENTS, string="Current Segment",
                                       readonly=True)
    current_risk_tier = fields.Selection(RISK_TIERS, string="Current Risk Tier",
                                         readonly=True)
    proposed_segment = fields.Selection(SEGMENTS, string="Proposed Segment",
                                        required=True)
    proposed_risk_tier = fields.Selection(RISK_TIERS, string="Proposed Risk Tier",
                                          required=True)
    currency_id = fields.Many2one("res.currency", string="Currency",
                                  default=lambda self: self.env.company.currency_id)
    annual_spend = fields.Monetary(string="Annual Spend", currency_field="currency_id")
    criticality = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"),
         ("critical", "Critical")], string="Supply Criticality", required=True,
        default="medium")
    rationale = fields.Text(string="Rationale", required=True)
    next_review_due = fields.Date(string="Next Review Due")
    decided_by = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(string="Decided At", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"),
         ("rejected", "Rejected")],
        string="Status", default="draft", required=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        Profile = self.env["fix.supplier.profile"]
        for vals in vals_list:
            profile = Profile.browse(vals.get("profile_id"))
            if profile.exists():
                vals.setdefault("current_segment", profile.segment)
                vals.setdefault("current_risk_tier", profile.risk_tier)
        return super().create(vals_list)

    def action_submit(self):
        self.filtered(lambda r: r.state == "draft").write({"state": "submitted"})

    def action_approve(self):
        for review in self:
            if review.state != "submitted":
                raise UserError("Only a submitted review can be approved")
            check_sod(review, "create_uid", self.env.user,
                      "The proposer of a segment change cannot approve it")
            review.profile_id.write({
                "segment": review.proposed_segment,
                "risk_tier": review.proposed_risk_tier,
                "next_segment_review": review.next_review_due,
            })
            review.write({"state": "approved", "decided_by": self.env.user.id,
                          "decided_at": fields.Datetime.now()})
            publish(self.env, "supplier.segment_changed", "fix.supplier.profile",
                    review.profile_id.id, {
                        "segment": review.proposed_segment,
                        "risk_tier": review.proposed_risk_tier,
                    })

    def action_reject(self):
        for review in self:
            if review.state != "submitted":
                raise UserError("Only a submitted review can be rejected")
        self.write({"state": "rejected", "decided_by": self.env.user.id,
                    "decided_at": fields.Datetime.now()})


class FixSupplierDocument(models.Model):
    """FR-SRM2-015/016/017: the compliance document register with expiry
    monitoring. Evidence is hashed at capture (T-11)."""

    _name = "fix.supplier.document"
    _description = "Supplier Compliance Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expires_on, id"
    _p03_capture = {
        "module": "M42",
        "form": "Supplier Document",
        "fields": ["profile_id", "doc_type", "reference", "issued_on",
                   "expires_on", "issuer", "notes"],
    }

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    profile_id = fields.Many2one("fix.supplier.profile", string="Supplier",
                                 required=True, index=True, ondelete="cascade")
    doc_type = fields.Selection(DOC_TYPES, string="Document Type", required=True)
    reference = fields.Char(string="Document Number", required=True)
    issuer = fields.Char(string="Issued By")
    issued_on = fields.Date(string="Issued On")
    expires_on = fields.Date(string="Expires On", index=True)
    notes = fields.Text(string="Notes")
    attachment_id = fields.Many2one("ir.attachment", string="Evidence File",
                                    ondelete="restrict")
    evidence_hash = fields.Char(string="Evidence SHA-256", readonly=True, copy=False)
    verified_by = fields.Many2one("res.users", string="Verified By", readonly=True)
    verified_at = fields.Datetime(string="Verified At", readonly=True)
    state = fields.Selection(
        [("draft", "Pending Verification"), ("verified", "Verified"),
         ("expired", "Expired"), ("rejected", "Rejected")],
        string="Status", default="draft", required=True, tracking=True)

    @api.constrains("issued_on", "expires_on", "doc_type")
    def _check_dates(self):
        for doc in self:
            if doc.issued_on and doc.expires_on and doc.expires_on < doc.issued_on:
                raise ValidationError("A document cannot expire before it is issued")
            if doc.doc_type == "brand_authorisation" and not doc.expires_on:
                # FR-SRM2-015: authorisation evidence carries an expiry date.
                raise ValidationError("Brand authorisation evidence needs an expiry date")

    @staticmethod
    def _hash_bytes(raw):
        return hashlib.sha256(raw or b"").hexdigest()

    @api.model_create_multi
    def create(self, vals_list):
        docs = super().create(vals_list)
        for doc in docs.filtered("attachment_id"):
            doc.evidence_hash = self._hash_bytes(doc.attachment_id.raw)
        return docs

    def action_verify(self):
        for doc in self:
            if doc.state != "draft":
                raise UserError("Only a pending document can be verified")
            check_sod(doc, "create_uid", self.env.user,
                      "The user who captured a document cannot verify it")
            if doc.expires_on and doc.expires_on < fields.Date.today():
                raise UserError("An already-expired document cannot be verified")
        self.write({"state": "verified", "verified_by": self.env.user.id,
                    "verified_at": fields.Datetime.now()})

    def action_reject(self):
        self.filtered(lambda d: d.state == "draft").write({"state": "rejected"})

    @api.model
    def _cron_expire_documents(self):
        """T-07: daily, idempotent — a verified document past its expiry
        moves to expired exactly once; the supplier owner is warned ahead of
        expiry by an activity (FR-SRM2-017)."""
        today = fields.Date.today()
        lapsed = self.search([("state", "=", "verified"), ("expires_on", "<", today)])
        for doc in lapsed:
            doc.state = "expired"
            publish(self.env, "supplier.document_expired", "fix.supplier.document",
                    doc.id, {"profile_id": doc.profile_id.id, "doc_type": doc.doc_type,
                             "expires_on": str(doc.expires_on)})
        horizon = today + timedelta(days=EXPIRY_WARNING_DAYS)
        expiring = self.search([("state", "=", "verified"),
                                ("expires_on", ">=", today),
                                ("expires_on", "<=", horizon)])
        for doc in expiring:
            owner = doc.profile_id.owner_user_id
            if owner and not doc.activity_ids:
                doc.activity_schedule(
                    "mail.mail_activity_data_todo", date_deadline=doc.expires_on,
                    summary="Supplier document expiring", user_id=owner.id)
        return len(lapsed)


class FixSupplierBankChange(models.Model):
    """FR-SRM2-018 / T-06: a bank-detail change needs documented
    verification and a second person's approval. The prior value is kept as
    a hash; the change and its approver are immutable once decided."""

    _name = "fix.supplier.bank.change"
    _description = "Supplier Bank Detail Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"
    _p03_capture = {
        "module": "M42",
        "form": "Bank Detail Change Request",
        "fields": ["profile_id", "bank_name", "branch_name", "routing_number",
                   "account_holder", "account_number", "verification_method",
                   "verification_note"],
    }

    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 index=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Operating Unit", index=True,
        default=lambda self: self.env.user._get_default_operating_unit())
    profile_id = fields.Many2one("fix.supplier.profile", string="Supplier",
                                 required=True, index=True, ondelete="restrict")
    bank_name = fields.Char(string="Bank", required=True)
    branch_name = fields.Char(string="Bank Branch")
    routing_number = fields.Char(string="Routing Number")
    account_holder = fields.Char(string="Account Holder", required=True)
    account_number = fields.Char(string="New Account Number", required=True)
    verification_method = fields.Selection(
        [("callback", "Call-back to Registered Contact"),
         ("bank_letter", "Bank Confirmation Letter"),
         ("cancelled_cheque", "Cancelled Cheque"),
         ("in_person", "In-Person Verification")],
        string="Verification Method", required=True)
    verification_note = fields.Text(string="Verification Evidence", required=True)
    previous_value_hash = fields.Char(string="Previous Value Hash", readonly=True,
                                      copy=False)
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(string="Approved At", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Awaiting Approval"),
         ("approved", "Approved"), ("rejected", "Rejected")],
        string="Status", default="draft", required=True, tracking=True)

    _DECIDED_LOCKED = {"bank_name", "branch_name", "routing_number",
                       "account_holder", "account_number", "verification_method",
                       "verification_note", "profile_id", "previous_value_hash"}

    @api.model_create_multi
    def create(self, vals_list):
        Profile = self.env["fix.supplier.profile"]
        for vals in vals_list:
            profile = Profile.browse(vals.get("profile_id"))
            if profile.exists():
                current = profile.partner_id.bank_ids[:1]
                vals["previous_value_hash"] = hashlib.sha256(
                    (current.acc_number or "").encode()).hexdigest()
        return super().create(vals_list)

    def write(self, vals):
        if self._DECIDED_LOCKED & set(vals) and any(
                r.state in ("approved", "rejected") for r in self):
            raise UserError("A decided bank-detail change is immutable (T-06)")
        return super().write(vals)

    def action_submit(self):
        self.filtered(lambda r: r.state == "draft").write({"state": "submitted"})

    def action_approve(self):
        for change in self:
            if change.state != "submitted":
                raise UserError("Only a submitted change can be approved")
            check_sod(change, "create_uid", self.env.user,
                      "The requester of a bank-detail change cannot approve it")
            if not self.env.user.has_group("base.group_partner_manager"):
                # The approver writes the party's bank account: Odoo's own
                # permission on res.partner.bank decides who may — no sudo.
                raise UserError("Approving a bank-detail change needs the right to "
                                "manage party bank accounts (Contact Creation)")
            partner = change.profile_id.partner_id
            self.env["res.partner.bank"].create({
                "partner_id": partner.id,
                "acc_number": change.account_number,
                "acc_holder_name": change.account_holder,
            })
            change.write({"state": "approved", "approved_by": self.env.user.id,
                          "approved_at": fields.Datetime.now()})
            # T-06: a security event for M29.
            publish(self.env, "supplier.bank_changed", "fix.supplier.bank.change",
                    change.id, {"profile_id": change.profile_id.id,
                                "requested_by": change.create_uid.id,
                                "approved_by": self.env.user.id,
                                "previous_value_hash": change.previous_value_hash})

    def action_reject(self):
        for change in self:
            if change.state != "submitted":
                raise UserError("Only a submitted change can be rejected")
        self.write({"state": "rejected", "approved_by": self.env.user.id,
                    "approved_at": fields.Datetime.now()})
