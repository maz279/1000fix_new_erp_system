# cd_warranty_claims — M09 Warranty, Protection Plans & Claims (P07-M02, CD-M09-nn).
#
# G4-01: claims auto-created within 24 hours of a completed warranty job
# (AUT-018) and submitted within 72. The evidence pack's completeness check
# BLOCKS submission (T05) — an incomplete claim is a rejected claim and a
# re-work cycle.
from odoo import api, fields, models
from odoo.exceptions import UserError

from datetime import timedelta

from libs.py.fix_events import publish  # FF-28

# The evidence pack: every item a brand submission needs (T04). The
# completeness check walks this list; a claim without all of it is blocked.
EVIDENCE_REQUIREMENTS = [
    ("photo_before", "Before Photograph"),
    ("photo_after", "After Photograph"),
    ("diagnostic", "Diagnostic Record"),
    ("parts_issued", "Parts Issued Evidence"),
    ("device_serial", "Device Serial Capture"),
    ("technician_cert", "Technician Certification"),
    ("purchase_proof", "Purchase Proof"),
]


class FixWarrantyProduct(models.Model):
    """T02: warranty extensions and protection plans sold through M37's
    catalogue. Waiting period, limits and excess — the claim-side contract."""

    _name = "fix.warranty.product"
    _description = "Warranty / Protection Product"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    name = fields.Char(required=True)
    product_type = fields.Selection(
        [("extension", "Warranty Extension"), ("protection", "Protection Plan")],
        required=True, default="extension")
    catalogue_item_id = fields.Many2one("product.template", string="Catalogue Item",
                                        help="Sold through M37's catalogue")
    duration_months = fields.Integer(required=True, default=12)
    waiting_days = fields.Integer(
        default=0,
        help="BRU/WTY-12: claims arising within the waiting period are rejected")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    claim_limit = fields.Monetary(
        string="Aggregate Claim Limit", currency_field="currency_id",
        help="WTY-14: settled claims decrement this; beyond the limit claims are refused")
    excess_amount = fields.Monetary(
        string="Customer Excess", currency_field="currency_id", default=0.0,
        help="WTY-13: collected before fulfilment unless waived with approval")
    active = fields.Boolean(default=True)

    @api.constrains("duration_months", "waiting_days", "claim_limit")
    def _check_product(self):
        for product in self:
            if product.duration_months <= 0:
                raise UserError("The duration must be positive")
            if product.waiting_days < 0 or product.claim_limit < 0:
                raise UserError("Waiting days and claim limit cannot be negative")


