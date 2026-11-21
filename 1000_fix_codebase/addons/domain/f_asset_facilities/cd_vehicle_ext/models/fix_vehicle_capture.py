# fix_vehicle_capture — M46 capture audit (2026-11-17).
#
# The audit found sub-module pages whose records could not be captured
# because the record did not exist at all:
#   * Statutory Documents: no renewal record (FR-FLT-013 P0, FR-FLT-014): a
#     renewal's government fee, agent fee and lapse penalty, and who was
#     responsible, were recorded nowhere;
#   * Pre-Use & PM: a defect existed only as an off-road record, so a
#     deferrable defect (FR-FLT-025: "classify it as safety-critical or
#     deferrable") could not be recorded without stopping the vehicle; a
#     service named no garage, work, invoice or next due (FR-FLT-027 P0);
#   * Telematics: the device was a free-text label on a snapshot. No register
#     held its identifier, SIM, data plan, firmware or fitment (FR-FLT-035 P0);
#   * Accidents & Insurance: no traffic fine or penalty (FR-FLT-043,
#     BRU-FLT-16: recorded against the vehicle and the driver on duty, with a
#     recover-or-absorb decision);
#   * Vehicle Register: no ownership basis (FR-FLT-003 P0), so a leased van
#     was capitalised in M49 like an owned one.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_vehicle_ops import (
    FLEET_OFFICER_GROUP,
    LOGISTICS_MANAGER_GROUP,
    PAYMENT_METHODS_NO_CARD,
    _reason,
    _vehicle_label,
    dhaka_default,
    dhaka_today,
    emit,
    like_exact,
    m52_raise,
    param_float,
    payment_problems,
    require_role,
)

OWNERSHIP_BASIS = [
    ("owned", "Owned"),
    ("leased", "Leased"),
    ("hired", "Hired"),
    ("employee_owned", "Employee-Owned (reimbursed)"),
]


def _money(value, what):
    if (value or 0.0) < 0:
        raise ValidationError("%s cannot be negative." % what)


# --------------------------------------------------------------------------
# Vehicle Register: ownership basis (FR-FLT-003)
# --------------------------------------------------------------------------
class FleetVehicleOwnership(models.Model):
    _inherit = "fleet.vehicle"

    fix_ownership_basis = fields.Selection(
        OWNERSHIP_BASIS,
        string="Ownership Basis",
        default="owned",
        required=True,
        help="Owned vehicles are capitalised in M49 from their purchase value. A leased, "
        "hired or employee-owned vehicle is not the company's asset and is not "
        "capitalised; it names its contract.",
    )
    fix_contract_ref = fields.Char(
        string="Lease / Hire / Reimbursement Contract",
        help="The contract under which a vehicle the company does not own is used.",
    )
    fix_contract_end = fields.Date(string="Contract End")
    fix_end_of_term = fields.Char(
        string="End-of-Term Obligation", help="Return, purchase option, buy-back..."
    )

    @api.constrains("fix_ownership_basis", "fix_contract_ref", "fix_contract_end")
    def _check_ownership_contract(self):
        for rec in self:
            if rec.fix_ownership_basis != "owned" and not (
                (rec.fix_contract_ref or "").strip() and rec.fix_contract_end
            ):
                label = dict(OWNERSHIP_BASIS)[rec.fix_ownership_basis]
                raise ValidationError(
                    "A vehicle used on a %s basis names its contract and the contract end "
                    "date (FR-FLT-003)." % label.lower()
                )

    def write(self, vals):
        # The basis decides whether M49 capitalises the vehicle: the same
        # Logistics Manager decision as the purchase value. The form posts
        # every field it shows, so an unchanged echo passes.
        if (
            not self.env.su
            and "fix_ownership_basis" in vals
            and any(rec.fix_ownership_basis != vals["fix_ownership_basis"] for rec in self)
        ):
            require_role(
                self.env, LOGISTICS_MANAGER_GROUP, "Changing the ownership basis of a vehicle"
            )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and any(
            vals.get("fix_ownership_basis", "owned") != "owned" for vals in vals_list
        ):
            require_role(
                self.env,
                LOGISTICS_MANAGER_GROUP,
                "Registering a leased, hired or employee-owned vehicle",
            )
        return super().create(vals_list)


