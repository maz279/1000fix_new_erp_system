# M36 quotations: the versioned customer quotation over an estimate and its
# internal review log. Estimates and counter-sales already exist in
# cd_service_order / cd_quotation; tenders and bonds are in fix_tender.py.
#
# A04 workflow audit (2026-11-03, M36-1/6/10/11/12) and the C2-C13 build
# (2026-11-04): fix.quotation had no transition method at all. A clerk wrote
# esign_state='signed' and state='accepted' on a draft quote, back-dated
# signed_at, accepted an expired quote, recorded an "approved" review in a
# director's name, quoted BDT 1 on a BDT 3,450 estimate and read a 100% margin
# with no cost. The lifecycle is now (spec §8.2):
#
#   draft --submit--> [M63 approval, value band, approver != author]
#         --approved--> approved --send--> sent
#   sent --accept (customer OTP / provider e-signature / signed form recorded
#          by someone else, within validity)--> accepted --> converted into the
#          M01 order or an M08 contract
#   sent --decline (governed reason)--> declined;  sent --(cron)--> expired
#   sent/expired/declined --revise--> a new version (the old sent one is
#          superseded); pre-decision --cancel (reason)--> cancelled
import hashlib
import hmac
import json
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_quotation import dhaka_today

# Value bands for the internal approval (spec BRU-QTE-06/07, FR-QTE-025), on
# the quotation value. Every quotation is approved by someone other than its
# author (BRU-QTE-09); the band decides who.
#   up to BDT 25,000   -> Tier 1 (team lead / supervisor)
#   up to BDT 100,000  -> Tier 2 (Branch Manager, BRU-QTE-06)
#   above BDT 100,000  -> Tier 3 (Operations Director, BRU-QTE-07)
# The rungs are the spec's; mapping "Operations Director" to DOFA Tier 3 (the
# director tier) is a default the business must confirm (report §7.1).
QUOTE_VALUE_DOFA_THRESHOLDS = [
    (25000.0, "tier_1"),
    (100000.0, "tier_2"),
    (float("inf"), "tier_3"),
]

# What the approval covered: any change after approval needs re-approval,
# any change after issue needs a new version (BRU-QTE-02).
QUOTE_TERMS = frozenset(
    {
        "value",
        "cost_amount",
        "vat_rate",
        "tds_rate",
        "customer_id",
        "estimate_id",
        "currency_id",
        "valid_until",
        "quote_type",
        "contract_family",
        "contract_months",
        "contract_start",
        "operating_unit_id",
        # Quote-to-cash P1 (12 Nov 2026): what is quoted and on what terms.
        "discount_amount",
        "scope_digest",
        "payment_term_id",
        "payment_method_ids",
        "advance_pct",
        "delivery_terms",
        "warranty_terms",
    }
)

# Set only by the lifecycle methods.
QUOTE_STAMPS = frozenset(
    {
        "state",
        "version",
        "parent_version_id",
        "esign_state",
        "signed_at",
        "esign_provider_ref",
        "approved_snapshot",
        "approved_at",
        "sent_at",
        "accepted_at",
        "declined_at",
        "acceptance_method",
        "acceptance_ref",
        "acceptance_recorded_by",
        "accepted_value",
        "accepted_version",
        "evidence_hash",
        "decline_reason",
        "cancel_reason",
        "service_order_id",
        "converted_res_model",
        "converted_res_id",
        "converted_ref",
        "converted_at",
        "acceptance_otp_digest",
        "acceptance_otp_expires_at",
        "acceptance_otp_attempts",
        # Computed figures: create() and write() would otherwise store a typed
        # value over the compute (A04 audit q_09: margin_pct set to 45%).
        "vat_amount",
        "amount_total",
        "accepted_total",
        # P1: set from the lines, never typed
        "scope_digest",
        "lines_total",
        "list_total",
        "discount_pct",
        "advance_amount",
        "tds_amount",
        "margin_known",
        "pretax_margin_bdt",
        "net_cash_margin_bdt",
        "net_cash_margin_pct",
        "margin_pct",
    }
)

FINAL_STATES = ("accepted", "declined", "expired", "cancelled", "superseded")

# The e-signature provider signs its completion callback with this shared
# secret (HMAC-SHA256). Unset = no provider configured: an e-signature
# acceptance is then impossible, never assumed.
ESIGN_PROVIDER_PARAM = "cd_quotation.esign_provider_secret"

CONTRACT_FAMILIES = [
    ("amc", "AMC (Annual Maintenance)"),
    ("ramc", "RAMC (Repair & Maintenance)"),
    ("managed", "Managed Services"),
    ("rental", "Rental"),
    ("marketplace", "Marketplace Agreement"),
]

DECLINE_REASONS = [
    ("price", "Price too high"),
    ("scope", "Scope does not fit"),
    ("timing", "Timing / turnaround"),
    ("competitor", "Went with a competitor"),
    ("no_repair", "Customer chose not to repair"),
    ("no_response", "No response before expiry"),
    ("other", "Other"),
]


def esign_signature(secret: str, name: str, version: int, value: float, signature_ref: str) -> str:
    """The provider's HMAC over the exact version and value it had signed."""
    message = "%s|%s|%.2f|%s" % (name, int(version), value or 0.0, signature_ref or "")
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


