# fix_tradein_capture — M14 second capture pass (19 Nov 2026).
#
# Every M14 sub-module page had a "+ New" after the 13 Nov pass, but read
# against the spec (M14 FR-TRF-001..039, §9 rules, §13 SoD) several captured
# the wrong thing or nothing the spec names:
#   p1  Intake (5 channels): no channel, no declared condition, faults, age,
#       photographs, OEM warranty status or accessories (FR-TRF-001/035), and
#       no physical intake verification: the post-inspection value was typed
#       with no evidence (FR-TRF-005, BRU-TRF-09 H).
#   p2  Valuation: no offer economics (resale estimate minus expected refurb,
#       logistics, destruction and channel cost) and no margin floor
#       (FR-TRF-033, BRU-TRF-10).
#   p4  Settlement: the method was always mobile money (FR-TRF-007).
#   p7  Refurbishment: no rework record after a failed QA (FR-TRF-036), no
#       before/after evidence (FR-TRF-013), and activation-lock removal
#       without proof of ownership (BRU-TRF-22 H).
#   p8  Grading & QA: the grade was a free choice (FR-TRF-019, BRU-TRF-12/13/
#       14, T-07) and QA kept two counters, not each test (FR-TRF-017).
#   p9  Resale: no listing re-check of NEIR (FR-TRF-038 P0) and nothing
#       captured a return of a sold refurbished unit (FR-TRF-026).
#   p10 Harvest: no parts-only routing or write-off approval (FR-TRF-020,
#       BRU-TRF-19, §13 SoD).
# Outcomes go to chatter: no new domain events are registered here.
from __future__ import annotations

from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_tradein import _EPS, FixRefurbishment, FixTradeinRequest, _param_float
from .fix_tradein_ops import FixTradeinValuation, _assert_amount_tier, _assert_role

GROUP_REFURB_SUPERVISOR = "cd_tradein.group_refurb_supervisor"
# M14-09: a unit that cannot be sold is routed to parts only from intake
# (collected / wiped), refurbishment (a failed QA included) or grading
ROUTABLE_STATES = ("collected", "wiped", "refurbished", "graded")
GROUP_WRITEOFF_APPROVER = "cd_tradein.group_refurb_writeoff_approver"
PARAM_MARGIN_FLOOR_PCT = "cd_tradein.offer_margin_floor_pct"  # 15
PARAM_RETURN_WINDOW_DAYS = "cd_tradein.return_window_days"  # 7

INTAKE_CHANNELS = [
    ("portal", "Customer Portal"),
    ("app", "Mobile App"),
    ("counter", "Service Counter"),
    ("field", "Field Visit"),
    ("corporate", "Corporate Buy-Back"),
]
CONDITIONS = [
    ("as_new", "As New"),
    ("good", "Good - light wear"),
    ("fair", "Fair - visible wear"),
    ("poor", "Poor - heavy wear"),
    ("faulty", "Faulty / not working"),
]
_CONDITION_RANK = {code: i for i, (code, _label) in enumerate(CONDITIONS)}
GRADES = [
    ("a", "A — Like New"),
    ("b", "B — Good"),
    ("c", "C — Fair"),
    ("d", "D — Poor"),
    ("e", "E — Parts Only"),
]
_AXIS_ORDER = ("a", "b", "c", "d")
# Fallback per-grade battery minimum when the grade master has none (the
# Back Market practice is 80% for a phone sold as good).
_BATTERY_MIN_DEFAULT = {"a": 85, "b": 80, "c": 75, "d": 70, "e": 0}


def _locked_refusal(rec, names, what):
    labels = ", ".join(sorted(rec._fields[n].string or n for n in names))
    raise UserError("%s %s is %s: %s can no longer change." % (what, rec.name, rec.state, labels))


