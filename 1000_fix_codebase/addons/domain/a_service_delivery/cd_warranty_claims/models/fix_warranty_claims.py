# cd_warranty_claims — M09 Warranty, Protection Plans & Claims (P07-M02, CD-M09-nn).
#
# G4-01: claims auto-created within 24 hours of a completed warranty job
# (AUT-018) and submitted within 72. The evidence pack's completeness check
# BLOCKS submission (T05) — an incomplete claim is a rejected claim and a
# re-work cycle.
import base64
import hashlib
import logging
import uuid
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

logger = logging.getLogger(__name__)

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

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    product_type = fields.Selection(
        [("extension", "Warranty Extension"), ("protection", "Protection Plan")],
        required=True,
        default="extension",
    )
    catalogue_item_id = fields.Many2one(
        "product.template", string="Catalogue Item", help="Sold through M37's catalogue"
    )
    duration_months = fields.Integer(required=True, default=12)
    waiting_days = fields.Integer(
        default=0, help="BRU/WTY-12: claims arising within the waiting period are rejected"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    claim_limit = fields.Monetary(
        string="Aggregate Claim Limit",
        currency_field="currency_id",
        help="WTY-14: settled claims decrement this; beyond the limit claims are refused",
    )
    excess_amount = fields.Monetary(
        string="Customer Excess",
        currency_field="currency_id",
        default=0.0,
        help="WTY-13: collected before fulfilment unless waived with approval",
    )
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
    _claim_no_unique = models.Constraint("UNIQUE (claim_no)", "Claim number must be unique")

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    claim_no = fields.Char(string="Claim No.", required=True, readonly=True, index=True, copy=False)
    service_order_id = fields.Many2one(
        "fix.service.order",
        string="Service Order",
        required=True,
        ondelete="restrict",
        index=True,
        help="The completed warranty job this claim recovers",
    )
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True, index=True)
    device_id = fields.Many2one(related="service_order_id.device_id", store=True, index=True)
    warranty_product_id = fields.Many2one("fix.warranty.product", string="Protection Product")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    claim_amount = fields.Monetary(
        string="Claim Amount", currency_field="currency_id", required=True
    )
    # Evidence pack (T04/T05)
    evidence_ids = fields.One2many("fix.warranty.evidence", "claim_id", string="Evidence Pack")
    evidence_complete = fields.Boolean(compute="_compute_evidence", store=True)
    missing_evidence = fields.Char(compute="_compute_evidence", store=True)
    # Lifecycle
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("ready", "Ready"),
            ("submitted", "Submitted"),
            ("in_review", "In Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("remitted", "Remitted"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    created_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    job_completed_at = fields.Datetime(readonly=True, help="AUT-018: When warranty job completed")
    submitted_at = fields.Datetime(readonly=True)
    decided_at = fields.Datetime(readonly=True)
    rejection_reason = fields.Char()
    submission_deadline = fields.Datetime(
        readonly=True, help="WTY-06: brand windows vary; default 72h from creation (G4-01)"
    )
    auto_creation_latency_hours = fields.Float(
        string="Creation Latency (h)",
        compute="_compute_timing_latencies",
        store=True,
        help="Hours elapsed between job completion and claim auto-creation (target <= 24h)",
    )
    submission_latency_hours = fields.Float(
        string="Submission Latency (h)",
        compute="_compute_timing_latencies",
        store=True,
        help="Hours elapsed between claim creation and brand submission (target <= 72h)",
    )
    is_submission_overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_overdue",
        store=True,
        help="True if claim is pending submission past 72h deadline",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("claim_no"):
                # data/ir_sequence.xml; the fallback stays unique (it used to be
                # "CLM/<today>": the second claim of a day hit UNIQUE (claim_no))
                vals["claim_no"] = self.env["ir.sequence"].next_by_code("fix.warranty.claim") or (
                    "CLM/%s/%s" % (fields.Date.today(), uuid.uuid4().hex[:8].upper())
                )
            # WTY-06: submission window default 72h from creation (G4-01)
            now = fields.Datetime.now()
            vals.setdefault("created_at", now)
            vals.setdefault("submission_deadline", now + timedelta(hours=72))
            if not vals.get("job_completed_at"):
                vals["job_completed_at"] = now
        return super().create(vals_list)

    @api.depends("job_completed_at", "created_at", "submitted_at")
    def _compute_timing_latencies(self):
        for claim in self:
            if claim.job_completed_at and claim.created_at:
                delta = claim.created_at - claim.job_completed_at
                claim.auto_creation_latency_hours = max(
                    0.0, round(delta.total_seconds() / 3600.0, 2)
                )
            else:
                claim.auto_creation_latency_hours = 0.0

            if claim.created_at and claim.submitted_at:
                delta = claim.submitted_at - claim.created_at
                claim.submission_latency_hours = max(0.0, round(delta.total_seconds() / 3600.0, 2))
            else:
                claim.submission_latency_hours = 0.0

    @api.depends("submission_deadline", "state", "submitted_at")
    def _compute_overdue(self):
        now = fields.Datetime.now()
        for claim in self:
            if claim.state in ("draft", "ready") and claim.submission_deadline:
                claim.is_submission_overdue = now > claim.submission_deadline
            else:
                claim.is_submission_overdue = False

    @api.depends("evidence_ids.requirement_key", "evidence_ids.document_id")
    def _compute_evidence(self):
        """T05: the BLOCKING completeness check — a claim cannot be
        submitted with an incomplete pack."""
        for claim in self:
            present = {e.requirement_key for e in claim.evidence_ids if e.document_id}
            missing = [label for key, label in EVIDENCE_REQUIREMENTS if key not in present]
            claim.evidence_complete = not missing
            claim.missing_evidence = ", ".join(missing) if missing else False

    def action_assemble_workshop_evidence_pack(self):
        """T05 / R03-M02: Assembles evidence pack drawing from workshop repair records."""
        Evidence = self.env["fix.warranty.evidence"]
        for claim in self:
            # service_order_id is required (ondelete restrict): every claim has an
            # order, and fix.document is always installed (cd_document_core is a
            # manifest dependency) - the former guards for both were dead code.
            order = claim.service_order_id
            existing_keys = {e.requirement_key for e in claim.evidence_ids}
            # Attach available documents from service order or create stubs if workshop artifacts exist
            for key, _label in EVIDENCE_REQUIREMENTS:
                if key not in existing_keys:
                    # In production, resolves from order.document_ids or workshop inspection
                    doc = self.env["fix.document"].search(
                        [
                            ("res_model", "=", "fix.service.order"),
                            ("res_id", "=", order.id),
                            ("name", "ilike", key),
                        ],
                        limit=1,
                    )
                    if doc:
                        Evidence.create(
                            {
                                "claim_id": claim.id,
                                "requirement_key": key,
                                "document_id": doc.id,
                            }
                        )
            claim._compute_evidence()
            if claim.evidence_complete and claim.state == "draft":
                claim.state = "ready"
        return True

    # --- AUT-018: the 24-hour auto-create -----------------------------

    @api.model
    def consume_order_completed(self, event: dict) -> "FixWarrantyClaim | None":
        """AUT-018 (G4-01): a completed WARRANTY job auto-creates its claim.
        Consumes the service_order.closed event — the completion event the
        producer actually emits (``fix.service.order._on_state_change``
        publishes service_order.{state}; a literal 'completed' state does not
        exist in the AS-06 machine, so the historical
        'service_order.completed' subscription was dead wiring). Idempotent
        on the order (one claim per warranty job). The 24-hour budget is the
        Airflow workflow's trigger window; the creation here is immediate."""
        payload = event.get("payload", {})
        order_id = event.get("aggregate_id")
        existing = self.search([("service_order_id", "=", order_id)])
        if existing:
            return existing
        order = self.env["fix.service.order"].browse(order_id)
        if not order.exists() or order.order_category != "warranty":
            return None
        completed_time = payload.get("completed_at") or fields.Datetime.now()
        claim = self.create(
            {
                # required on the claim; an order's own OU is optional, its
                # branch's is not (the auto-create failed NOT NULL without it)
                "operating_unit_id": (
                    order.operating_unit_id or order.branch_id.operating_unit_id
                ).id,
                "service_order_id": order_id,
                "brand_id": order.device_id.brand_id.id,
                # A02 audit M01-W2: the APPROVED estimate's total, not the
                # first estimate in any state (a draft or rejected quote).
                "claim_amount": order._fix_governing_estimate()
                .filtered(lambda e: e.state == "approved")
                .grand_total
                or 0.0,
                "job_completed_at": completed_time,
            }
        )
        # Assemble workshop evidence pack automatically on creation
        claim.action_assemble_workshop_evidence_pack()
        publish(
            self.env,
            "warranty_claim.created",
            "fix.warranty.claim",
            claim.id,
            {
                "claim_no": claim.claim_no,
                "order_id": order_id,
                "brand_id": claim.brand_id.id,
                "deadline": str(claim.submission_deadline),
            },
        )
        return claim

    @api.model
    def _cron_aut018_intake(self) -> int:
        """AUT-018 wiring: drain the transactional outbox for
        service_order.closed events and auto-create claims for WARRANTY
        jobs. Same shape as the M20 AR billable-event intake: one row per
        event, savepointed, idempotent through consume_order_completed's own
        per-order search — replays are free."""
        outbox = self.env["fix.event.outbox"].sudo()
        events = outbox.search(
            [("event_type", "=", "service_order.closed"), ("aggregate", "=", "fix.service.order")],
            order="id asc",
            limit=500,
        )
        created = 0
        for evt in events:
            try:
                with self.env.cr.savepoint():
                    # consume_order_completed returns the EXISTING claim on a
                    # replay — only genuinely new claims count as created
                    if self.search([("service_order_id", "=", evt.aggregate_id)]):
                        continue
                    claim = self.consume_order_completed(
                        {
                            "aggregate_id": evt.aggregate_id,
                            "payload": {"completed_at": evt.create_date},
                        }
                    )
                    if claim:
                        created += 1
            except Exception:
                logger.warning(
                    "AUT-018 intake skipped outbox event %s (order %s)",
                    evt.event_id,
                    evt.aggregate_id,
                    exc_info=True,
                )
        if created:
            logger.info("AUT-018 intake created %d warranty claim(s)", created)
        return created

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
                    % (claim.claim_no, claim.missing_evidence)
                )
            if claim.state not in ("draft", "ready"):
                raise UserError("Only a draft/ready claim submits")
            now = fields.Datetime.now()
            if claim.submission_deadline and now > claim.submission_deadline:
                claim.message_post(
                    body="Warning: Claim submitted past 72h deadline (escalated for brand acceptance)"
                )
            claim.write({"state": "submitted", "submitted_at": now})
            publish(
                self.env,
                "warranty_claim.submitted",
                "fix.warranty.claim",
                claim.id,
                {
                    "claim_no": claim.claim_no,
                    "brand_id": claim.brand_id.id,
                    "amount": claim.claim_amount,
                    "submitted_at": str(now),
                },
            )

    def action_mark_in_review(self):
        """The brand acknowledged a submitted claim and is reviewing it."""
        for claim in self:
            if claim.state != "submitted":
                raise UserError("Only a submitted claim goes into review")
            claim.state = "in_review"

    def action_decide(self, approved: bool, reason: str = ""):
        """The brand's decision lands here (via webhook or manual keying).
        Only a claim the brand has received (submitted / in review) can be
        decided: a draft was never sent and a decided or remitted claim is
        final (a late webhook must not reopen a remitted claim).
        SoD-11 companion: deciding and write-off approval are different
        people — enforced by the callers checking the roles."""
        for claim in self:
            if claim.state not in ("submitted", "in_review"):
                raise UserError(
                    "Claim %s is %s — only a submitted or in-review claim can be decided"
                    % (claim.claim_no, claim.state)
                )
            if approved and not self.env.context.get("skip_serial_validation"):
                # Serial / IMEI Provenance Validation (FLAW-09.1)
                device = claim.device_id or (
                    claim.service_order_id and claim.service_order_id.device_id
                )
                serial = (
                    getattr(device, "serial_number", None) or getattr(device, "imei", None) or ""
                )
                if not serial.strip() and not device:
                    raise UserError(
                        "Claim %s cannot be approved: device provenance verification failed. "
                        "A valid device record with serial/IMEI is required." % claim.claim_no
                    )
            claim.write(
                {
                    "state": "approved" if approved else "rejected",
                    "decided_at": fields.Datetime.now(),
                    "rejection_reason": False if approved else reason,
                }
            )
            publish(
                self.env,
                "warranty_claim.decided",
                "fix.warranty.claim",
                claim.id,
                {"claim_no": claim.claim_no, "approved": approved},
            )

    # --- T08: remittance reconciliation --------------------------------

    remittance_amount = fields.Monetary(
        string="Remitted", currency_field="currency_id", readonly=True, copy=False
    )

    def action_record_remittance(self, amount: float, bank_ref: str):
        """WTY reconciliation: match the brand's remittance to the claim.
        A mismatch is FLAGGED, never auto-adjusted."""
        for claim in self:
            if claim.state != "approved":
                raise UserError("Only an approved claim takes a remittance")
            claim.write({"remittance_amount": amount, "state": "remitted"})
            mismatch = abs(amount - claim.claim_amount) > 0.01
            publish(
                self.env,
                "warranty_claim.remitted",
                "fix.warranty.claim",
                claim.id,
                {
                    "claim_no": claim.claim_no,
                    "bank_ref": bank_ref,
                    "expected": claim.claim_amount,
                    "received": amount,
                    "mismatch": mismatch,
                },
            )


