# fix_vehicle_erp — A07 ERP audit (2026-11-20), stream M46.
#
#   * M46-04 money contract: a vehicle carries its branch's operating unit (a
#     user cannot leave an active vehicle with none, nor one that differs
#     from its branch's);
#   * M46-10 / D10 / BRU-FLT-20: a vehicle leaves the fleet only through a
#     disposal record (route, proceeds, buyer, evidence) that the CFO approves
#     through M63; Retire on its own is refused;
#   * M46-19 (FR-FLT-002/010/033): the class profile (documents, licence
#     class, tank, fuel-efficiency baseline and deterioration threshold);
#   * M46-20 (FR-FLT-017): the driver's licence and the M21 employee's licence
#     are one fact, kept in step both ways, and a legacy mismatch is shown;
#   * M46-25 (§8.1, T-01): a vehicle a user registers is "registered" until a
#     Fleet Officer commissions it (documents valid, a passed pre-use check,
#     and, with the switch on, a fitted telematics device);
#   * M46-08: the fleet's own odometer log is judged like every other reading.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_vehicle_ops import (
    FLEET_OFFICER_GROUP,
    LICENCE_CLASSES,
    LOGISTICS_MANAGER_GROUP,
    _reason,
    _vehicle_label,
    dhaka_default,
    dhaka_today,
    param_on,
    require_role,
)

COMMISSION_TELEMATICS_PARAM = "cd_vehicle_ext.commission_requires_telematics"
# In-process token: only a completed disposal retires a vehicle.
_DISPOSE_KEY = "fix_vehicle_disposing"
_DISPOSING = object()
_COMMISSION_KEY = "fix_vehicle_commissioning"
_COMMISSIONING = object()
_COMMISSION_FIELDS = ("fix_commissioned", "fix_commissioned_on", "fix_commissioned_by_id")

DISPOSAL_ROUTES = [
    ("sale", "Sale"),
    ("auction", "Auction"),
    ("scrap", "Scrap"),
    ("donation", "Donation"),
    ("write_off", "Write-Off (total loss / theft)"),
    ("lease_return", "Return to Lessor / Owner"),
]
_SOLD = ("sale", "auction")


class FixVehicleClassProfile(models.Model):
    """A07 ERP audit M46-19: what a class of vehicle needs and how it should
    perform (FR-FLT-002/010 class-driven documents; FR-FLT-033 baseline)."""

    _name = "fix.vehicle.class.profile"
    _description = "Vehicle Class Profile"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", string="Company", index=True)
    licence_class = fields.Selection(LICENCE_CLASSES, string="Licence Class Required")
    mandatory_document_types = fields.Char(
        string="Mandatory Documents",
        help="Comma-separated document type keys (fitness, insurance, tax, route_permit, "
        "registration). Empty = the fleet-wide list (cd_vehicle_ext.mandatory_document_types).",
    )
    tank_capacity_l = fields.Float(string="Fuel Tank Capacity (L)")
    baseline_km_per_litre = fields.Float(string="Baseline km/l")
    deterioration_pct = fields.Float(
        string="Deterioration Threshold (%)",
        help="Fuel efficiency this far below the baseline is flagged on the Fuel "
        "Efficiency report. Empty = no flag.",
    )

    @api.constrains(
        "tank_capacity_l", "baseline_km_per_litre", "deterioration_pct", "mandatory_document_types"
    )
    def _check_profile(self):
        Doc = self.env["fix.vehicle.document"]
        known = set(dict(Doc._fields["doc_type"].selection))
        for rec in self:
            if min(rec.tank_capacity_l, rec.baseline_km_per_litre, rec.deterioration_pct) < 0:
                raise ValidationError("A class profile's figures cannot be negative.")
            if rec.deterioration_pct >= 100:
                raise ValidationError("The deterioration threshold is a percentage below 100.")
            unknown = [
                t
                for t in self.env["fleet.vehicle"]._fix_parse_document_types(
                    rec.mandatory_document_types
                )
                if t not in known
            ]
            if unknown:
                raise ValidationError("Unknown document type(s): %s." % ", ".join(unknown))

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, FLEET_OFFICER_GROUP, "Recording a vehicle class profile")
        return super().create(vals_list)

    def write(self, vals):
        require_role(self.env, LOGISTICS_MANAGER_GROUP, "Changing a vehicle class profile")
        return super().write(vals)