# =========================================================================== p1/p4
class FixTradeinRequestCapture(models.Model):
    _inherit = "fix.tradein.request"

    # ---- p1 intake: the channel and the customer's declaration (FR-TRF-001/035)
    intake_channel = fields.Selection(
        INTAKE_CHANNELS, string="Intake Channel", default="counter", required=True, tracking=True
    )
    declared_condition = fields.Selection(CONDITIONS, string="Declared Condition", tracking=True)
    declared_faults = fields.Text(string="Declared Faults")
    declared_age_months = fields.Integer(string="Declared Age (months)")
    oem_warranty_status = fields.Selection(
        [
            ("unknown", "Unknown"),
            ("active", "Under OEM warranty"),
            ("expired", "OEM warranty expired"),
            ("none", "No OEM warranty"),
        ],
        string="OEM Warranty Status",
        default="unknown",
    )
    condition_photo_id = fields.Many2one(
        "ir.attachment", string="Condition Photographs", ondelete="set null"
    )
    acc_charger = fields.Boolean(string="Charger")
    acc_cable = fields.Boolean(string="Cable")
    acc_box = fields.Boolean(string="Original Box")
    acc_earphones = fields.Boolean(string="Earphones")
    acc_documents = fields.Boolean(string="Purchase Documents")
    accessories_notes = fields.Char(string="Other Accessories")
    intake_check_ids = fields.One2many(
        "fix.tradein.intake.check", "tradein_id", string="Physical Intake Verifications"
    )

    # ---- p4 settlement: how the seller is paid (FR-TRF-007)
    settlement_method = fields.Selection(
        [
            ("mobile_fs", "Mobile money (bKash / Nagad)"),
            ("bank_transfer", "Bank transfer"),
            ("cash", "Cash at the counter"),
        ],
        string="Settlement Method",
        default="mobile_fs",
        required=True,
        tracking=True,
    )
    settlement_bank_account_id = fields.Many2one(
        "res.partner.bank",
        string="Seller Bank Account / MFS Wallet",
        ondelete="restrict",
        help="The seller's bank account for a bank transfer, or the bKash / Nagad wallet "
        "(account number = the wallet number) for mobile money. Pinned by the payout "
        "approval: treasury pays only to this account.",
    )

    # ---- p7 rework cost kept apart from first-pass work (FR-TRF-036)
    rework_cost = fields.Monetary(
        string="Rework Cost",
        currency_field="currency_id",
        compute="_compute_rework_cost",
        store=True,
    )
    first_pass_cost = fields.Monetary(
        string="First-Pass Refurbishment Cost",
        currency_field="currency_id",
        compute="_compute_rework_cost",
        store=True,
    )

    _DECLARATION = frozenset(
        {
            "declared_condition",
            "declared_faults",
            "declared_age_months",
            "oem_warranty_status",
            "condition_photo_id",
            "acc_charger",
            "acc_cable",
            "acc_box",
            "acc_earphones",
            "acc_documents",
            "accessories_notes",
        }
    )
    # the offer is built on the declaration; the channel is fixed once accepted
    _FROZEN_FROM = {
        **FixTradeinRequest._FROZEN_FROM,
        "offered": FixTradeinRequest._FROZEN_FROM["offered"] | _DECLARATION,
        "accepted": FixTradeinRequest._FROZEN_FROM["accepted"] | {"intake_channel"},
    }

    @api.depends("refurbishment_ids.total_cost", "refurbishment_ids.is_rework")
    def _compute_rework_cost(self):
        for rec in self:
            steps = rec.refurbishment_ids
            rework = sum(steps.filtered("is_rework").mapped("total_cost"))
            rec.rework_cost = rework
            rec.first_pass_cost = sum(steps.mapped("total_cost")) - rework

    # ---- BRU-TRF-09: a value below the accepted offer needs intake evidence
    def _intake_check_confirmed(self):
        self.ensure_one()
        return (
            self.env["fix.tradein.intake.check"]
            .sudo()
            .search(
                [("tradein_id", "=", self.id), ("state", "=", "confirmed")],
                order="checked_at desc, id desc",
                limit=1,
            )
        )

    # A05 ERP M14-11: graded_value is guarded (set by the confirmed intake
    # verification, which carries the BRU-TRF-09 evidence rules), so the
    # former direct-write check here is gone: nobody types it.

    # ---- p4: the method and account are part of what the approval covers
    def _tradein_payout_terms(self):
        rec = self.sudo()
        return (
            *super()._tradein_payout_terms(),
            rec.settlement_method or "",
            rec.settlement_bank_account_id.id or 0,
        )

    def _settlement_denial(self) -> str:
        self.ensure_one()
        rec = self.sudo()
        if rec.settlement_method not in ("bank_transfer", "mobile_fs"):
            return ""
        account = rec.settlement_bank_account_id
        if not account:
            # A05 e2e walk defect 4: an MFS payout had no wallet, so treasury
            # added one after the approval - outside what the approver pinned
            return (
                "a bank-transfer settlement needs the seller's bank account"
                if rec.settlement_method == "bank_transfer"
                else "a mobile-money settlement needs the seller's bKash / Nagad wallet"
            )
        if not (account.acc_number or "").strip():
            return "account %s has no number" % account.display_name
        if account.partner_id.commercial_partner_id != rec.customer_id.commercial_partner_id:
            return "bank account %s is not the seller's (%s)" % (
                account.acc_number,
                rec.customer_id.name,
            )
        return ""

    def _tradein_check_payout_request(self):
        super()._tradein_check_payout_request()
        for rec in self:
            denial = rec._settlement_denial()
            if denial:
                raise UserError("Trade-in %s: %s." % (rec.name, denial))

    def action_pay(self):
        for rec in self:
            denial = rec._settlement_denial()
            if denial:
                raise UserError("Trade-in %s: %s." % (rec.name, denial))
        return super().action_pay()

    # ---- p8 / p9 gates
    def _grade_certificate(self):
        """The latest grading certificate of the CURRENT refurbishment cycle."""
        self.ensure_one()
        return (
            self.env["fix.tradein.grade"]
            .sudo()
            .search(
                [("tradein_id", "=", self.id), ("cycle", "=", self.refurb_cycle or 1)],
                order="id desc",
                limit=1,
            )
        )

    # ---- M14-09/21: the write-off of a parts-only unit
    def _tradein_writeoff_carrying(self, why, amount=None):
        """Dr write-off (500905) / Cr refurbished stock for what the ledger
        still carries (or `amount` of it); idempotent per reason."""
        from .fix_tradein_ledger import tradein_account

        self.ensure_one()
        rec = self.sudo()
        carrying = rec._ledger_carrying()
        value = round(carrying if amount is None else min(amount, carrying), 2)
        if value <= _EPS:
            return self.env["fix.refurb.ledger"]
        n = len(rec.ledger_ids.filtered(lambda r: r.kind == "writeoff")) + 1
        lines = [
            (
                tradein_account(self.env, rec.company_id, "writeoff"),
                "Trade-in %s: written off (%s)" % (rec.name, why),
                value,
                0.0,
                None,
            ),
            (
                tradein_account(self.env, rec.company_id, "refurb_stock"),
                "Trade-in %s: out of refurbished stock" % rec.name,
                0.0,
                value,
                None,
            ),
        ]
        return rec._ledger_post(
            "writeoff", "writeoff:%d" % n, value, -value, lines, "write-off: %s" % why
        )

    def _tradein_parts_only_route(self):
        self.ensure_one()
        return (
            self.env["fix.refurb.writeoff"]
            .sudo()
            .search(
                [("tradein_id", "=", self.id), ("state", "=", "approved")], order="id desc", limit=1
            )
        )

    def action_route_to_recycle(self):
        """A parts-only unit routed to recycling goes to M18 whole: a recycle
        harvest line (M18 opens its collection from tradein.harvested), the
        wipe gate and hold re-checked; what is left of its cost is written
        off and the trade-in closes."""
        for rec in self:
            route = rec._tradein_parts_only_route()
            if rec.state != "parts_only" or not route or route.destination != "recycle":
                raise UserError(
                    "Trade-in %s is not a parts-only unit routed to recycling." % rec.name
                )
            harvest = (
                self.env["fix.tradein.harvest"]
                .sudo()
                .search(
                    [
                        ("tradein_id", "=", rec.id),
                        ("target", "=", "recycle"),
                        ("component", "=", "other"),
                    ],
                    limit=1,
                )
            )
            if not harvest:
                harvest = (
                    self.env["fix.tradein.harvest"]
                    .sudo()
                    .create(
                        {
                            "tradein_id": rec.id,
                            "company_id": rec.company_id.id,
                            "component": "other",
                            "part_name": "Whole unit for recycling",
                            "quantity": 1,
                            "target": "recycle",
                        }
                    )
                )
            if harvest.state == "pending":
                harvest.with_env(self.env).action_harvest()
            rec._tradein_writeoff_carrying("recycled")
            rec.sudo()._guarded().write({"state": "closed"})
        return True

    def action_close_parts_only(self):
        """Harvest done: the cost still carried (the residue no part took) is
        written off and the trade-in closes (M14-20)."""
        for rec in self:
            if rec.state != "parts_only":
                raise UserError("Trade-in %s is not a parts-only unit." % rec.name)
            pending = (
                rec.env["fix.tradein.harvest"]
                .sudo()
                .search_count([("tradein_id", "=", rec.id), ("state", "=", "pending")])
            )
            if pending:
                raise UserError(
                    "Trade-in %s still has %d harvest line(s) pending: harvest or scrap them."
                    % (rec.name, pending)
                )
            rec._tradein_writeoff_carrying("harvest residue")
            rec.sudo()._guarded().write({"state": "closed"})
        return True

    def _tradein_gate_denial(self, target) -> str:
        denial = super()._tradein_gate_denial(target)
        if denial:
            return denial
        if target == "graded":
            cert = self._grade_certificate()
            if not cert:
                return (
                    "the unit has no grading certificate: the grade is computed from its QA "
                    "and grading results on Grading & QA (BRU-TRF-12)"
                )
            if cert.grade != self.grade:
                return "the grade %s is not the grading certificate's (%s)" % (
                    (self.grade or "?").upper(),
                    cert.grade.upper(),
                )
        if target == "resale_ready":
            device = self.device_id.sudo()
            if device and (device.imei_1 or device.imei_2):
                # FR-TRF-038 / AUT-TRF-15: a handset's NEIR status is
                # re-confirmed before listing, not carried from the purchase
                denial = self._provenance_denial()
                if denial:
                    return "listing a handset re-confirms its NEIR status: %s" % denial
        return ""

    def action_grade(self):
        """The grade is the latest grading certificate's, never typed here."""
        Grade = self.env["fix.refurb.grade"].sudo()
        for rec in self:
            if rec.state != "refurbished":
                continue
            cert = rec._grade_certificate()
            if not cert and (
                rec._provenance_hard_stop()
                or rec._wipe_gate_denial(rec.wipe_certificate_id, rec.device_id)
                or rec._refurb_denial()
            ):
                continue  # the provenance, wipe-gate and step / QA refusals come first
            if not cert:
                raise UserError(
                    "Trade-in %s has no grading certificate: record it on Grading & QA. The "
                    "grade is computed from the measured results, never typed (BRU-TRF-12)."
                    % rec.name
                )
            vals = {}
            if rec.grade != cert.grade:
                vals["grade"] = cert.grade
            if rec.battery_health_pct != cert.battery_health_pct:
                vals["battery_health_pct"] = cert.battery_health_pct
            master = Grade.search([("code", "=", cert.grade.upper())], limit=1)
            if master and rec.refurb_grade_id != master:
                vals["refurb_grade_id"] = master.id
            if vals:
                rec.write(vals)
        return super().action_grade()


