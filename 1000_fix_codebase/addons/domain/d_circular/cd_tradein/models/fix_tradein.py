# fix_tradein — M14: trade-in, refurbishment, resale (P09-M04 / R07-M03).
from __future__ import annotations

import re

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

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

# A Smart NID is 10 digits; the legacy NID 13 or 17. A 12-digit e-TIN.
_NID_RE = re.compile(r"^\d{10}(\d{3}|\d{7})?$")
_ETIN_RE = re.compile(r"^\d{12}$")


class FixTradeinRequest(models.Model):
    """Journey 9: trade-in -> offer -> intake -> data wipe -> refurbishment
    -> grading -> resale -> payout. The circular business's money path.
    Composes M03 logistics, M06 data wipe gate, M31 workshop refurbishment,
    M37 grading, M15 graded inventory valuation, and M50 treasury payout."""

    _name = "fix.tradein.request"
    _description = "Trade-In Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "create_date desc, id desc"

    # A05 DOFA matrix — Customer Trade-In Valuation & Payout: Appraisal
    # Specialist to 50k, Service Hub Lead to 250k, Head of Circular Economy
    # to 1M, CFO above.
    _DOFA_THRESHOLDS = [
        (50000.0, "tier_1"),
        (250000.0, "tier_2"),
        (1000000.0, "tier_3"),
        (float("inf"), "tier_4"),
    ]

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
        help="The trade-in offer (acquisition cost)",
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

    # Statutory Compliance (BTRC NEIR, ITA 2023 TDS & Customer NID)
    customer_nid = fields.Char(
        string="Customer Smart NID",
        copy=False,
        tracking=True,
        help="10-digit Smart NID or 13/17-digit legacy NID — required before any "
        "payout leaves (AML / ITA 2023 identification)",
    )
    taxpayer_tin = fields.Char(
        string="Taxpayer e-TIN",
        copy=False,
        help="The seller's 12-digit e-TIN; its absence lifts the TDS rate by 50%",
    )
    psr_verified = fields.Boolean(
        string="PSR Verified",
        default=False,
        copy=False,
        help="Presumptive Sadharan Rate acknowledgement sighted — without it the "
        "withholding rate is uplifted 50% (ITA 2023 s.142)",
    )
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
    tds_rate_pct = fields.Float(string="TDS Rate % (Contract)", default=5.0)
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
        string="TDS Withholding Certificate No",
        copy=False,
        help="The income-tax TDS certificate issued to the seller (NOT Mushak 6.6, "
        "which evidences only VAT deducted at source)",
    )

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

    state = fields.Selection(TRADEIN_STATES, default="draft", required=True, tracking=True)

    # M06 Data Wipe Gate
    wipe_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate",
        string="Data Wipe Certificate (M06)",
        ondelete="set null",
        index=True,
        help="M06's secure wipe; required before refurbishment (Journey 9 gate)",
    )

    # Refurbishment costing on M31 workshop model
    workshop_job_id = fields.Many2one(
        "fix.workshop.job", string="Workshop Refurb Job (M31)", ondelete="set null"
    )
    parts_cost = fields.Monetary(
        string="Refurb Parts Cost", currency_field="currency_id", default=0.0
    )
    labour_cost = fields.Monetary(
        string="Refurb Labour Cost", currency_field="currency_id", default=0.0
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
        help="Capitalized stock cost = Offered Value + Refurbishment Cost",
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

    @api.depends("parts_cost", "labour_cost")
    def _compute_refurb_cost(self):
        for rec in self:
            rec.refurbishment_cost = (rec.parts_cost or 0.0) + (rec.labour_cost or 0.0)

    @api.depends("offered_value", "refurbishment_cost")
    def _compute_inventory_valuation(self):
        for rec in self:
            rec.inventory_valuation = (rec.offered_value or 0.0) + (rec.refurbishment_cost or 0.0)

    @api.depends("graded_value", "tds_applicable", "tds_rate_pct", "psr_verified", "taxpayer_tin")
    def _compute_tds(self):
        for rec in self:
            val = rec.graded_value or 0.0
            # ITA 2023 s.142: withholding without a sighted PSR or e-TIN is
            # lifted by half again (the estate's x1.5 uplift, M53/M52 pattern).
            rate = rec.tds_rate_pct or 0.0
            if (
                rec.tds_applicable
                and rate > 0
                and not (rec.psr_verified or (rec.taxpayer_tin or "").strip())
            ):
                rate = round(rate * 1.5, 4)
            rec.tds_effective_rate_pct = rate if rec.tds_applicable else 0.0
            tds = round(val * (rate / 100.0), 2) if rec.tds_applicable and rate > 0 else 0.0
            rec.tds_amount = tds
            rec.net_payout = max(0.0, val - tds)

    @api.constrains("customer_nid", "taxpayer_tin")
    def _check_statutory_ids(self):
        for rec in self:
            if rec.customer_nid and not _NID_RE.match(rec.customer_nid.strip()):
                raise ValidationError(
                    "Customer NID %r is not a 10-digit Smart NID or 13/17-digit NID."
                    % rec.customer_nid
                )
            if rec.taxpayer_tin and not _ETIN_RE.match(rec.taxpayer_tin.strip()):
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.request") or "TRD/New"
                )
        return super().create(vals_list)

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
        workshops = self.env["fix.workshop"]
        domain = [("company_id", "=", self.company_id.id)]
        workshop = workshops.search([*domain, ("workshop_type", "=", "central")], limit=1)
        workshop = workshop or workshops.search(domain, limit=1)
        if not workshop:
            raise UserError(
                "No active M31 workshop is configured for %s — refurbishment cannot be "
                "scheduled" % self.company_id.name
            )
        return workshop

    def action_send_offer(self):
        for rec in self:
            if rec.offered_value <= 0:
                raise UserError("An offer requires a positive valuation")
            rec.state = "offered"
            publish(
                self.env,
                "tradein.offered",
                "fix.tradein.request",
                rec.id,
                {"customer": rec.customer_id.name, "value": float(rec.offered_value)},
            )

    def action_accept(self):
        for rec in self:
            if rec.state != "offered":
                raise UserError("Accept from offered")
            rec.state = "accepted"

    def action_collect(self):
        """Collection through M03 logistics (unbroken custody chain begins)."""
        for rec in self:
            if rec.state != "accepted":
                raise UserError("Collect from accepted")
            if not rec.consignment_id:
                consignment = self.env["fix.consignment"].create(
                    {
                        "consignment_type": "pickup",
                        "scheduled_date": fields.Datetime.now(),
                        "operating_unit_id": rec._operating_unit().id,
                    }
                )
                rec.consignment_id = consignment.id
            rec.state = "collected"
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

    @staticmethod
    def _wipe_gate_denial(cert, device=None) -> str:
        """'' when ``cert`` is a VERIFIED M06 wipe certificate for this
        device's media serial, else why not. A02 audit M06-1: the status alone
        was forgeable and one certificate released any number of devices."""
        if not cert:
            return "no M06 data wipe certificate is attached"
        return cert._fix_certify_denial(cert._fix_media_serial(device))

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
            rec.state = "wiped"
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

            # Create or link workshop job if absent
            if not rec.workshop_job_id:
                job = self.env["fix.workshop.job"].create(
                    {
                        "workshop_id": rec._refurb_workshop().id,
                        "device_id": rec.device_id.id if rec.device_id else False,
                        "customer_id": rec.customer_id.id,
                        "fault_description": "Trade-in refurbishment (%s): clean, test, "
                        "replace worn components" % rec.name,
                    }
                )
                rec.workshop_job_id = job.id

            # the Refurb Work Orders screen reads fix.refurbishment: create the
            # step plan once per unit so the workspace grid is the real plan,
            # not an empty model beside a workshop job
            steps = self.env["fix.refurbishment"]
            if not steps.search_count([("tradein_id", "=", rec.id)]):
                labels = dict(steps._fields["step"].selection)
                for step in ("intake", "repair", "cosmetic", "testing", "final_qa"):
                    steps.create(
                        {
                            "name": "%s · %s" % (rec.name, labels.get(step, step)),
                            "tradein_id": rec.id,
                            "step": step,
                            "state": "done" if step == "intake" else "pending",
                            "parts_cost": 0.0,
                        }
                    )

            rec.state = "refurbished"
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

            # Auto-align selection and master grade
            if rec.refurb_grade_id and not rec.grade:
                code_map = {"A": "a", "B": "b", "C": "c", "D": "d", "E": "e"}
                rec.grade = code_map.get(rec.refurb_grade_id.code, "b")
            elif rec.grade and not rec.refurb_grade_id:
                master_grade = self.env["fix.refurb.grade"].search(
                    [("code", "=", rec.grade.upper())], limit=1
                )
                if master_grade:
                    rec.refurb_grade_id = master_grade.id

            # Auto-compute resale value if not manually set
            if not rec.resale_value or rec.resale_value <= 0:
                multiplier = rec.refurb_grade_id.price_multiplier if rec.refurb_grade_id else 1.0
                base_benchmark = max(rec.offered_value * 1.6, 1000.0)
                rec.resale_value = base_benchmark * multiplier

            rec.state = "graded"
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

            # Create M15 graded inventory stock entry
            if not rec.graded_stock_id and rec.device_id and rec.refurb_grade_id:
                stock = self.env["fix.graded.stock"].create(
                    {
                        "device_id": rec.device_id.id,
                        "grade_id": rec.refurb_grade_id.id,
                        "acquisition_cost": rec.offered_value,
                        "refurbishment_cost": rec.refurbishment_cost,
                        "resale_price": rec.resale_value,
                        "state": "in_stock",
                        # the graded-stock screen shows the origin trade-in
                        "tradein_id": rec.id,
                        "tradein_ref": rec.name,
                    }
                )
                rec.graded_stock_id = stock.id

            rec.state = "resale_ready"
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

    def action_request_payout_approval(self):
        """Submit the graded payout value for approval (after grading)."""
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
            rec.write(
                {
                    "payout_approval_state": "pending",
                    "payout_requested_by_id": self.env.uid,
                    "payout_approved_by_id": False,
                    "payout_approved_at": False,
                }
            )
        return True

    def action_approve_payout(self):
        """Four-eyes approval: the approver is not the requester."""
        for rec in self:
            if rec.payout_approval_state != "pending":
                raise UserError("Only a pending payout can be approved")
            if rec.payout_requested_by_id.id == self.env.uid:
                raise UserError("Four-eyes: the payout requester cannot approve their own payout")
            rec.write(
                {
                    "payout_approval_state": "approved",
                    "payout_approved_by_id": self.env.uid,
                    "payout_approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject_payout(self):
        for rec in self:
            if rec.payout_approval_state != "pending":
                raise UserError("Only a pending payout can be rejected")
            rec.payout_approval_state = "rejected"
        return True

    def write(self, vals):
        # Changing the graded value voids an approval of the old amount.
        if "graded_value" in vals:
            for rec in self:
                if (
                    rec.payout_approval_state in ("pending", "approved")
                    and rec.graded_value != vals["graded_value"]
                ):
                    if rec.payout_execution_id or rec.state == "closed":
                        raise UserError(
                            "Payout for %s has already been sent to treasury" % rec.name
                        )
                    vals = dict(vals, payout_approval_state="none")
        return super().write(vals)

    def action_pay(self):
        """Trade-in payout through M50 treasury: the APPROVED graded value,
        never the pre-inspection offer regardless of grade. Statutory gates
        before a taka leaves: identified seller (NID), BTRC NEIR clearance,
        TDS certificate issued where withholding applies, and DOFA authority
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
            # Identified seller (AML / ITA 2023): an anonymous payout is a
            # laundering vector, not a customer-convenience feature.
            if not (rec.customer_nid or "").strip():
                raise UserError(
                    "Payout blocked: customer Smart NID is required before any "
                    "trade-in money leaves (AML identification)"
                )
            # BTRC Provenance Anti-Theft Validation
            prov = self.env["fix.tradein.provenance"].search([("tradein_id", "=", rec.id)], limit=1)
            if prov and (prov.stolen_hit or prov.blacklist_hit or prov.state == "flagged"):
                raise UserError(
                    "Payout blocked: Device IMEI flagged as stolen/blacklisted by BTRC NEIR"
                )
            # Withholding must be evidenced: the certificate number is the
            # seller's only proof of credit for the tax withheld.
            if rec.tds_applicable and rec.tds_amount and not (rec.tds_certificate_no or "").strip():
                raise UserError(
                    "Payout blocked: BDT %.2f TDS is withheld but no income-tax TDS "
                    "withholding certificate has been issued (ITA 2023 %s)"
                    % (rec.tds_amount, dict(rec._fields["tds_section"].selection)[rec.tds_section])
                )
            # DOFA: the payout amount decides the tier that must sign it off.
            rec._dofa_assert_approved("A trade-in payout")

            # Queue the payout with M50 treasury. Only treasury releases it and
            # marks it executed on bank/MFS evidence; trade-in never asserts
            # the money left. Created with sudo after the approval checks
            # above: a branch user requests a payout without treasury rights.
            # The seller receives the NET (graded value − TDS): the withheld
            # tax is the Crown's money and is remitted to NBR separately,
            # never bundled into the seller's payout.
            net_to_seller = rec.net_payout if rec.tds_applicable else rec.graded_value
            if not rec.payout_execution_id:
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
                rec.payout_execution_id = payment.id

            rec.write({"state": "closed", "payout_amount": net_to_seller})
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


class FixRefurbishment(models.Model):
    """A refurbishment step within a trade-in (composes the workshop)."""

    _name = "fix.refurbishment"
    _description = "Refurbishment Step"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
    )
    notes = fields.Text()
    technician_id = fields.Many2one("hr.employee", string="Technician")
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

    @api.depends("parts_cost", "labor_cost")
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = (rec.parts_cost or 0.0) + (rec.labor_cost or 0.0)

    def action_start(self):
        """Allocate technician and initiate repair session."""
        for rec in self:
            if not rec.technician_id:
                employee = self.env["hr.employee"].search(
                    [("user_id", "=", self.env.user.id)], limit=1
                )
                if employee:
                    rec.technician_id = employee.id
            rec.state = "in_progress"

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
            rec.state = "done"
            if rec.tradein_id:
                rec.tradein_id.message_post(
                    body="Refurbishment step '%s' completed by %s. Cost: BDT %.2f"
                    % (
                        dict(rec._fields["step"].selection).get(rec.step, rec.step),
                        rec.technician_id.name if rec.technician_id else "Technician",
                        rec.total_cost,
                    )
                )