# --------------------------------------------------------------------------
# Statutory Documents: renewal (FR-FLT-013 / FR-FLT-014)
# --------------------------------------------------------------------------
class FixVehicleDocumentRenewal(models.Model):
    _name = "fix.vehicle.document.renewal"
    _description = "Vehicle Document Renewal"
    _inherit = ["mail.thread", "fix.vehicle.lock.mixin"]
    _order = "initiated_on desc, id desc"
    _fix_insert_only = True

    name = fields.Char(required=True, default="New", copy=False)
    document_id = fields.Many2one(
        "fix.vehicle.document",
        string="Document Being Renewed",
        required=True,
        ondelete="restrict",
        index=True,
    )
    vehicle_id = fields.Many2one(
        "fleet.vehicle", related="document_id.vehicle_id", store=True, string="Vehicle"
    )
    doc_type = fields.Selection(related="document_id.doc_type", store=True, string="Document Type")
    expires_on = fields.Date(related="document_id.valid_to", string="Expires On")
    responsible_employee_id = fields.Many2one(
        "hr.employee", string="Responsible Person", required=True, ondelete="restrict"
    )
    issuing_authority = fields.Char(string="Issuing Authority", help="e.g. BRTA Mirpur circle")
    initiated_on = fields.Date(required=True, default=dhaka_default)
    submitted_on = fields.Date(string="Submitted On", readonly=True, copy=False)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    government_fee = fields.Monetary(currency_field="currency_id", string="Government Fee")
    agent_fee = fields.Monetary(currency_field="currency_id", string="Agent Fee")
    penalty = fields.Monetary(currency_field="currency_id", string="Late Penalty")
    penalty_reason = fields.Char(string="Why a Penalty Was Paid")
    total_cost = fields.Monetary(
        currency_field="currency_id", compute="_compute_total_cost", store=True, string="Total Cost"
    )
    receipt_file = fields.Binary(string="Fee Receipt (scan)", attachment=True, copy=False)
    receipt_filename = fields.Char(string="Fee Receipt File Name", copy=False)
    # A07 ERP audit M46-01 (money contract): who was paid the fees and how.
    payment_method = fields.Selection(PAYMENT_METHODS_NO_CARD, string="Payment Method")
    vendor_id = fields.Many2one(
        "res.partner",
        string="Paid To (BRTA / agent / insurer)",
        ondelete="restrict",
    )
    invoice_ref = fields.Char(string="Invoice / Receipt No")
    paid_on = fields.Date(string="Paid On", readonly=True, copy=False)
    payment_ref = fields.Char(string="Payment Ref", readonly=True, copy=False)
    new_document_id = fields.Many2one(
        "fix.vehicle.document",
        string="Renewed Document",
        ondelete="restrict",
        help="The new certificate, recorded in the register with its scan.",
    )
    state = fields.Selection(
        [
            ("initiated", "Initiated"),
            ("submitted", "Submitted"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="initiated",
        tracking=True,
    )
    completed_by_id = fields.Many2one("res.users", string="Completed By", readonly=True, copy=False)
    completed_on = fields.Date(string="Completed On", readonly=True, copy=False)
    cancel_reason = fields.Char(string="Cancellation Reason", readonly=True, copy=False)

    @api.depends("government_fee", "agent_fee", "penalty")
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = (
                (rec.government_fee or 0.0) + (rec.agent_fee or 0.0) + (rec.penalty or 0.0)
            )

    @api.constrains("government_fee", "agent_fee", "penalty")
    def _check_fees(self):
        for rec in self:
            _money(rec.government_fee, "A government fee")
            _money(rec.agent_fee, "An agent fee")
            _money(rec.penalty, "A penalty")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_on",
            "completed_by_id",
            "completed_on",
            "cancel_reason",
            "paid_on",
            "payment_ref",
        }

    def _fix_frozen_fields(self) -> set:
        if self.state in ("completed", "cancelled"):
            return {
                "document_id",
                "responsible_employee_id",
                "issuing_authority",
                "initiated_on",
                "government_fee",
                "agent_fee",
                "penalty",
                "penalty_reason",
                "new_document_id",
                "receipt_file",
                "receipt_filename",
                "payment_method",
                "vendor_id",
                "invoice_ref",
            }
        if isinstance(self.id, int):
            return {"document_id"}
        return set()

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, FLEET_OFFICER_GROUP, "Opening a document renewal")
        Doc = self.env["fix.vehicle.document"].sudo()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.document.renewal")
                    or "VREN/New"
                )
            doc = Doc.browse(vals.get("document_id"))
            if doc.exists() and self.sudo().search_count(
                [("document_id", "=", doc.id), ("state", "in", ("initiated", "submitted"))]
            ):
                raise UserError(
                    "%s already has a renewal in progress: continue that one." % doc.name
                )
        return super().create(vals_list)

    def action_submit(self):
        """Initiated -> submitted to the authority (BRTA, the insurer)."""
        require_role(self.env, FLEET_OFFICER_GROUP, "Submitting a document renewal")
        for rec in self:
            if rec.state != "initiated":
                raise UserError("Submit an initiated renewal.")
            rec._guarded().write({"state": "submitted", "submitted_on": dhaka_today(rec)})
        return True

    def action_complete(self):
        """Submitted -> completed: the new certificate is in the register,
        with its scan, for the same vehicle and type, and in date (§8.2 "new
        document issued, evidence uploaded"). A penalty is a lapse: the person
        responsible for the renewal may not be the one who completes it, so
        the penalty is never approved by the person it arose from (§13 SoD)."""
        require_role(self.env, FLEET_OFFICER_GROUP, "Completing a document renewal")
        today = dhaka_today(self)
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Complete a submitted renewal.")
            new = rec.new_document_id.sudo()
            old = rec.document_id.sudo()
            if not new:
                raise UserError(
                    "Record the renewed %s in Documents & Expiry, with its scan, and choose it "
                    "as the Renewed Document first."
                    % dict(old._fields["doc_type"].selection).get(old.doc_type, old.doc_type)
                )
            if new == old or new.vehicle_id != old.vehicle_id or new.doc_type != old.doc_type:
                raise UserError(
                    "The renewed document must be a new %s of %s."
                    % (old.doc_type, _vehicle_label(old.vehicle_id))
                )
            if not new.has_evidence:
                raise UserError("%s has no evidence scan attached." % new.name)
            if new.state != "valid" or not new.valid_to or new.valid_to < today:
                raise UserError("%s is not in date." % new.name)
            if rec.penalty and not (rec.penalty_reason or "").strip():
                raise UserError("Say why a late penalty of %s was paid." % rec.penalty)
            if not self.env.su and rec.total_cost > 0:
                # A07 ERP audit M46-01: the fees are money: how they were
                # paid, to whom, and the receipt or invoice.
                problems = payment_problems(
                    rec.payment_method,
                    rec.vendor_id,
                    rec.invoice_ref,
                    rec.receipt_file,
                    rec.responsible_employee_id,
                )
                if problems:
                    raise UserError(
                        "Record %s on %s: the fees of %.2f are paid through M52."
                        % (" and ".join(problems), rec.name, rec.total_cost)
                    )
            if (
                not self.env.su
                and rec.penalty
                and rec.responsible_employee_id.user_id == self.env.user
            ):
                raise UserError(
                    "Segregation of duties: a penalty arose from your renewal; another Fleet "
                    "Officer completes it."
                )
            rec._guarded().write(
                {"state": "completed", "completed_by_id": self.env.uid, "completed_on": today}
            )
            rec._fix_raise_renewal_cost()
            emit(
                rec,
                "vehicle.document_renewed",
                {
                    "vehicle": _vehicle_label(rec.vehicle_id),
                    "vehicle_id": rec.vehicle_id.id,
                    "renewal": rec.name,
                    "doc_type": rec.doc_type,
                    "new_document": new.name,
                    "valid_to": str(new.valid_to),
                    "total_cost": rec.total_cost,
                },
            )
        return True

    def _fix_raise_renewal_cost(self):
        """M46-01 money contract: a completed renewal's government fee, agent
        fee and penalty are one vehicle_renewal cost on the vehicle's branch
        OU (D3: 5000110 Certifications & Registrations, resolved by S6)."""
        for rec in self.filtered(lambda r: r.total_cost > 0):
            vals = dict(
                rec.vehicle_id._fix_cost_dimensions(),
                cost_type="vehicle_renewal",
                amount=rec.total_cost,
                cost_date=rec.completed_on or dhaka_today(rec),
                vendor_id=rec.vendor_id.id or False,
                invoice_ref=(rec.invoice_ref or "").strip() or False,
                payment_method=rec.payment_method or False,
                employee_id=rec.responsible_employee_id.id
                if rec.payment_method == "employee_expense"
                else False,
                detail="%s renewal %s: government %.2f, agent %.2f, penalty %.2f"
                % (
                    rec.doc_type,
                    rec.name,
                    rec.government_fee or 0.0,
                    rec.agent_fee or 0.0,
                    rec.penalty or 0.0,
                ),
            )
            m52_raise(rec, vals)

    def _m52_mark_paid(self, amount, date, ref):
        """Finance (the M52 bridge) records the payment; never typed."""
        for rec in self:
            rec._guarded().write({"paid_on": date or False, "payment_ref": ref or False})

    def action_cancel(self, reason=None):
        require_role(self.env, FLEET_OFFICER_GROUP, "Cancelling a document renewal")
        reason = _reason(reason, "cancelling the renewal")
        for rec in self:
            if rec.state not in ("initiated", "submitted"):
                raise UserError("Cancel a renewal that is still in progress.")
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason})
            rec.message_post(body="Renewal cancelled by %s: %s" % (self.env.user.name, reason))
        return True


