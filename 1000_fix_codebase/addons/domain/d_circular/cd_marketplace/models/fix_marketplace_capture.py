# M12 capture audit, second pass (19 Nov 2026).
#
# The first pass (13 Nov) gave each of the eleven M12 sub-module pages a
# "+ New" button. Four of them still captured nothing of their own:
#
#   * Ratings offered page 5's customer sign-off, which stores one 1-5 number.
#     The spec's review (FR-MKP-049/050: several ratings, written text,
#     moderation and one seller response) had no store.
#       -> fix.seller.review
#   * Trust & Safety offered page 7's Seller Consequence. A counterfeit-part
#     report, fraud or off-platform dealing (FR-MKP-064..066) had nowhere to
#     go, and BRU-MKP-11 (the listing is suspended at once) had no trigger.
#       -> fix.trust.signal
#   * Execution Oversight's "Job Completion" was a bare click: no photo, QC
#     checklist or parts declaration was captured, although BRU-MKP-02 (hard
#     block) says a job cannot complete without them (FR-MKP-040/042).
#       -> fix.marketplace.job.evidence, and action_complete requires it
#   * Job Broadcast could not record the customer's consent to an external
#     seller (FR-MKP-037, BRU-MKP-07, hard block before broadcast).
#       -> consent fields on the order; no seller quote is taken without it
#
# The seller form also gains the seller type (FR-MKP-001), whose identity
# documents KYC verification now checks.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_marketplace import OPERATOR_GROUP, _assert_role, _seller_users

SELLER_TYPES = [
    ("individual", "Individual Freelance Engineer"),
    ("business", "Shop / Business"),
]
CONSENT_METHODS = [
    ("signed", "Signed consent form"),
    ("otp", "OTP confirmation"),
    ("call", "Recorded call"),
    ("app", "In-app acceptance"),
]
EVIDENCE_TYPES = [
    ("before_photo", "Before Photograph"),
    ("after_photo", "After Photograph"),
    ("diagnostic", "Diagnostic Record"),
    ("qc_checklist", "QC Checklist"),
    ("parts_declaration", "Parts Used Declaration"),
]
PROVENANCE = [
    ("none", "No parts used"),
    ("genuine", "Genuine / OEM"),
    ("equivalent", "OEM-equivalent (compatible)"),
    ("refurbished", "Refurbished"),
    ("used", "Used / salvaged"),
]
# BRU-MKP-02: the evidence an owned job needs before it is closed. The system
# parameter `cd_marketplace.completion_evidence` may name another set.
DEFAULT_COMPLETION_EVIDENCE = "before_photo,after_photo,qc_checklist,parts_declaration"

SIGNAL_TYPES = [
    ("counterfeit_part", "Counterfeit / non-genuine part"),
    ("off_platform", "Off-platform dealing (disintermediation)"),
    ("collusion", "Collusion between sellers"),
    ("fake_job", "Fake job"),
    ("payment_fraud", "Payment fraud"),
    ("review_manipulation", "Review manipulation"),
    ("other", "Other trust concern"),
]
SIGNAL_SOURCES = [
    ("customer", "Customer report"),
    ("seller", "Seller report"),
    ("operator", "Operations observation"),
    ("audit", "Field audit (M23)"),
    ("system", "System pattern"),
]
SIGNAL_STATES = [
    ("open", "Reported"),
    ("investigating", "Under Investigation"),
    ("substantiated", "Substantiated"),
    ("dismissed", "Dismissed"),
]
# A substantiated finding of these kinds suspends the seller (BRU-MKP-11; the
# seller lifecycle s.8.1: "counterfeit-part finding" -> Suspended).
SUSPENDING_SIGNALS = {
    "counterfeit_part": "counterfeit",
    "payment_fraud": "fraud",
    "collusion": "fraud",
    "fake_job": "fraud",
}
REVIEW_STATES = [
    ("submitted", "Awaiting Moderation"),
    ("published", "Published"),
    ("rejected", "Rejected"),
]
# A review is of a verified job: the customer signed it off.
REVIEWABLE_ORDER_STATES = ("reviewed", "commissioned", "paid")


