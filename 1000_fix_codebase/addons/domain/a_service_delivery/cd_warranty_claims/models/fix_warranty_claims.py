# cd_warranty_claims — M09 Warranty, Protection Plans & Claims (P07-M02, CD-M09-nn).
#
# G4-01: claims auto-created within 24 hours of a completed warranty job
# (AUT-018) and submitted within 72. The evidence pack's completeness check
# BLOCKS submission (T05) — an incomplete claim is a rejected claim and a
# re-work cycle.
#
# A04 workflow audit (2026-11-03) M09-1..-14, C2-C13 build (2026-11-04):
# - the claim's state, amount, decision and remittance were writable by any
#   internal user, directly and through the P03 form (12,500 became 990,000
#   after approval); they are now guarded (fix.guarded.mixin) and a decided
#   claim is frozen;
# - a claim could be raised on a customer-paid or unclosed order (double
#   recovery) and AUT-018 raised a 0.0 claim on a DRAFT order: a claim now
#   recovers a CLOSED warranty job, for the APPROVED estimate's amount;
# - the submitting clerk recorded the OEM's approval himself, and the serial
#   check was switched off by a caller context: the decision is now keyed by
#   a clerk and recorded by a Claim Decision Officer from the M63 inbox
#   (never the submitter, the keyer or the creator), with requested vs
#   approved (partial) amounts and a decision history; there is no bypass;
# - one document satisfied all seven evidence items and the SHA-256 was never
#   read: every item needs its own, hashed, distinct document and the pack is
#   locked once submitted;
# - the product's waiting period and aggregate limit were never read;
# - the stored overdue flag froze: it is computed at read time and searchable.
import base64
import hashlib
import json
import logging
import uuid
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Domain

from libs.py.fix_events import publish  # FF-28

logger = logging.getLogger(__name__)

CLERK_GROUP = "cd_warranty_claims.group_warranty_claims_clerk"
OFFICER_GROUP = "cd_warranty_claims.group_warranty_claims_officer"

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

CLAIM_STATES = [
    ("draft", "Draft"),
    ("ready", "Ready"),
    ("submitted", "Submitted"),
    ("in_review", "In Review"),
    ("approved", "Approved"),
    ("partially_approved", "Partially Approved"),
    ("rejected", "Rejected"),
    ("remitted", "Remitted"),
    ("closed", "Closed"),
]
OPEN_STATES = ("draft", "ready")
RECEIVED_STATES = ("submitted", "in_review")
# A recovery the OEM agreed to pay (in full or in part).
RECOVERY_STATES = ("approved", "partially_approved")
# Decided by the OEM: frozen against direct edits (A04 C2).
FINAL_STATES = ("approved", "partially_approved", "rejected", "remitted", "closed")
# Settled recoveries consume a protection product's aggregate limit (WTY-14).
SETTLED_STATES = ("approved", "partially_approved", "remitted", "closed")

DECISIONS = [
    ("approve", "Approve in Full"),
    ("partial", "Approve in Part"),
    ("reject", "Reject"),
]
DECISION_STATE = {"approve": "approved", "partial": "partially_approved", "reject": "rejected"}

# AUT-018 raises the claim while M01 closes the job (action_close raises it
# from 'delivered', then the close gate checks for it); a user raises one
# only from a closed job.
AUTO_CLAIM_ORDER_STATES = ("delivered", "closed")
CLAIM_ORDER_STATES = ("closed",)
# A02 ERP pass 2 X5-22: the AUT-018 backup intake reads the outbox on from
# this cursor (the last outbox id walked), a batch at a time.
AUT018_CURSOR_PARAM = "cd_warranty_claims.aut018_outbox_cursor"
AUT018_BATCH = 500
# Review of X5-22: the cursor only moves past events (a) handled - done, or
# failed AUT018_MAX_ATTEMPTS times - and (b) older than the lag, so a lower
# outbox id whose transaction commits after a higher one is still read.
AUT018_LAG_PARAM = "cd_warranty_claims.aut018_cursor_lag_minutes"
AUT018_LAG_DEFAULT = 10
AUT018_FAILURES_PARAM = "cd_warranty_claims.aut018_failed_events"
AUT018_MAX_ATTEMPTS = 5

# Set once when the claim is raised and never edited by a user afterwards.
_FIXED_AT_CREATE = {"claim_amount", "service_order_id", "operating_unit_id", "company_id"}
# Editable while the claim is being prepared, frozen once it goes to the brand.
_FROZEN_ONCE_SUBMITTED = {"brand_id", "warranty_product_id", "currency_id", "evidence_ids"}
# Bookkeeping that never makes a write a business change.
_FREEZE_EXEMPT_PREFIXES = ("message_", "activity_", "website_message", "device_recheck_")