class FixWarrantyClaim(models.Model):
    """A brand warranty claim (CD-M09-03). The claim record, the evidence
    pack and the reconciliation live in Odoo — the per-brand TRANSFORMATION
    is an Airflow workflow (T06: configuration that changes when a brand
    changes its template, not code that requires a release)."""

    _name = "fix.warranty.claim"
    _description = "Warranty Claim"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "created_at desc, id desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _claim_no_unique = models.Constraint('UNIQUE (claim_no)', 'Claim number must be unique')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    claim_no = fields.Char(string="Claim No.", required=True, readonly=True,
                           index=True, copy=False)
    service_order_id = fields.Many2one(
        "fix.service.order", string="Service Order", required=True,
        ondelete="restrict", index=True,
        help="The completed warranty job this claim recovers")
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True,
                               index=True)
    device_id = fields.Many2one(related="service_order_id.device_id",
                                store=True, index=True)
    warranty_product_id = fields.Many2one("fix.warranty.product",
                                          string="Protection Product")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    claim_amount = fields.Monetary(string="Claim Amount", currency_field="currency_id",
                                   required=True)
    # Evidence pack (T04/T05)
    evidence_ids = fields.One2many("fix.warranty.evidence", "claim_id",
                                   string="Evidence Pack")
    evidence_complete = fields.Boolean(compute="_compute_evidence", store=True)
    missing_evidence = fields.Char(compute="_compute_evidence", store=True)
    # Lifecycle
    state = fields.Selection(
        [("draft", "Draft"), ("ready", "Ready"), ("submitted", "Submitted"),
         ("in_review", "In Review"), ("approved", "Approved"),
         ("rejected", "Rejected"), ("remitted", "Remitted")],
        default="draft", required=True, tracking=True)
    created_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    submitted_at = fields.Datetime(readonly=True)
    decided_at = fields.Datetime(readonly=True)
    rejection_reason = fields.Char()
    submission_deadline = fields.Datetime(
        readonly=True,
        help="WTY-06: brand windows vary; the claim escalates at the deadline")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("claim_no"):
                vals["claim_no"] = self.env["ir.sequence"].next_by_code(
                    "fix.warranty.claim") or ("CLM/%s" % fields.Date.today())
            # WTY-06: submission window default 72h from creation (G4-01)
            vals.setdefault("submission_deadline",
                            fields.Datetime.now() + timedelta(hours=72))
        return super().create(vals_list)

    @api.depends("evidence_ids.requirement_key", "evidence_ids.document_id")
    def _compute_evidence(self):
        """T05: the BLOCKING completeness check — a claim cannot be
        submitted with an incomplete pack."""
        for claim in self:
            present = {e.requirement_key for e in claim.evidence_ids
                       if e.document_id}
            missing = [label for key, label in EVIDENCE_REQUIREMENTS
                       if key not in present]
            claim.evidence_complete = not missing
            claim.missing_evidence = ", ".join(missing) if missing else False

    # --- AUT-018: the 24-hour auto-create -----------------------------

    @api.model
    def consume_order_completed(self, event: dict) -> "FixWarrantyClaim | None":
        """AUT-018 (G4-01): a completed WARRANTY job auto-creates its claim.
        Consumes the service_order.completed event; idempotent on the order
        (one claim per warranty job). The 24-hour budget is the Airflow
        workflow's trigger window; the creation here is immediate."""
        payload = event.get("payload", {})
        order_id = event.get("aggregate_id")
        existing = self.search([("service_order_id", "=", order_id)])
        if existing:
            return existing
        order = self.env["fix.service.order"].browse(order_id)
        if not order.exists() or order.order_category != "warranty":
            return None
        return self.create({
            "service_order_id": order_id,
            "brand_id": order.device_id.brand_id.id,
            "claim_amount": order.estimate_ids and
                order.estimate_ids[0].grand_total or 0.0,
        })

    # --- Submission with the blocking gate ------------------------------

    def action_submit(self):
        """T05: the completeness check blocks submission. BRU-WTY-04: a
        claim cannot be submitted until it passes the brand's rule set —
        the evidence pack IS that rule set's local half."""
        for claim in self:
            if not claim.evidence_complete:
                raise UserError(
                    "Claim %s cannot be submitted — missing evidence: %s "
                    "(an incomplete claim is a rejected claim)"
                    % (claim.claim_no, claim.missing_evidence))
            if claim.state not in ("draft", "ready"):
                raise UserError("Only a draft/ready claim submits")
            claim.write({"state": "submitted",
                         "submitted_at": fields.Datetime.now()})
            publish(self.env, "warranty_claim.submitted", "fix.warranty.claim",
                    claim.id, {
                        "claim_no": claim.claim_no,
                        "brand_id": claim.brand_id.id,
                        "amount": claim.claim_amount,
                    })

    def action_decide(self, approved: bool, reason: str = ""):
        """The brand's decision lands here (via webhook or manual keying).
        SoD-11 companion: deciding and write-off approval are different
        people — enforced by the callers checking the roles."""
        for claim in self:
            claim.write({
                "state": "approved" if approved else "rejected",
                "decided_at": fields.Datetime.now(),
                "rejection_reason": False if approved else reason,
            })
            publish(self.env, "warranty_claim.decided", "fix.warranty.claim",
                    claim.id, {"claim_no": claim.claim_no,
                               "approved": approved})

    # --- T08: remittance reconciliation --------------------------------

    remittance_amount = fields.Monetary(string="Remitted", currency_field="currency_id",
                                        readonly=True, copy=False)

    def action_record_remittance(self, amount: float, bank_ref: str):
        """WTY reconciliation: match the brand's remittance to the claim.
        A mismatch is FLAGGED, never auto-adjusted."""
        for claim in self:
            if claim.state != "approved":
                raise UserError("Only an approved claim takes a remittance")
            claim.write({"remittance_amount": amount, "state": "remitted"})
            mismatch = abs(amount - claim.claim_amount) > 0.01
            publish(self.env, "warranty_claim.remitted", "fix.warranty.claim",
                    claim.id, {
                        "claim_no": claim.claim_no, "bank_ref": bank_ref,
                        "expected": claim.claim_amount, "received": amount,
                        "mismatch": mismatch,
                    })


class FixWarrantyEvidence(models.Model):
    """One item in a claim's evidence pack."""

    _name = "fix.warranty.evidence"
    _description = "Claim Evidence Item"

    claim_id = fields.Many2one("fix.warranty.claim", required=True,
                               ondelete="cascade")
    requirement_key = fields.Selection(
        [(k, label) for k, label in EVIDENCE_REQUIREMENTS],
        required=True)
    document_id = fields.Many2one("fix.document", string="Document",
                                  ondelete="restrict")