def _stars(value, label, required=False):
    if value in (None, False, 0) and not required:
        return
    if not isinstance(value, int) or not 1 <= value <= 5:
        raise ValidationError("%s is a whole number from 1 to 5." % label)


# ---------------------------------------------------------------------------
# Seller type (FR-MKP-001/003)
# ---------------------------------------------------------------------------
class FixMarketplaceSellerCapture(models.Model):
    _inherit = "fix.marketplace.seller"

    seller_type = fields.Selection(
        SELLER_TYPES,
        string="Seller Type",
        required=True,
        default="business",
        tracking=True,
        help="An individual is verified on the NID; a shop or business on its "
        "trade licence and e-TIN (FR-MKP-001/003).",
    )
    trust_signal_ids = fields.One2many(
        "fix.trust.signal", "seller_id", string="Trust & Safety Reports", readonly=True
    )

    def _fix_missing_identity(self):
        self.ensure_one()
        if self.seller_type == "individual":
            needed = [("nid_number", "National ID")]
        else:
            needed = [("trade_license_no", "trade licence"), ("tin_number", "e-TIN")]
        return [label for name, label in needed if not (self[name] or "").strip()]

    def action_verify_kyc(self):
        for rec in self:
            missing = rec._fix_missing_identity()
            if missing:
                raise UserError(
                    "%s is a %s: KYC cannot be verified without the %s (FR-MKP-003)."
                    % (
                        rec.name,
                        dict(SELLER_TYPES)[rec.seller_type].lower(),
                        " and ".join(missing),
                    )
                )
        return super().action_verify_kyc()


