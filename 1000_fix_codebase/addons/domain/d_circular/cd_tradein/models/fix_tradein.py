# fix_tradein — M14: trade-in, refurbishment, resale (P09-M04 / R07-M03).
#
# A05 workflow audit (2026-11-03), E3-E12 + P2 for M14. Before this:
#   - request `state`, `payout_approval_state`, `psr_verified` and the payout
#     stamps were plain fields: a clerk forged 'graded' on a draft and a
#     treasury payout followed with no collection, wipe or refurbishment;
#   - the payout four-eyes needed no authority group, and the approval pinned
#     the amount only, so the payee was swapped and TDS switched off after it;
#   - provenance was decorative (pre-verified defaults, a stub NEIR check that
#     cleared any IMEI, payout with no row at all, a newer clean row masking a
#     stolen one) and the NID gate accepted 0000000000;
#   - the wipe gate ran only in wipe/refurbish, stock was capitalised at the
#     offer, TDS had no record, harvest and resale warranty were dead ends.
# Now every workflow, approval, money and evidence field is guarded
# (fix.guarded.mixin) and changes only through its action; each gate runs in
# the state change itself; the payout approval is ONE routed M63 request that
# pins the payee, the net, the TDS and the NID with the amount; provenance
# and KYC fail closed (cd_tradein.* switches, safe defaults, report §7).
from __future__ import annotations

import itertools
import logging
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

_logger = logging.getLogger(__name__)

TRADEIN_STATES = [
    ("draft", "Draft"),
    ("offered", "Offer Sent"),
    ("accepted", "Accepted"),
    ("collected", "Collected"),
    ("wiped", "Data Wiped"),
    ("refurbished", "Refurbished"),
    ("graded", "Graded"),
    ("resale_ready", "Resale Ready"),
    ("closed", "Closed"),
    ("rejected", "Rejected"),
]
_ORDER = [s[0] for s in TRADEIN_STATES]
_DONE = ("closed", "rejected")

# A05 audit M14-7 / E7: a Smart NID is 10 digits, the NID 17 (report §6 E7).
# The format alone let 0000000000 pay out, so placeholders are refused too.
_NID_RE = re.compile(r"^(\d{10}|\d{17})$")
_ETIN_RE = re.compile(r"^\d{12}$")

# Decision roles (report §7.2). They ship EMPTY: holders are a business
# appointment, made by the coordinator, never by this module.
GROUP_PAYOUT_APPROVER = "cd_tradein.group_tradein_payout_approver"
GROUP_PROVENANCE_OFFICER = "cd_tradein.group_tradein_provenance_officer"
GROUP_QA_INSPECTOR = "cd_tradein.group_tradein_qa_inspector"
GROUP_VALUATION_MANAGER = "cd_tradein.group_tradein_valuation_manager"
GROUP_WARRANTY_OFFICER = "cd_device_registry.group_warranty_officer"

# Open business decisions (report §7.3 KYC, §7.4 provenance), each a system
# parameter with a fail-closed default.
PARAM_ALLOW_NEIR_UNCHECKED = "cd_tradein.allow_neir_unchecked"  # "0": refuse
PARAM_PROVENANCE_VALIDITY_DAYS = "cd_tradein.provenance_validity_days"  # 30
PARAM_KYC_VERIFIED_NID = "cd_tradein.kyc_require_verified_nid"  # "1"
PARAM_KYC_CAP = "cd_tradein.kyc_payout_cap_per_nid_30d"  # BDT 100,000
PARAM_HOLD_DAYS = "cd_tradein.hold_days"  # 7
PARAM_OFFER_REQUIRES_VALUATION = "cd_tradein.offer_requires_valuation"  # "1"
PARAM_QA_MIN_PASS_PCT = "cd_tradein.qa_min_pass_pct"  # noqa: S105 - a parameter key, 100
PARAM_HARVEST_LOCATION = "cd_tradein.harvest_location_id"  # unset: refuse
PARAM_RESALE_WARRANTY_MONTHS = "cd_tradein.resale_warranty_months"  # 6

# ITA 2023 section -> the M51 statutory TDS rate row (fix.tax.rate.code).
_TDS_RATE_CODE = {"s89": "supply_of_goods", "s90": "service_general"}

_EPS = 0.005


def _param(env, key, default):
    return env["ir.config_parameter"].sudo().get_param(key, default)


def _param_on(env, key, default):
    return str(_param(env, key, default) or "").strip().lower() in ("1", "true", "yes", "on")


def _param_float(env, key, default):
    try:
        return float(_param(env, key, default))
    except (TypeError, ValueError):
        return float(default)


def nid_placeholder(nid: str) -> bool:
    """True for an identity number nobody holds: one digit repeated, or a run
    of seven or more consecutive digits (0123456..., 9876543...), the shape of
    every seed and test placeholder found live (A05 audit M14-7)."""
    digits = (nid or "").strip()
    if not digits.isdigit():
        return False
    if len(set(digits)) == 1:
        return True
    for step in (1, -1):
        run = 1
        for a, b in itertools.pairwise(digits):
            run = run + 1 if int(b) - int(a) == step else 1
            if run >= 7:
                return True
    return False