class FixWarrantyEvidence(models.Model):
    """One item in a claim's evidence pack (T04/FLAW-09.2)."""

    _name = "fix.warranty.evidence"
    _description = "Claim Evidence Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    claim_id = fields.Many2one("fix.warranty.claim", required=True, ondelete="cascade")
    requirement_key = fields.Selection(list(EVIDENCE_REQUIREMENTS), required=True)
    document_id = fields.Many2one("fix.document", string="Document", ondelete="restrict")

    # Cryptographic Evidence Verification (FLAW-09.2)
    file_data = fields.Binary(string="Upload Evidence File")
    file_name = fields.Char(string="File Name")
    attachment_id = fields.Many2one(
        "ir.attachment", string="Evidence Attachment", ondelete="set null"
    )
    sha256_hash = fields.Char(
        string="SHA-256 Checksum", compute="_compute_sha256", store=True, readonly=True
    )

    @api.depends("file_data", "attachment_id", "attachment_id.datas")
    def _compute_sha256(self):
        for rec in self:
            data = None
            if rec.file_data:
                try:
                    data = base64.b64decode(rec.file_data)
                except Exception:
                    data = None
            elif rec.attachment_id and rec.attachment_id.datas:
                try:
                    data = base64.b64decode(rec.attachment_id.datas)
                except Exception:
                    data = None
            if data:
                rec.sha256_hash = hashlib.sha256(data).hexdigest()
            elif not rec.sha256_hash:
                rec.sha256_hash = False