# ---------------------------------------------------------------------------
# Customer consent (FR-MKP-037, BRU-MKP-07) and evidence parity (BRU-MKP-02)
# ---------------------------------------------------------------------------
class FixMarketplaceOrderCapture(models.Model):
    _inherit = "fix.marketplace.order"

    customer_consent = fields.Boolean(
        string="Customer Consented to an External Seller",
        tracking=True,
        copy=False,
        help="The customer agreed that an external marketplace seller performs "
        "this job, with the implications stated (BRU-MKP-07). No seller can "
        "quote until it is recorded.",
    )
    consent_method = fields.Selection(CONSENT_METHODS, string="Consent Taken By", copy=False)
    consent_ref = fields.Char(
        string="Consent Reference", copy=False, help="Form number, OTP log or call reference."
    )
    consent_at = fields.Datetime(string="Consent Recorded At", readonly=True, copy=False)
    consent_by_id = fields.Many2one(
        "res.users", string="Consent Recorded By", readonly=True, copy=False
    )
    evidence_ids = fields.One2many(
        "fix.marketplace.job.evidence", "order_id", string="Job Evidence", readonly=True
    )
    review_ids = fields.One2many(
        "fix.seller.review", "order_id", string="Customer Review", readonly=True
    )

    _CONSENT = ("customer_consent", "consent_method", "consent_ref")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"consent_at", "consent_by_id"}

    def _fix_consent_stamp(self, vals):
        if vals.get("customer_consent"):
            if not vals.get("consent_method") and not (len(self) == 1 and self.consent_method):
                raise UserError("Record how the customer's consent was taken.")
            return {"consent_at": fields.Datetime.now(), "consent_by_id": self.env.uid}
        return {}

    @api.model_create_multi
    def create(self, vals_list):
        stamps = [self._fix_consent_stamp(vals) for vals in vals_list]
        records = super().create(vals_list)
        for rec, stamp in zip(records, stamps, strict=True):
            if stamp:
                rec._guarded().write(stamp)
        return records

    def write(self, vals):
        if self._fix_guard_open() or not set(self._CONSENT) & set(vals):
            return super().write(vals)
        for rec in self:
            if rec.customer_consent and rec.quote_ids:
                changed = [n for n in self._CONSENT if n in vals and vals[n] != rec[n]]
                if changed:
                    raise UserError(
                        "%s already has seller quotes: the customer's consent they were "
                        "taken under is pinned." % rec.name
                    )
        newly = self.filtered(lambda r: not r.customer_consent)
        stamp = newly._fix_consent_stamp(vals) if newly else {}
        # the workspace form re-posts unchanged fields: only a real withdrawal clears
        revoked = (
            self.filtered("customer_consent")
            if "customer_consent" in vals and not vals["customer_consent"]
            else self.browse()
        )
        res = super().write(vals)
        if stamp:
            newly._guarded().write(stamp)
        if revoked:
            revoked._guarded().write(
                {
                    "consent_method": False,
                    "consent_ref": False,
                    "consent_at": False,
                    "consent_by_id": False,
                }
            )
        return res

    def _fix_assert_consent(self):
        for rec in self:
            if rec.order_type == "service_quote" and not rec.customer_consent:
                raise UserError(
                    "%s has no recorded customer consent to an external seller: it is not "
                    "broadcast and no seller quotes on it (BRU-MKP-07)." % rec.name
                )

    def _fix_completion_evidence(self):
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cd_marketplace.completion_evidence", DEFAULT_COMPLETION_EVIDENCE)
        )
        return [t.strip() for t in (param or "").split(",") if t.strip()]

    def action_complete(self):
        labels = dict(EVIDENCE_TYPES)
        required = self._fix_completion_evidence()
        for rec in self:
            # the state and award checks of the base method come first
            if rec.order_type != "service_quote" or not (
                rec.state == "in_progress" and rec.selected_quote_id
            ):
                continue
            have = set(rec.evidence_ids.filtered("compliant").mapped("artefact_type"))
            missing = [labels.get(t, t) for t in required if t not in have]
            if missing:
                raise UserError(
                    "%s cannot complete without the same evidence as an owned job "
                    "(BRU-MKP-02). Missing: %s." % (rec.name, ", ".join(missing))
                )
        return super().action_complete()

    def _fix_job_rating(self):
        """A published review's overall rating is the customer's rating of the
        job; without one, the rating given at sign-off."""
        self.ensure_one()
        published = self.review_ids.filtered(lambda r: r.state == "published")[:1]
        return published.rating_overall or super()._fix_job_rating()


class FixSellerQuoteCapture(models.Model):
    _inherit = "fix.seller.quote"

    @api.model_create_multi
    def create(self, vals_list):
        orders = self.env["fix.marketplace.order"].browse(
            [v.get("marketplace_order_id") for v in vals_list if v.get("marketplace_order_id")]
        )
        orders.sudo()._fix_assert_consent()
        return super().create(vals_list)


