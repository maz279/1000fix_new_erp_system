# fix_tradein — M14: trade-in, refurbishment, resale (P09-M04 / R07-M03).
from __future__ import annotations

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


class FixTradeinRequest(models.Model):
    """Journey 9: trade-in -> offer -> intake -> data wipe -> refurbishment
    -> grading -> resale -> payout. The circular business's money path.
    Composes M03 logistics, M06 data wipe gate, M31 workshop refurbishment,
    M37 grading, M15 graded inventory valuation, and M50 treasury payout."""

    _name = "fix.tradein.request"
    _description = "Trade-In Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

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
    def _wipe_gate_denial(cert) -> str:
        """'' when ``cert`` is a VERIFIED M06 wipe certificate, else why not."""
        if not cert:
            return "no M06 data wipe certificate is attached"
        if cert.sanitization_status != "verified":
            return "wipe certificate %s is '%s', not verified" % (
                cert.name,
                cert.sanitization_status,
            )
        return ""

    def action_wipe(self):
        """The secure data wipe gate: the wipe operator's M06 certificate
        (evidence entered and verified in cd_data_case) must be attached and
        VERIFIED. Nothing is certified here - no certificate is created."""
        for rec in self:
            if rec.state != "collected":
                raise UserError("Wipe from collected")
            denial = rec._wipe_gate_denial(rec.wipe_certificate_id)
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
            denial = rec._wipe_gate_denial(rec.wipe_certificate_id)
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
                        "tradein_id": rec.id,
                        "grade_id": rec.refurb_grade_id.id,
                        "acquisition_cost": rec.offered_value,
                        "refurbishment_cost": rec.refurbishment_cost,
                        "resale_price": rec.resale_value,
                        "state": "in_stock",
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
        never the pre-inspection offer regardless of grade."""
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

            # Queue the payout with M50 treasury. Only treasury releases it and
            # marks it executed on bank/MFS evidence; trade-in never asserts
            # the money left. Created with sudo after the approval checks
            # above: a branch user requests a payout without treasury rights.
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
                            "amount": rec.graded_value,
                            "method": "mobile_fs",  # default bKash/Nagad
                        }
                    )
                )
                rec.payout_execution_id = payment.id

            rec.write({"state": "closed", "payout_amount": rec.graded_value})
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
        [("pending", "Pending"), ("done", "Done")], default="pending", required=True
    )
    notes = fields.Text()
    technician_id = fields.Many2one("hr.employee", string="Technician")
    parts_cost = fields.Monetary(
        string="Step Parts Cost", currency_field="currency_id", default=0.0
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