# --------------------------------------------------------------------------
# Pre-Use & PM: defect (FR-FLT-025, BRU-FLT-04)
# --------------------------------------------------------------------------
DEFECT_CATEGORIES = [
    ("brakes", "Brakes"),
    ("tyres", "Tyres / Wheels"),
    ("lights", "Lights / Indicators"),
    ("steering", "Steering / Suspension"),
    ("engine", "Engine / Fluids"),
    ("electrical", "Electrical / Battery"),
    ("body", "Body / Glass / Mirrors"),
    ("documents", "Documents Missing in the Vehicle"),
    ("other", "Other"),
]


class FixVehicleDefect(models.Model):
    _name = "fix.vehicle.defect"
    _description = "Vehicle Defect"
    _inherit = ["fix.vehicle.lock.mixin"]
    _order = "raised_on desc, id desc"
    _fix_insert_only = True

    name = fields.Char(required=True, default="New", copy=False)
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    raised_on = fields.Date(required=True, default=dhaka_default)
    raised_by_id = fields.Many2one("res.users", string="Raised By", readonly=True, copy=False)
    category = fields.Selection(DEFECT_CATEGORIES, required=True, default="other")
    safety_critical = fields.Boolean(
        string="Safety-Critical",
        help="A safety-critical defect takes the vehicle off the road at once (BRU-FLT-04). "
        "A deferrable one is recorded and repaired at the next service.",
    )
    description = fields.Text(required=True)
    evidence_file = fields.Binary(string="Photo / Evidence", attachment=True, copy=False)
    evidence_filename = fields.Char(string="Evidence File Name", copy=False)
    offroad_id = fields.Many2one(
        "fix.vehicle.offroad",
        string="Off-Road Record",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    state = fields.Selection(
        [("open", "Open"), ("cleared", "Cleared")], required=True, default="open"
    )
    cleared_by_id = fields.Many2one("res.users", string="Cleared By", readonly=True, copy=False)
    cleared_on = fields.Date(string="Cleared On", readonly=True, copy=False)
    clear_note = fields.Char(string="Repair / Clearance Note", readonly=True, copy=False)
    clear_check_id = fields.Many2one(
        "fix.vehicle.check", string="Re-Check", readonly=True, copy=False, ondelete="restrict"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "raised_by_id",
            "offroad_id",
            "cleared_by_id",
            "cleared_on",
            "clear_note",
            "clear_check_id",
        }

    def _fix_frozen_fields(self) -> set:
        # What was reported is evidence: a safety-critical defect is never
        # downgraded after the fact to put the vehicle back on the road.
        if isinstance(self.id, int):
            frozen = {"vehicle_id", "raised_on", "category", "safety_critical", "description"}
            if self.state == "cleared":
                frozen |= {"evidence_file", "evidence_filename"}
            return frozen
        return set()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.defect") or "VDEF/New"
                )
        recs = super().create(vals_list)
        raiser = self.env.user if not self.env.su else None
        for rec in recs:
            if raiser:
                rec._guarded().write({"raised_by_id": raiser.id})
            if rec.safety_critical:
                vehicle = rec.vehicle_id.sudo()
                off = vehicle._fix_take_offroad(
                    "defect",
                    "Safety-critical defect %s: %s" % (rec.name, rec.description),
                    raised_by=raiser,
                )
                if not off:
                    off = (
                        self.env["fix.vehicle.offroad"]
                        .sudo()
                        .search(
                            [
                                ("vehicle_id", "=", vehicle.id),
                                ("state", "=", "offroad"),
                                ("cause", "=", "defect"),
                            ],
                            limit=1,
                        )
                    )
                rec._guarded().write({"offroad_id": off.id or False})
            emit(
                rec,
                "vehicle.defect_raised",
                {
                    "vehicle": _vehicle_label(rec.vehicle_id),
                    "vehicle_id": rec.vehicle_id.id,
                    "defect": rec.name,
                    "category": rec.category,
                    "description": rec.description,
                    "safety_critical": rec.safety_critical,
                },
            )
        return recs

    def action_clear(self, note=None):
        """Open -> cleared, by a Fleet Officer who did not raise it. A
        safety-critical defect is cleared only on a passed pre-use check
        recorded after it was raised (BRU-FLT-04 "until the defect is cleared
        and re-checked")."""
        require_role(self.env, FLEET_OFFICER_GROUP, "Clearing a vehicle defect")
        note = _reason(note, "clearing the defect (what was repaired)")
        for rec in self:
            if rec.state != "open":
                raise UserError("Clear an open defect.")
            if not self.env.su and rec.raised_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you raised %s; another Fleet Officer clears it."
                    % rec.name
                )
            check = self.env["fix.vehicle.check"]
            if rec.safety_critical:
                check = check.sudo().search(
                    [
                        ("vehicle_id", "=", rec.vehicle_id.id),
                        ("passed", "=", True),
                        ("checked_on", ">=", rec.raised_on),
                        ("create_date", ">=", rec.create_date),
                    ],
                    order="create_date desc, id desc",
                    limit=1,
                )
                if not check:
                    raise UserError(
                        "%s is safety-critical: record a passed pre-use check after the repair "
                        "first." % rec.name
                    )
            rec._guarded().write(
                {
                    "state": "cleared",
                    "cleared_by_id": self.env.uid,
                    "cleared_on": dhaka_today(rec),
                    "clear_note": note,
                    "clear_check_id": check.id or False,
                }
            )
        return True