# ---------------------------------------------------------------------------
# Job evidence (FR-MKP-040/042, BRU-MKP-02)
# ---------------------------------------------------------------------------
class FixMarketplaceJobEvidence(models.Model):
    _name = "fix.marketplace.job.evidence"
    _description = "Marketplace Job Evidence"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "order_id, captured_at, id"

    name = fields.Char(string="Reference", default="New", readonly=True, copy=False)
    order_id = fields.Many2one(
        "fix.marketplace.order",
        string="Marketplace Job",
        required=True,
        ondelete="restrict",
        index=True,
        domain=[("state", "=", "in_progress")],
    )
    company_id = fields.Many2one(
        "res.company", related="order_id.company_id", store=True, index=True, readonly=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="order_id.operating_unit_id", store=True, readonly=True
    )
    seller_id = fields.Many2one(
        "fix.marketplace.seller",
        string="Seller",
        related="order_id.selected_quote_id.seller_id",
        store=True,
        readonly=True,
    )
    artefact_type = fields.Selection(EVIDENCE_TYPES, string="Evidence", required=True)
    evidence_file = fields.Binary(string="Photo / Scan", attachment=True, copy=False)
    evidence_filename = fields.Char(string="File Name", copy=False)
    note = fields.Text(string="Findings / Checklist Notes")
    qc_passed = fields.Boolean(
        string="Every QC Check Passed", help="QC checklist only: all items were passed."
    )
    provenance = fields.Selection(
        PROVENANCE, string="Parts Provenance", help="Parts declaration only (FR-MKP-042)."
    )
    part_description = fields.Char(string="Parts Used")
    part_warranty_days = fields.Integer(string="Parts Warranty (days)")
    captured_by_id = fields.Many2one("res.users", string="Captured By", readonly=True, copy=False)
    captured_at = fields.Datetime(string="Captured At", readonly=True, copy=False)
    compliant = fields.Boolean(
        string="Meets the Standard", compute="_compute_compliant", store=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"captured_by_id", "captured_at"}

    @api.depends(
        "artefact_type", "evidence_file", "note", "qc_passed", "provenance", "part_description"
    )
    def _compute_compliant(self):
        for rec in self:
            kind = rec.artefact_type
            if kind in ("before_photo", "after_photo"):
                ok = bool(rec.evidence_file)
            elif kind == "diagnostic":
                ok = bool(rec.evidence_file or (rec.note or "").strip())
            elif kind == "qc_checklist":
                ok = rec.qc_passed and bool(rec.evidence_file or (rec.note or "").strip())
            elif kind == "parts_declaration":
                ok = rec.provenance == "none" or bool(
                    rec.provenance and (rec.part_description or "").strip()
                )
            else:
                ok = False
            rec.compliant = ok

    @api.depends("name", "artefact_type", "order_id.name")
    def _compute_display_name(self):
        kinds = dict(EVIDENCE_TYPES)
        for rec in self:
            rec.display_name = "%s — %s (%s)" % (
                rec.name or "New",
                kinds.get(rec.artefact_type, "?"),
                rec.order_id.name or "?",
            )

    def _assert_job_open(self, orders, what):
        for order in orders:
            if order.state != "in_progress":
                raise UserError(
                    "%s is %s: evidence is %s only while the job is in progress."
                    % (order.name, dict(order._fields["state"].selection)[order.state], what)
                )

    @api.model_create_multi
    def create(self, vals_list):
        _assert_role(self.env, OPERATOR_GROUP, "Recording marketplace job evidence")
        orders = self.env["fix.marketplace.order"].browse(
            [v.get("order_id") for v in vals_list if v.get("order_id")]
        )
        self._assert_job_open(orders, "captured")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.marketplace.job.evidence")
                    or "JEV/New"
                )
        records = super().create(vals_list)
        records._guarded().write(
            {"captured_by_id": self.env.uid, "captured_at": fields.Datetime.now()}
        )
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            self._assert_job_open(self.mapped("order_id"), "changed")
            if "order_id" in vals and any(rec.order_id.id != vals["order_id"] for rec in self):
                raise UserError("Evidence stays on the job it was captured for.")
        return super().write(vals)

    def unlink(self):
        self._assert_job_open(self.mapped("order_id"), "removed")
        return super().unlink()


# ---------------------------------------------------------------------------
# Customer review (FR-MKP-049/050)
# ---------------------------------------------------------------------------
_REVIEW_TERMS = {
    "order_id",
    "rating_overall",
    "rating_workmanship",
    "rating_timeliness",
    "rating_communication",
    "rating_value",
    "review_text",
}