def _assert_role(env, xmlid, what):
    """Superuser service code is trusted; a user needs the role."""
    if env.su or env.user.has_group(xmlid):
        return
    group = env.ref(xmlid, raise_if_not_found=False)
    raise AccessError(
        "%s needs the %s role, which %s does not hold."
        % (what, group.sudo().name if group else xmlid, env.user.name)
    )


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
        help="WTY-14: settled claims of a device under this product count against it; "
        "a claim beyond the limit is refused (0 = no limit)",
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
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "created_at desc, id desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _claim_no_unique = models.Constraint("UNIQUE (claim_no)", "Claim number must be unique")
    # A04 C2: users READ claims (the clerk role writes them); a chatter note
    # is not a change to the claim, so reading is enough to post one.
    _mail_post_access = "read"

    # A04 C4/C9: the OEM decision keyed in-house is a routed four-eyes
    # approval. A clerk keys it, a Claim Decision Officer records it from the
    # M63 inbox; the brand API (P08) records the brand's own decision.
    _approval_domain = "warranty_claim_decision"
    _approval_apply_method = "action_apply_decision"
    _approval_group = OFFICER_GROUP
    _approval_routed = True

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
        help="The closed warranty job this claim recovers",
    )
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True, index=True)
    device_id = fields.Many2one(related="service_order_id.device_id", store=True, index=True)
    warranty_product_id = fields.Many2one("fix.warranty.product", string="Protection Product")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    claim_amount = fields.Monetary(
        string="Requested Amount",
        currency_field="currency_id",
        required=True,
        help="What the claim asks the OEM for: the approved warranty estimate of the job, "
        "fixed when the claim is raised (Refresh Amount re-reads the estimate while the "
        "claim is a draft).",
    )
    approved_amount = fields.Monetary(
        string="Approved Amount",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="What the OEM agreed to reimburse: the requested amount, or less on a partial "
        "approval. The remittance is reconciled against this.",
    )
    # Evidence pack (T04/T05)
    evidence_ids = fields.One2many("fix.warranty.evidence", "claim_id", string="Evidence Pack")
    evidence_complete = fields.Boolean(compute="_compute_evidence", store=True)
    missing_evidence = fields.Char(compute="_compute_evidence", store=True)
    # Lifecycle
    state = fields.Selection(CLAIM_STATES, default="draft", required=True, tracking=True)
    created_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    job_completed_at = fields.Datetime(readonly=True, help="AUT-018: When warranty job completed")
    submitted_at = fields.Datetime(readonly=True)
    submitted_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True, copy=False)
    decided_at = fields.Datetime(readonly=True)
    decided_by_id = fields.Many2one(
        "res.users",
        string="Decision Recorded By",
        readonly=True,
        copy=False,
        help="The Claim Decision Officer (inbox) or the brand partner user (P08 API)",
    )
    decision_source = fields.Selection(
        [("officer", "Claim Decision Officer"), ("brand_api", "Brand Partner API")],
        readonly=True,
        copy=False,
    )
    rejection_reason = fields.Char(readonly=True, copy=False)
    # The decision a clerk keyed from the OEM's answer, awaiting the officer.
    proposed_decision = fields.Selection(
        DECISIONS, string="Keyed Decision", readonly=True, copy=False
    )
    proposed_amount = fields.Monetary(
        string="Keyed Approved Amount", currency_field="currency_id", readonly=True, copy=False
    )
    proposed_reason = fields.Char(string="Keyed Reason", readonly=True, copy=False)
    oem_reference = fields.Char(
        string="OEM Decision Reference", readonly=True, copy=False, help="The brand's own reference"
    )
    decision_proposed_by_id = fields.Many2one(
        "res.users", string="Decision Keyed By", readonly=True, copy=False
    )
    decision_ids = fields.One2many(
        "fix.warranty.claim.decision", "claim_id", string="Decision History", readonly=True
    )
    appeal_ids = fields.One2many("fix.claim.appeal", "claim_id", string="Appeals", readonly=True)
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
    # A04 M09-12: NOT stored. "Overdue" depends on the clock; a stored value
    # froze at the last write (the deadline passed and the flag stayed False).
    is_submission_overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_overdue",
        search="_search_overdue",
        help="True if the claim is still unsubmitted past its submission deadline",
    )
    overdue_escalated_at = fields.Datetime(string="Overdue Escalated On", readonly=True, copy=False)
    # --- T08: remittance reconciliation --------------------------------
    remittance_amount = fields.Monetary(
        string="Remitted", currency_field="currency_id", readonly=True, copy=False
    )
    remittance_ref = fields.Char(string="Bank Reference", readonly=True, copy=False)
    remitted_at = fields.Datetime(readonly=True, copy=False)
    remitted_by_id = fields.Many2one(
        "res.users", string="Remittance Recorded By", readonly=True, copy=False
    )
    remittance_mismatch = fields.Boolean(
        string="Remittance Mismatch",
        readonly=True,
        copy=False,
        help="T08: what arrived differs from the approved amount — flagged, never adjusted",
    )
    remittance_advice_amount = fields.Monetary(
        string="Brand Remittance Advice",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="What the brand says it paid (P08 API). Not money until a Claim Decision "
        "Officer records the bank receipt.",
    )
    remittance_advice_ref = fields.Char(string="Brand Advice Reference", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_amount",
            "submitted_at",
            "submitted_by_id",
            "decided_at",
            "decided_by_id",
            "decision_source",
            "rejection_reason",
            "proposed_decision",
            "proposed_amount",
            "proposed_reason",
            "oem_reference",
            "decision_proposed_by_id",
            "job_completed_at",
            "submission_deadline",
            "created_at",
            "overdue_escalated_at",
            "remittance_amount",
            "remittance_ref",
            "remitted_at",
            "remitted_by_id",
            "remittance_mismatch",
            "remittance_advice_amount",
            "remittance_advice_ref",
        }

    def _fix_frozen_fields(self) -> set:
        """What a user may no longer change on THIS claim."""
        self.ensure_one()
        frozen = set(_FIXED_AT_CREATE)
        if self.state not in OPEN_STATES:
            frozen |= _FROZEN_ONCE_SUBMITTED
        if self.state in FINAL_STATES:
            frozen |= {
                name
                for name, field in self._fields.items()
                if field.store and not name.startswith(_FREEZE_EXEMPT_PREFIXES)
            }
        return frozen

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= self._fix_frozen_fields()
        return locked

    # ---- creation: a closed warranty job, for the approved estimate ----------

    @api.model
    def _approved_estimate_amount(self, order) -> float:
        """A02 audit M01-W2: the APPROVED estimate's total, not the first
        estimate in any state (a draft or rejected quote)."""
        est = order._fix_governing_estimate().filtered(lambda e: e.state == "approved")
        return est.grand_total if est else 0.0

    @api.model
    def _check_origin(self, order, states):
        if not order.exists():
            raise ValidationError("A warranty claim needs the service order it recovers.")
        if order.order_category != "warranty":
            raise ValidationError(
                "Order %s is a %s job: only a warranty job is claimed from the OEM (a "
                "customer-paid job claimed again from the brand is double recovery)."
                % (order.name, order.order_category or "non-warranty")
            )
        if order.state not in states:
            raise ValidationError(
                "Order %s is %s: an OEM claim recovers a closed warranty job."
                % (order.name, dict(order._fields["state"].selection).get(order.state))
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not self.env.su:
                # A04 M09-5 / C6: a user raises a claim only from a CLOSED
                # warranty job, and only for its approved estimate.
                _assert_role(self.env, CLERK_GROUP, "Raising a warranty claim")
                order = self.env["fix.service.order"].sudo().browse(vals.get("service_order_id"))
                self._check_origin(order, CLAIM_ORDER_STATES)
                amount = self._approved_estimate_amount(order)
                if amount <= 0:
                    raise ValidationError(
                        "Order %s has no approved estimate to claim: the claim amount is the "
                        "approved warranty estimate." % order.name
                    )
                typed = vals.get("claim_amount")
                if typed not in (None, False) and abs(float(typed) - amount) > 0.005:
                    raise ValidationError(
                        "The claim amount is the approved warranty estimate of %s (%.2f), "
                        "not a typed figure (%.2f)." % (order.name, amount, float(typed))
                    )
                vals["claim_amount"] = amount
            if not vals.get("claim_no"):
                # data/ir_sequence.xml; the fallback stays unique (it used to be
                # "CLM/<today>": the second claim of a day hit UNIQUE (claim_no))
                vals["claim_no"] = self.env["ir.sequence"].next_by_code("fix.warranty.claim") or (
                    "CLM/%s/%s" % (fields.Date.context_today(self), uuid.uuid4().hex[:8].upper())
                )
        # WTY-06: submission window default 72h from creation (G4-01). The
        # timestamps are system-set (guarded), so they are stamped in-process.
        now = fields.Datetime.now()
        stamps = []
        for vals in vals_list:
            stamps.append(
                {
                    key: value
                    for key, value in (
                        ("created_at", now),
                        ("submission_deadline", now + timedelta(hours=72)),
                        ("job_completed_at", now),
                    )
                    if not vals.get(key)
                }
            )
        claims = super().create(vals_list)
        for claim, stamp in zip(claims, stamps, strict=True):
            if stamp:
                claim._guarded().write(stamp)
        return claims

    def write(self, vals):
        if self and not self._fix_guard_open():
            names = set(vals)
            for claim in self:
                changed = {
                    n
                    for n in names & claim._fix_frozen_fields()
                    if n in claim._fields and claim._fix_guard_differs(n, vals[n], claim[n])
                }
                if changed:
                    labels = ", ".join(sorted(claim._fields[n].string or n for n in changed))
                    if claim.state in FINAL_STATES:
                        why = "the claim is %s and frozen" % claim.state
                    elif changed & _FIXED_AT_CREATE:
                        why = (
                            "the amount is the job's approved estimate and the job is fixed "
                            "when the claim is raised (Refresh Amount re-reads the estimate)"
                        )
                    else:
                        why = "the claim has been submitted to the brand"
                    raise UserError(
                        "%s cannot be changed on %s: %s." % (labels, claim.claim_no, why)
                    )
        return super().write(vals)

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

    @api.depends("submission_deadline", "state")
    def _compute_overdue(self):
        now = fields.Datetime.now()
        for claim in self:
            claim.is_submission_overdue = bool(
                claim.state in OPEN_STATES
                and claim.submission_deadline
                and now > claim.submission_deadline
            )

    def _search_overdue(self, operator, value):
        """The domain twin of _compute_overdue, evaluated at search time.
        Only `in` is implemented; Odoo derives `not in` / `=` / `!=` from it."""
        if operator != "in":
            return NotImplemented
        late = (
            Domain("state", "in", list(OPEN_STATES))
            & Domain("submission_deadline", "!=", False)
            & Domain("submission_deadline", "<", fields.Datetime.now())
        )
        return Domain.OR(late if flag else ~late for flag in value)

    @api.depends(
        "evidence_ids.requirement_key",
        "evidence_ids.document_id",
        "evidence_ids.evidence_hash",
    )
    def _compute_evidence(self):
        """T05: the BLOCKING completeness check — a claim cannot be
        submitted with an incomplete pack. An item counts when it carries a
        document AND a hash (A04 M09-6: the checksum is the evidence)."""
        for claim in self:
            present = {
                e.requirement_key for e in claim.evidence_ids if e.document_id and e.evidence_hash
            }
            missing = [label for key, label in EVIDENCE_REQUIREMENTS if key not in present]
            claim.evidence_complete = not missing
            claim.missing_evidence = ", ".join(missing) if missing else False

    def _evidence_defects(self) -> list:
        """A04 M09-6: one document reused for every item passed the pack. Each
        requirement needs exactly one item, and no two items may carry the
        same document or the same file (checksum)."""
        self.ensure_one()
        defects = []
        labels = dict(EVIDENCE_REQUIREMENTS)
        by_key = {}
        for ev in self.evidence_ids:
            by_key.setdefault(ev.requirement_key, []).append(ev)
        for key, rows in by_key.items():
            if len(rows) > 1:
                defects.append("%s is given %d times" % (labels.get(key, key), len(rows)))
        seen_doc, seen_hash = {}, {}
        for ev in self.evidence_ids.filtered("document_id"):
            label = labels.get(ev.requirement_key, ev.requirement_key)
            if ev.document_id.id in seen_doc:
                defects.append(
                    "%s and %s are the same document" % (seen_doc[ev.document_id.id], label)
                )
            elif ev.evidence_hash and ev.evidence_hash in seen_hash:
                defects.append(
                    "%s and %s are the same file (SHA-256)" % (seen_hash[ev.evidence_hash], label)
                )
            seen_doc.setdefault(ev.document_id.id, label)
            if ev.evidence_hash:
                seen_hash.setdefault(ev.evidence_hash, label)
        return defects

    def action_assemble_workshop_evidence_pack(self):
        """T05 / R03-M02: Assembles evidence pack drawing from workshop repair records."""
        Evidence = self.env["fix.warranty.evidence"]
        for claim in self:
            _assert_role(self.env, CLERK_GROUP, "Assembling a claim's evidence pack")
            if claim.state not in OPEN_STATES:
                raise UserError(
                    "Claim %s is %s: the evidence pack is locked once submitted."
                    % (claim.claim_no, claim.state)
                )
            # service_order_id is required (ondelete restrict): every claim has an
            # order, and fix.document is always installed (cd_document_core is a
            # manifest dependency) - the former guards for both were dead code.
            order = claim.service_order_id
            existing_keys = {e.requirement_key for e in claim.evidence_ids}
            used = set(claim.evidence_ids.mapped("document_id").ids)
            for key, _label in EVIDENCE_REQUIREMENTS:
                if key in existing_keys:
                    continue
                if key == "parts_issued":
                    # A04 ERP M09-F13: the parts evidence is the M15 issue record
                    # of a part issued to THIS job, never a file whose name
                    # happens to contain "parts_issued".
                    doc = claim._fix_parts_issue_document(exclude=used)
                    if doc:
                        used.add(doc.id)
                        Evidence.create(
                            {"claim_id": claim.id, "requirement_key": key, "document_id": doc.id}
                        )
                    continue
                # In production, resolves from order.document_ids or workshop inspection;
                # a document already used for another item is never reused (M09-6).
                doc = (
                    self.env["fix.document"]
                    .sudo()
                    .search(
                        [
                            ("res_model", "=", "fix.service.order"),
                            ("res_id", "=", order.id),
                            ("name", "ilike", key),
                            ("id", "not in", list(used)),
                        ],
                        limit=1,
                    )
                )
                if doc:
                    used.add(doc.id)
                    Evidence.create(
                        {"claim_id": claim.id, "requirement_key": key, "document_id": doc.id}
                    )
            claim._compute_evidence()
            if claim.evidence_complete and claim.state == "draft":
                claim._guarded().write({"state": "ready"})
        return True

    def _fix_parts_issue_document(self, exclude=()):
        """Hook (A04 ERP M09-F13, fix_a04_r2_claims): the M15 parts-issue
        document of this claim's job; empty when nothing was issued."""
        return self.env["fix.document"]

    def action_refresh_amount(self):
        """Re-read the job's approved estimate while the claim is a draft."""
        for claim in self:
            _assert_role(self.env, CLERK_GROUP, "Refreshing a claim amount")
            if claim.state not in OPEN_STATES:
                raise UserError(
                    "Claim %s is %s: its amount is fixed." % (claim.claim_no, claim.state)
                )
            amount = self._approved_estimate_amount(claim.service_order_id.sudo())
            if amount <= 0:
                raise UserError(
                    "Order %s has no approved estimate to claim." % claim.service_order_id.name
                )
            claim._guarded().write({"claim_amount": amount})
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
        Airflow workflow's trigger window; the creation here is immediate.

        A04 M09-5: only a job M01 is closing (delivered) or has closed raises
        a claim; a draft job raised a 0.0 claim. The intake is a system
        service: M01 and the cron call it as superuser."""
        payload = event.get("payload", {}) or {}
        Order = self.env["fix.service.order"].sudo()
        order_id = event.get("aggregate_id")
        order = Order.browse(order_id).exists() if order_id else Order
        if not order or order.order_category != "warranty":
            return None
        if order.state not in AUTO_CLAIM_ORDER_STATES:
            return None
        existing = self.sudo().search([("service_order_id", "=", order.id)])
        if existing:
            return existing
        if not self.env.su:
            raise AccessError(
                "AUT-018 claim intake is a system service (the M01 close, the intake cron)."
            )
        completed_time = payload.get("completed_at") or fields.Datetime.now()
        claim = self.create(
            {
                # required on the claim; an order's own OU is optional, its
                # branch's is not (the auto-create failed NOT NULL without it)
                "operating_unit_id": (
                    order.operating_unit_id or order.branch_id.operating_unit_id
                ).id,
                "service_order_id": order.id,
                "brand_id": order.device_id.brand_id.id,
                # 0.0 when the job has no approved estimate: the claim exists
                # (the M01 close gate needs it) but cannot be submitted until
                # Refresh Amount finds an approved estimate.
                "claim_amount": self._approved_estimate_amount(order),
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
                "order_id": order.id,
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
        per-order search — replays are free.

        A02 ERP pass 2 X5-22: the search always took the OLDEST 500 events,
        so once 500 had been seen the intake re-read them every hour and
        never reached a newer close. It now reads on from a cursor (the last
        outbox id it walked, a system parameter), 500 at a time.

        The cursor is a low-water mark, not "the last row read": it moves
        only over a contiguous run of events that are handled (claimed or
        skipped; a failure is retried on later runs and given up, with an
        error in the log, after AUT018_MAX_ATTEMPTS) and older than the lag
        (cd_warranty_claims.aut018_cursor_lag_minutes, default 10), because
        an outbox id is taken before its transaction commits: a lower id can
        become visible after a higher one. Events past the mark are still
        processed every run; re-reading them is free (one claim per order)."""
        outbox = self.env["fix.event.outbox"].sudo()
        params = self.env["ir.config_parameter"].sudo()
        try:
            cursor = int(params.get_param(AUT018_CURSOR_PARAM) or 0)
        except ValueError:
            cursor = 0
        try:
            lag = float(params.get_param(AUT018_LAG_PARAM) or AUT018_LAG_DEFAULT)
        except ValueError:
            lag = AUT018_LAG_DEFAULT
        aged_before = fields.Datetime.now() - timedelta(minutes=lag)
        try:
            failures = json.loads(params.get_param(AUT018_FAILURES_PARAM) or "{}")
        except ValueError:
            failures = {}
        events = outbox.search(
            [
                ("event_type", "=", "service_order.closed"),
                ("aggregate", "=", "fix.service.order"),
                ("id", ">", cursor),
            ],
            order="id asc",
            limit=AUT018_BATCH,
        )
        created = 0
        new_cursor, advancing = cursor, True
        for evt in events:
            handled = True
            try:
                with self.env.cr.savepoint():
                    # consume_order_completed returns the EXISTING claim on a
                    # replay — only genuinely new claims count as created
                    if not self.search([("service_order_id", "=", evt.aggregate_id)]):
                        claim = self.consume_order_completed(
                            {
                                "aggregate_id": evt.aggregate_id,
                                "payload": {"completed_at": evt.create_date},
                            }
                        )
                        if claim:
                            created += 1
                failures.pop(str(evt.id), None)
            except Exception:
                attempts = int(failures.get(str(evt.id), 0)) + 1
                failures[str(evt.id)] = attempts
                if attempts >= AUT018_MAX_ATTEMPTS:
                    failures.pop(str(evt.id), None)
                    logger.error(
                        "AUT-018 intake gave up on outbox event %s (order %s) after %d attempts",
                        evt.event_id,
                        evt.aggregate_id,
                        attempts,
                        exc_info=True,
                    )
                else:
                    handled = False
                    logger.warning(
                        "AUT-018 intake failed on outbox event %s (order %s), attempt %d: "
                        "retried on the next run",
                        evt.event_id,
                        evt.aggregate_id,
                        attempts,
                        exc_info=True,
                    )
            advancing = advancing and handled and evt.create_date <= aged_before
            if advancing:
                new_cursor = evt.id
        if new_cursor != cursor:
            params.set_param(AUT018_CURSOR_PARAM, str(new_cursor))
        params.set_param(AUT018_FAILURES_PARAM, json.dumps(failures, sort_keys=True))
        if created:
            logger.info("AUT-018 intake created %d warranty claim(s)", created)
        return created

    @api.model
    def cron_claim_overdue_escalation(self) -> int:
        """C10 (A04 M09-12/-13): a claim still unsubmitted past its 72h window
        was only ever noticed if someone submitted it late. Each overdue
        claim is escalated once: a chatter note and a to-do for the person
        who raised it. Idempotent through overdue_escalated_at."""
        claims = self.sudo().search(
            [("is_submission_overdue", "=", True), ("overdue_escalated_at", "=", False)],
            limit=500,
        )
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        now = fields.Datetime.now()
        for claim in claims:
            claim.message_post(
                body="Claim overdue: not submitted by its deadline %s (G4-01 72h window)."
                % claim.submission_deadline
            )
            user = claim.create_uid
            if todo and user and user.active and not user.share:
                claim.activity_schedule(
                    activity_type_id=todo.id,
                    summary="Overdue warranty claim %s" % claim.claim_no,
                    user_id=user.id,
                )
            claim._guarded().write({"overdue_escalated_at": now})
        return len(claims)

    # --- Submission with the blocking gate ------------------------------

    def _product_rule_defects(self, amount) -> list:
        """WTY-12 waiting period and WTY-14 aggregate limit (A04 M09-7): both
        were declared on the product and never read."""
        self.ensure_one()
        product = self.warranty_product_id
        if not product:
            return []
        defects = []
        order = self.service_order_id.sudo()
        arose = (order.create_date or fields.Datetime.now()).date()
        if product.waiting_days:
            cover = (
                self.env["fix.warranty"]
                .sudo()
                .search(
                    [("device_id", "=", self.device_id.id), ("start_date", "<=", arose)],
                    order="start_date desc",
                    limit=1,
                )
            )
            if not cover:
                defects.append(
                    "%s has a %d-day waiting period and the device has no cover start on "
                    "record to measure it from" % (product.name, product.waiting_days)
                )
            elif (arose - cover.start_date).days < product.waiting_days:
                defects.append(
                    "the fault arose on %s, %d day(s) into the cover that started %s, inside "
                    "%s's %d-day waiting period (WTY-12)"
                    % (
                        arose,
                        (arose - cover.start_date).days,
                        cover.start_date,
                        product.name,
                        product.waiting_days,
                    )
                )
        if product.claim_limit:
            used = sum(
                self.sudo()
                .search(
                    [
                        ("id", "!=", self.id),
                        ("device_id", "=", self.device_id.id),
                        ("warranty_product_id", "=", product.id),
                        ("state", "in", list(SETTLED_STATES)),
                    ]
                )
                .mapped("approved_amount")
            )
            if used + amount > product.claim_limit + 0.005:
                defects.append(
                    "%.2f on top of %.2f already settled exceeds %s's aggregate claim limit "
                    "of %.2f (WTY-14)" % (amount, used, product.name, product.claim_limit)
                )
        return defects

    def action_submit(self):
        """T05: the completeness check blocks submission. BRU-WTY-04: a
        claim cannot be submitted until it passes the brand's rule set —
        the evidence pack IS that rule set's local half."""
        for claim in self:
            if claim.state not in OPEN_STATES:
                raise UserError("Only a draft/ready claim submits")
            if not claim.evidence_complete:
                raise UserError(
                    "Claim %s cannot be submitted — missing evidence: %s "
                    "(an incomplete claim is a rejected claim)"
                    % (claim.claim_no, claim.missing_evidence)
                )
            _assert_role(self.env, CLERK_GROUP, "Submitting a warranty claim")
            defects = claim._evidence_defects()
            if defects:
                raise UserError(
                    "Claim %s cannot be submitted: each evidence item needs its own document "
                    "(%s)." % (claim.claim_no, "; ".join(defects))
                )
            if claim.claim_amount <= 0:
                raise UserError(
                    "Claim %s claims nothing: its order has no approved estimate (Refresh "
                    "Amount once the estimate is approved)." % claim.claim_no
                )
            defects = claim._product_rule_defects(claim.claim_amount)
            if defects:
                raise UserError(
                    "Claim %s cannot be submitted: %s." % (claim.claim_no, "; ".join(defects))
                )
            now = fields.Datetime.now()
            if claim.submission_deadline and now > claim.submission_deadline:
                claim.message_post(
                    body="Warning: Claim submitted past 72h deadline (escalated for brand acceptance)"
                )
            claim._guarded().write(
                {"state": "submitted", "submitted_at": now, "submitted_by_id": self.env.uid}
            )
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
            _assert_role(self.env, CLERK_GROUP, "Marking a claim in review")
            if claim.state != "submitted":
                raise UserError("Only a submitted claim goes into review")
            claim._guarded().write({"state": "in_review"})

    # --- The OEM decision -------------------------------------------------

    def _approval_amount(self) -> float:
        return abs(self.proposed_amount or 0.0)

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.state in RECEIVED_STATES and bool(self.proposed_decision)

    def _approval_pinned_fields(self) -> set:
        # The decision covers the claim it was keyed for.
        return super()._approval_pinned_fields() | {
            "proposed_decision",
            "brand_id",
            "claim_amount",
            "service_order_id",
        }

    def _approval_excluded(self):
        """The submitter and the person who keyed the decision never record
        it (four eyes), on top of the requester, creator and amount changer."""
        excluded = super()._approval_excluded()
        return excluded | (self.submitted_by_id | self.decision_proposed_by_id).sudo()

    def _check_decision_terms(self, decision, amount, reason):
        """The approved amount a decision stands for: the requested amount
        in full, a part of it (partial, with a reason) or nothing (reject,
        with the OEM's reason)."""
        self.ensure_one()
        if decision not in DECISION_STATE:
            raise UserError("A decision is approve, partial or reject.")
        if decision == "approve":
            return self.claim_amount
        if decision == "partial":
            if not (0 < (amount or 0.0) < self.claim_amount):
                raise UserError(
                    "A partial approval reimburses more than 0 and less than the requested "
                    "%.2f (got %.2f)." % (self.claim_amount, amount or 0.0)
                )
            if not (reason or "").strip():
                raise UserError("Say why the OEM reimburses only part of the claim.")
            return amount
        if not (reason or "").strip():
            raise UserError("A rejection needs the OEM's reason.")
        return 0.0

    def _check_provenance(self):
        """FLAW-09.1: serial / IMEI provenance. A04 M09-2: there is no caller
        switch; a claim on a device with no serial or IMEI is not approved."""
        self.ensure_one()
        device = self.sudo().device_id
        ident = ""
        if device:
            ident = " ".join(
                (device[f] or "")
                for f in ("serial_number", "imei_1", "imei_2")
                if f in device._fields
            ).strip()
        if not ident:
            raise UserError(
                "Claim %s cannot be approved: device provenance verification failed. A valid "
                "device record with serial/IMEI is required." % self.claim_no
            )

    def action_propose_decision(
        self, decision, approved_amount=None, reason=None, oem_reference=None
    ):
        """Key the OEM's answer (approve / partial / reject) and send it to a
        Claim Decision Officer's inbox. Nothing is decided until the officer
        records it."""
        for claim in self:
            _assert_role(self.env, CLERK_GROUP, "Keying an OEM decision")
            if claim.state not in RECEIVED_STATES:
                raise UserError(
                    "Claim %s is %s — only a submitted or in-review claim can be decided"
                    % (claim.claim_no, claim.state)
                )
            if claim.approval_state == "pending":
                raise UserError(
                    "Claim %s already has a decision awaiting the officer; recall it first."
                    % claim.claim_no
                )
            amount = claim._check_decision_terms(decision, approved_amount, reason)
            if decision != "reject":
                defects = claim._product_rule_defects(amount)
                if defects:
                    raise UserError(
                        "Claim %s cannot be approved: %s." % (claim.claim_no, "; ".join(defects))
                    )
            claim._guarded().write(
                {
                    "proposed_decision": decision,
                    "proposed_amount": amount,
                    "proposed_reason": (reason or "").strip() or False,
                    "oem_reference": (oem_reference or "").strip() or False,
                    "decision_proposed_by_id": self.env.uid,
                }
            )
            claim.action_request_approval(
                justification="OEM decision: %s, %.2f of %.2f%s"
                % (
                    dict(DECISIONS)[decision],
                    amount,
                    claim.claim_amount,
                    (" (%s)" % reason) if reason else "",
                )
            )
        return True

    def action_propose_approve(self, oem_reference=None):
        return self.action_propose_decision("approve", oem_reference=oem_reference)

    def action_propose_partial(self, approved_amount=None, reason=None):
        try:
            amount = float(approved_amount or 0.0)
        except (TypeError, ValueError) as exc:
            raise UserError("The approved amount must be a number.") from exc
        return self.action_propose_decision(
            "partial",
            approved_amount=amount,
            reason=reason or "Partial reimbursement by the OEM",
        )

    def action_propose_reject(self, reason=None):
        return self.action_propose_decision("reject", reason=reason)

    def action_apply_decision(self):
        """The M63 apply method: a Claim Decision Officer records the keyed
        OEM decision from his inbox. A direct press is refused (routed)."""
        self._approval_assert_routed()
        trusted = self.env.su and not self._approval_task()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for claim in self:
            if claim.state not in RECEIVED_STATES:
                raise UserError(
                    "Claim %s is %s — only a submitted or in-review claim can be decided"
                    % (claim.claim_no, claim.state)
                )
            if not claim.proposed_decision:
                raise UserError("Claim %s has no keyed decision." % claim.claim_no)
            if not trusted:
                if not authority.has_group(OFFICER_GROUP):
                    raise UserError(
                        "The OEM decision is recorded by a Claim Decision Officer, which %s "
                        "is not." % authority.name
                    )
                if acting & (
                    claim.submitted_by_id | claim.decision_proposed_by_id | claim.create_uid
                ):
                    raise UserError(
                        "Segregation of duties: whoever raised, submitted or keyed claim %s "
                        "does not record its decision." % claim.claim_no
                    )
            claim._apply_decision(
                claim.proposed_decision,
                claim.proposed_amount,
                claim.proposed_reason,
                source="officer",
                decided_by=self.env.user,
                oem_reference=claim.oem_reference,
            )
        return True

    def _approval_on_rejected(self, comment):
        # Runs after the request is closed (approval_state 'rejected'), so
        # clearing the keyed terms voids nothing.
        for claim in self.filtered("proposed_decision"):
            claim.sudo()._guarded().write(
                {
                    "proposed_decision": False,
                    "proposed_amount": 0.0,
                    "proposed_reason": False,
                    "decision_proposed_by_id": False,
                }
            )
            claim.sudo().message_post(
                body="The keyed OEM decision was sent back by the officer: %s" % (comment or "-")
            )

    def action_decide(
        self, approved: bool, reason: str = "", approved_amount=None, decided_by_id=None
    ):
        """The brand's own decision (P08 brand API, as superuser). A user
        never decides here: the OEM decision keyed in-house is proposed
        (Propose Decision) and recorded by a Claim Decision Officer from the
        approval inbox (A04 M09-2). Only a claim the brand has received
        (submitted / in review) can be decided: a draft was never sent and a
        decided or remitted claim is final (a late webhook must not reopen a
        remitted claim)."""
        if not self.env.su:
            raise UserError(
                "The OEM decision is recorded by a Claim Decision Officer: key it with "
                "Propose Decision and it is approved from the officer's inbox."
            )
        decided_by = self.env["res.users"].browse(decided_by_id or []).exists() or self.env.user
        for claim in self:
            if claim.state not in RECEIVED_STATES:
                raise UserError(
                    "Claim %s is %s — only a submitted or in-review claim can be decided"
                    % (claim.claim_no, claim.state)
                )
            if not approved:
                decision = "reject"
                reason = reason or "Rejected by the brand"
            elif approved_amount not in (None, False) and (
                float(approved_amount) < claim.claim_amount - 0.005
            ):
                decision = "partial"
                reason = reason or "Partial reimbursement by the brand"
            else:
                decision = "approve"
            amount = claim._check_decision_terms(decision, float(approved_amount or 0.0), reason)
            claim._apply_decision(decision, amount, reason, "brand_api", decided_by)

    def _apply_decision(self, decision, amount, reason, source, decided_by, oem_reference=None):
        self.ensure_one()
        if decision != "reject":
            self._check_provenance()
        now = fields.Datetime.now()
        # The keyed terms stay as they are: the approval being granted is
        # pinned to them (clearing them here would void it mid-decision).
        self._guarded().write(
            {
                "state": DECISION_STATE[decision],
                "approved_amount": amount,
                "decided_at": now,
                "decided_by_id": decided_by.id,
                "decision_source": source,
                "rejection_reason": (reason or False) if decision == "reject" else False,
            }
        )
        self.env["fix.warranty.claim.decision"].sudo().create(
            {
                "claim_id": self.id,
                "decision": decision,
                "requested_amount": self.claim_amount,
                "approved_amount": amount,
                "reason": reason or False,
                "oem_reference": oem_reference or False,
                "source": source,
                "decided_by_id": decided_by.id,
                "proposed_by_id": self.decision_proposed_by_id.id or False,
                "decided_at": now,
            }
        )
        publish(
            self.env,
            "warranty_claim.decided",
            "fix.warranty.claim",
            self.id,
            {
                "claim_no": self.claim_no,
                "approved": decision != "reject",
                "decision": decision,
                "requested_amount": self.claim_amount,
                "approved_amount": amount,
                "brand_id": self.brand_id.id,
                "company_id": self.company_id.id,
                "currency": self.currency_id.name or "BDT",
                "source": source,
            },
        )

    # --- T08: remittance reconciliation --------------------------------

    def action_record_remittance(self, amount: float, bank_ref: str):
        """WTY reconciliation: match the money RECEIVED to the approved
        amount. A mismatch is FLAGGED, never auto-adjusted (T08). A04 M09-4:
        the brand attested its own remittance; the receipt is now recorded
        in-house by a Claim Decision Officer against a bank reference, and a
        short payment leaves the claim open and flagged (it is chased, not
        settled)."""
        for claim in self:
            _assert_role(self.env, OFFICER_GROUP, "Recording an OEM remittance")
            if claim.state not in RECOVERY_STATES:
                raise UserError("Only an approved claim takes a remittance")
            if not (bank_ref or "").strip():
                raise UserError("A remittance needs the bank reference it arrived under.")
            try:
                received = float(amount)
            except (TypeError, ValueError) as exc:
                raise UserError("The remitted amount must be a number.") from exc
            if received <= 0:
                raise UserError("A remittance is a positive amount received.")
            total = (claim.remittance_amount or 0.0) + received
            expected = claim.approved_amount or 0.0
            mismatch = abs(total - expected) > 0.01
            settled = total + 0.01 >= expected
            vals = {
                "remittance_amount": total,
                "remittance_ref": ", ".join(r for r in (claim.remittance_ref, bank_ref) if r),
                "remitted_at": fields.Datetime.now(),
                "remitted_by_id": self.env.uid,
                "remittance_mismatch": mismatch,
            }
            if settled:
                vals["state"] = "remitted"
            claim._guarded().write(vals)
            publish(
                self.env,
                "warranty_claim.remitted",
                "fix.warranty.claim",
                claim.id,
                {
                    "claim_no": claim.claim_no,
                    "bank_ref": bank_ref,
                    "expected": expected,
                    "received": received,
                    "received_total": total,
                    "mismatch": mismatch,
                    "settled": settled,
                },
            )
        return True

    def action_record_remittance_advice(self, amount, bank_ref):
        """The brand's remittance advice (P08 API): noted for the officer,
        never itself money received."""
        for claim in self:
            _assert_role(self.env, CLERK_GROUP, "Noting a brand remittance advice")
            if claim.state not in (*RECOVERY_STATES, "remitted"):
                raise UserError("Only an approved claim takes a remittance")
            advised = float(amount or 0.0)
            claim._guarded().write(
                {"remittance_advice_amount": advised, "remittance_advice_ref": bank_ref or False}
            )
            claim.message_post(
                body="Brand remittance advice: %.2f under %s (approved %.2f). Record the bank "
                "receipt to settle the claim." % (advised, bank_ref or "-", claim.approved_amount)
            )
        return True

    def _oem_invoice(self):
        """The M20 receivable raised on the brand for this claim (the
        warranty_claim.decided hand-off in cd_billing_engine), not cancelled.
        cd_billing_engine depends on this module, so the model is reached by
        name; without it there is no receivable model at all."""
        self.ensure_one()
        if "fix.ar.invoice" not in self.env:
            return None
        # A04 ERP M09-F7: a re-decision after an appeal may raise a
        # supplementary invoice on the decision record; the open one (money
        # still owed) is the receivable a remittance is collected against.
        invoices = (
            self.env["fix.ar.invoice"]
            .sudo()
            .search(
                [
                    "|",
                    "&",
                    ("source_model", "=", self._name),
                    ("source_id", "=", self.id),
                    "&",
                    ("source_model", "=", "fix.warranty.claim.decision"),
                    ("source_id", "in", self.decision_ids.ids or [0]),
                    ("state", "!=", "cancelled"),
                ],
                order="id",
            )
        )
        open_ = invoices.filtered(
            lambda i: i.state == "issued" and (i.amount_residual or 0.0) > 0.005
        )
        return (open_ or invoices)[:1]

    def _check_receivable_raised(self):
        """E3-07: a claim the brand agreed to pay is closed only once the
        receivable on the brand exists. Recording a remittance posts nothing
        to the ledger, so a claim could be remitted and closed with the money
        never owed in the books. A rejection, or an approval of nothing, has
        no money leg and closes as before."""
        self.ensure_one()
        if (self.approved_amount or 0.0) <= 0.005:
            return
        if self._oem_invoice():
            return
        raise UserError(
            "Claim %s was approved for %.2f but no OEM invoice was ever raised on the brand "
            "(M20, source %s). Raise and issue the brand's invoice first — the remittance is "
            "collected against it — then close the claim."
            % (self.claim_no, self.approved_amount, self._name)
        )

    def action_close(self):
        """Close a settled claim, or a rejected one with no open appeal. A
        claim with an approved amount closes only once its OEM invoice exists
        (E3-07)."""
        for claim in self:
            _assert_role(self.env, OFFICER_GROUP, "Closing a warranty claim")
            open_appeal = claim.appeal_ids.filtered(lambda a: a.decision == "pending")
            if claim.state == "remitted" or (claim.state == "rejected" and not open_appeal):
                claim._check_receivable_raised()
                claim._guarded().write({"state": "closed"})
            else:
                raise UserError(
                    "Claim %s is %s: a remitted claim, or a rejected claim with no open "
                    "appeal, is closed." % (claim.claim_no, claim.state)
                )
        return True

    def _reopen_for_appeal(self, appeal):
        """An upheld appeal sends the claim back to the OEM (re-submitted).
        The earlier decision stays in the decision history."""
        self.ensure_one()
        # A system consequence of the appeal decision, so the upholding
        # officer is not recorded as having moved the claim's terms.
        self.sudo()._guarded().write(
            {
                "approval_state": "none",
                "state": "submitted",
                "submitted_at": fields.Datetime.now(),
                "approved_amount": 0.0,
                "rejection_reason": False,
                "decided_at": False,
                "decided_by_id": False,
                "decision_source": False,
                "proposed_decision": False,
                "proposed_amount": 0.0,
                "proposed_reason": False,
                "oem_reference": False,
                "decision_proposed_by_id": False,
            }
        )
        self.sudo().message_post(
            body="Appeal %s upheld: claim re-submitted to the brand." % appeal.name
        )


class FixWarrantyClaimDecision(models.Model):
    """A04 P2 (M09): requested vs reimbursed, version by version. One row per
    decision recorded on a claim (an upheld appeal re-opens it, so a claim
    can have several); rows are written by the decision path, never edited."""

    _name = "fix.warranty.claim.decision"
    _description = "Warranty Claim Decision"
    _order = "decided_at desc, id desc"

    claim_id = fields.Many2one(
        "fix.warranty.claim", required=True, ondelete="cascade", index=True, readonly=True
    )
    currency_id = fields.Many2one(related="claim_id.currency_id")
    decision = fields.Selection(DECISIONS, required=True, readonly=True)
    requested_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    approved_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    reason = fields.Char(readonly=True)
    oem_reference = fields.Char(string="OEM Reference", readonly=True)
    source = fields.Selection(
        [("officer", "Claim Decision Officer"), ("brand_api", "Brand Partner API")],
        readonly=True,
    )
    proposed_by_id = fields.Many2one("res.users", string="Keyed By", readonly=True)
    decided_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)
    decided_at = fields.Datetime(readonly=True)

    def write(self, vals):
        if not self.env.su:
            raise UserError("A recorded claim decision cannot be edited.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A recorded claim decision cannot be deleted.")
        return super().unlink()


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
    evidence_hash = fields.Char(
        string="Evidence Hash",
        compute="_compute_evidence_hash",
        store=True,
        help="The SHA-256 of the evidence: the uploaded file's, else the document's "
        "repository checksum (M24), else its stored file's. An item without one is not "
        "evidence.",
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

    @api.depends(
        "sha256_hash",
        "document_id",
        "document_id.checksum_sha256",
        "document_id.attachment_id",
        "document_id.attachment_id.datas",
    )
    def _compute_evidence_hash(self):
        for rec in self:
            doc = rec.sudo().document_id
            digest = rec.sha256_hash or doc.checksum_sha256 or False
            if not digest and doc.attachment_id.datas:
                # the repository checksum is only stamped on the Mayan sync;
                # the stored file itself is the evidence until then
                try:
                    digest = hashlib.sha256(base64.b64decode(doc.attachment_id.datas)).hexdigest()
                except Exception:
                    digest = False
            rec.evidence_hash = digest

    def _assert_pack_open(self, claims):
        """A04 M09-6: evidence was deletable after submission. The pack is
        locked once the claim has gone to the brand."""
        if self.env.su:
            return
        locked = claims.filtered(lambda c: c.state not in OPEN_STATES)
        if locked:
            raise UserError(
                "The evidence pack of %s is locked: the claim has been submitted."
                % ", ".join(locked.mapped("claim_no"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        claims = self.env["fix.warranty.claim"].browse(
            [v["claim_id"] for v in vals_list if v.get("claim_id")]
        )
        self._assert_pack_open(claims)
        return super().create(vals_list)

    def write(self, vals):
        self._assert_pack_open(self.mapped("claim_id"))
        if vals.get("claim_id"):
            self._assert_pack_open(self.env["fix.warranty.claim"].browse(vals["claim_id"]))
        return super().write(vals)

    def unlink(self):
        self._assert_pack_open(self.mapped("claim_id"))
        return super().unlink()


class FixApprovalMatrixWarrantyClaim(models.Model):
    """A04 C9: lets a DoA matrix row target the routed claim decision."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("warranty_claim_decision", "Warranty Claim OEM Decision")],
        ondelete={"warranty_claim_decision": "cascade"},
    )