class FixTradeinRequest(models.Model):
    """Journey 9: trade-in -> offer -> intake -> data wipe -> refurbishment
    -> grading -> resale -> payout. The circular business's money path.
    Composes M03 logistics, M06 data wipe gate, M31 workshop refurbishment,
    M37 grading, M15 graded inventory valuation, and M50 treasury payout."""

    _name = "fix.tradein.request"
    _description = "Trade-In Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "create_date desc, id desc"

    # A05 audit M14-3 / E5 / E11: the payout four-eyes and the DOFA sign-off
    # are ONE routed M63 request. The engine routes it to holders of the DOFA
    # tier the amount needs who also hold the trade-in payout approver role,
    # minus the requester, the creator and whoever last changed the amount;
    # the decision runs action_approve_payout, which refuses a direct press.
    _approval_routed = True
    _approval_domain = "tradein_payout"
    _approval_apply_method = "action_approve_payout"

    # A05 DOFA matrix — Customer Trade-In Valuation & Payout: Appraisal
    # Specialist to 50k, Service Hub Lead to 250k, Head of Circular Economy
    # to 1M, CFO above.
    _DOFA_THRESHOLDS = [
        (50000.0, "tier_1"),
        (250000.0, "tier_2"),
        (1000000.0, "tier_3"),
        (float("inf"), "tier_4"),
    ]

    # Written only by the transitions (E3, M14-1/2/10/11).
    _GUARDED = frozenset(
        {
            "state",
            "payout_approval_state",
            "payout_requested_by_id",
            "payout_approved_by_id",
            "payout_approved_at",
            "payout_approved_partner_id",
            "payout_approved_net",
            "payout_approved_tds",
            "payout_approved_nid",
            "payout_amount",
            "payout_execution_id",
            "paid_at",
            "psr_verified",
            "psr_verified_by_id",
            "psr_verified_at",
            "tds_certificate_no",
            "withholding_line_id",
            "accepted_offer_value",
            "accepted_at",
            "accepted_by_id",
            "revision_accepted_value",
            "revision_accepted_at",
            "revision_accepted_by_id",
            "rejected_reason",
            "hold_until",
            "hold_released",
            "consignment_id",
            "workshop_job_id",
            "graded_stock_id",
            "marketplace_order_id",
            "ewaste_collection_id",
            "ewaste_collection_ref",
            # direct costs: the refurbishment cost comes from the costed steps
            "parts_cost",
            "labour_cost",
        }
    )
    # Frozen once the step that relies on them has happened (M14-14 etc.).
    _FROZEN_FROM = {
        "offered": frozenset({"offered_value", "currency_id"}),
        "accepted": frozenset({"customer_id", "acceptance_channel"}),
        "collected": frozenset({"device_id", "operating_unit_id", "company_id"}),
        "wiped": frozenset({"wipe_certificate_id"}),
        "graded": frozenset({"grade", "refurb_grade_id", "battery_health_pct"}),
        "resale_ready": frozenset({"resale_value", "resale_channel", "marketplace_seller_id"}),
    }
    # What a closed or rejected trade-in may still change: its chatter.
    _DONE_EDITABLE = frozenset(
        {
            "message_follower_ids",
            "message_ids",
            "activity_ids",
            "message_main_attachment_id",
        }
    )

    def _dofa_thresholds(self):
        return self._DOFA_THRESHOLDS

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.graded_value or self.offered_value or 0.0

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (graded payout value)" % self._dofa_amount()

    @api.depends("graded_value", "offered_value")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    device_id = fields.Many2one("fix.device", string="Device", ondelete="set null", index=True)
    device_model_id = fields.Many2one(
        "fix.device.model", string="Device Model", related="device_id.device_model_id", store=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    offered_value = fields.Monetary(
        string="Offered Value",
        currency_field="currency_id",
        required=True,
        default=0.0,
        help="The trade-in offer. Set in draft (from an applied valuation); frozen once "
        "the offer is sent.",
    )
    payout_amount = fields.Monetary(
        string="Payout Amount",
        currency_field="currency_id",
        readonly=True,
        help="The actual payout (M50 treasury)",
    )
    # The payout is the value of the device AS GRADED, approved by a second
    # person - never the pre-inspection offer paid out regardless of grade.
    graded_value = fields.Monetary(
        string="Graded Payout Value",
        currency_field="currency_id",
        tracking=True,
        help="The payout value confirmed after grading (may be below the offer "
        "when the inspected grade is worse than declared)",
    )
    payout_approval_state = fields.Selection(
        [
            ("none", "Not Requested"),
            ("pending", "Pending Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Payout Approval",
        default="none",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )
    payout_requested_by_id = fields.Many2one(
        "res.users", string="Payout Requested By", readonly=True, copy=False
    )
    payout_approved_by_id = fields.Many2one(
        "res.users", string="Payout Approved By", readonly=True, copy=False
    )
    payout_approved_at = fields.Datetime(readonly=True, copy=False)
    # E5 / M14-4: what the approval covered, besides the amount.
    payout_approved_partner_id = fields.Many2one(
        "res.partner", string="Approved Payee", readonly=True, copy=False
    )
    payout_approved_net = fields.Monetary(
        string="Approved Net Payout", currency_field="currency_id", readonly=True, copy=False
    )
    payout_approved_tds = fields.Monetary(
        string="Approved TDS", currency_field="currency_id", readonly=True, copy=False
    )
    payout_approved_nid = fields.Char(string="Approved Payee NID", readonly=True, copy=False)
    paid_at = fields.Datetime(string="Payout Queued On", readonly=True, copy=False)

    # Statutory Compliance (BTRC NEIR, ITA 2023 TDS & Customer NID)
    customer_nid = fields.Char(
        string="Customer Smart NID",
        copy=False,
        tracking=True,
        help="10-digit Smart NID or 17-digit NID — required, verified by the provenance "
        "officer and bound to this customer before any payout leaves (AML / ITA 2023)",
    )
    taxpayer_tin = fields.Char(
        string="Taxpayer e-TIN",
        copy=False,
        help="The seller's 12-digit e-TIN; its absence lifts the TDS rate by 50%",
    )
    psr_verified = fields.Boolean(
        string="PSR Verified",
        default=False,
        readonly=True,
        copy=False,
        help="Proof of Submission of Return sighted and recorded by Verify PSR, with "
        "the seller's e-TIN and the PSR document attached (M14-10).",
    )
    psr_attachment_id = fields.Many2one(
        "ir.attachment", string="PSR Document", copy=False, ondelete="restrict"
    )
    psr_verified_by_id = fields.Many2one(
        "res.users", string="PSR Verified By", readonly=True, copy=False
    )
    psr_verified_at = fields.Datetime(string="PSR Verified On", readonly=True, copy=False)
    tds_section = fields.Selection(
        [
            ("s89", "s.89 — supply of goods"),
            ("s90", "s.90 — services"),
            ("s140", "s.140 — e-commerce collection"),
        ],
        string="TDS Section (ITA 2023)",
        default="s89",
        help="A used-device trade-in is a supply of goods: s.89",
    )
    tds_applicable = fields.Boolean(
        string="ITA 2023 TDS Applicable", default=False, help="Withholding tax under Section 89/90"
    )
    tds_rate_pct = fields.Float(
        string="TDS Rate % (Contract)",
        default=5.0,
        help="Never below the statutory rate of the section (M51 rate master).",
    )
    tds_effective_rate_pct = fields.Float(
        string="TDS Effective Rate %",
        compute="_compute_tds",
        store=True,
        help="Contract rate, uplifted ×1.5 when no PSR/e-TIN is sighted (s.142)",
    )
    tds_amount = fields.Monetary(
        string="TDS Withheld (BDT)",
        currency_field="currency_id",
        compute="_compute_tds",
        store=True,
    )
    net_payout = fields.Monetary(
        string="Net Payout (BDT)", currency_field="currency_id", compute="_compute_tds", store=True
    )
    tds_certificate_no = fields.Char(
        string="TDS Certificate No (legacy, typed)",
        copy=False,
        readonly=True,
        help="Typed before the A05 remediation; never typed again. The certificate is "
        "issued by M51 on the withholding register line after the challan deposit.",
    )
    # E10 / M14-11: the withheld tax as an M51 register line (TDS), deposited by
    # challan and certified by finance.
    withholding_line_id = fields.Many2one(
        "fix.withholding.line",
        string="TDS Register Line (M51)",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )
    withholding_state = fields.Selection(
        related="withholding_line_id.state", string="TDS Register State"
    )
    withholding_certificate_no = fields.Char(
        related="withholding_line_id.certificate_id.certificate_no",
        string="TDS Certificate No",
    )

    # Customer acceptance (M14-19) and the revised offer (P2).
    acceptance_channel = fields.Selection(
        [
            ("counter", "In person at the counter (signed)"),
            ("sms", "SMS reply"),
            ("app", "Customer app"),
            ("call", "Recorded call"),
        ],
        string="Acceptance Channel",
        default="counter",
    )
    accepted_offer_value = fields.Monetary(
        string="Accepted Offer", currency_field="currency_id", readonly=True, copy=False
    )
    accepted_at = fields.Datetime(readonly=True, copy=False)
    accepted_by_id = fields.Many2one(
        "res.users", string="Acceptance Recorded By", readonly=True, copy=False
    )
    revision_accepted_value = fields.Monetary(
        string="Revised Value Accepted", currency_field="currency_id", readonly=True, copy=False
    )
    revision_accepted_at = fields.Datetime(readonly=True, copy=False)
    revision_accepted_by_id = fields.Many2one(
        "res.users", string="Revision Acceptance Recorded By", readonly=True, copy=False
    )
    revision_state = fields.Selection(
        [
            ("none", "Not Needed"),
            ("pending", "Customer Re-acceptance Pending"),
            ("accepted", "Revised Value Accepted"),
        ],
        string="Revised Offer",
        compute="_compute_revision_state",
        store=True,
        help="A graded value below the accepted offer is a revised offer: the customer "
        "must accept it again before it is approved or paid.",
    )
    rejected_reason = fields.Text(readonly=True, copy=False)

    # Grading on M37 grades (fix.refurb.grade)
    refurb_grade_id = fields.Many2one(
        "fix.refurb.grade", string="Refurb Grade Master (M37)", index=True, ondelete="restrict"
    )
    grade = fields.Selection(
        [
            ("a", "Grade A (Like New)"),
            ("b", "Grade B (Good)"),
            ("c", "Grade C (Fair)"),
            ("d", "Grade D (Poor)"),
            ("e", "Grade E (Parts Only)"),
        ],
        string="Refurbishment Grade",
        tracking=True,
    )

    state = fields.Selection(
        TRADEIN_STATES, default="draft", required=True, readonly=True, tracking=True
    )

    # M06 Data Wipe Gate
    wipe_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate",
        string="Data Wipe Certificate (M06)",
        ondelete="set null",
        index=True,
        help="M06's secure wipe; required before refurbishment (Journey 9 gate)",
    )

    # E12: the hold period before a bought-in device may be resold or broken
    # up (a stolen report can still arrive).
    hold_until = fields.Date(string="Hold Until", readonly=True, copy=False)
    hold_released = fields.Boolean(string="Hold Released", readonly=True, copy=False)

    # Refurbishment costing on M31 workshop model
    workshop_job_id = fields.Many2one(
        "fix.workshop.job", string="Workshop Refurb Job (M31)", ondelete="set null"
    )
    refurbishment_ids = fields.One2many("fix.refurbishment", "tradein_id", string="Refurb Steps")
    parts_cost = fields.Monetary(
        string="Refurb Parts Cost (direct)", currency_field="currency_id", default=0.0
    )
    labour_cost = fields.Monetary(
        string="Refurb Labour Cost (direct)", currency_field="currency_id", default=0.0
    )
    steps_cost = fields.Monetary(
        string="Costed Steps",
        currency_field="currency_id",
        compute="_compute_refurb_cost",
        store=True,
        help="Parts + labour recorded on the refurbishment steps (M14-12)",
    )
    refurbishment_cost = fields.Monetary(
        string="Total Refurb Cost",
        currency_field="currency_id",
        compute="_compute_refurb_cost",
        store=True,
    )

    # M15 Graded Inventory Valuation
    inventory_valuation = fields.Monetary(
        string="Inventory Valuation",
        currency_field="currency_id",
        compute="_compute_inventory_valuation",
        store=True,
        help="Capitalised stock cost = acquisition (the graded payout value, else the "
        "offer until grading) + refurbishment cost (M14-15)",
    )
    resale_value = fields.Monetary(
        string="Resale Value",
        currency_field="currency_id",
        default=0.0,
        help="The graded resale valuation / listed price",
    )
    resale_channel = fields.Selection(
        [
            ("marketplace", "Marketplace (M12)"),
            ("store", "Own Store (M38)"),
            ("direct", "Direct / Walk-in"),
            ("none", "Not listed"),
        ],
        string="Resale Channel",
        default="none",
    )
    resale_listed_on = fields.Date(string="Listed On")
    battery_health_pct = fields.Integer(
        string="Battery Health %",
        default=100,
        help="Measured at grading; the A–E grade and resale price reflect it",
    )
    graded_stock_id = fields.Many2one(
        "fix.graded.stock", string="Graded Inventory Unit (M15)", ondelete="set null"
    )

    # M03 Logistics Consignment
    consignment_id = fields.Many2one(
        "fix.consignment", string="Collection Consignment (M03)", ondelete="set null"
    )

    # M50 Treasury Payout Seam
    payout_execution_id = fields.Many2one(
        "fix.payment.execution", string="Treasury Payout (M50)", ondelete="set null"
    )

    # M12 Resale Seam
    marketplace_seller_id = fields.Many2one(
        "res.partner", string="Marketplace Channel (M12)", ondelete="set null"
    )
    marketplace_order_id = fields.Integer(
        string="M12 Listing (order id)",
        readonly=True,
        copy=False,
        help="The fix.marketplace.order the resale was listed as (cd_marketplace sits above "
        "this module, so this is an id, not a relation).",
    )

    # M18 -> M14 (A05 P2 M18: a reuse item routes to M14): the e-waste
    # collection this intake was opened from (cd_ewaste sits beside this
    # module, so this is an id, not a relation). One intake per collection.
    ewaste_collection_id = fields.Integer(
        string="E-waste Collection (M18) id", readonly=True, copy=False, index=True
    )
    ewaste_collection_ref = fields.Char(
        string="E-waste Collection (M18)", readonly=True, copy=False
    )

    provenance_ids = fields.One2many(
        "fix.tradein.provenance", "tradein_id", string="Provenance Screens"
    )

    # ------------------------------------------------------------------ computes
    @api.depends("parts_cost", "labour_cost", "refurbishment_ids.total_cost")
    def _compute_refurb_cost(self):
        for rec in self:
            steps = sum(rec.refurbishment_ids.mapped("total_cost"))
            rec.steps_cost = steps
            rec.refurbishment_cost = (rec.parts_cost or 0.0) + (rec.labour_cost or 0.0) + steps

    @api.depends("offered_value", "graded_value", "refurbishment_cost")
    def _compute_inventory_valuation(self):
        for rec in self:
            acquisition = rec.graded_value or rec.offered_value or 0.0
            rec.inventory_valuation = acquisition + (rec.refurbishment_cost or 0.0)

    @api.depends("graded_value", "tds_applicable", "tds_rate_pct", "psr_verified", "taxpayer_tin")
    def _compute_tds(self):
        for rec in self:
            val = rec.graded_value or 0.0
            # ITA 2023 s.142: withholding without a sighted PSR or e-TIN is
            # lifted by half again (the estate's x1.5 uplift, M53/M52 pattern).
            # PSR counts only with its e-TIN (M14-10): the tick alone cut TDS.
            rate = rec.tds_rate_pct or 0.0
            tin = (rec.taxpayer_tin or "").strip()
            if rec.tds_applicable and rate > 0 and not ((rec.psr_verified and tin) or tin):
                rate = round(rate * 1.5, 4)
            rec.tds_effective_rate_pct = rate if rec.tds_applicable else 0.0
            tds = round(val * (rate / 100.0), 2) if rec.tds_applicable and rate > 0 else 0.0
            rec.tds_amount = tds
            rec.net_payout = max(0.0, val - tds)

    @api.depends("graded_value", "accepted_offer_value", "offered_value", "revision_accepted_value")
    def _compute_revision_state(self):
        for rec in self:
            accepted = rec.accepted_offer_value or rec.offered_value or 0.0
            if not rec.graded_value or rec.graded_value >= accepted - _EPS:
                rec.revision_state = "none"
            elif abs((rec.revision_accepted_value or 0.0) - rec.graded_value) <= _EPS:
                rec.revision_state = "accepted"
            else:
                rec.revision_state = "pending"

    # --------------------------------------------------------------- constraints
    @api.constrains("customer_nid", "taxpayer_tin", "customer_id")
    def _check_statutory_ids(self):
        for rec in self:
            nid = (rec.customer_nid or "").strip()
            if nid:
                if not _NID_RE.match(nid):
                    raise ValidationError(
                        "Customer NID %r is not a 10-digit Smart NID or a 17-digit NID."
                        % rec.customer_nid
                    )
                if nid_placeholder(nid):
                    raise ValidationError(
                        "Customer NID %s is a placeholder (one digit repeated or a run of "
                        "consecutive digits), not a person's identity number." % nid
                    )
                # M14-7: one NID, one seller. Live data had one NID on five
                # different customers.
                other = (
                    self.sudo()
                    .with_context(active_test=False)
                    .search(
                        [
                            ("customer_nid", "=", nid),
                            ("id", "!=", rec.id),
                            (
                                "customer_id.commercial_partner_id",
                                "!=",
                                rec.customer_id.commercial_partner_id.id,
                            ),
                        ],
                        limit=1,
                    )
                )
                if other:
                    raise ValidationError(
                        "NID %s is already bound to another customer (trade-in %s). An "
                        "identity number belongs to one seller." % (nid, other.name)
                    )
            tin = (rec.taxpayer_tin or "").strip()
            if tin and (not _ETIN_RE.match(tin) or len(set(tin)) == 1):
                raise ValidationError("Taxpayer e-TIN %r is not 12 digits." % rec.taxpayer_tin)

    @api.constrains("offered_value", "resale_value", "parts_cost", "labour_cost", "graded_value")
    def _check_monetary_bounds(self):
        for rec in self:
            if rec.offered_value < 0:
                raise ValidationError("Offered value cannot be negative")
            if rec.graded_value < 0:
                raise ValidationError("Graded value cannot be negative")
            if rec.resale_value < 0:
                raise ValidationError("Resale value cannot be negative")
            if rec.parts_cost < 0:
                raise ValidationError("Parts cost cannot be negative")
            if rec.labour_cost < 0:
                raise ValidationError("Labour cost cannot be negative")

    @api.constrains("tds_applicable", "tds_rate_pct", "tds_section")
    def _check_tds_rate(self):
        """The contract rate may exceed the statutory rate, never undercut it."""
        for rec in self.filtered("tds_applicable"):
            rate_row = rec._tds_rate_row()
            if rate_row and (rec.tds_rate_pct or 0.0) < rate_row.rate - 1e-6:
                raise ValidationError(
                    "The TDS rate %.2f%% is below the statutory %.2f%% of %s."
                    % (rec.tds_rate_pct, rate_row.rate, rate_row.section or rate_row.code)
                )

    @api.constrains("tds_certificate_no")
    def _check_certificate_unique(self):
        for rec in self.filtered("tds_certificate_no"):
            if self.sudo().search_count(
                [("tds_certificate_no", "=", rec.tds_certificate_no), ("id", "!=", rec.id)]
            ):
                raise ValidationError(
                    "TDS certificate %s is already used on another trade-in."
                    % rec.tds_certificate_no
                )

    # ------------------------------------------------------------- guard + freeze
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._GUARDED

    def _tradein_frozen_fields(self) -> set:
        self.ensure_one()
        if self.state in _DONE:
            return {
                name
                for name, field in self._fields.items()
                if field.store and name not in self._DONE_EDITABLE
            }
        rank = _ORDER.index(self.state)
        frozen = set()
        for state, names in self._FROZEN_FROM.items():
            if rank >= _ORDER.index(state):
                frozen |= names
        if self.payout_approval_state in ("pending", "approved"):
            frozen |= {"dofa_justification"}
        return frozen

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        for rec in self:
            locked |= rec._tradein_frozen_fields()
        return locked

    def _tradein_refuse_direct(self, vals):
        guarded = self._fix_guarded_fields() & set(vals)
        changed = {
            name
            for rec in self
            for name in guarded
            if rec._fix_guard_differs(name, vals[name], rec[name])
        }
        if changed:
            self._fix_guard_refuse(changed)
        for rec in self:
            frozen = rec._tradein_frozen_fields() & set(vals)
            names = [n for n in frozen if rec._fix_guard_differs(n, vals[n], rec[n])]
            if names:
                labels = ", ".join(sorted(self._fields[n].string or n for n in names))
                if rec.state in _DONE:
                    raise UserError(
                        "Trade-in %s is %s: it is a closed record and %s can no longer "
                        "change." % (rec.name, rec.state, labels)
                    )
                raise UserError(
                    "Trade-in %s is %s: %s is frozen at this stage. A revised offer goes "
                    "through a new valuation and the customer's re-acceptance."
                    % (rec.name, rec.state, labels)
                )

    # ------------------------------------------------------------- create / write
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.request") or "TRD/New"
                )
        return super().create(vals_list)

    def _tradein_payout_terms(self):
        """What a payout approval covers (E5 / M14-4)."""
        self.ensure_one()
        rec = self.sudo()
        return (
            rec.customer_id.id,
            round(rec.graded_value or 0.0, 2),
            round(rec.net_payout or 0.0, 2),
            round(rec.tds_amount or 0.0, 2),
            (rec.customer_nid or "").strip(),
            bool(rec.tds_applicable),
            round(rec.tds_rate_pct or 0.0, 4),
            rec.tds_section or "",
            bool(rec.psr_verified),
            (rec.taxpayer_tin or "").strip(),
            rec.currency_id.id,
        )

    def write(self, vals):
        if self and not self._fix_guard_open():
            self._tradein_refuse_direct(vals)
        # A paid payout's amount never moves, whoever writes (treasury has it).
        if "graded_value" in vals:
            for rec in self:
                sent = rec.state == "closed" or (
                    rec.payout_execution_id and rec.payout_approval_state in ("pending", "approved")
                )
                if sent and rec._fix_guard_differs(
                    "graded_value", vals["graded_value"], rec.graded_value
                ):
                    raise UserError("Payout for %s has already been sent to treasury" % rec.name)
        if "state" in vals and not self.env.su:
            for rec in self:
                if rec.state != vals["state"]:
                    rec._tradein_assert_gate(vals["state"])
        watched = self.filtered(lambda r: r.payout_approval_state in ("pending", "approved"))
        terms = {rec.id: rec._tradein_payout_terms() for rec in watched}
        psr = {
            rec.id: ((rec.taxpayer_tin or "").strip(), rec.psr_attachment_id.id)
            for rec in self.filtered("psr_verified")
        }
        result = super().write(vals)
        # M14-10: a PSR is verified against one e-TIN and one document.
        stale = self.filtered(
            lambda r: r.id in psr
            and ((r.taxpayer_tin or "").strip(), r.psr_attachment_id.id) != psr[r.id]
        )
        if stale:
            stale._guarded().write(
                {"psr_verified": False, "psr_verified_by_id": False, "psr_verified_at": False}
            )
        for rec in watched:
            if rec.payout_approval_state in ("pending", "approved") and (
                rec._tradein_payout_terms() != terms[rec.id]
            ):
                rec._tradein_void_payout(
                    "the payee, NID, graded value, TDS or net payout changed after the payout "
                    "approval was %s; it covered the terms it was given for. Request it again."
                    % ("requested" if rec.payout_approval_state == "pending" else "granted")
                )
        return result

    # ------------------------------------------------------------------ helpers
    def _operating_unit(self):
        """M03 consignments and M50 payouts are OU-scoped (operating_unit_id
        is required on both): the request's OU, else the acting user's
        default OU."""
        self.ensure_one()
        ou = self.operating_unit_id or self.env.user.default_operating_unit_id
        if not ou:
            raise UserError(
                "Trade-in %s has no operating unit — logistics and payout are OU-scoped" % self.name
            )
        return ou

    def _refurb_workshop(self):
        """The M31 facility for the refurbishment job: the company's central
        depot when there is one, else any active workshop of the company."""
        self.ensure_one()
        workshops = self.env["fix.workshop"].sudo()
        domain = [("company_id", "=", self.company_id.id)]
        workshop = workshops.search([*domain, ("workshop_type", "=", "central")], limit=1)
        workshop = workshop or workshops.search(domain, limit=1)
        if not workshop:
            raise UserError(
                "No active M31 workshop is configured for %s — refurbishment cannot be "
                "scheduled" % self.company_id.name
            )
        return workshop

    def _tds_rate_row(self):
        self.ensure_one()
        code = _TDS_RATE_CODE.get(self.tds_section or "")
        if not code:
            return self.env["fix.tax.rate"]
        return (
            self.env["fix.tax.rate"]
            .sudo()
            .search(
                [
                    ("tax_kind", "=", "tds"),
                    ("code", "=", code),
                    ("company_id", "in", (False, self.company_id.id)),
                ],
                order="company_id desc, id desc",
                limit=1,
            )
        )

    @staticmethod
    def _wipe_gate_denial(cert, device=None) -> str:
        """'' when ``cert`` is a VERIFIED M06 wipe certificate for this
        device's media serial, else why not. A02 audit M06-1: the status alone
        was forgeable and one certificate released any number of devices."""
        if not cert:
            return "no M06 data wipe certificate is attached"
        return cert._fix_certify_denial(cert._fix_media_serial(device))

    # ---- provenance (E7, M14-5/6) ---------------------------------------------
    def _provenance_rows(self):
        self.ensure_one()
        return self.env["fix.tradein.provenance"].sudo().search([("tradein_id", "=", self.id)])

    def _provenance_hard_stop(self) -> str:
        """'' unless the device is flagged stolen or blacklisted. A hit is a hard
        stop with no override: no newer row, clearance or action lifts it."""
        self.ensure_one()
        hit = self._provenance_rows().filtered(
            lambda p: p.stolen_hit or p.blacklist_hit or p.state == "flagged"
        )
        if hit:
            return (
                "provenance screen %s flagged the device (stolen/blacklisted). A flagged device "
                "is a hard stop: it is not traded, refurbished, resold or paid for." % hit[0].name
            )
        device = self.device_id.sudo()
        if device and "state" in device._fields and device.state == "lost":
            return "device %s is registered LOST/STOLEN in the device registry" % device.name
        return ""

    def _provenance_current(self):
        """The latest cleared screen, if it is still current."""
        self.ensure_one()
        days = int(_param_float(self.env, PARAM_PROVENANCE_VALIDITY_DAYS, 30))
        cutoff = fields.Date.context_today(self) - timedelta(days=max(days, 0))
        rows = self._provenance_rows().filtered(
            lambda p: p.state == "cleared" and p.checked_on and p.checked_on >= cutoff
        )
        return rows.sorted(lambda p: (p.checked_on, p.id), reverse=True)[:1]

    def _provenance_denial(self) -> str:
        self.ensure_one()
        stop = self._provenance_hard_stop()
        if stop:
            return stop
        current = self._provenance_current()
        if not current:
            return (
                "the device has no current, cleared provenance screen (IMEI, blacklist, "
                "stolen and activation-lock check by a provenance officer)"
            )
        device = self.device_id.sudo()
        imeis = {i for i in (device.imei_1, device.imei_2) if i} if device else set()
        if imeis and current.imei not in imeis:
            return "provenance screen %s checked IMEI %s, not this device's IMEI" % (
                current.name,
                current.imei,
            )
        if current.btrc_neir_status != "valid" and not _param_on(
            self.env, PARAM_ALLOW_NEIR_UNCHECKED, "0"
        ):
            return (
                "the BTRC NEIR status of %s is '%s': no NEIR check has run (the NEIR register "
                "relaunches 1 January 2027), and trading unchecked devices is not allowed "
                "(system parameter %s)"
                % (current.imei, current.btrc_neir_status, PARAM_ALLOW_NEIR_UNCHECKED)
            )
        return ""

    # ---- refurbishment / QA ----------------------------------------------------
    def _qa_latest(self):
        self.ensure_one()
        return (
            self.env["fix.refurb.qa"]
            .sudo()
            .search(
                [("tradein_id", "=", self.id), ("qa_state", "in", ("pass", "fail"))],
                order="id desc",
                limit=1,
            )
        )

    def _refurb_denial(self) -> str:
        self.ensure_one()
        steps = self.sudo().refurbishment_ids
        if not steps:
            return "the unit has no refurbishment step plan"
        open_steps = steps.filtered(lambda s: s.state != "done")
        if open_steps:
            return "%d refurbishment step(s) are not done (%s)" % (
                len(open_steps),
                ", ".join(open_steps.mapped("name")),
            )
        qa = self._qa_latest()
        if not qa or qa.qa_state != "pass":
            return "the unit has no passed QA (the latest QA result is %s)" % (
                qa.qa_state if qa else "missing"
            )
        return ""

    def _hold_denial(self) -> str:
        self.ensure_one()
        if not self.hold_until:
            return "the trade-in hold period has not started (no collection recorded)"
        if fields.Date.context_today(self) < self.hold_until:
            return "the trade-in hold period runs until %s" % self.hold_until
        return ""

    # ---- the gate of each state (E4) -------------------------------------------
    def _tradein_gate_denial(self, target) -> str:
        """Why this record may not enter `target`, or ''. Runs in every
        transition and again in write() for every non-superuser state change,
        so no path (action, routed decision, P03, RPC) skips it."""
        self.ensure_one()
        if target in ("draft", "rejected"):
            return ""
        stop = self._provenance_hard_stop()
        if stop:
            return stop
        if target == "offered" and (self.offered_value or 0.0) <= 0:
            return "an offer requires a positive valuation"
        if target in ("accepted", "collected"):
            return self._provenance_denial()
        if target in ("wiped", "refurbished", "graded", "resale_ready", "closed"):
            denial = self._wipe_gate_denial(self.wipe_certificate_id, self.device_id)
            if denial:
                return "Journey 9 wipe gate: %s" % denial
        if target in ("graded", "resale_ready"):
            denial = self._refurb_denial()
            if denial:
                return denial
        if target == "resale_ready":
            if not self.device_id:
                return "a unit without a registered device cannot be stocked or resold"
            if not self.refurb_grade_id:
                return "a unit is stocked on its M37 grade: set the master grade"
            if self.grade == "e":
                return "a grade E unit is parts only: harvest it, do not resell it"
            denial = self._hold_denial()
            if denial:
                return denial
        if target == "closed":
            denial = self._provenance_denial()
            if denial:
                return denial
        return ""

    def _tradein_assert_gate(self, target):
        for rec in self:
            denial = rec._tradein_gate_denial(target)
            if denial:
                raise UserError("Trade-in %s cannot move to %s: %s." % (rec.name, target, denial))

    def _tradein_move(self, target, extra=None):
        for rec in self:
            rec._tradein_assert_gate(target)
            vals = dict(extra or {}, state=target)
            rec._guarded().write(vals)

    # ------------------------------------------------------------------ offer
    def _offer_valuation(self):
        self.ensure_one()
        return (
            self.env["fix.tradein.valuation"]
            .sudo()
            .search(
                [("tradein_id", "=", self.id), ("state", "=", "applied")],
                order="id desc",
                limit=1,
            )
        )

    def action_send_offer(self):
        for rec in self:
            # M14-13: a closed, paid trade-in was reopened to 'offered'.
            if rec.state != "draft":
                raise UserError(
                    "Trade-in %s is '%s': an offer is sent from draft only." % (rec.name, rec.state)
                )
            if rec.offered_value <= 0:
                raise UserError("An offer requires a positive valuation")
            if _param_on(self.env, PARAM_OFFER_REQUIRES_VALUATION, "1"):
                val = rec._offer_valuation()
                if not val or abs(val.applied_offer - rec.offered_value) > _EPS:
                    raise UserError(
                        "The offer of %s must come from an applied valuation on the governed "
                        "price grid (an override is approved by a valuation manager). Run "
                        "the valuation and apply it." % rec.name
                    )
            rec._tradein_move("offered")
            publish(
                self.env,
                "tradein.offered",
                "fix.tradein.request",
                rec.id,
                {"customer": rec.customer_id.name, "value": float(rec.offered_value)},
            )

    def action_accept(self):
        """The customer accepts the offer: recorded with its channel, who
        recorded it and the value accepted (M14-19)."""
        for rec in self:
            if rec.state != "offered":
                raise UserError("Accept from offered")
            rec._tradein_move(
                "accepted",
                {
                    "accepted_offer_value": rec.offered_value,
                    "accepted_at": fields.Datetime.now(),
                    "accepted_by_id": self.env.uid,
                },
            )

    def action_reject(self, reason=None):
        """The customer declines (the offer, or the revised value after
        inspection). Before any money: a device already collected is
        returned to the customer through the consignment desk."""
        for rec in self:
            if not (reason or "").strip():
                raise UserError("State why the trade-in is rejected.")
            if rec.state in _DONE or rec.payout_execution_id:
                raise UserError("Trade-in %s is %s and cannot be rejected." % (rec.name, rec.state))
            if rec.payout_approval_state in ("pending", "approved"):
                raise UserError(
                    "Trade-in %s has a payout approval %s: recall or reject it first."
                    % (rec.name, rec.payout_approval_state)
                )
            rec._tradein_move("rejected", {"rejected_reason": reason.strip()})
            rec.message_post(body="Trade-in rejected: %s" % reason.strip())
        return True

    def action_accept_revision(self):
        """The customer accepts the revised (graded) value (P2)."""
        for rec in self:
            if rec.revision_state != "pending":
                raise UserError("Trade-in %s has no revised value awaiting acceptance." % rec.name)
            rec._guarded().write(
                {
                    "revision_accepted_value": rec.graded_value,
                    "revision_accepted_at": fields.Datetime.now(),
                    "revision_accepted_by_id": self.env.uid,
                }
            )
            rec.message_post(
                body="Customer accepted the revised value BDT %.2f (offer was BDT %.2f) via %s."
                % (
                    rec.graded_value,
                    rec.accepted_offer_value or rec.offered_value,
                    dict(rec._fields["acceptance_channel"].selection).get(rec.acceptance_channel),
                )
            )
        return True

    # ------------------------------------------------------------------ intake
    def action_collect(self):
        """Collection through M03 logistics (unbroken custody chain begins)."""
        for rec in self:
            if rec.state != "accepted":
                raise UserError("Collect from accepted")
            rec._tradein_assert_gate("collected")
            ou = rec._operating_unit()
            consignment = rec.consignment_id
            if not consignment:
                # sudo after the gate: the trade-in desk books the pickup
                # without logistics rights (A05 audit M14-21)
                consignment = (
                    self.env["fix.consignment"]
                    .sudo()
                    .create(
                        {
                            "consignment_type": "pickup",
                            "scheduled_date": fields.Datetime.now(),
                            "operating_unit_id": ou.id,
                        }
                    )
                )
            hold_days = int(_param_float(self.env, PARAM_HOLD_DAYS, 7))
            rec._tradein_move(
                "collected",
                {
                    "consignment_id": consignment.id,
                    "hold_until": fields.Date.context_today(rec)
                    + timedelta(days=max(hold_days, 0)),
                    "hold_released": False,
                },
            )
            publish(
                self.env,
                "tradein.collected",
                "fix.tradein.request",
                rec.id,
                {
                    "device": rec.device_id.name if rec.device_id else "",
                    "consignment": rec.consignment_id.name if rec.consignment_id else "",
                },
            )

    def action_wipe(self):
        """The secure data wipe gate: the wipe operator's M06 certificate
        (evidence entered and verified in cd_data_case) must be attached and
        VERIFIED. Nothing is certified here - no certificate is created."""
        for rec in self:
            if rec.state != "collected":
                raise UserError("Wipe from collected")
            denial = rec._wipe_gate_denial(rec.wipe_certificate_id, rec.device_id)
            if denial:
                raise UserError("Journey 9 wipe gate: %s" % denial)
            rec._tradein_move("wiped")
            publish(
                self.env,
                "tradein.wiped",
                "fix.tradein.request",
                rec.id,
                {
                    "certificate": rec.wipe_certificate_id.name,
                    "method": rec.wipe_certificate_id.method,
                    "verification_hash": rec.wipe_certificate_id.verification_hash,
                },
            )

    def action_refurbish(self):
        """Refurbishment on M31's workshop model (composes the estate).
        STRICT WIPE GATE: cannot refurbish without valid M06 data wipe certificate."""
        for rec in self:
            if rec.state != "wiped":
                raise UserError("Refurbish from data-wiped (the wipe gate)")
            denial = rec._wipe_gate_denial(rec.wipe_certificate_id, rec.device_id)
            if denial:
                raise UserError(
                    "Journey 9 gate violation: refurbishment is strictly blocked "
                    "without a verified M06 data wipe certificate (%s)." % denial
                )
            rec._tradein_assert_gate("refurbished")

            # Create or link workshop job if absent (sudo after the gate: the
            # trade-in desk sends units to the bench, A05 audit M14-21)
            job = rec.workshop_job_id
            if not job:
                job = (
                    self.env["fix.workshop.job"]
                    .sudo()
                    .create(
                        {
                            "workshop_id": rec._refurb_workshop().id,
                            "device_id": rec.device_id.id if rec.device_id else False,
                            "customer_id": rec.customer_id.id,
                            "fault_description": "Trade-in refurbishment (%s): clean, test, "
                            "replace worn components" % rec.name,
                        }
                    )
                )

            # the Refurb Work Orders screen reads fix.refurbishment: create the
            # step plan once per unit so the workspace grid is the real plan,
            # not an empty model beside a workshop job
            steps = self.env["fix.refurbishment"]
            if not steps.sudo().search_count([("tradein_id", "=", rec.id)]):
                labels = dict(steps._fields["step"].selection)
                now = fields.Datetime.now()
                for step in ("intake", "repair", "cosmetic", "testing", "final_qa"):
                    steps._guarded().create(
                        {
                            "name": "%s · %s" % (rec.name, labels.get(step, step)),
                            "tradein_id": rec.id,
                            "company_id": rec.company_id.id,
                            "step": step,
                            "state": "done" if step == "intake" else "pending",
                            "completed_at": now if step == "intake" else False,
                            "completed_by_id": self.env.uid if step == "intake" else False,
                            "parts_cost": 0.0,
                        }
                    )

            rec._tradein_move("refurbished", {"workshop_job_id": job.id})
            publish(
                self.env,
                "tradein.refurbished",
                "fix.tradein.request",
                rec.id,
                {
                    "workshop_job": rec.workshop_job_id.name if rec.workshop_job_id else "",
                    "refurb_cost": float(rec.refurbishment_cost),
                },
            )

    def action_grade(self):
        """Grading against M37's refurbishment grades."""
        for rec in self:
            if rec.state != "refurbished":
                raise UserError("Grade from refurbished")
            if not rec.grade and not rec.refurb_grade_id:
                raise UserError("A grade is required before resale")
            rec._tradein_assert_gate("graded")

            # Auto-align selection and master grade
            vals = {}
            if rec.refurb_grade_id and not rec.grade:
                code_map = {"A": "a", "B": "b", "C": "c", "D": "d", "E": "e"}
                vals["grade"] = code_map.get(rec.refurb_grade_id.code, "b")
            elif rec.grade and not rec.refurb_grade_id:
                master_grade = self.env["fix.refurb.grade"].search(
                    [("code", "=", rec.grade.upper())], limit=1
                )
                if master_grade:
                    vals["refurb_grade_id"] = master_grade.id

            # Auto-compute resale value if not manually set
            if not rec.resale_value or rec.resale_value <= 0:
                grade_id = vals.get("refurb_grade_id") or rec.refurb_grade_id.id
                master = self.env["fix.refurb.grade"].browse(grade_id) if grade_id else None
                multiplier = master.price_multiplier if master else 1.0
                base_benchmark = max(rec.offered_value * 1.6, 1000.0)
                vals["resale_value"] = base_benchmark * multiplier
            if vals:
                rec.write(vals)

            rec._tradein_move("graded")
            publish(
                self.env,
                "tradein.graded",
                "fix.tradein.request",
                rec.id,
                {
                    "grade": rec.grade,
                    "grade_master": rec.refurb_grade_id.name if rec.refurb_grade_id else "",
                    "resale_value": float(rec.resale_value),
                },
            )

    def action_resale_ready(self):
        """The resale seam: M15 graded inventory stock + M12 marketplace listing seam."""
        for rec in self:
            if rec.state != "graded":
                raise UserError("Resale from graded")
            rec._tradein_assert_gate("resale_ready")

            # Create M15 graded inventory stock entry, capitalised at what the
            # seller is paid (the graded value), not the offer (M14-15)
            stock = rec.graded_stock_id
            if not stock:
                stock = (
                    self.env["fix.graded.stock"]
                    .sudo()
                    .create(
                        {
                            "device_id": rec.device_id.id,
                            "grade_id": rec.refurb_grade_id.id,
                            "company_id": rec.company_id.id,
                            "acquisition_cost": rec.graded_value or rec.offered_value,
                            "refurbishment_cost": rec.refurbishment_cost,
                            "resale_price": rec.resale_value,
                            "state": "in_stock",
                            # the graded-stock screen shows the origin trade-in
                            "tradein_id": rec.id,
                            "tradein_ref": rec.name,
                        }
                    )
                )
            rec._tradein_move("resale_ready", {"graded_stock_id": stock.id})
            rec._tradein_list_on_marketplace()
            publish(
                self.env,
                "tradein.resale_ready",
                "fix.tradein.request",
                rec.id,
                {
                    "grade": rec.grade,
                    "resale_value": float(rec.resale_value),
                    "inventory_valuation": float(rec.inventory_valuation),
                    "graded_stock": rec.graded_stock_id.name if rec.graded_stock_id else "",
                },
            )

    def _tradein_list_on_marketplace(self):
        """E10 / M14-17: a marketplace-channel unit is listed through M12's own
        public path (fix.marketplace.order.action_list_refurb_resale). M12
        depends on this module, so it is reached only when installed."""
        self.ensure_one()
        if self.resale_channel != "marketplace" or self.marketplace_order_id:
            return
        Order = self.env.get("fix.marketplace.order")
        if Order is None:
            return
        try:
            with self.env.cr.savepoint():
                order = Order.sudo().create(
                    {
                        "customer_id": (
                            self.marketplace_seller_id or self.company_id.partner_id
                        ).id,
                        "description": "Refurbished %s, grade %s (trade-in %s)"
                        % (
                            self.device_model_id.name or self.device_id.name or "device",
                            (self.grade or "").upper(),
                            self.name,
                        ),
                        "company_id": self.company_id.id,
                        "tradein_request_id": self.id,
                    }
                )
                order.action_list_refurb_resale(
                    self.graded_stock_id,
                    self.resale_value,
                    battery_health=float(self.battery_health_pct or 0),
                    defects="Grade %s refurbished unit; QA %s"
                    % ((self.grade or "").upper(), self._qa_latest().name or ""),
                )
                self._guarded().write(
                    {"marketplace_order_id": order.id, "resale_listed_on": fields.Date.today()}
                )
        except Exception as exc:  # the stock is booked; the listing is retried by hand
            _logger.warning("M12 listing of %s failed: %s", self.name, exc)
            self.message_post(body="The M12 marketplace listing could not be created: %s" % exc)

    # ---------------------------------------------------- payout approval (E5)
    def _approval_group_xmlid(self):
        return GROUP_PAYOUT_APPROVER

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {
            "customer_id",
            "customer_nid",
            "tds_applicable",
            "tds_rate_pct",
            "tds_section",
            "psr_verified",
            "taxpayer_tin",
            "graded_value",
        }

    def _approval_resolve(self, rule, tier):
        """The DOFA tier holders who also hold the payout approver role."""
        pairs = super()._approval_resolve(rule, tier)
        return [(u, b) for u, b in pairs if (b or u).has_group(GROUP_PAYOUT_APPROVER)]

    def _tradein_check_payout_request(self):
        for rec in self:
            if rec.state not in ("resale_ready", "graded"):
                raise UserError("Payout approval from graded or resale-ready")
            if rec.graded_value <= 0:
                raise UserError(
                    "Enter the graded payout value (the device's value as inspected) "
                    "before requesting payout approval"
                )
            if rec.payout_approval_state == "approved":
                raise UserError("Payout for %s is already approved" % rec.name)
            if rec.revision_state == "pending":
                raise UserError(
                    "The graded value BDT %.2f is below the accepted offer: the customer must "
                    "accept the revised value first." % rec.graded_value
                )
            stop = rec._provenance_hard_stop()
            if stop:
                raise UserError("Payout blocked: %s" % stop)

    def action_request_approval(self, justification=None):
        """Route the payout for approval (M63). Also the P03 button."""
        self._tradein_check_payout_request()
        result = super().action_request_approval(justification=justification)
        for rec in self:
            rec._guarded().write(
                {
                    "payout_approval_state": "pending",
                    "payout_requested_by_id": self.env.uid,
                    "payout_approved_by_id": False,
                    "payout_approved_at": False,
                }
            )
        return result

    def action_request_payout_approval(self, justification=None):
        """Submit the graded payout value for approval (after grading) — A11
        P2 entry point: defaults the justification to the graded amount."""
        for rec in self:
            rec.action_request_approval(
                justification=justification
                or "Trade-in payout of BDT %.2f" % (rec.graded_value or 0.0)
            )
        return True

    def _approval_on_rejected(self, comment):
        """A11 audit P2: an inbox rejection declines the payout — the grader
        re-grades or lets the request lapse."""
        for rec in self:
            if rec.payout_approval_state == "pending":
                rec.write({"payout_approval_state": "rejected"})
            rec.message_post(
                body="Payout approval rejected by %s: %s"
                % (rec.env.user.name, comment or "no comment recorded")
            )

    def action_approve_payout(self):
        """The routed decision: run from the approver's inbox task only. Four
        eyes (never the requester), the payout approver role, and the DOFA
        tier, creator SoD and justification of action_dofa_approve. Pins the
        payee, NID, net and TDS with the amount."""
        self._approval_assert_routed()
        for rec in self:
            if rec.payout_approval_state != "pending":
                raise UserError("Only a pending payout can be approved")
            if rec.payout_requested_by_id and rec.payout_requested_by_id in (
                rec._approval_acting_users()
            ):
                raise UserError("Four-eyes: the payout requester cannot approve their own payout")
            if not rec._approval_authority_user().has_group(GROUP_PAYOUT_APPROVER):
                raise AccessError(
                    "Approving a trade-in payout needs the Trade-In Payout Approver role."
                )
            if rec.revision_state == "pending":
                raise UserError("The customer has not accepted the revised value.")
            rec.action_dofa_approve()
            rec._guarded().write(
                {
                    "payout_approval_state": "approved",
                    "payout_approved_by_id": self.env.uid,
                    "payout_approved_at": fields.Datetime.now(),
                    "payout_approved_partner_id": rec.customer_id.id,
                    "payout_approved_net": rec.net_payout
                    if rec.tds_applicable
                    else rec.graded_value,
                    "payout_approved_tds": rec.tds_amount if rec.tds_applicable else 0.0,
                    "payout_approved_nid": (rec.customer_nid or "").strip(),
                }
            )
        return True

    def action_reject_payout(self, reason=None):
        """Rejected from the approver's inbox (the task's Reject, with a
        reason). Pressed directly it is refused, like the approval."""
        for rec in self:
            if rec.payout_approval_state != "pending":
                raise UserError("Only a pending payout can be rejected")
        self._approval_assert_routed()
        for rec in self:
            if rec.payout_requested_by_id and rec.payout_requested_by_id in (
                rec._approval_acting_users()
            ):
                raise UserError("Four-eyes: the payout requester cannot reject their own payout")
            if not rec._approval_authority_user().has_group(GROUP_PAYOUT_APPROVER):
                raise AccessError(
                    "Rejecting a trade-in payout needs the Trade-In Payout Approver role."
                )
            if not (reason or "").strip():
                raise UserError("State why the payout is rejected.")
            rec._tradein_payout_reset("rejected")
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec._tradein_payout_reset("rejected")
        return super()._approval_on_rejected(comment)

    def _approval_clear_stamp(self, reason):
        for rec in self.filtered(lambda r: r.payout_approval_state in ("pending", "approved")):
            rec._tradein_payout_reset("none")
        return super()._approval_clear_stamp(reason)

    def _tradein_payout_reset(self, state):
        for rec in self:
            rec.sudo()._guarded().write(
                {
                    "payout_approval_state": state,
                    "payout_approved_by_id": False,
                    "payout_approved_at": False,
                    "payout_approved_partner_id": False,
                    "payout_approved_net": 0.0,
                    "payout_approved_tds": 0.0,
                    "payout_approved_nid": False,
                }
            )

    def _tradein_void_payout(self, reason):
        for rec in self:
            if rec.approval_state in ("pending", "approved"):
                rec._approval_void(reason)  # clears the DOFA stamp and the payout
            if rec.payout_approval_state in ("pending", "approved"):
                rec._tradein_payout_reset("none")
            if rec.dofa_approved:
                rec.sudo()._guarded().write(
                    {
                        "dofa_approved": False,
                        "dofa_approved_by": False,
                        "dofa_approved_at": False,
                        "dofa_approved_tier": False,
                        "dofa_approved_amount": 0.0,
                    }
                )
            rec.message_post(body="Payout approval withdrawn: %s" % reason)

    # ---------------------------------------------------------------- PSR (M14-10)
    def action_verify_psr(self):
        """Record the sighted PSR: needs the seller's 12-digit e-TIN and the PSR
        document, and is recorded by someone other than the trade-in's creator."""
        for rec in self:
            if rec.state in _DONE:
                raise UserError("Trade-in %s is %s." % (rec.name, rec.state))
            if not _ETIN_RE.match((rec.taxpayer_tin or "").strip()):
                raise UserError("A PSR is verified against the seller's 12-digit e-TIN: enter it.")
            if not rec.psr_attachment_id:
                raise UserError("Attach the PSR document before verifying it.")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: the PSR of a trade-in you raised is verified by "
                    "someone else."
                )
            rec._guarded().write(
                {
                    "psr_verified": True,
                    "psr_verified_by_id": self.env.uid,
                    "psr_verified_at": fields.Datetime.now(),
                }
            )
        return True

    # --------------------------------------------------------------- the payout
    def _kyc_denial(self) -> str:
        self.ensure_one()
        nid = (self.customer_nid or "").strip()
        if not _NID_RE.match(nid) or nid_placeholder(nid):
            return "customer NID %s is not a valid identity number" % (nid or "(none)")
        if _param_on(self.env, PARAM_KYC_VERIFIED_NID, "1"):
            current = self._provenance_current()
            if not current:
                return "the device has no current, cleared provenance screen"
            if not (
                current.customer_nid_verified and (current.customer_nid_no or "").strip() == nid
            ):
                return (
                    "NID %s has not been verified against this seller by a provenance "
                    "officer (KYC policy %s)" % (nid, PARAM_KYC_VERIFIED_NID)
                )
        cap = _param_float(self.env, PARAM_KYC_CAP, 100000.0)
        if cap > 0:
            since = fields.Datetime.now() - timedelta(days=30)
            paid = self.sudo().search(
                [
                    ("customer_nid", "=", nid),
                    ("id", "!=", self.id),
                    ("paid_at", ">=", since),
                ]
            )
            total = sum(paid.mapped("payout_amount")) + (
                self.net_payout if self.tds_applicable else self.graded_value
            )
            if total > cap + _EPS:
                return (
                    "payouts to NID %s would reach BDT %.2f in 30 days, above the KYC cap of "
                    "BDT %.2f (%s)" % (nid, total, cap, PARAM_KYC_CAP)
                )
        return ""

    def _tradein_raise_withholding(self):
        """E10 / M14-11: the withheld TDS as an M51 register line (state
        withheld), which finance deposits by challan and certifies. Created
        through the register's service path (sudo); idempotent per trade-in."""
        self.ensure_one()
        if not (self.tds_applicable and self.tds_amount > _EPS):
            return self.env["fix.withholding.line"]
        if self.withholding_line_id:
            return self.withholding_line_id
        rate_row = self._tds_rate_row()
        if not rate_row:
            raise UserError(
                "Payout blocked: BDT %.2f TDS is withheld under %s, but M51 has no statutory "
                "TDS rate row for that section, so the withholding cannot be registered for "
                "NBR remittance." % (self.tds_amount, self.tds_section)
            )
        tin = (self.taxpayer_tin or "").strip()
        uplifted = (self.tds_effective_rate_pct or 0.0) > (self.tds_rate_pct or 0.0) + 1e-6
        Line = self.env["fix.withholding.line"].sudo()
        line = Line.search([("source_ref", "=", self.name), ("tax_kind", "=", "tds")], limit=1)
        if not line:
            line = Line.create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": self._operating_unit().id,
                    "tax_kind": "tds",
                    "partner_id": self.customer_id.id,
                    "partner_tin": tin or False,
                    "rate_id": rate_row.id,
                    "document_date": fields.Date.context_today(self),
                    "currency_id": self.currency_id.id,
                    "base_amount": self.graded_value,
                    "rate": self.tds_rate_pct,
                    "multiplier": 1.5 if uplifted else 1.0,
                    "amount": self.tds_amount,
                    "psr_received": bool(self.psr_verified and tin),
                    "paid_by_bank": True,  # M50 pays by bank / MFS, never cash
                    "source_ref": self.name,
                }
            )
        return line

    def action_pay(self):
        """Trade-in payout through M50 treasury: the APPROVED graded value,
        never the pre-inspection offer regardless of grade. Statutory gates
        before a taka leaves: identified seller (NID), BTRC NEIR clearance,
        TDS registered where withholding applies, and DOFA authority
        covering the amount."""
        for rec in self:
            if rec.state not in ("resale_ready", "graded"):
                raise UserError("Payout from graded or resale-ready")
            if rec.graded_value <= 0:
                raise UserError("Payout needs the graded payout value")
            if rec.payout_approval_state != "approved":
                raise UserError(
                    "Payout for %s is '%s': it must be approved before it is paid"
                    % (rec.name, rec.payout_approval_state)
                )
            # M14-2: an approval nobody gave (no approver stamp, no routed
            # request decided) is not one.
            if not rec.payout_approved_by_id or rec.approval_state != "approved":
                raise UserError(
                    "Payout for %s has no recorded approver: request the approval again." % rec.name
                )
            # E5 / M14-4: the approval covers who is paid, the net and the TDS.
            approved = (
                rec.payout_approved_partner_id.id,
                round(rec.payout_approved_net, 2),
                round(rec.payout_approved_tds, 2),
                (rec.payout_approved_nid or "").strip(),
            )
            now = (
                rec.customer_id.id,
                round(rec.net_payout if rec.tds_applicable else rec.graded_value, 2),
                round(rec.tds_amount if rec.tds_applicable else 0.0, 2),
                (rec.customer_nid or "").strip(),
            )
            if approved != now:
                rec._tradein_void_payout("the payee, NID, net or TDS differs from the approval")
                raise UserError(
                    "Payout blocked: the payee, NID, net payout or TDS of %s is not what was "
                    "approved. The approval is withdrawn; request it again." % rec.name
                )
            # Identified seller (AML / ITA 2023): an anonymous payout is a
            # laundering vector, not a customer-convenience feature.
            if not (rec.customer_nid or "").strip():
                raise UserError(
                    "Payout blocked: customer Smart NID is required before any "
                    "trade-in money leaves (AML identification)"
                )
            if rec.revision_state == "pending":
                raise UserError("Payout blocked: the customer has not accepted the revised value.")
            denial = rec._kyc_denial()
            if denial:
                raise UserError("Payout blocked: %s." % denial)
            # BTRC provenance: a current cleared screen, and no hit on ANY row
            # (a newer clean row no longer masks a stolen one), plus the wipe.
            denial = rec._tradein_gate_denial("closed")
            if denial:
                raise UserError("Payout blocked: %s." % denial)
            # DOFA: the payout amount decides the tier that must sign it off.
            rec._dofa_assert_approved("A trade-in payout")

            # Queue the payout with M50 treasury. Only treasury releases it and
            # marks it executed on bank/MFS evidence; trade-in never asserts
            # the money left. Created with sudo after the approval checks
            # above: a branch user requests a payout without treasury rights.
            # The seller receives the NET (graded value − TDS): the withheld
            # tax is registered with M51 (fix.withholding.line) for NBR
            # remittance, never bundled into the seller's payout.
            net_to_seller = rec.net_payout if rec.tds_applicable else rec.graded_value
            withholding = rec._tradein_raise_withholding()
            payment = rec.payout_execution_id
            if not payment:
                payment = (
                    self.env["fix.payment.execution"]
                    .sudo()
                    .create(
                        {
                            "operating_unit_id": rec._operating_unit().id,
                            "source_model": "fix.tradein.request",
                            "source_id": rec.id,
                            "payee": rec.customer_id.name,
                            "partner_id": rec.customer_id.id,
                            "amount": net_to_seller,
                            "method": "mobile_fs",  # default bKash/Nagad
                        }
                    )
                )
            # M14-15: the stock is capitalised at what the seller is paid
            # (the graded value, TDS included), not the offer.
            stock = rec.graded_stock_id.sudo()
            if stock and abs(stock.acquisition_cost - rec.graded_value) > _EPS:
                stock.write({"acquisition_cost": rec.graded_value})

            rec._guarded().write(
                {
                    "state": "closed",
                    "payout_amount": net_to_seller,
                    "payout_execution_id": payment.id,
                    "withholding_line_id": withholding.id or False,
                    "paid_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "tradein.paid",
                "fix.tradein.request",
                rec.id,
                {
                    "payout": float(rec.payout_amount),
                    # the treasury instruction's reference (PEX/...)
                    "payment_ref": rec.payout_execution_id.display_name
                    if rec.payout_execution_id
                    else "",
                },
            )

    # ------------------------------------------------------------ E12 hold cron
    @api.model
    def cron_tradein_hold_period(self):
        """Release the hold on trade-ins whose hold period has run out (safe
        to re-run: a released hold is not released twice). A unit still
        flagged by provenance stays held."""
        today = fields.Date.context_today(self)
        due = self.sudo().search(
            [
                ("hold_until", "!=", False),
                ("hold_until", "<=", today),
                ("hold_released", "=", False),
                ("state", "not in", _DONE),
            ]
        )
        released = self.browse()
        for rec in due:
            if rec._provenance_hard_stop():
                continue
            rec._guarded().write({"hold_released": True})
            rec.message_post(body="Trade-in hold period ended on %s." % rec.hold_until)
            released |= rec
        return len(released)

    # ------------------------------------------- M18 reuse routing -> intake
    @api.model
    def consume_ewaste_reuse_routed(self, event):
        """R8 consumer of ewaste.reuse_routed: an e-waste item an assessor
        triaged as reuse/refurbish opens a DRAFT trade-in intake here.

        Superuser only (the relay); one intake per collection (a repeat
        delivery returns the existing one); the payload is a claim: the
        collection is re-read and must be 'routed'. The device, customer,
        company and wipe certificate come from the collection, never from
        the payload, and nothing is skipped downstream: the intake goes
        through valuation, provenance and the serial-bound M06 wipe gate like
        any trade-in, whatever data_bearing the payload says."""
        if not self.env.su:
            raise AccessError("E-waste reuse routing is consumed only by the event relay.")
        if event.get("aggregate") not in (None, "fix.ewaste.collection"):
            raise UserError("Reuse intake refused: the event is not an e-waste collection event.")
        try:
            coll_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            coll_id = 0
        existing = self.sudo().search([("ewaste_collection_id", "=", coll_id)], limit=1)
        if coll_id and existing:
            return {"model": self._name, "id": existing.id, "created": False}
        Collection = self.env.get("fix.ewaste.collection")
        if Collection is None:
            raise UserError("Reuse intake refused: M18 (cd_ewaste) is not installed.")
        coll = Collection.sudo().browse(coll_id).exists() if coll_id > 0 else None
        if not coll:
            raise UserError("Reuse intake refused: there is no e-waste collection #%s." % coll_id)
        if coll.state != "routed":
            raise UserError(
                "Reuse intake refused: collection %s is %s, not routed to M14."
                % (coll.name, coll.state)
            )
        vals = {
            "company_id": coll.company_id.id,
            "customer_id": coll.customer_id.id,
            "device_id": coll.device_id.id or False,
            "ewaste_collection_id": coll.id,
            "ewaste_collection_ref": coll.name,
            "offered_value": 0.0,
        }
        if "operating_unit_id" in coll._fields and coll.operating_unit_id:
            vals["operating_unit_id"] = coll.operating_unit_id.id
        if "wipe_certificate_id" in coll._fields and coll.wipe_certificate_id:
            # attached as evidence only: the wipe gate still re-checks it
            vals["wipe_certificate_id"] = coll.wipe_certificate_id.id
        rec = self.sudo().browse(self.sudo()._guarded().create(vals).id)
        rec.message_post(
            body="Opened from e-waste collection %s, triaged %s by M18. Valuation, "
            "provenance and the M06 wipe gate apply as for any trade-in."
            % (coll.name, coll.triage_grade or "")
        )
        return {"model": self._name, "id": rec.id, "created": True}

    # -------------------------------------------- E10 / M14-17 resale warranty
    @api.model
    def consume_graded_stock_sold(self, event):
        """R8 consumer of graded_stock.sold: the resold refurbished unit gets
        its warranty — the trade-in warranty record (active from the sale) and
        an M17 fix.warranty (extended cover, pending the warranty officer's
        verification). Superuser only (the relay); idempotent per stock unit;
        the payload is a claim, the stock unit is re-read."""
        if not self.env.su:
            raise AccessError("Resale warranties are issued only by the event relay.")
        try:
            stock_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            stock_id = 0
        if event.get("aggregate") not in (None, "fix.graded.stock"):
            raise UserError("Resale warranty refused: the event is not a graded-stock event.")
        stock = self.env["fix.graded.stock"].sudo().browse(stock_id).exists()
        if not stock:
            raise UserError("Resale warranty refused: there is no graded stock #%s." % stock_id)
        if stock.state != "sold":
            raise UserError(
                "Resale warranty refused: %s is %s, not sold." % (stock.name, stock.state)
            )
        rec = self.sudo().browse(stock.tradein_id or 0).exists()
        if not rec:
            return {"created": False, "reason": "not a trade-in unit"}
        Warranty = self.env["fix.tradein.warranty"].sudo()
        existing = Warranty.search([("graded_stock_ref", "=", stock.name)], limit=1)
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}
        months = int(_param_float(self.env, PARAM_RESALE_WARRANTY_MONTHS, 6)) or 6
        start = fields.Date.context_today(self)
        warranty = Warranty._guarded().create(
            {
                "tradein_id": rec.id,
                "company_id": rec.company_id.id,
                "months": months,
                "start_date": start,
                "graded_stock_ref": stock.name,
                "terms": "Refurbished grade %s unit %s, %d months' cover from the resale."
                % ((rec.grade or "").upper(), stock.name, months),
            }
        )
        warranty = Warranty.browse(warranty.id)  # the guard token stays on the create
        cover = (
            self.env["fix.warranty"]
            .sudo()
            .create(
                {
                    "device_id": stock.device_id.id,
                    "company_id": rec.company_id.id,
                    "warranty_type": "extended",
                    "start_date": start,
                    "end_date": warranty.end_date,
                    "coverage_details": "1000FiX refurbished-unit warranty %s (trade-in %s)"
                    % (warranty.name, rec.name),
                }
            )
        )
        warranty._guarded().write({"device_warranty_id": cover.id})
        rec.message_post(
            body="Resale warranty %s issued on the sale of %s." % (warranty.name, stock.name)
        )
        return {"model": warranty._name, "id": warranty.id, "created": True}