class FixSellerReview(models.Model):
    _name = "fix.seller.review"
    _description = "Seller Review"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Reference", default="New", readonly=True, copy=False)
    order_id = fields.Many2one(
        "fix.marketplace.order",
        string="Marketplace Job",
        required=True,
        ondelete="restrict",
        index=True,
        domain=[("state", "in", list(REVIEWABLE_ORDER_STATES))],
    )
    company_id = fields.Many2one(
        "res.company", related="order_id.company_id", store=True, index=True, readonly=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="order_id.operating_unit_id", store=True, readonly=True
    )
    seller_id = fields.Many2one(
        "fix.marketplace.seller",
        string="Seller",
        related="order_id.selected_quote_id.seller_id",
        store=True,
        readonly=True,
        index=True,
    )
    customer_id = fields.Many2one(
        "res.partner", related="order_id.customer_id", store=True, readonly=True
    )
    rating_overall = fields.Integer(string="Overall (1-5)", required=True)
    rating_workmanship = fields.Integer(string="Workmanship (1-5)")
    rating_timeliness = fields.Integer(string="Timeliness (1-5)")
    rating_communication = fields.Integer(string="Communication (1-5)")
    rating_value = fields.Integer(string="Value for Money (1-5)")
    review_text = fields.Text(string="Customer's Review")
    state = fields.Selection(
        REVIEW_STATES, required=True, default="submitted", readonly=True, tracking=True, copy=False
    )
    moderated_by_id = fields.Many2one("res.users", string="Moderated By", readonly=True, copy=False)
    moderated_at = fields.Datetime(string="Moderated At", readonly=True, copy=False)
    moderation_note = fields.Text(string="Moderation Note", readonly=True, copy=False)
    seller_response = fields.Text(string="Seller's Response", readonly=True, copy=False)
    response_at = fields.Datetime(string="Responded At", readonly=True, copy=False)

    _one_review_per_job = models.Constraint(
        "UNIQUE(order_id)", "A marketplace job carries one customer review."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "moderated_by_id",
            "moderated_at",
            "moderation_note",
            "seller_response",
            "response_at",
        }

    @api.depends("name", "seller_id.name", "rating_overall")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s — %s (%s/5)" % (
                rec.name or "New",
                rec.seller_id.name or "?",
                rec.rating_overall or "?",
            )

    @api.constrains(
        "rating_overall",
        "rating_workmanship",
        "rating_timeliness",
        "rating_communication",
        "rating_value",
    )
    def _check_ratings(self):
        for rec in self:
            _stars(rec.rating_overall, "The overall rating", required=True)
            for name in (
                "rating_workmanship",
                "rating_timeliness",
                "rating_communication",
                "rating_value",
            ):
                _stars(rec[name], rec._fields[name].string)

    @api.model_create_multi
    def create(self, vals_list):
        _assert_role(self.env, OPERATOR_GROUP, "Recording a customer review")
        Order = self.env["fix.marketplace.order"]
        for vals in vals_list:
            order = Order.browse(vals.get("order_id"))
            if order and order.state not in REVIEWABLE_ORDER_STATES:
                raise UserError(
                    "%s is not signed off by the customer: a review is of a verified job "
                    "(FR-MKP-049)." % order.name
                )
            # a duplicate would surface as an uncatchable UniqueViolation
            if order and self.sudo().search_count([("order_id", "=", order.id)]):
                raise UserError("%s already has its customer review." % order.name)
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.seller.review") or "SRV/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "submitted"):
                changed = [
                    n
                    for n in _REVIEW_TERMS & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "Review %s is %s: what the customer wrote is pinned."
                        % (rec.name, dict(REVIEW_STATES)[rec.state])
                    )
        return super().write(vals)

    def _assert_moderator(self):
        for rec in self:
            if self.env.su:
                continue
            if self.env.user in (rec.create_uid | _seller_users(rec.seller_id)):
                raise UserError(
                    "Segregation of duties: whoever recorded review %s, or acts for the "
                    "seller, does not moderate it (FR-MKP-050)." % rec.name
                )

    def _moderate(self, state, note):
        _assert_role(self.env, OPERATOR_GROUP, "Moderating a customer review")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Review %s is already moderated." % rec.name)
            rec._assert_moderator()
            rec._guarded().write(
                {
                    "state": state,
                    "moderated_by_id": self.env.uid,
                    "moderated_at": fields.Datetime.now(),
                    "moderation_note": note,
                }
            )
        return True

    def action_publish(self):
        return self._moderate("published", False)

    def action_reject(self, note=None):
        if not (note or "").strip():
            raise UserError("Give the policy reason the review is rejected.")
        return self._moderate("rejected", note.strip())

    def action_record_response(self, response=None):
        """FR-MKP-050: one response per review, by the seller (or an operator
        recording it for them)."""
        if not (response or "").strip():
            raise UserError("Record the seller's response.")
        for rec in self:
            if not (
                self.env.su
                or self.env.user.has_group(OPERATOR_GROUP)
                or self.env.user in _seller_users(rec.seller_id)
            ):
                raise UserError("Only the seller, or an operator for them, responds.")
            if rec.state != "published":
                raise UserError("The seller responds to a published review.")
            if rec.seller_response:
                raise UserError("The seller has already responded to %s." % rec.name)
            # the seller holds no write right on reviews: who may respond is
            # checked above, and the response is the only thing written
            rec.sudo()._guarded().write(
                {"seller_response": response.strip(), "response_at": fields.Datetime.now()}
            )
        return True