# --------------------------------------------------------------------------
# Pre-Use & PM: service execution (FR-FLT-026/027)
# --------------------------------------------------------------------------
class FixVehiclePmExecution(models.Model):
    _inherit = "fix.vehicle.pm"

    provider_id = fields.Many2one("res.partner", string="Garage / Workshop", ondelete="restrict")
    work_performed = fields.Text(string="Work Performed")
    parts_used = fields.Char(string="Parts Used")
    invoice_ref = fields.Char(string="Invoice Ref")
    downtime_hours = fields.Float(string="Downtime (hours)")
    next_due_date = fields.Date(string="Next Service Due (date)")
    next_due_odometer = fields.Integer(string="Next Service Due (km)")
    next_pm_id = fields.Many2one(
        "fix.vehicle.pm", string="Next Service", readonly=True, copy=False, ondelete="set null"
    )
    # A07 ERP audit M46-01/02 (money contract): how the service was paid.
    payment_method = fields.Selection(PAYMENT_METHODS_NO_CARD, string="Payment Method")
    paid_by_employee_id = fields.Many2one(
        "hr.employee", string="Paid By (employee)", ondelete="restrict"
    )
    receipt_file = fields.Binary(string="Receipt (scan)", attachment=True, copy=False)
    receipt_filename = fields.Char(string="Receipt File Name", copy=False)

    @api.constrains("downtime_hours", "next_due_odometer", "odometer")
    def _check_execution(self):
        for rec in self:
            if (rec.downtime_hours or 0.0) < 0:
                raise ValidationError("Downtime cannot be negative.")
            if rec.next_due_odometer and rec.odometer and rec.next_due_odometer <= rec.odometer:
                raise ValidationError(
                    "The next service is due beyond the odometer at this service (%s km)."
                    % rec.odometer
                )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"next_pm_id"}

    def _fix_frozen_fields(self) -> set:
        frozen = super()._fix_frozen_fields()
        if self.state == "done":
            frozen |= {
                "provider_id",
                "work_performed",
                "parts_used",
                "invoice_ref",
                "downtime_hours",
                "next_due_date",
                "next_due_odometer",
                "payment_method",
                "paid_by_employee_id",
                "receipt_file",
                "receipt_filename",
            }
        return frozen

    def _m52_cost_facts(self):
        """The money-contract facts of this service for the M52 cost entry the
        finance bridge raises from vehicle.service_completed (M46-02: the
        garage and its invoice; M46-04: the vehicle's branch OU)."""
        self.ensure_one()
        rec = self.sudo()
        return dict(
            rec.vehicle_id._fix_cost_dimensions(),
            payment_method=rec.payment_method or False,
            vendor_id=rec.provider_id.id or False,
            invoice_ref=(rec.invoice_ref or "").strip() or False,
            employee_id=rec.paid_by_employee_id.id
            if rec.payment_method == "employee_expense"
            else False,
        )

    def action_done(self):
        """FR-FLT-027: a service done at a garage names its invoice, the
        reference M52 pays against. (The work text stays optional: the M45/M47
        work-order spine completes services that carry their work on the work
        order.) The next due date or odometer opens the next service, so the
        schedule continues (FR-FLT-026)."""
        for rec in self:
            if rec.state == "open" and rec.provider_id and not (rec.invoice_ref or "").strip():
                raise UserError(
                    "%s was done by %s: record the invoice reference."
                    % (rec.name, rec.provider_id.name)
                )
            # A07 ERP audit M46-01/02/04: a paid service names how it was
            # paid, the garage for a bill, and the vehicle's branch OU.
            if not self.env.su and rec.state == "open" and (rec.cost or 0.0) > 0:
                problems = payment_problems(
                    rec.payment_method,
                    rec.provider_id,
                    rec.invoice_ref,
                    rec.receipt_file,
                    rec.paid_by_employee_id,
                )
                if problems:
                    raise UserError(
                        "Record %s on %s before completing it: its cost of %.2f is paid "
                        "through M52." % (" and ".join(problems), rec.name, rec.cost)
                    )
                rec.vehicle_id._fix_cost_dimensions()
        res = super().action_done()
        Pm = self.env["fix.vehicle.pm"].sudo()
        for rec in self.filtered(lambda r: r.next_due_date or r.next_due_odometer):
            if rec.next_pm_id:
                continue
            nxt = Pm.create(
                {
                    "vehicle_id": rec.vehicle_id.id,
                    "pm_type": rec.pm_type if rec.pm_type != "repair" else "service",
                    "due_date": rec.next_due_date or False,
                    "due_odometer": rec.next_due_odometer or 0,
                    "scheduled_on": rec.next_due_date or dhaka_today(rec),
                    "notes": "Next service after %s" % rec.name,
                }
            )
            rec._guarded().write({"next_pm_id": nxt.id})
        return res