class FleetVehicleErp(models.Model):
    _inherit = "fleet.vehicle"

    fix_class_profile_id = fields.Many2one(
        "fix.vehicle.class.profile", string="Class Profile", ondelete="restrict"
    )
    fix_baseline_km_per_litre = fields.Float(
        string="Baseline km/l (this vehicle)",
        help="Overrides the class profile's baseline for this vehicle.",
    )
    # M46-25: registered -> commissioned (available) lifecycle.
    fix_commissioned = fields.Boolean(
        string="Commissioned",
        default=True,
        copy=False,
        readonly=True,
        help="A vehicle a user registers is not dispatchable until a Fleet Officer "
        "commissions it.",
    )
    fix_commissioned_on = fields.Date(string="Commissioned On", readonly=True, copy=False)
    fix_commissioned_by_id = fields.Many2one(
        "res.users", string="Commissioned By", readonly=True, copy=False
    )
    fix_lifecycle_state = fields.Selection(
        [
            ("registered", "Registered"),
            ("available", "Available"),
            ("not_dispatchable", "Not Dispatchable"),
            ("off_road", "Off Road"),
            ("retired", "Retired"),
        ],
        string="Lifecycle",
        compute="_compute_lifecycle_state",
    )
    fix_disposal_id = fields.Many2one(
        "fix.vehicle.disposal", string="Disposal", readonly=True, copy=False
    )
    # FIN-09 / D5(d): a leased van or motorbike goes on the IFRS 16 book. The
    # asset bridge drafts its lease from the contract's start, end
    # (fix_contract_end) and monthly rent; exempt when 12 months or less, or
    # worth BDT 500,000 or less new (D5e).
    fix_contract_start = fields.Date(
        string="Contract Start", help="Start of the lease / hire contract (IFRS 16 commencement)"
    )
    fix_lease_monthly_rent = fields.Monetary(
        string="Lease Monthly Rent",
        currency_field="currency_id",
        help="The monthly rent of a leased vehicle (IFRS 16 lease payment)",
    )

    @api.constrains("fix_contract_start", "fix_contract_end", "fix_lease_monthly_rent")
    def _check_lease_contract_terms(self):
        for rec in self:
            if (rec.fix_lease_monthly_rent or 0.0) < 0.0:
                raise ValidationError("A vehicle's lease rent cannot be negative.")
            if (
                rec.fix_contract_start
                and rec.fix_contract_end
                and rec.fix_contract_end < rec.fix_contract_start
            ):
                raise ValidationError("The contract cannot end before it starts.")

    # ---------------------------------------------------- licence / tank / docs
    @api.depends("model_id.vehicle_type", "fix_class_profile_id.licence_class")
    def _compute_licence_class_required(self):
        res = super()._compute_licence_class_required()
        for rec in self.filtered(lambda r: r.fix_class_profile_id.licence_class):
            rec.fix_licence_class_required = rec.fix_class_profile_id.licence_class
        return res

    def _fix_required_document_types(self):
        profile = self.sudo().fix_class_profile_id
        if profile and (profile.mandatory_document_types or "").strip():
            return self._fix_parse_document_types(profile.mandatory_document_types)
        return super()._fix_required_document_types()

    def _fix_fuel_baseline(self):
        """(baseline km/l, deterioration %) or (0, 0) when none is recorded."""
        self.ensure_one()
        profile = self.sudo().fix_class_profile_id
        baseline = self.fix_baseline_km_per_litre or profile.baseline_km_per_litre or 0.0
        return baseline, profile.deterioration_pct or 0.0

    # ---------------------------------------------------- lifecycle
    def _compute_lifecycle_state(self):
        blockers = self.filtered("active")._fix_dispatch_blockers()
        Off = self.env["fix.vehicle.offroad"].sudo()
        off = set(
            Off.search([("vehicle_id", "in", self.ids), ("state", "=", "offroad")])
            .mapped("vehicle_id")
            .ids
        )
        for rec in self:
            if not rec.active:
                rec.fix_lifecycle_state = "retired"
            elif not rec.fix_commissioned:
                rec.fix_lifecycle_state = "registered"
            elif rec.id in off:
                rec.fix_lifecycle_state = "off_road"
            elif blockers.get(rec.id):
                rec.fix_lifecycle_state = "not_dispatchable"
            else:
                rec.fix_lifecycle_state = "available"

    def _fix_dispatch_blockers(self, driver=None, day=None, require_driver=False):
        out = super()._fix_dispatch_blockers(driver=driver, day=day, require_driver=require_driver)
        for vehicle in self.sudo().filtered(lambda v: v.active and not v.fix_commissioned):
            out.setdefault(vehicle.id, []).append(
                "it is registered but not commissioned yet (a Fleet Officer commissions it "
                "once its documents are valid and it has passed a pre-use check)"
            )
        return out

    def action_commission(self):
        """Registered -> commissioned (M46-25, §8.1): a Fleet Officer, on a
        vehicle whose mandatory documents are valid today, with a passed
        pre-use check, and (switch on) a fitted telematics device."""
        require_role(self.env, FLEET_OFFICER_GROUP, "Commissioning a vehicle")
        today = dhaka_today(self)
        for rec in self:
            label = _vehicle_label(rec)
            if rec.fix_commissioned:
                raise UserError("%s is already commissioned." % label)
            problems = list(rec._fix_document_problems(today, today).get(rec.id, []))
            if (
                not self.env["fix.vehicle.check"]
                .sudo()
                .search_count([("vehicle_id", "=", rec.id), ("passed", "=", True)])
            ):
                problems.append("no passed pre-use check is recorded")
            if param_on(self.env, COMMISSION_TELEMATICS_PARAM) and not self.env[
                "fix.telematics.device"
            ].sudo().search_count([("vehicle_id", "=", rec.id)]):
                problems.append("no telematics device is fitted")
            if problems:
                raise UserError("%s cannot be commissioned: %s." % (label, "; ".join(problems)))
            rec.with_context(**{_COMMISSION_KEY: _COMMISSIONING}).write(
                {
                    "fix_commissioned": True,
                    "fix_commissioned_on": today,
                    "fix_commissioned_by_id": self.env.uid,
                }
            )
            rec.message_post(body="Commissioned by %s." % self.env.user.name)
        return True

    # ---------------------------------------------------- OU from branch
    @api.model
    def _fix_branch_ou(self, branch_id):
        branch = self.env["fix.branch"].sudo().browse(branch_id) if branch_id else None
        return branch.operating_unit_id if branch else self.env["operating.unit"]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            ou = self._fix_branch_ou(vals.get("branch_id"))
            if ou and not vals.get("operating_unit_id"):
                vals["operating_unit_id"] = ou.id
            if not self.env.su:
                # M46-25: a user's new vehicle starts registered
                vals["fix_commissioned"] = False
                for name in _COMMISSION_FIELDS[1:]:
                    vals.pop(name, None)
        records = super().create(vals_list)
        if not self.env.su:
            records._fix_check_operating_unit()
        return records

    def write(self, vals):
        if not self.env.su:
            if any(f in vals for f in _COMMISSION_FIELDS) and (
                self.env.context.get(_COMMISSION_KEY) is not _COMMISSIONING
            ):
                raise UserError("A vehicle is commissioned with Commission, by a Fleet Officer.")
            if "fix_disposal_id" in vals:
                raise UserError("A vehicle's disposal is linked by the disposal itself.")
        if vals.get("branch_id") and "operating_unit_id" not in vals:
            ou = self._fix_branch_ou(vals["branch_id"])
            if ou:
                vals = dict(vals, operating_unit_id=ou.id)
        res = super().write(vals)
        if not self.env.su and {"branch_id", "operating_unit_id", "active"} & set(vals):
            self._fix_check_operating_unit()
        return res

    def _fix_check_operating_unit(self):
        """M46-04: an active vehicle is costed on its branch's operating unit."""
        for rec in self.sudo().filtered("active"):
            label = _vehicle_label(rec)
            if not rec.operating_unit_id:
                raise UserError(
                    "%s needs its branch (and so its operating unit): every fuel fill, "
                    "service, renewal and fine is costed there." % label
                )
            branch_ou = rec.branch_id.operating_unit_id
            if branch_ou and rec.operating_unit_id != branch_ou:
                raise UserError(
                    "%s: the operating unit follows the branch (%s is in %s)."
                    % (label, rec.branch_id.display_name, branch_ou.display_name)
                )

    # ---------------------------------------------------- disposal only
    def action_retire(self, reason=None):
        """M46-10 (D10): a vehicle leaves the fleet only through an approved
        disposal (Vehicle Disposals); Retire is its last step, not a shortcut."""
        if not self.env.su and self.env.context.get(_DISPOSE_KEY) is not _DISPOSING:
            raise UserError(
                "A vehicle leaves the fleet through a Vehicle Disposal (route, proceeds, "
                "buyer, evidence) approved by the CFO; completing it retires the vehicle."
            )
        return super().action_retire(reason=reason)