class FixRefurbishment(models.Model):
    """A refurbishment step within a trade-in (composes the workshop).

    A05 audit M14-12: the step state was a free write, a step completed from
    pending, and step costs never reached the request or the stock. Now the
    state changes only through Start and Complete, a step's costs are frozen
    once it is done, and they roll up into the request's refurbishment cost."""

    _name = "fix.refurbishment"
    _description = "Refurbishment Step"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    _FROZEN_WHEN_DONE = frozenset(
        {"tradein_id", "step", "parts_cost", "labor_cost", "technician_id", "currency_id"}
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", ondelete="cascade", index=True
    )
    step = fields.Selection(
        [
            ("intake", "Intake Inspection"),
            ("repair", "Repair"),
            ("cosmetic", "Cosmetic Restoration"),
            ("testing", "Testing"),
            ("final_qa", "Final QA"),
        ],
        required=True,
        default="intake",
    )
    state = fields.Selection(
        [("pending", "Pending"), ("in_progress", "In Progress"), ("done", "Done")],
        default="pending",
        required=True,
        readonly=True,
    )
    notes = fields.Text()
    technician_id = fields.Many2one("hr.employee", string="Technician")
    started_at = fields.Datetime(readonly=True, copy=False)
    completed_at = fields.Datetime(readonly=True, copy=False)
    completed_by_id = fields.Many2one("res.users", string="Completed By", readonly=True, copy=False)
    parts_cost = fields.Monetary(
        string="Step Parts Cost", currency_field="currency_id", default=0.0
    )
    labor_cost = fields.Monetary(
        string="Step Labor Cost", currency_field="currency_id", default=0.0
    )
    total_cost = fields.Monetary(
        string="Total Step Cost",
        currency_field="currency_id",
        compute="_compute_total_cost",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )

    _costs_positive = models.Constraint(
        "CHECK (parts_cost >= 0 AND labor_cost >= 0)", "Step costs cannot be negative"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "started_at",
            "completed_at",
            "completed_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(s.state == "done" or s._tradein_closed() for s in self):
            locked |= self._FROZEN_WHEN_DONE
        return locked

    def _tradein_closed(self) -> bool:
        """The unit is graded or beyond: its cost basis is fixed."""
        self.ensure_one()
        return bool(self.tradein_id) and self.tradein_id.state in (
            "graded",
            "resale_ready",
            "closed",
            "rejected",
        )

    @api.depends("parts_cost", "labor_cost")
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = (rec.parts_cost or 0.0) + (rec.labor_cost or 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            ids = [v.get("tradein_id") for v in vals_list if v.get("tradein_id")]
            for rec in self.env["fix.tradein.request"].browse(ids):
                if rec.state in ("graded", "resale_ready", "closed", "rejected"):
                    raise UserError(
                        "Trade-in %s is %s: its refurbishment plan and costs are closed."
                        % (rec.name, rec.state)
                    )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state == "done" or rec._tradein_closed():
                    names = [
                        n
                        for n in self._FROZEN_WHEN_DONE & set(vals)
                        if rec._fix_guard_differs(n, vals[n], rec[n])
                    ]
                    if names:
                        raise UserError(
                            "Refurbishment step %s is %s: %s can no longer change."
                            % (
                                rec.name,
                                "done" if rec.state == "done" else "closed with its trade-in",
                                ", ".join(sorted(self._fields[n].string or n for n in names)),
                            )
                        )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(s.state != "pending" or s._tradein_closed() for s in self):
            raise UserError("A started, done or closed refurbishment step is not deleted.")
        return super().unlink()

    def _check_in_refurbishment(self):
        for rec in self:
            if not rec.tradein_id or rec.tradein_id.state != "refurbished":
                raise UserError(
                    "Step %s belongs to a trade-in that is not in refurbishment." % rec.name
                )

    def action_start(self):
        """Allocate technician and initiate repair session."""
        for rec in self:
            if rec.state != "pending":
                raise UserError(
                    "Step %s is %s: only a pending step starts." % (rec.name, rec.state)
                )
            rec._check_in_refurbishment()
            vals = {"state": "in_progress", "started_at": fields.Datetime.now()}
            if not rec.technician_id:
                employee = (
                    self.env["hr.employee"]
                    .sudo()
                    .search([("user_id", "=", self.env.user.id)], limit=1)
                )
                if employee:
                    vals["technician_id"] = employee.id
            rec._guarded().write(vals)
        return True

    def action_request_parts(self):
        """Record spare parts request from M15 inventory."""
        self.ensure_one()
        self.message_post(
            body="Parts requested for step %s: Parts cost BDT %.2f" % (self.step, self.parts_cost)
        )
        return True

    def action_complete_repair(self):
        """Mark refurbishment step as done and log to trade-in request."""
        for rec in self:
            if rec.state != "in_progress":
                raise UserError(
                    "Step %s is %s: start it before completing it." % (rec.name, rec.state)
                )
            rec._check_in_refurbishment()
            if not rec.technician_id:
                raise UserError("Step %s needs the technician who did the work." % rec.name)
            rec._guarded().write(
                {
                    "state": "done",
                    "completed_at": fields.Datetime.now(),
                    "completed_by_id": self.env.uid,
                }
            )
            if rec.tradein_id:
                rec.tradein_id.message_post(
                    body="Refurbishment step '%s' completed by %s. Cost: BDT %.2f"
                    % (
                        dict(rec._fields["step"].selection).get(rec.step, rec.step),
                        rec.technician_id.name if rec.technician_id else "Technician",
                        rec.total_cost,
                    )
                )
        return True


class FixApprovalMatrixTradeinDomains(models.Model):
    """A11 audit P2: lets a DoA matrix row target the routed trade-in payout
    (SLA, escalation, policy) without touching any other DOFA approval."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("tradein_payout", "Trade-In Payout")],
        ondelete={"tradein_payout": "cascade"},
    )