# --------------------------------------------------------------------------
# Telematics: device register (FR-FLT-035/036)
# --------------------------------------------------------------------------
class FixTelematicsDevice(models.Model):
    _name = "fix.telematics.device"
    _description = "Telematics Device"
    _inherit = ["mail.thread", "fix.vehicle.lock.mixin"]
    _order = "name"
    _fix_insert_only = True

    name = fields.Char(string="Device Identifier (IMEI / serial)", required=True, tracking=True)
    provider_id = fields.Many2one("res.partner", string="Provider", ondelete="restrict")
    sim_number = fields.Char(string="SIM Number", tracking=True)
    data_plan_ref = fields.Char(string="Data Plan")
    firmware = fields.Char(string="Firmware", tracking=True)
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Fitted To", ondelete="restrict", index=True, tracking=True
    )
    fitted_on = fields.Date(string="Fitted On", tracking=True)
    removed_on = fields.Date(string="Last Removed On", readonly=True, copy=False)
    retired = fields.Boolean(readonly=True, copy=False)
    state = fields.Selection(
        [("stock", "Not Fitted"), ("fitted", "Fitted"), ("retired", "Retired")],
        compute="_compute_state",
        store=True,
    )
    last_report_at = fields.Datetime(compute="_compute_health", string="Last Report")
    health_state = fields.Selection(
        [
            ("online", "Reporting"),
            ("stale", "Silent"),
            ("offline", "Never Reported"),
            ("not_fitted", "Not Fitted"),
        ],
        compute="_compute_health",
        string="Health",
    )

    @api.depends("vehicle_id", "retired")
    def _compute_state(self):
        for rec in self:
            rec.state = "retired" if rec.retired else ("fitted" if rec.vehicle_id else "stock")

    def _compute_health(self):
        Tel = self.env["fix.vehicle.telemetry"].sudo()
        for rec in self:
            if not rec.vehicle_id:
                rec.health_state, rec.last_report_at = "not_fitted", False
                continue
            latest = Tel.search(
                [("vehicle_id", "=", rec.vehicle_id.id), ("device_id", "=", rec.id)],
                order="last_ping desc, id desc",
                limit=1,
            )
            rec.last_report_at = latest.last_ping or False
            rec.health_state = latest.state if latest else "offline"

    @api.constrains("name")
    def _check_unique_identifier(self):
        for rec in self:
            key = (rec.name or "").strip()
            if not key:
                raise ValidationError("A device needs its identifier.")
            if self.sudo().search_count(
                [("id", "!=", rec.id), ("name", "=ilike", like_exact(key))]
            ):
                raise ValidationError("Device %s is already registered." % key)

    @api.constrains("vehicle_id", "retired")
    def _check_one_device_per_vehicle(self):
        for rec in self.filtered("vehicle_id"):
            if rec.retired:
                raise ValidationError("A retired device is not fitted to a vehicle.")
            other = self.sudo().search(
                [("id", "!=", rec.id), ("vehicle_id", "=", rec.vehicle_id.id)], limit=1
            )
            if other:
                raise ValidationError(
                    "%s already carries device %s: remove it first."
                    % (_vehicle_label(rec.vehicle_id), other.name)
                )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"removed_on", "retired"}

    def _fix_frozen_fields(self) -> set:
        # A fitted device moves to another vehicle only through Remove, so
        # the fitment history (chatter) is never rewritten.
        if self.retired:
            return {"name", "vehicle_id", "fitted_on", "sim_number", "provider_id"}
        if isinstance(self.id, int) and self.vehicle_id:
            return {"name", "vehicle_id", "fitted_on"}
        if isinstance(self.id, int):
            return {"name"}
        return set()

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, FLEET_OFFICER_GROUP, "Registering a telematics device")
        for vals in vals_list:
            if vals.get("name"):
                vals["name"] = vals["name"].strip()
            if vals.get("vehicle_id") and not vals.get("fitted_on"):
                vals["fitted_on"] = dhaka_today(self)
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("vehicle_id") and not vals.get("fitted_on"):
            vals = dict(vals, fitted_on=dhaka_today(self))
        res = super().write(vals)
        if vals.get("vehicle_id"):
            for rec in self:
                rec.message_post(
                    body="Fitted to %s on %s." % (_vehicle_label(rec.vehicle_id), rec.fitted_on)
                )
        return res

    def action_remove(self, reason=None):
        require_role(self.env, FLEET_OFFICER_GROUP, "Removing a telematics device")
        reason = _reason(reason, "removing the device")
        for rec in self:
            if not rec.vehicle_id:
                raise UserError("%s is not fitted to a vehicle." % rec.name)
            label = _vehicle_label(rec.vehicle_id)
            rec._guarded().write(
                {"vehicle_id": False, "fitted_on": False, "removed_on": dhaka_today(rec)}
            )
            rec.message_post(body="Removed from %s by %s: %s" % (label, self.env.user.name, reason))
        return True

    def action_retire(self, reason=None):
        require_role(self.env, FLEET_OFFICER_GROUP, "Retiring a telematics device")
        reason = _reason(reason, "retiring the device")
        for rec in self:
            if rec.retired:
                raise UserError("%s is already retired." % rec.name)
            if rec.vehicle_id:
                raise UserError("Remove %s from its vehicle before retiring it." % rec.name)
            rec._guarded().write({"retired": True})
            rec.message_post(body="Retired by %s: %s" % (self.env.user.name, reason))
        return True