class FleetVehicleOdometerCheck(models.Model):
    _inherit = "fleet.vehicle.odometer"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.su:
            for rec in records.filtered("value"):
                problem = rec.vehicle_id.sudo()._fix_odometer_problem(
                    rec.value, rec.date or dhaka_today(rec), exclude=rec
                )
                if problem:
                    raise UserError(problem)
        return records


class FixVehicleDisposal(models.Model):
    """M46-10 (BRU-FLT-20, FR-FLT-044, D10): how a vehicle leaves the fleet.

    Recorded by a Logistics Manager with the route, the reason and the
    evidence; a sale or auction names the buyer and the proceeds. Every
    disposal is approved by the CFO (DOFA Tier 4) through the M63 inbox, by
    someone other than its requester; the approval covers the route, the
    proceeds, the buyer and the vehicle (a change voids it). Completing it
    retires the vehicle. A vehicle the company does not own goes back to its
    lessor or owner (route Return); finance reads the facts from
    _m49_disposal_facts (only a capitalised vehicle concerns M49)."""

    _name = "fix.vehicle.disposal"
    _description = "Vehicle Disposal"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin", "fix.vehicle.lock.mixin"]
    _order = "id desc"
    _fix_insert_only = True

    _approval_domain = "vehicle_disposal"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    name = fields.Char(required=True, default="New", copy=False)
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle",
        required=True,
        ondelete="restrict",
        index=True,
        domain=[("active", "=", True)],
    )
    company_id = fields.Many2one(
        "res.company", related="vehicle_id.company_id", store=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="vehicle_id.operating_unit_id", store=True
    )
    ownership_basis = fields.Selection(
        related="vehicle_id.fix_ownership_basis", string="Ownership Basis"
    )
    route = fields.Selection(DISPOSAL_ROUTES, required=True, tracking=True)
    reason = fields.Text(required=True)
    disposal_date = fields.Date(string="Disposal Date", default=dhaka_default, required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    book_value = fields.Monetary(
        string="Book Value",
        currency_field="currency_id",
        compute="_compute_book_value",
        help="M49 net book value when the vehicle is capitalised, else its purchase value "
        "(D10): the amount the CFO approves the disposal on.",
    )
    proceeds = fields.Monetary(string="Sale Proceeds", currency_field="currency_id", tracking=True)
    buyer_id = fields.Many2one("res.partner", string="Buyer", ondelete="restrict", tracking=True)
    evidence_file = fields.Binary(
        string="Evidence (sale agreement / scrap or police certificate)", attachment=True
    )
    evidence_filename = fields.Char(string="Evidence File Name")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Disposed"), ("cancelled", "Cancelled")],
        required=True,
        default="draft",
        tracking=True,
    )
    done_by_id = fields.Many2one("res.users", string="Completed By", readonly=True, copy=False)
    done_on = fields.Date(string="Completed On", readonly=True, copy=False)
    cancel_reason = fields.Char(string="Cancellation Reason", readonly=True, copy=False)

    # ---- DOFA: the CFO, always (BRU-FLT-20) ---------------------------------
    def _compute_book_value(self):
        for rec in self:
            rec.book_value = rec._fix_book_value()

    def _fix_book_value(self) -> float:
        vehicle = self.vehicle_id.sudo()
        asset = vehicle["fixed_asset_id"] if "fixed_asset_id" in vehicle._fields else None
        if asset and "book_nbv" in asset._fields:
            return asset.book_nbv or 0.0
        return vehicle.net_car_value or 0.0

    def _dofa_thresholds(self):
        return [(float("inf"), "tier_4")]

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self._fix_book_value()

    def _dofa_current_tier(self) -> str:
        # BRU-FLT-20: every vehicle disposal is the CFO's, whatever its value.
        return "tier_4"

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "Vehicle %s disposal (%s, book value BDT %.2f, proceeds BDT %.2f)" % (
            _vehicle_label(self.vehicle_id),
            dict(DISPOSAL_ROUTES).get(self.route, self.route),
            self._fix_book_value(),
            self.proceeds or 0.0,
        )

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"vehicle_id", "route", "proceeds", "buyer_id"}

    # ---- guard / lock -------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "done_by_id",
            "done_on",
            "cancel_reason",
        }

    def _fix_frozen_fields(self) -> set:
        if self.state in ("done", "cancelled"):
            return {
                "vehicle_id",
                "route",
                "reason",
                "disposal_date",
                "proceeds",
                "buyer_id",
                "evidence_file",
                "evidence_filename",
            }
        if isinstance(self.id, int):
            return {"vehicle_id"}
        return set()

    @api.constrains("proceeds")
    def _check_proceeds(self):
        for rec in self:
            if (rec.proceeds or 0.0) < 0:
                raise ValidationError("Sale proceeds cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, LOGISTICS_MANAGER_GROUP, "Raising a vehicle disposal")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.vehicle.disposal")
                    or "VDSP/New"
                )
            if vals.get("vehicle_id") and self.sudo().search_count(
                [("vehicle_id", "=", vals["vehicle_id"]), ("state", "=", "draft")]
            ):
                raise UserError("This vehicle already has a disposal in progress.")
        return super().create(vals_list)

    def _fix_disposal_problems(self):
        """What the disposal still lacks before it can be approved or done."""
        self.ensure_one()
        out = []
        owned = (self.vehicle_id.sudo().fix_ownership_basis or "owned") == "owned"
        if owned and self.route == "lease_return":
            out.append("an owned vehicle is sold, auctioned, scrapped, donated or written off")
        if not owned and self.route != "lease_return":
            out.append(
                "a %s vehicle goes back to its lessor or owner (route Return)"
                % self.vehicle_id.fix_ownership_basis
            )
        if self.route in _SOLD:
            if not self.buyer_id:
                out.append("the buyer")
            if not (self.proceeds or 0.0) > 0:
                out.append("the sale proceeds")
        elif self.proceeds:
            out.append("no proceeds on a %s" % dict(DISPOSAL_ROUTES)[self.route].lower())
        if not self.evidence_file:
            out.append("the evidence (sale agreement, scrap or police certificate)")
        if not (self.reason or "").strip():
            out.append("the reason")
        return out

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Request approval of a draft disposal.")
            problems = rec._fix_disposal_problems()
            if problems:
                raise UserError("%s needs %s." % (rec.name, "; ".join(problems)))
        return super().action_request_approval(justification=justification)

    def action_recall_approval(self):
        """The requester withdraws a disposal waiting for the CFO."""
        return super().action_recall_approval()

    def action_complete(self):
        """Draft -> disposed, on the CFO's approval of these exact terms. The
        vehicle is retired (refused while a booking still needs it)."""
        require_role(self.env, LOGISTICS_MANAGER_GROUP, "Completing a vehicle disposal")
        today = dhaka_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Complete a draft disposal.")
            problems = rec._fix_disposal_problems()
            if problems:
                raise UserError("%s needs %s." % (rec.name, "; ".join(problems)))
            if rec.approval_state != "approved":
                raise UserError(
                    "%s is not approved: request the CFO's approval (DOFA Tier 4) first." % rec.name
                )
            rec._dofa_assert_approved("Disposing of the vehicle")
            vehicle = rec.vehicle_id
            vehicle.with_context(**{_DISPOSE_KEY: _DISPOSING}).sudo().action_retire(
                reason="%s: %s (%s)"
                % (rec.name, dict(DISPOSAL_ROUTES)[rec.route], (rec.reason or "").strip()[:80])
            )
            vehicle.sudo().write({"fix_disposal_id": rec.id})
            rec._guarded().write({"state": "done", "done_by_id": self.env.uid, "done_on": today})
            rec.message_post(
                body="Disposed by %s: %s." % (self.env.user.name, rec._dofa_amount_label())
            )
        return True

    def action_cancel(self, reason=None):
        require_role(self.env, LOGISTICS_MANAGER_GROUP, "Cancelling a vehicle disposal")
        reason = _reason(reason, "cancelling the disposal")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Cancel a draft disposal.")
            if rec.approval_state == "pending":
                rec.action_recall_approval()
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason})
        return True

    def _m49_disposal_facts(self):
        """What M49 derecognises a capitalised vehicle on (D10): the route,
        the proceeds and the buyer, approved by the CFO."""
        self.ensure_one()
        rec = self.sudo()
        return {
            "disposal_ref": rec.name,
            "route": rec.route,
            "kind": "sale"
            if rec.route in _SOLD
            else ("scrap" if rec.route == "scrap" else rec.route),
            "proceeds": rec.proceeds or 0.0,
            "buyer_id": rec.buyer_id.id or False,
            "disposal_date": rec.disposal_date,
            "book_value": rec._fix_book_value(),
            "approved_by_id": rec.dofa_approved_by.id or False,
            "operating_unit_id": rec.vehicle_id.operating_unit_id.id or False,
        }