# ---------------------------------------------------------------------------
# Trust & safety report (FR-MKP-064..066, BRU-MKP-11)
# ---------------------------------------------------------------------------
class FixTrustSignal(models.Model):
    _name = "fix.trust.signal"
    _description = "Marketplace Trust & Safety Report"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Reference", default="New", readonly=True, copy=False)
    seller_id = fields.Many2one(
        "fix.marketplace.seller", required=True, ondelete="restrict", index=True, tracking=True
    )
    company_id = fields.Many2one(
        "res.company", related="seller_id.company_id", store=True, index=True, readonly=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="seller_id.operating_unit_id", store=True, readonly=True
    )
    signal_type = fields.Selection(SIGNAL_TYPES, string="Concern", required=True, tracking=True)
    source = fields.Selection(SIGNAL_SOURCES, required=True, default="customer")
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")], required=True, default="medium"
    )
    order_id = fields.Many2one("fix.marketplace.order", string="Marketplace Job", index=True)
    listing_id = fields.Many2one("fix.marketplace.listing", string="Listing", index=True)
    description = fields.Text(string="What Was Reported", required=True)
    evidence_file = fields.Binary(string="Evidence", attachment=True, copy=False)
    evidence_filename = fields.Char(string="Evidence File Name", copy=False)
    state = fields.Selection(
        SIGNAL_STATES, required=True, default="open", readonly=True, tracking=True, copy=False
    )
    listing_paused = fields.Boolean(
        string="Listing Suspended by this Report", readonly=True, copy=False
    )
    reported_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True, copy=False)
    investigator_id = fields.Many2one(
        "res.users", string="Investigated By", readonly=True, copy=False
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_at = fields.Datetime(string="Decided At", readonly=True, copy=False)
    finding = fields.Text(string="Finding", readonly=True, copy=False)
    consequence_id = fields.Many2one(
        "fix.seller.consequence", string="Suspension Imposed", readonly=True, copy=False
    )

    _FACTS = {"seller_id", "signal_type", "order_id", "listing_id", "description"}

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "listing_paused",
            "reported_by_id",
            "investigator_id",
            "decided_by_id",
            "decided_at",
            "finding",
            "consequence_id",
        }

    @api.depends("name", "seller_id.name", "signal_type")
    def _compute_display_name(self):
        kinds = dict(SIGNAL_TYPES)
        for rec in self:
            rec.display_name = "%s — %s (%s)" % (
                rec.name or "New",
                rec.seller_id.name or "?",
                kinds.get(rec.signal_type, "?"),
            )

    @api.constrains("seller_id", "order_id", "listing_id")
    def _check_subject(self):
        for rec in self:
            if rec.listing_id and rec.listing_id.seller_id != rec.seller_id:
                raise ValidationError("The listing belongs to another seller.")
            awarded = rec.order_id.selected_quote_id.seller_id
            if awarded and awarded != rec.seller_id:
                raise ValidationError("The job was awarded to another seller.")

    @api.model_create_multi
    def create(self, vals_list):
        _assert_role(self.env, OPERATOR_GROUP, "Recording a trust & safety report")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.trust.signal") or "TSR/New"
                )
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"reported_by_id": self.env.uid})
            rec._suspend_reported_listing()
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "open"):
                changed = [
                    n for n in self._FACTS & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "Report %s is %s: what was reported is pinned."
                        % (rec.name, dict(SIGNAL_STATES)[rec.state])
                    )
        return super().write(vals)

    def _suspend_reported_listing(self):
        """BRU-MKP-11 / FR-MKP-066: a counterfeit-part report suspends the
        listing at once, pending the investigation."""
        self.ensure_one()
        listing = self.listing_id.sudo()
        if self.signal_type == "counterfeit_part" and listing.state == "active":
            listing._guarded().write({"state": "paused"})
            listing.message_post(body="Suspended pending investigation of %s." % self.name)
            self._guarded().write({"listing_paused": True})

    def _assert_decider(self):
        for rec in self:
            if self.env.su:
                continue
            if self.env.user in (
                rec.reported_by_id | rec.create_uid | _seller_users(rec.seller_id)
            ):
                raise UserError(
                    "Segregation of duties: whoever recorded report %s, or acts for the "
                    "seller, does not decide it." % rec.name
                )

    def action_investigate(self):
        _assert_role(self.env, OPERATOR_GROUP, "Investigating a trust & safety report")
        for rec in self:
            if rec.state != "open":
                raise UserError("Only a reported concern is taken into investigation.")
            rec._guarded().write({"state": "investigating", "investigator_id": self.env.uid})
        return True

    def _decide(self, state, finding):
        if not (finding or "").strip():
            raise UserError("Record the finding.")
        for rec in self:
            if rec.state != "investigating":
                raise UserError("A report is decided after its investigation.")
            rec._assert_decider()
            rec._guarded().write(
                {
                    "state": state,
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "finding": finding.strip(),
                }
            )

    def action_substantiate(self, finding=None):
        """The concern is upheld. A counterfeit-part, fraud, collusion or fake
        job finding suspends the seller (BRU-MKP-11); another operator decides
        any appeal against it (BRU-MKP-18)."""
        _assert_role(self.env, OPERATOR_GROUP, "Deciding a trust & safety report")
        self._decide("substantiated", finding)
        for rec in self:
            trigger = SUSPENDING_SIGNALS.get(rec.signal_type)
            if not trigger or rec.seller_id._active_suspension():
                continue
            consequence = self.env["fix.seller.consequence"].create(
                {
                    "seller_id": rec.seller_id.id,
                    "consequence_type": "suspension",
                    "trigger": trigger,
                    "reason": "%s substantiated: %s" % (rec.name, rec.finding),
                }
            )
            consequence.action_impose()
            rec._guarded().write({"consequence_id": consequence.id})
        return True

    def action_dismiss(self, finding=None):
        """Not upheld: a listing this report suspended goes live again unless
        the seller is suspended for another reason."""
        _assert_role(self.env, OPERATOR_GROUP, "Deciding a trust & safety report")
        self._decide("dismissed", finding)
        for rec in self:
            listing = rec.listing_id.sudo()
            if (
                rec.listing_paused
                and listing.state == "paused"
                and not (rec.seller_id._active_suspension())
            ):
                listing._guarded().write({"state": "active"})
                listing.message_post(body="Live again: %s was dismissed." % rec.name)
        return True