class FixVehicleTelemetryDevice(models.Model):
    _inherit = "fix.vehicle.telemetry"

    device_id = fields.Many2one(
        "fix.telematics.device", string="Registered Device", ondelete="restrict", index=True
    )

    def _fix_frozen_fields(self) -> set:
        frozen = super()._fix_frozen_fields()
        return frozen | {"device_id"} if isinstance(self.id, int) else frozen

    @api.model_create_multi
    def create(self, vals_list):
        Device = self.env["fix.telematics.device"].sudo()
        for vals in vals_list:
            typed = (vals.get("device_ref") or "").strip()
            device = Device.browse(vals.get("device_id")) if vals.get("device_id") else Device
            if not device and typed:
                device = Device.search([("name", "=ilike", like_exact(typed))], limit=1)
            fitted = (
                Device.search([("vehicle_id", "=", vals["vehicle_id"])], limit=1)
                if vals.get("vehicle_id")
                else Device
            )
            if not device and not typed:
                device = fitted
            if not device:
                if typed and fitted and not self.env.su:
                    raise UserError(
                        "Device %s is not in the device register; this vehicle carries %s."
                        % (typed, fitted.name)
                    )
                continue  # a device not yet registered: kept as typed
            if not self.env.su and device.vehicle_id.id != vals.get("vehicle_id"):
                raise UserError(
                    "Device %s is not fitted to this vehicle (it is %s)."
                    % (
                        device.name,
                        "fitted to %s" % _vehicle_label(device.vehicle_id)
                        if device.vehicle_id
                        else "not fitted",
                    )
                )
            vals["device_id"] = device.id
            vals["device_ref"] = device.name
        return super().create(vals_list)


# --------------------------------------------------------------------------
# Accidents & Insurance: traffic fine / penalty (FR-FLT-043, BRU-FLT-16)
# --------------------------------------------------------------------------
# A07 ERP audit (2026-11-20) M46-14, owner decision D11: the recover-or-absorb
# decision follows the estate DOFA ladder: up to BDT 10,000 the Logistics
# Manager decides alone, up to BDT 50,000 the Operations Director (DOFA Tier 3)
# approves it, above that the CFO (Tier 4). The two bounds are parameters
# (the decision states the figures); the approval is routed by M63.
FINE_LM_LIMIT_PARAM = "cd_vehicle_ext.fine_decision_lm_limit_bdt"
FINE_LM_LIMIT_DEFAULT = 10000.0
FINE_DIRECTOR_LIMIT_PARAM = "cd_vehicle_ext.fine_decision_director_limit_bdt"
FINE_DIRECTOR_LIMIT_DEFAULT = 50000.0