class FixDriverHrLicence(models.Model):
    """M46-20 (FR-FLT-017): one driving licence per person. The M21 employee
    record (cd_hr_core: driving_license_no / driving_license_exp, when that
    module is installed) and the fleet driver record are kept in step: a
    change on either side is copied to the other, and a legacy difference is
    shown on the driver."""

    _inherit = "fix.driver"

    hr_licence_mismatch = fields.Char(
        string="Differs From HR", compute="_compute_hr_licence_mismatch"
    )

    _HR_SYNC_KEY = "fix_driver_hr_sync"

    @api.model
    def _fix_hr_fields(self):
        Emp = self.env["hr.employee"]
        return all(f in Emp._fields for f in ("driving_license_no", "driving_license_exp"))

    def _compute_hr_licence_mismatch(self):
        hr = self._fix_hr_fields()
        for rec in self:
            emp = rec.employee_id.sudo()
            diffs = []
            if hr and emp:
                no = (emp.driving_license_no or "").replace(" ", "").upper()
                if no and no != (rec.license_no or "").replace(" ", "").upper():
                    diffs.append("licence number %s" % emp.driving_license_no)
                if emp.driving_license_exp and emp.driving_license_exp != rec.license_expiry:
                    diffs.append("expiry %s" % emp.driving_license_exp)
            rec.hr_licence_mismatch = ("HR records " + ", ".join(diffs)) if diffs else False

    def _fix_push_to_hr(self):
        if not self._fix_hr_fields() or self.env.context.get(self._HR_SYNC_KEY):
            return
        for rec in self:
            emp = rec.employee_id.sudo().with_context(**{self._HR_SYNC_KEY: True})
            vals = {}
            if rec.license_no and rec.license_no != emp.driving_license_no:
                vals["driving_license_no"] = rec.license_no
            if rec.license_expiry and rec.license_expiry != emp.driving_license_exp:
                vals["driving_license_exp"] = rec.license_expiry
            if vals:
                emp.write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs._fix_push_to_hr()
        return recs

    def write(self, vals):
        res = super().write(vals)
        if {"license_no", "license_expiry", "employee_id"} & set(vals):
            self._fix_push_to_hr()
        return res