def estimate_untaxed(estimate) -> float:
    """The estimate's chargeable amount before VAT (P0 quote-to-cash review,
    12 Nov 2026). fix.estimate.grand_total INCLUDES VAT; the quotation's
    `value` is the pre-VAT amount, the same base fix.contract and
    fix.subscription bill VAT on top of."""
    return round((estimate.grand_total or 0.0) - (estimate.vat_amount or 0.0), 2)


class FixQuotation(models.Model):
    _name = "fix.quotation"
    _description = "Quotation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "create_date desc, id desc"

    # A04 audit M36-12: numbers came from a count, reused after a delete.
    _name_version_unique = models.Constraint(
        "UNIQUE (name, version)", "A quotation number and version are unique"
    )

    _approval_domain = "quotation"
    _approval_apply_method = "action_approve_quote"
    _approval_routed = True

    name = fields.Char(required=True, copy=False, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    estimate_id = fields.Many2one("fix.estimate", string="Estimate", index=True)
    customer_id = fields.Many2one("res.partner", string="Customer", index=True, ondelete="restrict")
    quote_type = fields.Selection(
        [
            ("service", "Service order scope (M01)"),
            ("contract", "Contract (M08)"),
            ("subscription", "Subscription plan (M39)"),
        ],
        string="Converts Into",
        required=True,
        default="service",
    )
    contract_family = fields.Selection(CONTRACT_FAMILIES, default="amc")
    contract_months = fields.Integer(string="Contract Term (months)", default=12)
    contract_start = fields.Date(help="Empty: the contract starts on the day of acceptance.")
    version = fields.Integer(required=True, default=1, readonly=True, copy=False)
    parent_version_id = fields.Many2one(
        "fix.quotation", string="Previous Version", readonly=True, copy=False
    )
    # P0 quote-to-cash review (12 Nov 2026): `value` was copied from the
    # estimate's VAT-INCLUSIVE grand_total, then VAT was added again: a BDT
    # 10,000 repair (11,500 with VAT) printed "Total Payable 13,225" and was
    # invoiced at 11,500. `value` is now always the amount BEFORE VAT -- the
    # base contracts and subscriptions already bill VAT on -- and
    # amount_total is what the customer pays.
    value = fields.Monetary(
        string="Quotation Value (excl. VAT)",
        currency_field="currency_id",
        help="The quoted amount before VAT. From an estimate: its total less its VAT.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # Statutory Margin Calculation & TDS (ITA 2023 s.89/90 / FLAW-36.1)
    cost_amount = fields.Monetary(
        string="Estimated Direct Cost", currency_field="currency_id", default=0.0
    )
    vat_rate = fields.Float(string="VAT Rate (%)", default=15.0)
    vat_amount = fields.Monetary(
        string="Mushak VAT Amount",
        currency_field="currency_id",
        compute="_compute_statutory_margins",
        store=True,
    )
    amount_total = fields.Monetary(
        string="Total Payable (incl. VAT)",
        currency_field="currency_id",
        compute="_compute_statutory_margins",
        store=True,
        help="Value plus VAT: what the customer pays. TDS is withheld by the customer "
        "from its payment and is never added here.",
    )
    tds_rate = fields.Float(string="Withholding Tax TDS Rate (%)", default=5.0)
    tds_amount = fields.Monetary(
        string="TDS Deduction (ITA 2023 s.89/90)",
        currency_field="currency_id",
        compute="_compute_statutory_margins",
        store=True,
    )
    margin_known = fields.Boolean(
        compute="_compute_statutory_margins",
        store=True,
        help="False while no direct cost is recorded: the margin is then unknown, not 100%.",
    )
    pretax_margin_bdt = fields.Monetary(
        string="Pre-Tax Operational Margin",
        currency_field="currency_id",
        compute="_compute_statutory_margins",
        store=True,
    )
    net_cash_margin_bdt = fields.Monetary(
        string="Net Cash Margin (After-Tax)",
        currency_field="currency_id",
        compute="_compute_statutory_margins",
        store=True,
    )
    net_cash_margin_pct = fields.Float(
        string="Net Cash Margin (%)",
        compute="_compute_statutory_margins",
        store=True,
    )
    # A04 audit M36-11 (q_09): readonly=False let a clerk type 45% on a
    # zero-margin quote. It is computed, never typed.
    margin_pct = fields.Float(
        string="Margin %",
        compute="_compute_statutory_margins",
        store=True,
    )

    @api.depends(
        "value",
        "cost_amount",
        "vat_rate",
        "tds_rate",
        "estimate_id.grand_total",
        "estimate_id.vat_amount",
    )
    def _compute_statutory_margins(self):
        for rec in self:
            val = rec.value or 0.0
            cost = rec.cost_amount or 0.0
            est = rec.estimate_id.sudo()
            if est and abs(val - estimate_untaxed(est)) <= 0.005:
                # Quoting the estimate as it stands: its own VAT, to the
                # paisa, so the total equals the estimate (and the invoice).
                rec.vat_amount = round((est.grand_total or 0.0) - val, 2)
            else:
                rec.vat_amount = round(val * (rec.vat_rate / 100.0), 2)
            rec.amount_total = round(val + rec.vat_amount, 2)
            # TDS (ITA 2023 s.89/90) is withheld on the value before VAT.
            rec.tds_amount = round(val * (rec.tds_rate / 100.0), 2)
            # A04 audit M36-11 (q_08): a quote with no cost read a 100% margin
            # (live QTN/2026/1). No cost is an unknown margin.
            known = bool(val and cost > 0.0)
            rec.margin_known = known
            if not known:
                rec.pretax_margin_bdt = 0.0
                rec.net_cash_margin_bdt = 0.0
                rec.net_cash_margin_pct = 0.0
                rec.margin_pct = 0.0
                continue
            rec.pretax_margin_bdt = round(val - cost, 2)
            net_cash = round(val - cost - rec.tds_amount, 2)
            rec.net_cash_margin_bdt = net_cash
            rec.net_cash_margin_pct = round((net_cash / val) * 100.0, 2)
            rec.margin_pct = round(((val - cost) / val) * 100.0, 2)

    valid_until = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("sent", "Sent"),
            ("accepted", "Accepted"),
            ("declined", "Declined"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
            ("superseded", "Superseded"),
        ],
        required=True,
        default="draft",
        readonly=True,
        copy=False,
        tracking=True,
    )
    esign_state = fields.Selection(
        [
            ("none", "Not requested"),
            ("sent", "Signature requested"),
            ("signed", "Signed"),
            ("declined", "Signature declined"),
        ],
        required=True,
        default="none",
        readonly=True,
        copy=False,
    )
    signed_at = fields.Datetime(readonly=True, copy=False)
    esign_provider_ref = fields.Char(string="E-Signature Provider Ref", readonly=True, copy=False)
    approved_snapshot = fields.Text(
        readonly=True,
        copy=False,
        help="The terms the internal approval covered. Issuing or accepting a quote whose "
        "terms differ from it is refused.",
    )
    approved_at = fields.Datetime(readonly=True, copy=False)
    sent_at = fields.Datetime(string="Issued At", readonly=True, copy=False)
    accepted_at = fields.Datetime(readonly=True, copy=False)
    declined_at = fields.Datetime(readonly=True, copy=False)
    # Acceptance evidence pack (FR-QTE-038): the accepted version, method,
    # reference, time, who recorded it, and a hash over all of it.
    acceptance_method = fields.Selection(
        [
            ("otp", "Customer one-time code"),
            ("esign", "Provider e-signature"),
            ("signed_form", "Signed quotation recorded"),
        ],
        readonly=True,
        copy=False,
    )
    acceptance_ref = fields.Char(readonly=True, copy=False)
    acceptance_recorded_by = fields.Many2one("res.users", readonly=True, copy=False)
    accepted_value = fields.Monetary(
        string="Accepted Value (excl. VAT)",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    accepted_total = fields.Monetary(
        string="Accepted Total (incl. VAT)",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The total payable the customer accepted; the invoice must match it (D3-01).",
    )
    accepted_version = fields.Integer(readonly=True, copy=False)
    evidence_hash = fields.Char(string="Evidence Hash (SHA-256)", readonly=True, copy=False)
    signed_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Signed Quotation",
        copy=False,
        help="The customer's signed quotation; recorded as acceptance by someone other "
        "than the author.",
    )
    acceptance_otp_digest = fields.Char(copy=False, groups="base.group_system")
    acceptance_otp_expires_at = fields.Datetime(readonly=True, copy=False)
    acceptance_otp_attempts = fields.Integer(readonly=True, copy=False)
    decline_reason_code = fields.Selection(
        DECLINE_REASONS, string="Decline Reason (governed)", copy=False
    )
    decline_reason = fields.Char(readonly=True, copy=False)
    cancel_reason = fields.Char(readonly=True, copy=False)
    # C8 hand-off: what the accepted quotation became.
    service_order_id = fields.Many2one(
        "fix.service.order", string="Service Order", readonly=True, copy=False
    )
    converted_res_model = fields.Char(string="Converted Into (model)", readonly=True, copy=False)
    converted_res_id = fields.Many2oneReference(
        string="Converted Into (id)", model_field="converted_res_model", readonly=True, copy=False
    )
    converted_ref = fields.Char(string="Converted Into", readonly=True, copy=False)
    converted_at = fields.Datetime(readonly=True, copy=False)

    # ---- guard -------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | QUOTE_STAMPS

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields()) | {"name"}
        if self and any(q.state not in ("draft", "approved") for q in self):
            locked |= QUOTE_TERMS
        if self and any(q.state != "sent" for q in self):
            locked |= {"signed_attachment_id", "decline_reason_code"}
        return locked

    def _approval_pinned_fields(self) -> set:
        # Snapshot re-approval: the approval covered these terms, so a change
        # to any of them withdraws it (and the quote returns to draft).
        return super()._approval_pinned_fields() | QUOTE_TERMS

    # ---- DOFA (internal approval) -----------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.value or 0.0

    def _dofa_thresholds(self):
        return QUOTE_VALUE_DOFA_THRESHOLDS

    @api.depends("value")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_needed(self) -> bool:
        return self.state == "draft" and super()._approval_needed()

    # ---- create / write ----------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        Estimate = self.env["fix.estimate"].sudo()
        for vals in vals_list:
            estimate = Estimate.browse(vals.get("estimate_id")).exists()
            if estimate:
                # A04 audit M36-11 (q_07): the value is the estimate's.
                vals.setdefault("value", estimate_untaxed(estimate))
                vals.setdefault("vat_rate", estimate.vat_rate)
                vals.setdefault("currency_id", estimate.currency_id.id)
                if estimate.order_id.customer_id:
                    vals.setdefault("customer_id", estimate.order_id.customer_id.id)
                if estimate.operating_unit_id:
                    vals.setdefault("operating_unit_id", estimate.operating_unit_id.id)
            if not vals.get("operating_unit_id") and "default_operating_unit_id" in self.env.user:
                ou = self.env.user.default_operating_unit_id
                if ou:
                    vals["operating_unit_id"] = ou.id
            if vals.get("name", "New") == "New":
                seq = (
                    self.env["ir.sequence"]
                    .sudo()
                    .with_context(tz="Asia/Dhaka")
                    .next_by_code("fix.quotation")
                )
                if not seq:
                    raise UserError(
                        "The quotation number sequence (fix.quotation) is missing; numbers "
                        "are never derived from a count."
                    )
                vals["name"] = seq
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            if "name" in vals and any(q.name != vals["name"] for q in self):
                raise UserError("A quotation number never changes.")
            terms = QUOTE_TERMS & set(vals)
            if terms:
                frozen = self.filtered(
                    lambda q: q.state not in ("draft", "approved")
                    and any(q._fix_guard_differs(n, vals[n], q[n]) for n in terms)
                )
                if frozen:
                    raise UserError(
                        "Quotation %s is %s: an issued version is immutable (BRU-QTE-02). "
                        "Revise it to make a new version." % (frozen[0].name, frozen[0].state)
                    )
            staged = {"signed_attachment_id", "decline_reason_code"} & set(vals)
            if staged and any(
                q.state != "sent" and any(q._fix_guard_differs(n, vals[n], q[n]) for n in staged)
                for q in self
            ):
                raise UserError(
                    "The signed quotation and the decline reason are recorded only while "
                    "the quotation is with the customer."
                )
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state != "draft" or rec.approval_state != "none" or rec.version > 1:
                raise UserError(
                    "Quotation %s has been through the approval or issue cycle: cancel it "
                    "instead of deleting it (its number and history stay)." % rec.name
                )
        return super().unlink()

    @api.constrains("value", "estimate_id")
    def _check_value_matches_estimate(self):
        for rec in self:
            est = rec.estimate_id.sudo()
            if est and abs((rec.value or 0.0) - estimate_untaxed(est)) > 0.005:
                raise ValidationError(
                    "Quotation %s quotes BDT %.2f before VAT but its estimate %s comes to "
                    "BDT %.2f before VAT (BDT %.2f with VAT); the quotation value is the "
                    "estimate's (A04 audit M36-11)."
                    % (
                        rec.name,
                        rec.value or 0.0,
                        est.display_name,
                        estimate_untaxed(est),
                        est.grand_total or 0.0,
                    )
                )

    @api.constrains("contract_months", "cost_amount", "value")
    def _check_amounts(self):
        for rec in self:
            if rec.contract_months < 0 or (rec.cost_amount or 0.0) < 0 or (rec.value or 0.0) < 0:
                raise ValidationError("Value, cost and contract term cannot be negative.")

    # ---- helpers -----------------------------------------------------------
    def _snapshot(self) -> str:
        self.ensure_one()
        est = self.estimate_id.sudo()
        return json.dumps(
            {
                "version": self.version,
                "value": round(self.value or 0.0, 2),
                "cost_amount": round(self.cost_amount or 0.0, 2),
                "vat_rate": round(self.vat_rate or 0.0, 4),
                "tds_rate": round(self.tds_rate or 0.0, 4),
                "currency": self.currency_id.name,
                "customer_id": self.customer_id.id or False,
                "estimate_id": est.id or False,
                "estimate_total": round(est.grand_total or 0.0, 2) if est else 0.0,
                "estimate_discount_pct": round(est.discount_pct or 0.0, 2) if est else 0.0,
                "valid_until": str(self.valid_until or ""),
                "quote_type": self.quote_type,
                "contract_family": self.contract_family or "",
                "contract_months": self.contract_months,
                "contract_start": str(self.contract_start or ""),
                "operating_unit_id": self.operating_unit_id.id or False,
            },
            sort_keys=True,
        )

    def _readiness_problems(self) -> list:
        """What stops this quotation being approved or issued (spec §8.2
        Draft -> Pending Approval guards)."""
        self.ensure_one()
        problems = []
        today = dhaka_today(self)
        if not self.customer_id:
            problems.append("Identify the customer.")
        if (self.value or 0.0) <= 0.0:
            problems.append("The quotation has no value.")
        if (self.cost_amount or 0.0) <= 0.0:
            problems.append(
                "Record the estimated direct cost: without it the margin is unknown "
                "(A04 audit M36-11)."
            )
        if not self.valid_until or self.valid_until < today:
            problems.append("Set a validity date that has not passed.")
        if self.quote_type == "service" and not self.estimate_id:
            problems.append("A service quotation is built from its estimate (M01).")
        if self.quote_type == "contract":
            if self.contract_months <= 0:
                problems.append("State the contract term in months.")
            if not self.operating_unit_id:
                problems.append("Set the operating unit the contract will belong to.")
        est = self.estimate_id.sudo()
        if est:
            if est.state != "approved":
                problems.append(
                    "Estimate %s is %s; quote only an approved estimate."
                    % (est.display_name, est.state)
                )
            if abs((self.value or 0.0) - estimate_untaxed(est)) > 0.005:
                problems.append(
                    "The estimate now comes to BDT %.2f before VAT, not the BDT %.2f quoted."
                    % (estimate_untaxed(est), self.value or 0.0)
                )
            if abs((self.vat_rate or 0.0) - (est.vat_rate or 0.0)) > 0.0001:
                problems.append(
                    "The VAT rate %.2f%% differs from its estimate's %.2f%%."
                    % (self.vat_rate or 0.0, est.vat_rate or 0.0)
                )
            if est.currency_id != self.currency_id:
                problems.append("The quotation currency differs from its estimate's.")
            owner = est.order_id.customer_id
            if owner and owner != self.customer_id:
                problems.append("The estimate belongs to %s, not this customer." % owner.name)
            problems += est._quotation_discount_blockers()
            problems += self._sale_problems(est)
        return problems

    def _sale_problems(self, est) -> list:
        """The one selling check on every priced line (A04 build 2026-11-04,
        M37-2 / M11-4): product.product._fix_check_sale (cd_catalogue's
        lifecycle gate, extended by cd_rate_card with the M11 floor), run on
        the estimate lines this quotation prices, as the acting user, at
        submit, approval and issue. An item discontinued or a floor raised
        since the estimate stops the quotation."""
        problems = []
        for line in est.line_ids.filtered("product_id"):
            product = line.product_id.with_env(self.env)
            if not hasattr(product, "_fix_check_sale"):
                break
            try:
                product._fix_check_sale(unit_price=line.unit_price or 0.0, channel="quotation")
            except (UserError, ValidationError) as exc:
                problems.append(
                    "%s: %s" % (line.product_id.display_name, exc.args[0] if exc.args else exc)
                )
        return problems

    def _assert_ready(self):
        for rec in self:
            problems = rec._readiness_problems()
            if problems:
                raise UserError("Quotation %s: %s" % (rec.name, " ".join(problems)))

    def _log_review(self, decision, notes=""):
        """The review log is written by the approval engine's decision, never
        typed (A04 audit M36-6: reviews were rows anyone could create in
        anyone's name)."""
        task = self._approval_task()
        Review = self.env["fix.quote.review"].sudo()
        for rec in self:
            Review.create(
                {
                    "quotation_id": rec.id,
                    "version": rec.version,
                    "value_reviewed": rec.value,
                    "reviewer_id": self.env.user.id,
                    "on_behalf_of_id": task.on_behalf_of_id.id if task else False,
                    "approval_request_id": rec.approval_request_id.id or False,
                    "decision": decision,
                    "notes": notes or False,
                }
            )

    def _event_payload(self) -> dict:
        self.ensure_one()
        return {
            "version": self.version,
            "grand_total": self.amount_total,
            "untaxed": self.value,
            "quotation": self.name,
            "quote_type": self.quote_type,
            "customer_id": self.customer_id.id or None,
        }

    # ---- internal approval (submit -> M63 -> approved) ---------------------
    def action_submit(self, justification=None):
        """Draft -> pending approval: routed by value band to someone other
        than the author (BRU-QTE-06/07/09)."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft quotation is submitted; this one is %s." % rec.state)
            rec._assert_ready()
            tier = rec._dofa_current_tier()
            if (
                rec._dofa_tier_rank(tier) >= rec._dofa_tier_rank("tier_2")
                and not (justification or rec.dofa_justification or "").strip()
            ):
                raise UserError(
                    "Quotation %s needs Branch Manager approval or above: state the business "
                    "justification." % rec.name
                )
        return self.action_request_approval(justification=justification)

    def action_approve_quote(self):
        """The approver's decision, run by the M63 inbox only."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Quotation %s is %s, not awaiting approval." % (rec.name, rec.state)
                )
            rec._assert_ready()
        # Tier from the live value, approver holds it, approver != creator,
        # justification at Tier 2+, the approved amount pinned.
        self.action_dofa_approve()
        now = fields.Datetime.now()
        for rec in self:
            rec._guarded().write(
                {"state": "approved", "approved_snapshot": rec._snapshot(), "approved_at": now}
            )
        tiers = dict(self._fields["dofa_approved_tier"].selection)
        for rec in self:
            rec._log_review(
                "approved",
                "Approved at %s for BDT %.2f."
                % (tiers.get(rec.dofa_approved_tier, "no tier"), rec.value or 0.0),
            )
        return True

    def _approval_on_rejected(self, comment):
        # A rejected review blocks issue: the quote stays in draft, unapproved.
        self._log_review("rejected", comment)

    def _approval_clear_stamp(self, reason):
        res = super()._approval_clear_stamp(reason)
        for rec in self.filtered(lambda q: q.state == "approved"):
            rec._guarded().write({"state": "draft", "approved_snapshot": False})
            rec.message_post(body="Back to draft for re-approval: %s" % reason)
        return res

    # ---- issue -------------------------------------------------------------
    def action_send(self):
        """Approved -> sent (issued). The terms issued are the terms approved."""
        today = dhaka_today(self)
        for rec in self:
            if rec.state != "approved" or rec.approval_state != "approved":
                raise UserError(
                    "Quotation %s is %s: only an internally approved quotation is issued."
                    % (rec.name, rec.state)
                )
            rec._dofa_assert_approved("Issuing quotation %s" % rec.name)
            if rec._snapshot() != rec.approved_snapshot:
                raise UserError(
                    "Quotation %s changed after it was approved; it must be approved again "
                    "before it is issued." % rec.name
                )
            if not rec.valid_until or rec.valid_until < today:
                raise UserError("Quotation %s is past its validity date." % rec.name)
            rec._assert_ready()
            rec._guarded().write(
                {"state": "sent", "sent_at": fields.Datetime.now(), "esign_state": "sent"}
            )
            payload = rec._event_payload()
            payload["valid_until"] = str(rec.valid_until)
            publish(self.env, "quotation.issued", "fix.quotation", rec.id, payload)
        return True

    # ---- customer acceptance -----------------------------------------------
    def _accept(self, method, ref):
        """Sent -> accepted, with its evidence pack, then the hand-off."""
        self.ensure_one()
        today = dhaka_today(self)
        if self.state != "sent":
            raise UserError(
                "Quotation %s is %s: only an issued quotation can be accepted."
                % (self.name, self.state)
            )
        if not self.valid_until or today > self.valid_until:
            raise UserError(
                "Quotation %s was valid until %s (BRU-QTE-03): acceptance is impossible "
                "after expiry. Revise it to re-issue at current prices."
                % (self.name, self.valid_until)
            )
        self._dofa_assert_approved("Accepting quotation %s" % self.name)
        if self._snapshot() != self.approved_snapshot:
            raise UserError("Quotation %s no longer matches what was approved." % self.name)
        now = fields.Datetime.now()
        recorder = False if self.env.su else self.env.user.id
        pack = {
            "quotation": self.name,
            "version": self.version,
            "value": round(self.value or 0.0, 2),
            "currency": self.currency_id.name,
            "customer_id": self.customer_id.id,
            "method": method,
            "ref": ref,
            "accepted_at": str(now),
            "recorded_by": recorder,
            "approved_snapshot": self.approved_snapshot,
        }
        evidence = hashlib.sha256(json.dumps(pack, sort_keys=True).encode()).hexdigest()
        vals = {
            "state": "accepted",
            "accepted_at": now,
            "acceptance_method": method,
            "acceptance_ref": ref,
            "acceptance_recorded_by": recorder,
            "accepted_value": self.value,
            "accepted_total": self.amount_total,
            "accepted_version": self.version,
            "evidence_hash": evidence,
        }
        if method == "esign":
            vals.update({"esign_state": "signed", "signed_at": now})
        self._guarded().write(vals)
        payload = self._event_payload()
        payload.update({"acceptance_method": method, "evidence_hash": evidence})
        publish(self.env, "quotation.accepted", "fix.quotation", self.id, payload)
        self._convert_safely()
        return True

    def action_send_acceptance_otp(self):
        """Send the customer a one-time code to accept this quotation."""
        for rec in self:
            if rec.state != "sent":
                raise UserError("Issue the quotation to the customer first.")
            phone = fix_otp_util.bd_mobile(rec.customer_id) if rec.customer_id else ""
            if not phone:
                raise UserError(
                    "The customer has no valid Bangladesh mobile number for an acceptance code."
                )
            code = fix_otp_util.issue_code()
            fix_otp_util.dispatch_otp(phone, code, fix_otp_util.OTP_TTL_SECONDS)
            rec.sudo()._guarded().write(
                {
                    "acceptance_otp_digest": fix_otp_util.digest(
                        self.env, "quotation_acceptance", rec.id, code
                    ),
                    "acceptance_otp_expires_at": fields.Datetime.now()
                    + timedelta(seconds=fix_otp_util.OTP_TTL_SECONDS),
                    "acceptance_otp_attempts": 0,
                }
            )
            rec.message_post(
                body="Acceptance code sent to the customer's phone %s." % fix_otp_util.mask(phone)
            )
        return True

    def action_verify_acceptance_otp(self, otp=None, code=None):
        """Accept on the code the customer reads back. A wrong code is
        counted, not raised (a raise would roll the counter back)."""
        code = (otp or code or "").strip()
        result = {"verified": True}
        for rec in self:
            stored = rec.sudo().acceptance_otp_digest
            if rec.state != "sent" or not stored or not rec.acceptance_otp_expires_at:
                raise UserError("Send the customer an acceptance code first.")
            if fields.Datetime.now() > rec.acceptance_otp_expires_at:
                raise UserError("The acceptance code has expired. Send a new one.")
            if not fix_otp_util.matches(self.env, "quotation_acceptance", rec.id, code, stored):
                attempts = rec.acceptance_otp_attempts + 1
                burnt = attempts >= fix_otp_util.OTP_MAX_ATTEMPTS
                rec.sudo()._guarded().write(
                    {
                        "acceptance_otp_attempts": attempts,
                        "acceptance_otp_digest": False if burnt else stored,
                    }
                )
                result = {
                    "verified": False,
                    "error": "That acceptance code is not correct."
                    + (" Too many attempts: send a new code." if burnt else ""),
                }
                continue
            phone = fix_otp_util.bd_mobile(rec.customer_id)
            rec.sudo()._guarded().write({"acceptance_otp_digest": False})
            rec._accept("otp", "OTP %s" % fix_otp_util.mask(phone))
        return result

    def action_record_signed_acceptance(self):
        """Record the customer's signed quotation as acceptance. The person
        recording it is not the author (the A02 estimate rule)."""
        for rec in self:
            if rec.state != "sent":
                raise UserError("Issue the quotation to the customer first.")
            att = rec.signed_attachment_id.sudo()
            if not att:
                raise UserError("Attach the customer's signed quotation first.")
            if rec.create_uid == self.env.user and not self.env.su:
                raise UserError(
                    "Segregation of duties: the author of a quotation cannot record the "
                    "customer's signed acceptance of it."
                )
            digest = att.checksum or (hashlib.sha256(att.raw).hexdigest() if att.raw else "")
            if not digest:
                raise UserError("The signed quotation attachment is empty.")
            rec._accept("signed_form", "SIGNED %s (%s)" % (att.name or att.id, digest))
        return True

    @api.model
    def _esign_provider_complete(self, name, version, signature_ref, signature):
        """The e-signature provider's completion callback (controllers/
        esign.py). Accepted only when its HMAC over the exact number, version
        and value verifies against the configured provider secret, so a
        signature cannot be typed into the record (A04 audit M36-1)."""
        secret = self.env["ir.config_parameter"].sudo().get_param(ESIGN_PROVIDER_PARAM)
        if not secret:
            raise UserError("No e-signature provider is configured for quotations.")
        try:
            version = int(version)
        except (TypeError, ValueError):
            raise UserError("The callback names no quotation version.") from None
        quote = self.sudo().search([("name", "=", name or ""), ("version", "=", version)], limit=1)
        if not quote:
            raise UserError("No such quotation version.")
        expected = esign_signature(secret, quote.name, quote.version, quote.value, signature_ref)
        if not signature_ref or not hmac.compare_digest(expected, signature or ""):
            raise UserError("The e-signature callback does not verify.")
        if quote.esign_state != "sent":
            raise UserError("No signature was requested on quotation %s." % quote.name)
        quote._guarded().write({"esign_provider_ref": signature_ref})
        quote._accept("esign", "ESIGN %s" % signature_ref)
        return quote.id

    # ---- decline / cancel / revise / expire --------------------------------
    def action_decline(self, reason=None, code=None):
        """BRU-QTE-16: a decline carries a reason from the governed list."""
        reason = (reason or "").strip()
        labels = dict(DECLINE_REASONS)
        for rec in self:
            if rec.state != "sent":
                raise UserError(
                    "Only an issued quotation can be declined; %s is %s." % (rec.name, rec.state)
                )
            key = code or rec.decline_reason_code
            if key not in labels:
                raise UserError("Choose the decline reason from the governed list (BRU-QTE-16).")
            if not reason:
                raise UserError("Describe why the customer declined.")
            rec._guarded().write(
                {
                    "state": "declined",
                    "declined_at": fields.Datetime.now(),
                    "decline_reason_code": key,
                    "decline_reason": "%s: %s" % (labels[key], reason),
                }
            )
            payload = rec._event_payload()
            payload["reason_code"] = key
            publish(self.env, "quotation.declined", "fix.quotation", rec.id, payload)
        return True

    def action_cancel(self, reason=None):
        """Withdrawn by 1000FiX before the customer decided (spec §8.2)."""
        reason = (reason or "").strip()
        for rec in self:
            if rec.state not in ("draft", "approved", "sent"):
                raise UserError(
                    "Quotation %s is %s and cannot be cancelled." % (rec.name, rec.state)
                )
            if not reason:
                raise UserError("Record why the quotation is withdrawn.")
            if rec.approval_state in ("pending", "approved"):
                rec._approval_void("the quotation was cancelled")
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason})
        return True

    def action_revise(self):
        """A new version: an issued, expired or declined quotation is never
        edited or extended (BRU-QTE-02/04)."""
        self.ensure_one()
        if self.state not in ("sent", "expired", "declined"):
            raise UserError(
                "Only an issued, expired or declined quotation is revised; edit a draft directly."
            )
        latest = (
            self.sudo().search([("name", "=", self.name)], order="version desc", limit=1).version
        )
        new = self._guarded().copy(
            {
                "name": self.name,
                "version": latest + 1,
                "parent_version_id": self.id,
                "state": "draft",
                "valid_until": False,
            }
        )
        if self.state == "sent":
            self._guarded().write({"state": "superseded"})
            publish(
                self.env,
                "quotation.superseded",
                "fix.quotation",
                self.id,
                {"quotation": self.name, "old_version": self.version, "new_version": new.version},
            )
        return {
            "type": "ir.actions.act_window",
            "res_model": "fix.quotation",
            "res_id": new.id,
            "view_mode": "form",
        }

    @api.model
    def cron_expire_quotations(self):
        """AUT-QTE-06: an issued quotation past its validity expires; so does
        a quoted estimate. Idempotent: only live quotes are touched."""
        today = dhaka_today(self)
        stale = self.sudo().search([("state", "=", "sent"), ("valid_until", "<", today)])
        for rec in stale:
            rec._guarded().write({"state": "expired"})
            publish(self.env, "quotation.expired", "fix.quotation", rec.id, rec._event_payload())
        estimates = self.env["fix.estimate"].sudo()._cron_expire_quoted_estimates()
        return len(stale) + estimates

    # ---- C8 hand-off --------------------------------------------------------
    def _convert(self):
        """Accepted -> the downstream record (spec §8.2 'Converted', C8).

        - service: the estimate's M01 service order is the approved scope;
          the quotation is linked to it.
        - contract: an M08 draft contract, through its own create
          (fix.contract.create, as the superuser service: the contract then
          runs M08's activation path).
        - subscription: fix.subscription is A08-owned; quotation.accepted
          (quote_type=subscription) is the hand-off it consumes."""
        self.ensure_one()
        if self.converted_res_id:
            return self.converted_res_model, self.converted_res_id
        now = fields.Datetime.now()
        if self.quote_type == "service":
            order = self.estimate_id.sudo().order_id
            if not order:
                raise UserError("Quotation %s has no service order to release." % self.name)
            target = order
            extra = {"service_order_id": order.id}
            order.message_post(
                body="Quotation %s v%d accepted (%s): the approved scope is released."
                % (self.name, self.version, self.acceptance_ref)
            )
        elif self.quote_type == "contract":
            if "fix.contract" not in self.env:
                raise UserError("M08 Contracts is not installed; the contract cannot be created.")
            if not self.operating_unit_id:
                raise UserError("Set the operating unit the contract belongs to.")
            months = self.contract_months or 12
            start = self.contract_start or dhaka_today(self)
            target = (
                self.env["fix.contract"]
                .sudo()
                .create(
                    {
                        "name": "%s v%d — %s" % (self.name, self.version, self.customer_id.name),
                        "family": self.contract_family or "amc",
                        "customer_id": self.customer_id.id,
                        "operating_unit_id": self.operating_unit_id.id,
                        "company_id": self.company_id.id,
                        "currency_id": self.currency_id.id,
                        "date_start": start,
                        "date_end": start + relativedelta(months=months) - timedelta(days=1),
                        # The quotation value is the whole term's price.
                        "annual_value": round((self.value or 0.0) * 12.0 / months, 2),
                    }
                )
            )
            extra = {}
        else:
            raise UserError(
                "A subscription quotation is handed to M39 through the quotation.accepted "
                "event; no record is created here."
            )
        self._guarded().write(
            dict(
                extra,
                converted_res_model=target._name,
                converted_res_id=target.id,
                converted_ref=target.display_name,
                converted_at=now,
            )
        )
        publish(
            self.env,
            "quotation.converted",
            "fix.quotation",
            self.id,
            {"quotation": self.name, "target_model": target._name, "target_id": target.id},
        )
        return target._name, target.id

    def _convert_safely(self):
        """Run the hand-off without undoing the acceptance: a missing
        prerequisite is reported on the quotation and retried by Convert."""
        try:
            with self.env.cr.savepoint():
                return self._convert()
        except (UserError, ValidationError, AccessError) as exc:
            self.message_post(
                body="Accepted, not yet converted: %s" % (exc.args[0] if exc.args else exc)
            )
            return False

    def action_convert(self):
        for rec in self:
            if rec.state != "accepted":
                raise UserError("Only an accepted quotation is converted.")
            rec._convert()
        return True