class FixVehiclePenalty(models.Model):
    _name = "fix.vehicle.penalty"
    _description = "Traffic Fine / Penalty"
    # fix.dofa.mixin after the chatter, as on fix.vehicle.accident: it
    # carries the M63 routed approval (fix.approvable.mixin).
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin", "fix.vehicle.lock.mixin"]
    _order = "issued_on desc, id desc"
    _fix_insert_only = True

    _approval_domain = "vehicle_penalty_decision"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    name = fields.Char(required=True, default="New", copy=False)
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="restrict", index=True
    )
    driver_id = fields.Many2one(
        "fix.driver",
        string="Driver on Duty",
        ondelete="restrict",
        help="Empty = the driver booked on the vehicle that day, else its assigned driver.",
    )
    issued_on = fields.Date(required=True, default=dhaka_default)
    authority = fields.Char(string="Issuing Authority", help="e.g. DMP Traffic Division")
    case_ref = fields.Char(string="Case / Slip No")
    offence = fields.Char(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    evidence_file = fields.Binary(string="Fine Slip (scan)", attachment=True, copy=False)
    evidence_filename = fields.Char(string="Fine Slip File Name", copy=False)
    # A07 ERP audit M46-14 (D11): "paid" is recorded by finance when the fine
    # is paid through AP or petty cash (_m52_mark_paid), never typed.
    paid_on = fields.Date(string="Paid On", readonly=True, copy=False)
    payment_ref = fields.Char(string="Payment Ref", readonly=True, copy=False)
    payment_method = fields.Selection(
        [("vendor_bill", "Vendor Bill (AP)"), ("petty_cash", "Petty Cash")],
        string="Paid Through",
    )
    vendor_id = fields.Many2one(
        "res.partner",
        string="Payable To (authority)",
        ondelete="restrict",
        help="The authority the fine is paid to (e.g. DMP Traffic Division, BRTA).",
    )
    proposed_decision = fields.Selection(
        [("recover", "Recover from the Driver"), ("absorb", "Absorb (company cost)")],
        string="Proposed Decision",
        readonly=True,
        copy=False,
        help="Above the Logistics Manager limit the decision waits for its DOFA approval.",
    )
    proposed_by_id = fields.Many2one("res.users", string="Proposed By", readonly=True, copy=False)
    recorded_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True, copy=False)
    recovery_decision = fields.Selection(
        [("recover", "Recover from the Driver"), ("absorb", "Absorb (company cost)")],
        string="Decision",
        readonly=True,
        copy=False,
    )
    decision_reason = fields.Char(string="Decision Reason", readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Date(string="Decided On", readonly=True, copy=False)
    state = fields.Selection(
        [("recorded", "Recorded"), ("decided", "Decided")],
        required=True,
        default="recorded",
        tracking=True,
    )

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if (rec.amount or 0.0) <= 0:
                raise ValidationError("A fine has an amount above zero.")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "recorded_by_id",
            "recovery_decision",
            "decision_reason",
            "decided_by_id",
            "decided_on",
            "paid_on",
            "payment_ref",
            "proposed_decision",
            "proposed_by_id",
        }

    def _fix_frozen_fields(self) -> set:
        if self.state == "decided":
            return {
                "vehicle_id",
                "driver_id",
                "issued_on",
                "offence",
                "amount",
                "authority",
                "case_ref",
                "payment_method",
                "vendor_id",
                "evidence_file",
                "evidence_filename",
            }
        return set()

    # ---- DOFA (fix.dofa.mixin, M63) ---------------------------------------
    def _dofa_thresholds(self):
        lm = param_float(self.env, FINE_LM_LIMIT_PARAM, FINE_LM_LIMIT_DEFAULT)
        director = param_float(self.env, FINE_DIRECTOR_LIMIT_PARAM, FINE_DIRECTOR_LIMIT_DEFAULT)
        return [(lm, "tier_0"), (max(director, lm), "tier_3"), (float("inf"), "tier_4")]

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.amount or 0.0

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (traffic fine %s)" % (self._dofa_amount(), self.name)

    @api.depends("amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_pinned_fields(self) -> set:
        # The approval covers this fine, this driver and this decision.
        return super()._approval_pinned_fields() | {
            "vehicle_id",
            "driver_id",
            "proposed_decision",
            "payment_method",
        }

    def _fix_payment_problems(self):
        self.ensure_one()
        return payment_problems(
            self.payment_method, self.vendor_id, self.case_ref, self.evidence_file
        )

    @api.model
    def _fix_driver_on_duty(self, vehicle, day):
        booking = (
            self.env["fix.vehicle.assignment"]
            .sudo()
            .search(
                [("vehicle_id", "=", vehicle.id), ("date", "=", day), ("driver_id", "!=", False)],
                limit=1,
            )
        )
        return booking.driver_id or vehicle.sudo().fix_driver_id

    @api.model_create_multi
    def create(self, vals_list):
        Vehicle = self.env["fleet.vehicle"].sudo()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.penalty") or "VPEN/New"
                )
            if not vals.get("driver_id") and vals.get("vehicle_id"):
                day = fields.Date.to_date(vals.get("issued_on")) or dhaka_today(self)
                driver = self._fix_driver_on_duty(Vehicle.browse(vals["vehicle_id"]), day)
                if not driver:
                    raise UserError(
                        "No driver was booked on %s that day and it has no assigned driver: "
                        "name the driver on duty (BRU-FLT-16)."
                        % _vehicle_label(Vehicle.browse(vals["vehicle_id"]))
                    )
                vals["driver_id"] = driver.id
        recs = super().create(vals_list)
        if not self.env.su:
            recs._guarded().write({"recorded_by_id": self.env.uid})
        for rec in recs:
            emit(
                rec,
                "vehicle.penalty_recorded",
                {
                    "vehicle": _vehicle_label(rec.vehicle_id),
                    "vehicle_id": rec.vehicle_id.id,
                    "penalty": rec.name,
                    "driver_id": rec.driver_id.id,
                    "amount": rec.amount,
                    "issued_on": str(rec.issued_on),
                },
            )
        return recs

    def _decide(self, decision, reason):
        """The Logistics Manager decides recover or absorb (BRU-FLT-16), with
        the reason, and is not the person who recorded the fine. A07 ERP audit
        M46-14 (D11): within the LM limit the decision stands at once; above
        it the decision is PROPOSED and routed through M63 to the Operations
        Director (Tier 3) or the CFO (Tier 4), whose approval completes it.
        Either way the fine names how it is paid (AP or petty cash) and its
        vehicle has a branch OU, because deciding it raises the cost."""
        require_role(self.env, LOGISTICS_MANAGER_GROUP, "Deciding a traffic fine")
        reason = _reason(reason, "the decision")
        for rec in self:
            if rec.state != "recorded":
                raise UserError("%s is already decided." % rec.name)
            if not self.env.su and rec.recorded_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you recorded %s; another Logistics Manager decides "
                    "it." % rec.name
                )
            if rec.approval_state == "pending":
                raise UserError(
                    "%s already waits for its DOFA approval (%s)."
                    % (rec.name, rec.approval_request_id.name or "-")
                )
            if not self.env.su:
                problems = rec._fix_payment_problems()
                if decision == "recover" and not rec.driver_id.employee_id:
                    problems.append("the driver (an employee) it is recovered from")
                if problems:
                    raise UserError("Record %s on %s first." % (" and ".join(problems), rec.name))
            rec.vehicle_id._fix_cost_dimensions()
            rec._guarded().write(
                {
                    "proposed_decision": decision,
                    "proposed_by_id": self.env.uid,
                    "decision_reason": reason,
                }
            )
            if rec._dofa_current_tier() == "tier_0":
                rec._fix_finalize_decision()
            else:
                rec.action_request_approval(justification=reason)
        return True

    def action_recall_approval(self):
        """The Logistics Manager withdraws a decision waiting for its DOFA
        approval; the proposal stays on record and can be decided again."""
        return super().action_recall_approval()

    def action_dofa_approve(self):
        """The routed approval (M63 inbox) completes the proposed decision."""
        res = super().action_dofa_approve()
        for rec in self.filtered(lambda r: r.state == "recorded" and r.proposed_decision):
            rec._fix_finalize_decision()
        return res

    def _fix_finalize_decision(self):
        for rec in self:
            rec._dofa_assert_approved("Deciding the fine")
            decision = rec.proposed_decision
            rec._guarded().write(
                {
                    "state": "decided",
                    "recovery_decision": decision,
                    "decided_by_id": rec.proposed_by_id.id or self.env.uid,
                    "decided_on": dhaka_today(rec),
                }
            )
            rec.message_post(
                body="Decided: %s (%s), proposed by %s%s."
                % (
                    dict(rec._fields["recovery_decision"].selection).get(decision),
                    rec.decision_reason or "-",
                    rec.proposed_by_id.name or "-",
                    ", approved by %s" % rec.dofa_approved_by.name if rec.dofa_approved_by else "",
                )
            )
            rec._fix_raise_fine_cost()
            # M52/M21 act on a recovery; the score never feeds discipline
            # (BRU-FLT-17), and neither does this event.
            emit(
                rec,
                "vehicle.penalty_decided",
                {
                    "vehicle_id": rec.vehicle_id.id,
                    "penalty": rec.name,
                    "driver_id": rec.driver_id.id,
                    "employee_id": rec.driver_id.employee_id.id,
                    "amount": rec.amount,
                    "decision": decision,
                },
            )

    def _fix_raise_fine_cost(self):
        """Money contract (D3/D9/D11): the fine is paid to the authority
        through AP or petty cash (cost type vehicle_fine, on the vehicle's
        branch OU). Absorbed, it is the company's penalty expense; recovered,
        the entry names the employee (recovery_employee_id) for the D9
        employee-recovery receivable and the M56 deduction."""
        for rec in self:
            vals = dict(
                rec.vehicle_id._fix_cost_dimensions(),
                cost_type="vehicle_fine",
                amount=rec.amount,
                cost_date=rec.decided_on or dhaka_today(rec),
                vendor_id=rec.vendor_id.id or False,
                invoice_ref=(rec.case_ref or "").strip() or False,
                payment_method=rec.payment_method or False,
                recovery_employee_id=rec.driver_id.employee_id.id
                if rec.recovery_decision == "recover"
                else False,
                detail="Traffic fine %s (%s): %s"
                % (rec.name, rec.offence or "-", rec.recovery_decision),
            )
            m52_raise(rec, vals)

    def _m52_mark_paid(self, amount, date, ref):
        """Finance records the payment of the fine (AP or petty cash)."""
        for rec in self:
            rec._guarded().write({"paid_on": date or False, "payment_ref": ref or False})

    def action_recover(self, reason=None):
        return self._decide("recover", reason)

    def action_absorb(self, reason=None):
        return self._decide("absorb", reason)