class HrEmployeeDriverLicence(models.Model):
    _inherit = "hr.employee"

    def write(self, vals):
        res = super().write(vals)
        keys = {"driving_license_no", "driving_license_exp"} & set(vals)
        if keys and not self.env.context.get(FixDriverHrLicence._HR_SYNC_KEY):
            Driver = (
                self.env["fix.driver"]
                .sudo()
                .with_context(**{FixDriverHrLicence._HR_SYNC_KEY: True})
            )
            for emp in self.sudo():
                driver = Driver.search([("employee_id", "=", emp.id)], limit=1)
                if not driver:
                    continue
                dvals = {}
                if "driving_license_no" in keys and emp.driving_license_no:
                    dvals["license_no"] = emp.driving_license_no
                if "driving_license_exp" in keys and emp.driving_license_exp:
                    dvals["license_expiry"] = emp.driving_license_exp
                if dvals:
                    driver.write(dvals)
                    driver.message_post(body="Licence updated from the HR employee record (M21).")
        return res


class FixVehicleFuelClassTank(models.Model):
    _inherit = "fix.vehicle.fuel"

    @api.model
    def _fix_tank_capacity(self, vehicle=None) -> float:
        """M46-19: the vehicle's own tank, else its class profile's, else the
        fleet-wide ceiling."""
        if vehicle:
            vehicle = vehicle.sudo()
            if not (vehicle.fix_tank_capacity_l and vehicle.fix_tank_capacity_l > 0):
                profile_tank = vehicle.fix_class_profile_id.tank_capacity_l
                if profile_tank and profile_tank > 0:
                    return profile_tank
        return super()._fix_tank_capacity(vehicle)