class FixQuoteReview(models.Model):
    """The internal review log: one row per decision, written by the M63
    approval of the quotation (append-only)."""

    _name = "fix.quote.review"
    _description = "Quotation Internal Review"
    _order = "reviewed_at desc, id desc"

    quotation_id = fields.Many2one("fix.quotation", required=True, ondelete="cascade", index=True)
    version = fields.Integer(readonly=True)
    value_reviewed = fields.Float(string="Value Reviewed", readonly=True)
    reviewer_id = fields.Many2one("res.users", readonly=True)
    on_behalf_of_id = fields.Many2one("res.users", string="On Behalf Of", readonly=True)
    approval_request_id = fields.Many2one("fix.approval.request", readonly=True)
    decision = fields.Selection(
        [("approved", "Approved"), ("rejected", "Rejected"), ("revision", "Revision requested")],
        required=True,
        readonly=True,
    )
    notes = fields.Char(readonly=True)
    reviewed_at = fields.Datetime(required=True, default=fields.Datetime.now, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        # A04 audit M36-6 (qr_01/qr_02): the author recorded an approved review
        # under a director's name, or their own.
        if not self.env.su:
            raise UserError(
                "A quotation review is recorded by the approver's decision in the M63 "
                "inbox, not typed. Submit the quotation for approval."
            )
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError("The quotation review log cannot be edited.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("The quotation review log cannot be deleted.")
        return super().unlink()