# =========================================================================== p1
class FixTradeinIntakeCheck(models.Model):
    """Physical intake verification (FR-TRF-005, BRU-TRF-09, AUT-TRF-05).

    The device as received is checked against the customer's declaration. A
    value below the accepted offer is accepted only where the verified
    condition is worse than declared, described and photographed; it becomes
    the trade-in's graded value, which the customer must then accept. The
    checker is not the person who valued the unit (§13 SoD)."""

    _name = "fix.tradein.intake.check"
    _description = "Trade-In Physical Intake Verification"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    _INPUTS = frozenset(
        {
            "tradein_id",
            "verified_condition",
            "identity_matches",
            "accessories_as_declared",
            "accessories_notes",
            "difference_notes",
            "evidence_attachment_id",
            "verified_value",
            "company_id",
        }
    )
    # M14-10 / BRU-TRF-09: the offer is revised at intake only (before the
    # data wipe and the stock), never after the unit was refurbished or sold
    _OPEN_STATES = ("accepted", "collected")

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    currency_id = fields.Many2one(related="tradein_id.currency_id", string="Currency")
    declared_condition = fields.Selection(
        related="tradein_id.declared_condition", string="Declared Condition"
    )
    accepted_value = fields.Monetary(
        string="Accepted Offer", currency_field="currency_id", compute="_compute_accepted"
    )
    verified_condition = fields.Selection(CONDITIONS, string="Verified Condition", required=True)
    identity_matches = fields.Boolean(
        string="Serial / IMEI Matches the Request",
        default=True,
        help="The unit received is the one the offer was made on.",
    )
    accessories_as_declared = fields.Boolean(string="Accessories as Declared", default=True)
    accessories_notes = fields.Char(string="Accessories Missing or Extra")
    condition_differs = fields.Boolean(
        string="Worse Than Declared", compute="_compute_differs", store=True
    )
    difference_notes = fields.Text(string="What Differs From the Declaration")
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Photographic Evidence", ondelete="restrict"
    )
    verified_value = fields.Monetary(
        string="Verified Value", currency_field="currency_id", required=True
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    checked_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    checked_at = fields.Datetime(string="Verified At", readonly=True, copy=False)

    _value_positive = models.Constraint(
        "CHECK (verified_value >= 0)", "A verified value cannot be negative"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "checked_by_id", "checked_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._INPUTS
        return locked

    @api.depends("tradein_id.accepted_offer_value", "tradein_id.offered_value")
    def _compute_accepted(self):
        for rec in self:
            t = rec.tradein_id
            rec.accepted_value = t.accepted_offer_value or t.offered_value or 0.0

    @api.depends("verified_condition", "tradein_id.declared_condition")
    def _compute_differs(self):
        for rec in self:
            declared = rec.tradein_id.declared_condition
            rec.condition_differs = bool(
                rec.verified_condition
                and (
                    not declared
                    or _CONDITION_RANK[rec.verified_condition] > _CONDITION_RANK[declared]
                )
            )

    def _refuse_tradein_stage(self, tradeins):
        late = tradeins.filtered(
            lambda t: t.state not in self._OPEN_STATES
            or t.payout_approval_state in ("pending", "approved")
        )
        if late:
            t = late[0]
            raise UserError(
                "Trade-in %s is %s%s: the unit is verified after acceptance and before its "
                "payout is requested."
                % (
                    t.name,
                    t.state,
                    " with a payout approval %s" % t.payout_approval_state
                    if t.payout_approval_state in ("pending", "approved")
                    else "",
                )
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            ids = [v.get("tradein_id") for v in vals_list if v.get("tradein_id")]
            self._refuse_tradein_stage(self.env["fix.tradein.request"].sudo().browse(ids))
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.intake.check") or "TIC/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                names = [
                    n
                    for n in self._INPUTS & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if names:
                    _locked_refusal(rec, names, "Intake verification")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(r.state != "draft" for r in self):
            raise UserError("A confirmed intake verification is evidence and is not deleted.")
        return super().unlink()

    def _confirm_denial(self) -> str:
        self.ensure_one()
        accepted = self.accepted_value
        if not self.identity_matches:
            return (
                "the unit received is not the one the offer was made on: decline the trade-in "
                "and return the unit"
            )
        if accepted and self.verified_value > accepted + _EPS:
            return "an intake verification does not raise the accepted offer of BDT %.2f" % (
                accepted
            )
        if accepted and self.verified_value < accepted - _EPS:
            if not self.condition_differs:
                return (
                    "the verified condition is not worse than the declaration, so the offer "
                    "stands (BRU-TRF-09)"
                )
            if not (self.difference_notes or "").strip():
                return "describe what differs from the declaration"
            if not self.evidence_attachment_id:
                return "attach the photographs that show the difference (BRU-TRF-09)"
        return ""

    def action_confirm(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Intake verification %s is already confirmed." % rec.name)
            tradein = rec.tradein_id.sudo()
            self._refuse_tradein_stage(tradein)
            denial = rec._confirm_denial()
            if denial:
                raise UserError("Intake verification %s: %s." % (rec.name, denial))
            valuers = (
                self.env["fix.tradein.valuation"]
                .sudo()
                .search([("tradein_id", "=", tradein.id), ("state", "=", "applied")])
            )
            if not self.env.su and self.env.user in (
                valuers.mapped("valuated_by_id") | valuers.mapped("create_uid")
            ):
                raise UserError(
                    "Segregation of duties: the person who valued the unit does not also "
                    "confirm its condition at intake (§13)."
                )
            rec._guarded().write(
                {
                    "state": "confirmed",
                    "checked_by_id": self.env.uid,
                    "checked_at": fields.Datetime.now(),
                }
            )
            tradein._guarded().write({"graded_value": rec.verified_value})
            tradein.message_post(
                body="Physical intake verified (%s): condition %s, verified value BDT %.2f%s."
                % (
                    rec.name,
                    dict(CONDITIONS).get(rec.verified_condition),
                    rec.verified_value,
                    "; the customer must accept the revised value"
                    if tradein.revision_state == "pending"
                    else "",
                )
            )
        return True


# =========================================================================== p2
class FixTradeinValuationEconomics(models.Model):
    """FR-TRF-033 / BRU-TRF-10: the offer is the resale estimate MINUS the
    expected refurbishment, logistics, destruction and channel cost; a
    modelled margin below the floor is an exception a valuation manager
    approves (the override path)."""

    _inherit = "fix.tradein.valuation"

    _ECONOMICS = frozenset(
        {
            "resale_estimate",
            "expected_refurb_cost",
            "expected_logistics_cost",
            "expected_destruction_cost",
            "expected_channel_cost",
        }
    )
    _INPUTS = FixTradeinValuation._INPUTS | _ECONOMICS

    resale_estimate = fields.Monetary(string="Resale Estimate", currency_field="currency_id")
    expected_refurb_cost = fields.Monetary(
        string="Expected Refurbishment Cost", currency_field="currency_id"
    )
    expected_logistics_cost = fields.Monetary(
        string="Expected Logistics Cost", currency_field="currency_id"
    )
    expected_destruction_cost = fields.Monetary(
        string="Expected Data Destruction Cost", currency_field="currency_id"
    )
    expected_channel_cost = fields.Monetary(
        string="Expected Channel Cost", currency_field="currency_id"
    )
    expected_cost_total = fields.Monetary(
        string="Expected Cost",
        currency_field="currency_id",
        compute="_compute_economics",
        store=True,
    )
    modelled_margin = fields.Monetary(
        string="Modelled Margin",
        currency_field="currency_id",
        compute="_compute_economics",
        store=True,
    )
    modelled_margin_pct = fields.Float(
        string="Modelled Margin (%)", compute="_compute_economics", store=True
    )
    margin_floor_pct = fields.Float(string="Margin Floor (%)", compute="_compute_floor")
    below_margin_floor = fields.Boolean(string="Below the Margin Floor", compute="_compute_floor")

    _costs_positive = models.Constraint(
        "CHECK (COALESCE(resale_estimate, 0) >= 0 AND COALESCE(expected_refurb_cost, 0) >= 0 "
        "AND COALESCE(expected_logistics_cost, 0) >= 0 "
        "AND COALESCE(expected_destruction_cost, 0) >= 0 "
        "AND COALESCE(expected_channel_cost, 0) >= 0)",
        "The resale estimate and expected costs cannot be negative",
    )

    @api.depends(
        "resale_estimate",
        "expected_refurb_cost",
        "expected_logistics_cost",
        "expected_destruction_cost",
        "expected_channel_cost",
        "final_offer",
        "computed_offer",
    )
    def _compute_economics(self):
        for rec in self:
            cost = (
                (rec.expected_refurb_cost or 0.0)
                + (rec.expected_logistics_cost or 0.0)
                + (rec.expected_destruction_cost or 0.0)
                + (rec.expected_channel_cost or 0.0)
            )
            offer = rec.final_offer or rec.computed_offer or 0.0
            rec.expected_cost_total = cost
            if rec.resale_estimate:
                margin = rec.resale_estimate - offer - cost
                rec.modelled_margin = round(margin, 2)
                rec.modelled_margin_pct = round(margin / rec.resale_estimate * 100.0, 2)
            else:
                rec.modelled_margin = 0.0
                rec.modelled_margin_pct = 0.0

    @api.depends("modelled_margin_pct", "resale_estimate")
    def _compute_floor(self):
        floor = _param_float(self.env, PARAM_MARGIN_FLOOR_PCT, 15.0)
        for rec in self:
            rec.margin_floor_pct = floor
            rec.below_margin_floor = bool(
                rec.resale_estimate and rec.modelled_margin_pct < floor - 1e-6
            )

    @api.depends(
        "grid_id",
        "market_ref_price",
        "final_offer",
        "computed_offer",
        "method",
        "modelled_margin_pct",
        "resale_estimate",
    )
    def _compute_override(self):
        super()._compute_override()
        for rec in self:
            if rec.below_margin_floor:
                rec.is_override = True

    def action_apply_to_tradein(self):
        for rec in self:
            if rec.state == "draft" and (rec.resale_estimate or 0.0) <= 0:
                raise UserError(
                    "Valuation %s has no resale estimate: every offer is built as the resale "
                    "estimate minus the expected refurbishment, logistics, destruction and "
                    "channel cost (FR-TRF-033)." % rec.name
                )
        return super().action_apply_to_tradein()


# =========================================================================== p7
class FixRefurbishmentCapture(models.Model):
    _inherit = "fix.refurbishment"

    is_rework = fields.Boolean(string="Rework", readonly=True, copy=False)
    rework_qa_id = fields.Many2one(
        "fix.refurb.qa", string="Failed QA", readonly=True, copy=False, ondelete="set null"
    )
    rework_cause = fields.Selection(
        [
            ("workmanship", "Workmanship"),
            ("part_defect", "Defective part"),
            ("missed_fault", "Fault missed in diagnostics"),
            ("cosmetic", "Cosmetic finish"),
            ("battery", "Battery"),
            ("other", "Other"),
        ],
        string="Rework Cause",
    )
    rework_notes = fields.Char(string="Rework Detail")
    before_photo_id = fields.Many2one("ir.attachment", string="Before Photo", ondelete="set null")
    after_photo_id = fields.Many2one("ir.attachment", string="After Photo", ondelete="set null")
    activation_lock_removed = fields.Boolean(string="Activation Lock Removed")
    ownership_proof_id = fields.Many2one(
        "ir.attachment", string="Seller's Proof of Ownership", ondelete="restrict"
    )

    # the base write and form lock read self._FROZEN_WHEN_DONE
    _FROZEN_WHEN_DONE = FixRefurbishment._FROZEN_WHEN_DONE | {
        "rework_cause",
        "rework_notes",
        "before_photo_id",
        "after_photo_id",
        "activation_lock_removed",
        "ownership_proof_id",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"is_rework", "rework_qa_id"}

    @api.constrains("activation_lock_removed", "ownership_proof_id")
    def _check_ownership_proof(self):
        for rec in self:
            if rec.activation_lock_removed and not rec.ownership_proof_id:
                raise ValidationError(
                    "Step %s: an activation lock is removed only on the seller's documented "
                    "proof of ownership (BRU-TRF-22). Attach it." % rec.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        guard_open = self._fix_guard_open()
        failed = {}
        Request = self.env["fix.tradein.request"].sudo()
        labels = dict(self._fields["step"].selection)
        for vals in vals_list:
            tradein = Request.browse(vals.get("tradein_id") or [])
            # the form shows the reference read-only: a step added from the
            # workspace had no name and its save failed (NOT NULL)
            if not vals.get("name"):
                vals["name"] = "%s · %s" % (
                    tradein.name or "Refurbishment",
                    labels.get(vals.get("step"), vals.get("step") or "Step"),
                )
            qa = tradein._qa_latest() if tradein else None
            if qa and qa.qa_state == "fail":
                failed[id(vals)] = qa
                if not guard_open and not vals.get("rework_cause"):
                    raise UserError(
                        "Trade-in %s failed QA %s: a step added now is rework. State its cause "
                        "(FR-TRF-036)." % (tradein.name, qa.name)
                    )
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list, strict=True):
            qa = failed.get(id(vals))
            if qa:
                rec._guarded().write({"is_rework": True, "rework_qa_id": qa.id})
        return records


# =========================================================================== p8
class FixRefurbGradeBattery(models.Model):
    """The published grade carries its battery minimum (FR-TRF-016/018)."""

    _inherit = "fix.refurb.grade"

    battery_minimum_pct = fields.Integer(
        string="Battery Health Minimum (%)",
        default=0,
        help="A unit whose battery health is below this cannot carry the grade "
        "(BRU-TRF-14): the battery is replaced or the grade drops.",
    )

    _battery_min_range = models.Constraint(
        "CHECK (battery_minimum_pct >= 0 AND battery_minimum_pct <= 100)",
        "A battery minimum is a percentage between 0 and 100",
    )

    @api.model
    def _m14_seed_battery_minimums(self):
        """Install-time defaults; a minimum the quality manager set is kept."""
        for rec in self.sudo().search([("battery_minimum_pct", "=", 0)]):
            value = _BATTERY_MIN_DEFAULT.get((rec.code or "").lower(), 0)
            if value:
                rec.battery_minimum_pct = value


def _battery_minimum(env, grade) -> int:
    if not grade:
        return 0
    master = env["fix.refurb.grade"].sudo().search([("code", "=", grade.upper())], limit=1)
    if master and master.battery_minimum_pct:
        return master.battery_minimum_pct
    return _BATTERY_MIN_DEFAULT.get(grade, 0)


def _computed_grade(env, screen, cosmetic, functional, battery) -> str:
    """BRU-TRF-12: the worst axis sets the grade; a battery below the grade's
    minimum drops it until it meets one, and below grade D's it is parts
    only (BRU-TRF-14)."""
    worst = max(_AXIS_ORDER.index(axis or "a") for axis in (screen, cosmetic, functional))
    for grade in _AXIS_ORDER[worst:]:
        if (battery or 0) >= _battery_minimum(env, grade):
            return grade
    return "e"


class FixTradeinGradeCapture(models.Model):
    """FR-TRF-019 / T-07: the grade is computed from the measured axes and the
    battery; an override records its justification and its author, who holds
    the Refurbishment Supervisor role and did not run the unit's QA."""

    _name = "fix.tradein.grade"
    _inherit = ["fix.tradein.grade", "fix.guarded.mixin"]

    # blank on the form = the computed grade (filled in at create), so the
    # form does not demand it; a certificate never stays without one
    grade = fields.Selection(default=False, required=False)
    computed_grade = fields.Selection(
        GRADES, string="Computed Grade", compute="_compute_grade", store=True
    )
    is_override = fields.Boolean(string="Supervisor Override", compute="_compute_grade", store=True)
    override_reason = fields.Text(string="Override Justification")
    override_by_id = fields.Many2one("res.users", string="Overridden By", readonly=True, copy=False)
    override_at = fields.Datetime(string="Overridden At", readonly=True, copy=False)
    qa_id = fields.Many2one(
        "fix.refurb.qa", string="QA Result Used", readonly=True, copy=False, ondelete="set null"
    )
    battery_minimum_pct = fields.Integer(
        string="Battery Minimum of the Grade (%)", compute="_compute_battery_minimum"
    )

    @api.depends(
        "screen_grade", "cosmetic_grade", "functional_grade", "battery_health_pct", "grade"
    )
    def _compute_grade(self):
        for rec in self:
            rec.computed_grade = _computed_grade(
                self.env,
                rec.screen_grade,
                rec.cosmetic_grade,
                rec.functional_grade,
                rec.battery_health_pct,
            )
            rec.is_override = bool(rec.grade and rec.grade != rec.computed_grade)

    @api.depends("grade")
    def _compute_battery_minimum(self):
        for rec in self:
            rec.battery_minimum_pct = _battery_minimum(self.env, rec.grade)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"override_by_id", "override_at", "qa_id", "cycle"}

    @api.constrains("grade")
    def _check_grade_present(self):
        for rec in self:
            if not rec.grade:
                raise ValidationError("Grading certificate %s has no grade." % rec.name)

    def _grade_assert_rules(self):
        """Runs after every user create/write, so a refusal rolls it back."""
        if self.env.su:
            return
        for rec in self:
            minimum = _battery_minimum(self.env, rec.grade)
            if (rec.battery_health_pct or 0) < minimum:
                raise UserError(
                    "Grade %s needs a battery health of at least %d%%; %s measured %d%%. Replace "
                    "the battery or record the lower grade (BRU-TRF-14)."
                    % (rec.grade.upper(), minimum, rec.tradein_id.name, rec.battery_health_pct)
                )
            if not rec.is_override:
                continue
            if not (rec.override_reason or "").strip():
                raise UserError(
                    "The measured results give grade %s; recording %s is an override and needs "
                    "a justification (BRU-TRF-13)."
                    % (rec.computed_grade.upper(), rec.grade.upper())
                )
            _assert_role(self.env, GROUP_REFURB_SUPERVISOR, "Overriding a computed grade")
            tradein = rec.tradein_id.sudo()
            qa_people = self.env["res.users"]
            for qa in self.env["fix.refurb.qa"].sudo().search([("tradein_id", "=", tradein.id)]):
                qa_people |= qa.inspected_by_id | qa.inspector_id.user_id | qa.create_uid
            if self.env.user in qa_people:
                raise UserError(
                    "Segregation of duties: the person who ran this unit's QA does not override "
                    "its grade (T-07)."
                )

    def _grade_stamp(self):
        for rec in self:
            vals = {}
            if rec.is_override and rec.override_by_id != self.env.user:
                vals.update({"override_by_id": self.env.uid, "override_at": fields.Datetime.now()})
            elif not rec.is_override and rec.override_by_id:
                vals.update({"override_by_id": False, "override_at": False})
            if vals:
                rec._guarded().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        Request = self.env["fix.tradein.request"].sudo()
        for vals in vals_list:
            tradein = Request.browse(vals.get("tradein_id") or [])
            qa = tradein._qa_latest() if tradein else None
            # M14-14: the battery health is the QA's measurement, never typed
            if qa:
                typed = vals.get("battery_health_pct")
                if (
                    typed not in (None, False)
                    and int(typed) != qa.battery_health_pct
                    and not (self._fix_guard_open())
                ):
                    raise UserError(
                        "Trade-in %s: the battery health is QA %s's measurement (%d%%), not a "
                        "typed figure (%s%%)."
                        % (tradein.name, qa.name, qa.battery_health_pct, typed)
                    )
                vals["battery_health_pct"] = qa.battery_health_pct
            if not vals.get("grade"):
                vals["grade"] = _computed_grade(
                    self.env,
                    vals.get("screen_grade", "a"),
                    vals.get("cosmetic_grade", "a"),
                    vals.get("functional_grade", "a"),
                    vals.get("battery_health_pct", 100),
                )
        records = super().create(vals_list)
        records._grade_assert_rules()
        records._grade_stamp()
        for rec in records:
            qa = rec.tradein_id._qa_latest()
            if qa:
                rec._guarded().write({"qa_id": qa.id})
        return records

    def write(self, vals):
        if not self._fix_guard_open() and "battery_health_pct" in vals:
            for rec in self.filtered("qa_id"):
                if rec._fix_guard_differs(
                    "battery_health_pct", vals["battery_health_pct"], rec.battery_health_pct
                ):
                    raise UserError(
                        "Grading certificate %s: the battery health is QA %s's measurement."
                        % (rec.name, rec.qa_id.name)
                    )
        result = super().write(vals)
        if not self._fix_guard_open() and set(vals) - {"override_by_id", "override_at", "qa_id"}:
            self._grade_assert_rules()
            self._grade_stamp()
        return result


class FixRefurbQaTest(models.Model):
    """One measured result of the QA protocol (FR-TRF-017, T-02)."""

    _name = "fix.refurb.qa.test"
    _description = "Refurbishment QA Test Result"
    _order = "qa_id, sequence, id"

    qa_id = fields.Many2one("fix.refurb.qa", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="qa_id.company_id", store=True, index=True)
    sequence = fields.Integer(default=10)
    test_code = fields.Selection(
        [
            ("hardware", "Hardware components"),
            ("ports", "Ports & buttons"),
            ("display", "Display & touch"),
            ("camera", "Cameras"),
            ("connectivity", "Connectivity (cellular, Wi-Fi, Bluetooth)"),
            ("thermal", "Thermal"),
            ("audio", "Audio"),
            ("battery", "Battery & charging"),
            ("software", "Software functionality"),
            ("other", "Other"),
        ],
        string="Test",
        required=True,
    )
    expected = fields.Char(string="Expected")
    measured = fields.Char(string="Measured")
    outcome = fields.Selection(
        [("pass", "Pass"), ("fail", "Fail")], string="Outcome", required=True, default="pass"
    )
    equipment_ref = fields.Char(string="Equipment / Tool")

    def _refuse_submitted(self, qas):
        if self.env.su:
            return
        done = qas.filtered(lambda q: q.qa_state != "pending")
        if done:
            raise UserError(
                "QA %s is submitted (%s): its test results are frozen. A re-test is a new QA "
                "record." % (done[0].name, done[0].qa_state)
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = [v.get("qa_id") for v in vals_list if v.get("qa_id")]
        self._refuse_submitted(self.env["fix.refurb.qa"].sudo().browse(ids))
        return super().create(vals_list)

    def write(self, vals):
        self._refuse_submitted(self.mapped("qa_id"))
        return super().write(vals)

    def unlink(self):
        self._refuse_submitted(self.mapped("qa_id"))
        return super().unlink()


class FixRefurbQaCapture(models.Model):
    _inherit = "fix.refurb.qa"

    test_ids = fields.One2many("fix.refurb.qa.test", "qa_id", string="Test Results")

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(q.qa_state != "pending" for q in self):
            locked |= {"test_ids"}
        return locked

    def action_submit_result(self):
        """With recorded tests, the counters ARE the tests (no typed tally)."""
        for rec in self.filtered(lambda q: q.qa_state == "pending" and q.test_ids):
            rec.write(
                {
                    "tests_total": len(rec.test_ids),
                    "tests_passed": len(rec.test_ids.filtered(lambda t: t.outcome == "pass")),
                }
            )
        return super().action_submit_result()


# =========================================================================== p9
class FixRefurbReturn(models.Model):
    """A sold refurbished unit comes back (FR-TRF-026, AUT-TRF-18): within the
    return window or the refurbished warranty, its failure is recorded against
    the grade it was sold at, and a supervisor decides what happens to it."""

    _name = "fix.refurb.return"
    _description = "Refurbished Unit Return"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "return_date desc, id desc"

    _INPUTS = frozenset(
        {
            "tradein_id",
            "return_date",
            "reason",
            "failure_code",
            "description",
            "evidence_attachment_id",
            "company_id",
        }
    )

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Sold Unit (Trade-In)", required=True, index=True
    )
    graded_stock_id = fields.Many2one(
        related="tradein_id.graded_stock_id", string="Graded Stock Unit", store=True
    )
    device_id = fields.Many2one(related="tradein_id.device_id", string="Device")
    warranty_id = fields.Many2one(
        "fix.tradein.warranty", string="Refurbished Warranty", readonly=True, copy=False
    )
    grade_at_sale = fields.Selection(GRADES, string="Grade at Sale", readonly=True, copy=False)
    return_date = fields.Date(required=True, default=fields.Date.context_today)
    reason = fields.Selection(
        [
            ("doa", "Dead on arrival"),
            ("hardware", "Hardware fault"),
            ("battery", "Battery"),
            ("display", "Display"),
            ("not_as_described", "Condition not as described"),
            ("software", "Software"),
            ("change_of_mind", "Change of mind"),
            ("other", "Other"),
        ],
        string="Return Reason",
        required=True,
    )
    failure_code = fields.Char(string="Failure Code (feeds grading analysis)")
    description = fields.Text(string="What the Buyer Reports")
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Evidence", ondelete="set null"
    )
    within_terms = fields.Boolean(string="Within Return Window or Warranty", readonly=True)
    outcome = fields.Selection(
        [
            ("re_refurbish", "Re-refurbish and re-grade"),
            ("harvest", "Harvest for parts"),
            ("replace", "Replace the unit"),
            ("refund", "Refund"),
            ("decline", "Decline the return"),
        ],
        string="Decision",
    )
    decision_notes = fields.Text(string="Decision Notes")
    state = fields.Selection(
        [("draft", "Draft"), ("received", "Received"), ("decided", "Decided")],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    received_by_id = fields.Many2one("res.users", string="Received By", readonly=True, copy=False)
    received_at = fields.Datetime(readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "warranty_id",
            "grade_at_sale",
            "within_terms",
            "received_by_id",
            "received_at",
            "decided_by_id",
            "decided_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._INPUTS
        if self and any(r.state == "decided" for r in self):
            locked |= {"outcome", "decision_notes"}
        return locked

    @staticmethod
    def _sold(tradein) -> bool:
        stock = tradein.sudo().graded_stock_id
        return bool(stock) and stock.state == "sold"

    @api.model_create_multi
    def create(self, vals_list):
        Request = self.env["fix.tradein.request"].sudo()
        for vals in vals_list:
            tradein = Request.browse(vals.get("tradein_id") or [])
            if not self._fix_guard_open() and tradein and not self._sold(tradein):
                raise UserError(
                    "Trade-in %s has not been sold: only a sold refurbished unit is returned."
                    % tradein.name
                )
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.refurb.return") or "RRT/New"
                )
        records = super().create(vals_list)
        Warranty = self.env["fix.tradein.warranty"].sudo()
        for rec in records:
            warranty = Warranty.search(
                [("tradein_id", "=", rec.tradein_id.id), ("state", "!=", "void")],
                order="start_date desc, id desc",
                limit=1,
            )
            rec._guarded().write(
                {"warranty_id": warranty.id or False, "grade_at_sale": rec.tradein_id.grade}
            )
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                locked = rec._fix_form_locked_fields()
                names = [
                    n for n in locked & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if names:
                    _locked_refusal(rec, names, "Return")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(r.state != "draft" for r in self):
            raise UserError("A received return is evidence and is not deleted.")
        return super().unlink()

    def _within_terms(self) -> bool:
        self.ensure_one()
        warranty = self.warranty_id.sudo()
        if not warranty or not warranty.start_date:
            return False
        days = int(_param_float(self.env, PARAM_RETURN_WINDOW_DAYS, 7))
        if self.return_date <= warranty.start_date + timedelta(days=max(days, 0)):
            return True
        return bool(
            warranty.state == "active"
            and warranty.end_date
            and self.return_date <= warranty.end_date
        )

    def action_receive(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Return %s is already %s." % (rec.name, rec.state))
            if not self._sold(rec.tradein_id):
                raise UserError("Trade-in %s has not been sold." % rec.tradein_id.name)
            if not (rec.failure_code or rec.reason == "change_of_mind"):
                raise UserError(
                    "Return %s: record the failure code; it is what the grading analysis reads "
                    "(FR-TRF-026)." % rec.name
                )
            within = rec._within_terms()
            if not within:
                raise UserError(
                    "Return %s: the unit is outside its return window and its refurbished "
                    "warranty. It is not taken back as a refurbished return." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "received",
                    "within_terms": True,
                    "received_by_id": self.env.uid,
                    "received_at": fields.Datetime.now(),
                }
            )
            if rec.warranty_id and rec.reason != "change_of_mind":
                warranty = rec.warranty_id.sudo()
                warranty._guarded().write({"claims_count": (warranty.claims_count or 0) + 1})
            # M14-05: the unit is held for a new wipe, QA and grade, the sale's
            # cost reversed and its warranty closed (through the stock)
            stock = rec.tradein_id.sudo().graded_stock_id
            if stock and stock.state == "sold":
                stock.with_context(refurb_return_id=rec.id).action_receive_return(
                    reason="refurbished return %s" % rec.name
                )
            rec.tradein_id.sudo().message_post(
                body="Refurbished unit returned (%s): %s, failure code %s, sold at grade %s."
                % (
                    rec.name,
                    dict(self._fields["reason"].selection).get(rec.reason),
                    rec.failure_code or "-",
                    (rec.grade_at_sale or "?").upper(),
                )
            )
        return True

    def action_decide(self):
        _assert_role(self.env, GROUP_REFURB_SUPERVISOR, "Deciding a refurbished return")
        for rec in self:
            if rec.state != "received":
                raise UserError(
                    "Return %s is %s: it is decided once received." % (rec.name, rec.state)
                )
            if not rec.outcome:
                raise UserError("Return %s: choose the decision first." % rec.name)
            if not self.env.su and self.env.user == rec.received_by_id:
                raise UserError(
                    "Segregation of duties: the person who received the return does not decide it."
                )
            rec._guarded().write(
                {
                    "state": "decided",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
            rec.tradein_id.sudo().message_post(
                body="Return %s decided: %s."
                % (rec.name, dict(self._fields["outcome"].selection).get(rec.outcome))
            )
        return True


# =========================================================================== p10
class FixRefurbWriteoff(models.Model):
    """Parts-only routing and the write-off of its accumulated cost
    (FR-TRF-020, BRU-TRF-19, §8.1 QA -> Parts-Only "Supervisor + approval",
    §13: parts-only routing and write-off approval are two people)."""

    _name = "fix.refurb.writeoff"
    _description = "Parts-Only Routing & Write-off"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    _INPUTS = frozenset(
        {
            "tradein_id",
            "cause",
            "cause_notes",
            "destination",
            "resale_estimate",
            "cost_to_complete",
            "company_id",
        }
    )

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Unit (Trade-In)", required=True, index=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cause = fields.Selection(
        [
            ("qa_failed", "Failed QA"),
            ("unrecoverable_fault", "Unrecoverable fault"),
            ("cost_to_complete", "Cost to complete exceeds the resale estimate"),
            ("other", "Other"),
        ],
        string="Cause",
        required=True,
    )
    cause_notes = fields.Text(string="Why the Unit Cannot Be Sold")
    destination = fields.Selection(
        [("harvest", "Harvest for parts (M15)"), ("recycle", "Recycle (M18)")],
        string="Route To",
        required=True,
        default="harvest",
    )
    resale_estimate = fields.Monetary(string="Resale Estimate", currency_field="currency_id")
    cost_to_complete = fields.Monetary(string="Cost to Complete", currency_field="currency_id")
    accumulated_cost = fields.Monetary(
        string="Accumulated Cost Written Off",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Approval Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    requested_by_id = fields.Many2one("res.users", string="Routed By", readonly=True, copy=False)
    requested_at = fields.Datetime(readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Text(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "accumulated_cost",
            "requested_by_id",
            "requested_at",
            "approved_by_id",
            "approved_at",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._INPUTS
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            Request = self.env["fix.tradein.request"].sudo()
            for vals in vals_list:
                tradein = Request.browse(vals.get("tradein_id") or [])
                if tradein and tradein.state not in ROUTABLE_STATES:
                    raise UserError(
                        "Trade-in %s is %s: a unit is routed to parts only from intake, "
                        "refurbishment or grading." % (tradein.name, tradein.state)
                    )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.refurb.writeoff") or "RWO/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                names = [
                    n
                    for n in self._INPUTS & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if names:
                    _locked_refusal(rec, names, "Write-off")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(r.state != "draft" for r in self):
            raise UserError("A routed write-off is evidence and is not deleted.")
        return super().unlink()

    def action_request(self):
        _assert_role(self.env, GROUP_REFURB_SUPERVISOR, "Routing a unit to parts only")
        for rec in self:
            if rec.state not in ("draft", "rejected"):
                raise UserError("Write-off %s is %s." % (rec.name, rec.state))
            tradein = rec.tradein_id.sudo()
            if tradein.state not in ROUTABLE_STATES:
                raise UserError(
                    "Trade-in %s is %s: a unit is routed to parts only from intake, "
                    "refurbishment or grading." % (tradein.name, tradein.state)
                )
            if not (rec.cause_notes or "").strip():
                raise UserError("Write-off %s: state why the unit cannot be sold." % rec.name)
            if rec.cause == "cost_to_complete" and not (
                rec.resale_estimate > 0 and rec.cost_to_complete > rec.resale_estimate
            ):
                raise UserError(
                    "Write-off %s: a cost-to-complete routing needs a cost to complete above "
                    "the resale estimate." % rec.name
                )
            live = self.search_count(
                [
                    ("tradein_id", "=", tradein.id),
                    ("state", "in", ("pending", "approved")),
                    ("id", "!=", rec.id),
                ]
            )
            if live:
                raise UserError(
                    "Trade-in %s already has a parts-only routing pending or approved."
                    % tradein.name
                )
            rec._guarded().write(
                {
                    "state": "pending",
                    "accumulated_cost": tradein._tradein_landed_cost(),
                    "requested_by_id": self.env.uid,
                    "requested_at": fields.Datetime.now(),
                    "approved_by_id": False,
                    "approved_at": False,
                    "rejection_reason": False,
                }
            )
        return True

    def action_approve(self):
        _assert_role(self.env, GROUP_WRITEOFF_APPROVER, "Approving a refurbishment write-off")
        for rec in self:
            if rec.state != "pending":
                raise UserError(
                    "Write-off %s is %s: only a pending one is approved." % (rec.name, rec.state)
                )
            if not self.env.su and self.env.user == rec.requested_by_id:
                raise UserError(
                    "Segregation of duties: the person who routed the unit to parts only does "
                    "not approve its write-off (§13)."
                )
            tradein = rec.tradein_id.sudo()
            if tradein.state not in ROUTABLE_STATES:
                raise UserError(
                    "Trade-in %s is %s: its parts-only routing can no longer be approved."
                    % (tradein.name, tradein.state)
                )
            # XC-24: the approver's DOFA tier covers the cost written off
            amount = max(tradein._tradein_landed_cost(), rec.accumulated_cost or 0.0)
            _assert_amount_tier(self.env, amount, "Approving a refurbishment write-off")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                    "accumulated_cost": amount,
                }
            )
            # M14-09/21: the unit leaves the sellable path (parts only), its
            # stock unit is scrapped, and a recycling route writes its cost off
            # now (a harvest relieves it part by part, the residue at close)
            tradein._guarded().write({"state": "parts_only", "written_off": True})
            stock = tradein.graded_stock_id
            if stock and stock.state in ("in_stock", "reserved", "returned"):
                stock._guarded().write({"state": "scrapped"})
            if rec.destination == "recycle":
                tradein._tradein_writeoff_carrying("routed to recycling (%s)" % rec.name)
            rec.tradein_id.sudo().message_post(
                body="Routed to %s as parts only (%s); accumulated cost BDT %.2f written off, "
                "approved by %s."
                % (
                    dict(self._fields["destination"].selection).get(rec.destination),
                    rec.name,
                    rec.accumulated_cost,
                    self.env.user.name,
                )
            )
        return True

    def action_reject(self, reason=None):
        _assert_role(self.env, GROUP_WRITEOFF_APPROVER, "Rejecting a refurbishment write-off")
        for rec in self:
            if rec.state != "pending":
                raise UserError("Write-off %s is %s." % (rec.name, rec.state))
            if not (reason or "").strip():
                raise UserError("State why the write-off is rejected.")
            rec._guarded().write({"state": "rejected", "rejection_reason": reason.strip()})
        return True


class FixTradeinHarvestRouting(models.Model):
    _inherit = "fix.tradein.harvest"

    def _harvest_denial(self) -> str:
        denial = super()._harvest_denial()
        if denial:
            return denial
        approved = (
            self.env["fix.refurb.writeoff"]
            .sudo()
            .search_count(
                [
                    ("tradein_id", "=", self.tradein_id.id),
                    ("state", "=", "approved"),
                    ("destination", "=", "recycle" if self.target == "recycle" else "harvest"),
                ]
            )
        )
        if not approved:
            return (
                "trade-in %s has no approved parts-only routing to %s: a supervisor routes "
                "it and a write-off approver approves its cost (FR-TRF-020, BRU-TRF-19)"
                % (self.tradein_id.name, "recycling" if self.target == "recycle" else "harvest")
            )
        return ""
