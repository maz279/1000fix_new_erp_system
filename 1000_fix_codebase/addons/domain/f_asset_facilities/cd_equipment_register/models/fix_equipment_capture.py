# fix_equipment_capture — M45 capture audit (2026-11-16): the spec records the
# sub-module pages could not capture.
#
# Before this file the register held a free-text category and no identity
# (manufacturer, model, serial, tag, supplier, warranty), and the fitness gate
# demanded a current calibration of EVERY item, so a screwdriver or a laptop,
# which the spec registers on purpose (§4 "the register is deliberately wide,
# the control deliberately narrow"), could never be issued. Nothing captured:
#   - the equipment class and its control behaviour (FR-EAM-002/003);
#   - what a branch should hold (FR-EAM-009/037, BRU-EAM-20);
#   - the reference standard a calibration used (FR-EAM-028, BRU-EAM-04);
#   - a calibration recall (FR-EAM-029);
#   - a preventive maintenance plan (FR-EAM-032);
#   - a loss / damage report with its accountability (FR-EAM-040/041,
#     BRU-EAM-12);
#   - a blind physical count by branch (FR-EAM-038, AUT-EAM-12);
#   - the retirement and disposal route (FR-EAM-042/043, BRU-EAM-16).
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_equipment import (
    ROLE_CALIBRATION,
    ROLE_CUSTODIAN,
    ROLE_QM,
    m45_require_role,
    m45_today,
)

# D9 (A07 ERP decisions 2026-11-20): a staff recharge needs an HR-approved
# recovery decision; M56 deducts it within the statutory limit (S6 / M56).
ROLE_HR = ("hr.group_hr_manager",)

# FR-EAM-002: the spec's classes.
EQUIPMENT_CLASSES = [
    ("measuring_instrument", "Measuring Instrument"),
    ("calibration_standard", "Calibration Standard"),
    ("general_tool", "General Tool"),
    ("it_asset", "IT Asset"),
    ("branch_equipment", "Branch Equipment"),
    ("specialist_equipment", "Specialist Equipment"),
    ("safety_equipment", "Safety / ESD Equipment"),
]
# FR-EAM-003: the classes whose items verify conformity by default.
CALIBRATED_CLASSES = ("measuring_instrument", "calibration_standard")
# A loss that keeps the item missing until it is recovered or written off.
OPEN_LOSS = ("reported", "writeoff_requested")


def _today(env):
    # A07 ERP audit M45-08: the Dhaka business day, whatever the user's tz
    return m45_today(env)


def _same_code(model, rec, field="code"):
    """Another row of the company with this code, compared trimmed and
    case-insensitively."""
    code = (rec[field] or "").strip()
    if not code:
        return model.browse()
    key = code.lower()
    return (
        model.sudo()
        .with_context(active_test=False)
        .search(
            [("id", "!=", rec.id), ("company_id", "=", rec.company_id.id), (field, "ilike", code)]
        )
        .filtered(lambda r: (r[field] or "").strip().lower() == key)
    )


# ---------------------------------------------------------------------------
# Equipment class (FR-EAM-002/003)
# ---------------------------------------------------------------------------
class FixEquipmentCategory(models.Model):
    _name = "fix.equipment.category"
    _description = "Equipment Class"
    # A07 ERP audit (2026-11-20) M45-04: switching calibration control off is
    # a routed approval (M63), not a tick by the Quality Manager
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "classification, code"

    _approval_domain = "calibration_control"
    _approval_apply_method = "action_apply_control_off"
    _approval_group = ROLE_QM
    _approval_routed = True

    code = fields.Char(required=True, tracking=True)
    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    classification = fields.Selection(
        EQUIPMENT_CLASSES, required=True, default="general_tool", tracking=True
    )
    requires_calibration = fields.Boolean(
        string="Calibration Controlled",
        compute="_compute_class_defaults",
        store=True,
        readonly=False,
        tracking=True,
        help="Items of this class verify conformity (ISO 9001 7.1.5): they need a current "
        "calibration to be issued, used or put on a QC record. Measuring instruments and "
        "calibration standards are controlled by default.",
    )
    requires_verification = fields.Boolean(
        string="Periodic Verification",
        help="A simpler periodic check instead of a formal calibration (ESD straps, "
        "mats, torque drivers: FR-EAM-031).",
    )
    data_bearing = fields.Boolean(
        compute="_compute_class_defaults",
        store=True,
        readonly=False,
        tracking=True,
        help="Items hold data: a retired one leaves only with an M06 erasure certificate "
        "(BRU-EAM-16). IT assets are data-bearing by default.",
    )
    default_calibration_months = fields.Integer(string="Default Calibration Interval (months)")
    critical = fields.Boolean(
        string="Critical", help="A branch cannot work without an item of this class."
    )
    active = fields.Boolean(default=True)
    equipment_count = fields.Integer(compute="_compute_equipment_count", string="Items")
    # M45-04: the proposal a Quality Manager requests approval for
    proposed_classification = fields.Selection(
        EQUIPMENT_CLASSES,
        string="Proposed Classification",
        copy=False,
        help="Optional: the class the items move to when control is switched off.",
    )
    control_change_reason = fields.Text(
        string="Why Calibration Control Is Switched Off",
        copy=False,
        help="Why items of this class no longer verify conformity. Approved by a Quality "
        "Manager other than the requester (an M63 rule may add the CTO).",
    )

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields()
        if any(rec.approval_state == "pending" for rec in self):
            guarded |= {"proposed_classification", "control_change_reason"}
        return guarded

    @api.depends("classification")
    def _compute_class_defaults(self):
        for rec in self:
            rec.requires_calibration = rec.classification in CALIBRATED_CLASSES
            rec.data_bearing = rec.classification == "it_asset"

    def _compute_equipment_count(self):
        groups = (
            self.env["fix.equipment"]
            .sudo()
            ._read_group([("category_id", "in", self.ids)], ["category_id"], ["__count"])
        )
        counts = {category.id: count for category, count in groups}
        for rec in self:
            rec.equipment_count = counts.get(rec.id, 0)

    @api.constrains("code", "company_id")
    def _check_unique_code(self):
        for rec in self:
            dupes = _same_code(self, rec)
            if dupes:
                raise ValidationError(
                    "Class code %s is already used by %s." % (rec.code.strip(), dupes[0].name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        # spec §13: the Quality Manager owns the register standard
        m45_require_role(self.env, (ROLE_QM,), "An equipment class")
        return super().create(vals_list)

    def _m45_turns_control_off(self, vals) -> bool:
        if "requires_calibration" in vals:
            after = bool(vals["requires_calibration"])
        elif "classification" in vals:
            after = vals["classification"] in CALIBRATED_CLASSES
        else:
            return False
        return any(rec.requires_calibration and not after for rec in self)

    def write(self, vals):
        if not self._fix_guard_open():
            m45_require_role(self.env, (ROLE_QM,), "Changing an equipment class")
            if not self.env.su and self._m45_turns_control_off(vals):
                raise UserError(
                    "Switching calibration control off releases every instrument of the "
                    "class from the fitness gate (BRU-EAM-01 has no override). State why "
                    "under 'Why Calibration Control Is Switched Off' and Request Approval: "
                    "a Quality Manager other than you decides it."
                )
        return super().write(vals)

    def _approval_needed(self) -> bool:
        return True

    def action_request_approval(self, justification=None):
        """Ask for calibration control to be switched off on the class."""
        m45_require_role(self.env, (ROLE_QM,), "Requesting a calibration-control change")
        for rec in self:
            if not rec.requires_calibration:
                raise UserError("%s is not calibration-controlled." % rec.name)
            reason = (justification or rec.control_change_reason or "").strip()
            if not reason:
                raise UserError("State why calibration control is switched off on %s." % rec.name)
            if rec.proposed_classification in CALIBRATED_CLASSES:
                raise UserError(
                    "%s is a calibration-controlled classification: propose an "
                    "uncontrolled one, or leave it empty." % rec.proposed_classification
                )
            if not (rec.control_change_reason or "").strip():
                rec.write({"control_change_reason": reason})
            super(FixEquipmentCategory, rec).action_request_approval(justification=reason)
        return True

    def action_apply_control_off(self):
        """The approver's decision, from the inbox task (engine-routed). The open
        calibration and recall holds of the class stay open: only a passing
        re-calibration clears them (fix.equipment.oos.action_resolve)."""
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        for rec in self:
            if not self.env.su and not authority.has_group(ROLE_QM):
                raise UserError(
                    "Approving a calibration-control change needs the Quality Manager role."
                )
            vals = {"requires_calibration": False}
            if rec.proposed_classification:
                vals["classification"] = rec.proposed_classification
            reason = rec.control_change_reason
            rec._guarded().write(vals)
            rec._guarded().write({"proposed_classification": False, "control_change_reason": False})
            rec.message_post(
                body="Calibration control switched off, approved by %s. Justification: %s"
                % (self.env.user.name, reason or "-")
            )
        return True


# ---------------------------------------------------------------------------
# Equipment: identity, class, calibration control, recall, losses
# ---------------------------------------------------------------------------
class FixEquipmentRegister(models.Model):
    _inherit = "fix.equipment"

    category_id = fields.Many2one(
        "fix.equipment.category",
        string="Equipment Class",
        ondelete="restrict",
        index=True,
        tracking=True,
    )
    classification = fields.Selection(
        related="category_id.classification", store=True, string="Classification"
    )
    measurement_critical = fields.Boolean(
        string="Measurement-Critical",
        compute="_compute_measurement_critical",
        store=True,
        help="Calibration control applies (FR-EAM-003): taken from the class. An item "
        "with no class is controlled, so nothing escapes the gate by being unclassified.",
    )
    data_bearing = fields.Boolean(related="category_id.data_bearing", store=True)
    manufacturer = fields.Char()
    model_name = fields.Char(string="Model")
    serial_no = fields.Char(string="Serial Number", index=True)
    asset_tag = fields.Char(
        string="Asset Tag",
        copy=False,
        index=True,
        help="The QR / barcode label. Generated when left empty; permanent once registered.",
    )
    acquisition_ref = fields.Char(string="Purchase / GRN Reference")
    acquired_on = fields.Date(string="Acquired On")
    expected_life_months = fields.Integer(string="Expected Life (months)")
    supplier_id = fields.Many2one("res.partner", string="Supplier")
    warranty_until = fields.Date(string="Warranty Until")
    warranty_active = fields.Boolean(compute="_compute_warranty_active", string="Under Warranty")
    criticality = fields.Selection(
        [("normal", "Normal"), ("critical", "Critical: work stops without it")],
        default="normal",
        required=True,
    )
    home_location = fields.Char(
        string="Home Location", help="Where the item lives in its branch: store shelf, bench."
    )
    calibration_recall_note = fields.Char(
        string="Recall Reason",
        readonly=True,
        copy=False,
        help="Why the item was last recalled for calibration (FR-EAM-029).",
    )
    calibration_state = fields.Selection(
        selection_add=[("not_required", "Not Required (not measurement-critical)")]
    )

    @api.depends("category_id", "category_id.requires_calibration")
    def _compute_measurement_critical(self):
        for rec in self:
            rec.measurement_critical = not rec.category_id or rec.category_id.requires_calibration

    def _compute_warranty_active(self):
        today = _today(self.env)
        for rec in self:
            rec.warranty_active = bool(rec.warranty_until and rec.warranty_until >= today)

    @api.depends(
        "calibration_ids.calibrated_on",
        "calibration_ids.next_due",
        "calibration_ids.result",
        "calibration_ids.superseded_by_id",
        "calibration_ids.decision_state",
        "measurement_critical",
    )
    def _compute_calibration(self):
        super()._compute_calibration()
        for rec in self:
            if not rec.measurement_critical:
                # §4: the control is deliberately narrow. The dates stay visible.
                rec.calibration_state = "not_required"
                rec.calibration_overdue = False

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {"calibration_recall_note"}
        if self:
            guarded |= {"asset_tag"}
        if any(rec.operational_status == "retired" for rec in self):
            guarded |= {"category_id", "serial_no", "manufacturer", "model_name"}
        return guarded

    @api.constrains("asset_tag", "company_id")
    def _check_unique_tag(self):
        for rec in self:
            dupes = _same_code(self, rec, "asset_tag")
            if dupes:
                raise ValidationError(
                    "Asset tag %s is already on %s: a tag identifies one item."
                    % (rec.asset_tag.strip(), dupes[0].name)
                )

    @api.constrains("warranty_until", "acquired_on")
    def _check_warranty_dates(self):
        for rec in self:
            if rec.warranty_until and rec.acquired_on and rec.warranty_until < rec.acquired_on:
                raise ValidationError(
                    "%s: the warranty ends before the item was acquired." % rec.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not (vals.get("asset_tag") or "").strip():
                vals["asset_tag"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.tag") or False
                )
        return super().create(vals_list)

    def write(self, vals):
        # a class change can switch calibration control off: the Quality Manager's
        # decision, never a store keeper's (FR-EAM-003, BRU-EAM-01 has no override)
        if "category_id" in vals and not self._fix_guard_open():
            new = vals["category_id"] or False
            moved = self.filtered(lambda r: (r.category_id.id or False) != new)
            if moved:
                m45_require_role(self.env, (ROLE_QM,), "Changing the class of registered equipment")
            target = self.env["fix.equipment.category"].sudo().browse(new or [])
            # A07 ERP audit M45-04: an overdue meter was moved to an
            # uncontrolled class and was at once "not required" and usable.
            # Moving an item out of calibration control is allowed only while
            # it is in calibration (current, no calibration or recall hold).
            if target and not target.requires_calibration and not self.env.su:
                today = _today(self.env)
                Hold = self.env["fix.equipment.oos"].sudo()
                for rec in moved.sudo().filtered("measurement_critical"):
                    state = rec._m45_certificate_state(rec._m45_latest_calibration(), today)
                    held = Hold.search_count(
                        [
                            ("equipment_id", "=", rec.id),
                            ("state", "=", "open"),
                            ("hold_type", "in", ("calibration", "recall")),
                        ]
                    )
                    if state != "current" or held:
                        raise UserError(
                            "%s is not in calibration (%s): it cannot leave calibration "
                            "control. Recalibrate it first; the class change then follows."
                            % (rec.name, "on hold" if held else state)
                        )
        return super().write(vals)

    # ---- the measurement-critical gate (FR-EAM-003) -------------------------
    def _m45_calibration_problem(self):
        self.ensure_one()
        if not self.sudo().measurement_critical:
            return None
        return super()._m45_calibration_problem()

    def _m45_fitness_problem_on(self, day):
        """An item outside calibration control is judged on holds, custody and
        loss only: its certificate state decides nothing."""
        self.ensure_one()
        if self.sudo().measurement_critical:
            return super()._m45_fitness_problem_on(day)
        rec = self.sudo()
        if rec.retired_on and rec.retired_on <= day:
            return "%s had been retired by %s." % (rec.name, day)
        hold = (
            self.env["fix.equipment.oos"]
            .sudo()
            .search(
                [
                    ("equipment_id", "=", rec.id),
                    ("started_on", "<=", day),
                    "|",
                    ("state", "=", "open"),
                    ("resolved_on", ">", day),
                ],
                limit=1,
            )
        )
        if hold:
            return "%s was out of service on %s (%s)." % (rec.name, day, hold.reason)
        return None

    def _m45_released_status(self):
        """A reported loss keeps the item missing until it is recovered or the
        write-off is decided (FR-EAM-040)."""
        self.ensure_one()
        if self.sudo().operational_status != "retired" and self.env[
            "fix.equipment.loss"
        ].sudo().search_count(
            [
                ("equipment_id", "=", self.id),
                ("state", "in", OPEN_LOSS),
                ("kind", "in", ("lost", "stolen")),
            ]
        ):
            return "missing"
        return super()._m45_released_status()

    # ---- calibration recall (FR-EAM-029) ------------------------------------
    def action_recall_calibration(self, reason=None):
        """Recall an instrument for calibration: it is unavailable until a passing
        calibration returns it to service, and its holder is asked to hand it in."""
        m45_require_role(
            self.env, (ROLE_QM, ROLE_CALIBRATION), "Recalling an instrument for calibration"
        )
        Hold = self.env["fix.equipment.oos"]._guarded()
        for rec in self:
            equipment = rec.sudo()
            if equipment.operational_status in ("retired", "missing"):
                raise UserError(
                    "%s is %s: there is nothing to recall."
                    % (equipment.name, equipment.operational_status)
                )
            if not equipment.measurement_critical:
                raise UserError(
                    "%s is not measurement-critical: its class is outside calibration "
                    "control, so it is not recalled." % equipment.name
                )
            if Hold.sudo().search_count(
                [
                    ("equipment_id", "=", equipment.id),
                    ("state", "=", "open"),
                    ("hold_type", "=", "recall"),
                ]
            ):
                raise UserError("%s is already recalled for calibration." % equipment.name)
            note = (reason or "").strip()
            if not note:
                raise UserError("State why %s is recalled for calibration." % equipment.name)
            rec._guarded().write({"calibration_recall_note": note})
            Hold.create(
                {
                    "equipment_id": equipment.id,
                    "reason": "Recalled for calibration: %s" % note,
                    "hold_type": "recall",
                }
            )
            issue = (
                self.env["fix.equipment.issue"]
                .sudo()
                .search([("equipment_id", "=", equipment.id), ("state", "=", "issued")], limit=1)
            )
            holder = (issue.custodian_id or equipment.custodian_id).user_id
            if holder and holder._is_internal():
                equipment.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=holder.id,
                    summary="Hand %s in for calibration" % equipment.code,
                    note="%s is recalled for calibration: %s" % (equipment.name, note),
                )
            publish(
                self.env,
                "equipment.calibration_recalled",
                "fix.equipment",
                equipment.id,
                {
                    "equipment": equipment.code,
                    "reason": note,
                    "holder": (issue.custodian_id or equipment.custodian_id).name or None,
                    "branch": equipment.branch_id.name or None,
                },
            )
        return True

    # ---- write-off: loss reporters and retirement records (BRU-EAM-12) ------
    def _m45_open_loss_reporters(self):
        return (
            self.env["fix.equipment.loss"]
            .sudo()
            .search([("equipment_id", "in", self.ids), ("state", "in", OPEN_LOSS)])
            .reported_by_id
        )

    def _approval_excluded(self):
        # the person who reported the loss never receives its write-off task
        return (super()._approval_excluded() | self._m45_open_loss_reporters()).sudo()

    def action_approve_writeoff(self):
        if not self.env.su:
            for rec in self:
                if self.env.user in rec._m45_open_loss_reporters():
                    raise UserError(
                        "Segregation of duties (BRU-EAM-12): you reported the loss of %s and "
                        "cannot approve its write-off." % rec.name
                    )
        res = super().action_approve_writeoff()
        now = fields.Datetime.now()
        for rec in self:
            losses = (
                self.env["fix.equipment.loss"]
                .sudo()
                .search([("equipment_id", "=", rec.id), ("state", "=", "writeoff_requested")])
            )
            losses._guarded().write(
                {"state": "written_off", "decided_by_id": self.env.user.id, "decided_on": now}
            )
            for loss in losses.filtered(lambda r: r.recharge_employee_id and r.recharge_amount):
                # AUT-EAM-14 / D9: payroll recovers it only on HR's approval
                if loss.recharge_hr_decision == "approved":
                    loss._m45_publish_recharge()
                elif not loss.recharge_hr_decision:
                    loss.message_post(
                        body="Written off. The proposed recharge of BDT %.2f to %s waits for "
                        "HR's recovery decision."
                        % (loss.recharge_amount, loss.recharge_employee_id.name)
                    )
            self.env["fix.equipment.retirement"].sudo().search(
                [("equipment_id", "=", rec.id), ("state", "=", "requested")]
            )._guarded().write({"state": "approved"})
        return res


# ---------------------------------------------------------------------------
# Calibration: the reference standard and the provider (FR-EAM-021/023/028)
# ---------------------------------------------------------------------------
STANDARD_EVIDENCE = {"standard_equipment_id", "provider_id", "accreditation_ref"}


class FixCalibrationStandard(models.Model):
    _inherit = "fix.calibration"

    standard_equipment_id = fields.Many2one(
        "fix.equipment",
        string="Reference Standard (in-house)",
        ondelete="restrict",
        index=True,
        help="The company's own calibration standard this calibration was made against. "
        "It must itself be in calibration on the day (BRU-EAM-04).",
    )
    provider_id = fields.Many2one("res.partner", string="Calibration Provider")
    accreditation_ref = fields.Char(string="Accreditation Reference")

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields()
        if self:
            guarded |= STANDARD_EVIDENCE
        return guarded

    @api.model
    def _m45_standard_problem(self, vals):
        """AUT-EAM-06: a calibration against a standard that is itself out of
        calibration is invalid. Checked for every caller: there is no failure path."""
        std = self.env["fix.equipment"].sudo().browse(vals.get("standard_equipment_id") or [])
        if not std:
            return None
        if std.id == vals.get("equipment_id"):
            return "An instrument cannot be calibrated against itself."
        if std.classification != "calibration_standard":
            return "%s is not registered as a calibration standard (its class is %s)." % (
                std.name,
                std.category_id.name or "unclassified",
            )
        day = fields.Date.to_date(vals.get("calibrated_on")) or _today(self.env)
        state = std._m45_certificate_state(std._m45_calibration_at(day), day)
        if state != "current":
            label = dict(std._fields["calibration_state"].selection).get(state, state)
            return (
                "The reference standard %s was not in calibration on %s (%s): a calibration "
                "made against it is invalid (BRU-EAM-04)." % (std.name, day, label.lower())
            )
        problem = std._m45_fitness_problem_on(day)
        if problem and not problem.startswith("%s was issued" % std.name):
            return "The reference standard is not usable: %s" % problem
        return None

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            problem = self._m45_standard_problem(vals)
            if problem:
                raise UserError(problem)
            std = self.env["fix.equipment"].sudo().browse(vals.get("standard_equipment_id") or [])
            if std:
                # A07 ERP audit M45-07: the reference is the standard's own code;
                # a different typed reference would hide which standard was used
                typed = (vals.get("standard_ref") or "").strip()
                if not typed:
                    vals["standard_ref"] = std.code
                elif (
                    typed.lower()
                    not in {
                        (std.code or "").strip().lower(),
                        (std.asset_tag or "").strip().lower(),
                    }
                    and not self.env.su
                ):
                    raise UserError(
                        "The standard reference %s does not match the reference standard "
                        "chosen (%s): leave it empty, it is taken from the standard."
                        % (
                            typed,
                            std.code,
                        )
                    )
        return super().create(vals_list)


# ---------------------------------------------------------------------------
# Out of service: the recall hold; non-critical items return without a
# calibration (§8.1 "re-calibrated where measurement-critical")
# ---------------------------------------------------------------------------
class FixEquipmentOosRecall(models.Model):
    _inherit = "fix.equipment.oos"

    hold_type = fields.Selection(
        selection_add=[("recall", "At calibration (recalled)")],
        ondelete={"recall": "set default"},
    )


# ---------------------------------------------------------------------------
# Branch equipment profile (FR-EAM-009/037, BRU-EAM-20)
# ---------------------------------------------------------------------------
class FixBranchEquipmentProfile(models.Model):
    _name = "fix.branch.equipment.profile"
    _description = "Branch Equipment Profile"
    _order = "branch_id, category_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True, index=True)
    category_id = fields.Many2one(
        "fix.equipment.category", string="Equipment Class", required=True, ondelete="restrict"
    )
    minimum_quantity = fields.Integer(string="Minimum Held", required=True, default=1)
    critical = fields.Boolean(
        help="The branch stops work without a fit item of this class: a branch with none "
        "available is a capability exception (BRU-EAM-20)."
    )
    effective_from = fields.Date(default=lambda self: _today(self.env))
    active = fields.Boolean(default=True)
    held_count = fields.Integer(compute="_compute_cover", string="Held")
    fit_count = fields.Integer(compute="_compute_cover", string="Fit & Available")
    shortfall = fields.Integer(compute="_compute_cover", string="Shortfall")
    capability_exception = fields.Boolean(compute="_compute_cover", string="Capability Exception")

    _branch_class_unique = models.Constraint(
        "UNIQUE (company_id, branch_id, category_id)",
        "A branch has one profile line per equipment class.",
    )
    _minimum_positive = models.Constraint(
        "CHECK (minimum_quantity > 0)", "The minimum held must be at least one."
    )

    def _compute_cover(self):
        Equipment = self.env["fix.equipment"].sudo()
        for rec in self:
            items = Equipment.search(
                [
                    ("branch_id", "=", rec.branch_id.id),
                    ("category_id", "=", rec.category_id.id),
                    ("operational_status", "not in", ("retired", "missing")),
                ]
            )
            fit = items.filtered(
                lambda e: e.operational_status == "available" and not e._m45_calibration_problem()
            )
            rec.held_count = len(items)
            rec.fit_count = len(fit)
            rec.shortfall = max(0, rec.minimum_quantity - len(items))
            rec.capability_exception = bool(rec.critical and not fit)

    @api.model_create_multi
    def create(self, vals_list):
        m45_require_role(self.env, (ROLE_QM,), "A branch equipment profile")
        return super().create(vals_list)

    def write(self, vals):
        m45_require_role(self.env, (ROLE_QM,), "Changing a branch equipment profile")
        return super().write(vals)


# ---------------------------------------------------------------------------
# Preventive maintenance plan (FR-EAM-032, AUT-EAM-11)
# ---------------------------------------------------------------------------
class FixEquipmentPmPlan(models.Model):
    _name = "fix.equipment.pm.plan"
    _description = "Equipment PM Plan"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "name desc"

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", index=True, ondelete="cascade"
    )
    category_id = fields.Many2one(
        "fix.equipment.category", string="Equipment Class", ondelete="restrict"
    )
    trigger_type = fields.Selection(
        [("elapsed", "Elapsed Time"), ("usage", "Usage Counter")],
        required=True,
        default="elapsed",
    )
    interval_value = fields.Integer(string="Every", required=True, default=6)
    interval_unit = fields.Selection(
        [("days", "Days"), ("months", "Months"), ("uses", "Uses")],
        required=True,
        default="months",
    )
    start_on = fields.Date(
        string="Counting From", required=True, default=lambda self: _today(self.env)
    )
    task = fields.Text(string="Work To Do", required=True)
    active = fields.Boolean(default=True, tracking=True)
    job_ids = fields.One2many("fix.equipment.pm", "plan_id", string="Jobs")
    next_due = fields.Date(compute="_compute_due", string="Next Due")
    open_jobs = fields.Integer(compute="_compute_due", string="Open Jobs")

    _interval_positive = models.Constraint(
        "CHECK (interval_value > 0)", "The interval must be at least one."
    )

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields()
        if self:
            guarded |= {"equipment_id", "category_id", "company_id"}
        return guarded

    @api.constrains("equipment_id", "category_id", "trigger_type", "interval_unit")
    def _check_scope(self):
        for rec in self:
            if bool(rec.equipment_id) == bool(rec.category_id):
                raise ValidationError(
                    "A PM plan covers one item or one equipment class: choose exactly one."
                )
            if (rec.trigger_type == "usage") != (rec.interval_unit == "uses"):
                raise ValidationError(
                    "A usage plan counts uses; an elapsed-time plan counts days or months."
                )

    def _m45_scope(self):
        self.ensure_one()
        if self.equipment_id:
            return self.equipment_id.sudo().filtered(lambda e: e.operational_status != "retired")
        return (
            self.env["fix.equipment"]
            .sudo()
            .search(
                [
                    ("category_id", "=", self.category_id.id),
                    ("company_id", "=", self.company_id.id),
                    ("operational_status", "!=", "retired"),
                ]
            )
        )

    def _m45_due(self, equipment, today):
        """(due, date) for one item: counted from its last completed job of this
        plan, or the plan's start. Never due while a job of the plan is open."""
        self.ensure_one()
        jobs = self.sudo().job_ids.filtered(lambda j, e=equipment: j.equipment_id == e)
        if jobs.filtered(lambda j: j.state == "open"):
            return False, None
        done = jobs.filtered(lambda j: j.state == "done" and j.done_on).sorted("done_on")
        base = done[-1].done_on if done else self.start_on
        if self.trigger_type == "elapsed":
            step = (
                relativedelta(months=self.interval_value)
                if self.interval_unit == "months"
                else relativedelta(days=self.interval_value)
            )
            due = base + step
            return due <= today, due
        used = sum(
            self.env["fix.equipment.usage"]
            .sudo()
            # M45-29: uses on the completion day itself belong to the old period
            .search([("equipment_id", "=", equipment.id), ("used_on", ">", base)])
            .mapped("uses")
        )
        return used >= self.interval_value, today

    def _compute_due(self):
        today = _today(self.env)
        for rec in self:
            dates = []
            if rec.id and rec.active and (rec.equipment_id or rec.category_id):
                for equipment in rec._m45_scope():
                    __, due = rec._m45_due(equipment, today)
                    if due:
                        dates.append(due)
            rec.next_due = min(dates) if dates else False
            rec.open_jobs = len(rec.sudo().job_ids.filtered(lambda j: j.state == "open"))

    @api.model_create_multi
    def create(self, vals_list):
        m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), "A PM plan")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.pm.plan") or "EPMP/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), "Changing a PM plan")
        return super().write(vals)

    def _m45_raise_due_jobs(self, today=None):
        today = today or _today(self.env)
        Job = self.env["fix.equipment.pm"].sudo()
        raised = Job.browse()
        for plan in self.filtered("active"):
            for equipment in plan._m45_scope():
                due, when = plan._m45_due(equipment, today)
                if not due:
                    continue
                job = Job.create(
                    {
                        "equipment_id": equipment.id,
                        "pm_type": "preventive",
                        "scheduled_on": when,
                        "description": (plan.task or "")[:250],
                    }
                )
                job._guarded().write({"plan_id": plan.id})
                raised |= job
        return raised

    def action_raise_due_jobs(self):
        """Raise the jobs that are due now (the nightly job does the same)."""
        m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), "Raising PM jobs")
        raised = self._m45_raise_due_jobs()
        return {"warning": "Nothing is due yet."} if not raised else True

    @api.model
    def cron_pm_plans(self):
        """Nightly (AUT-EAM-11): every active plan raises its due jobs, once."""
        return len(self.sudo().search([("active", "=", True)])._m45_raise_due_jobs())


class FixEquipmentPmCapture(models.Model):
    _inherit = "fix.equipment.pm"

    plan_id = fields.Many2one(
        "fix.equipment.pm.plan", string="PM Plan", readonly=True, index=True, ondelete="set null"
    )
    description = fields.Char(string="Work To Do")
    # FR-EAM-033/034/036: the fault, where it is repaired, and the downtime
    symptom = fields.Char(help="What is wrong (a corrective job).")
    repair_route = fields.Selection(
        [("internal", "Internal (M31 workshop)"), ("external", "External provider")],
        default="internal",
    )
    external_provider_id = fields.Many2one("res.partner", string="External Provider")
    downtime_hours = fields.Float(string="Downtime (hours)")

    _downtime_positive = models.Constraint(
        "CHECK (downtime_hours IS NULL OR downtime_hours >= 0)", "Downtime cannot be negative."
    )

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {"plan_id"}
        if any(rec.state == "done" for rec in self):
            guarded |= {
                "description",
                "symptom",
                "repair_route",
                "external_provider_id",
                "downtime_hours",
            }
        return guarded

    @api.constrains("repair_route", "external_provider_id", "pm_type", "symptom")
    def _check_route(self):
        for rec in self:
            if rec.repair_route == "external" and not rec.external_provider_id:
                raise ValidationError("%s: name the external provider." % rec.name)


# ---------------------------------------------------------------------------
# Loss, theft and damage (FR-EAM-040/041, BRU-EAM-12, AUT-EAM-13/14)
# ---------------------------------------------------------------------------
RECHARGE_STAMPS = {
    "recharge_hr_decision",
    "recharge_hr_decided_by_id",
    "recharge_hr_decided_on",
    "recharge_hr_note",
    "recharge_requested_on",
}
LOSS_STAMPS = {
    "state",
    "reported_by_id",
    "reported_on",
    "custodian_at_loss_id",
    "value_impact",
    "decided_by_id",
    "decided_on",
    "decision_note",
    "repair_job_id",
}


class FixEquipmentLoss(models.Model):
    _name = "fix.equipment.loss"
    _description = "Equipment Loss / Damage Report"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "occurred_on desc, id desc"

    name = fields.Char(required=True, default="New", copy=False)
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(
        related="equipment_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="equipment_id.operating_unit_id", store=True, index=True, string="Operating Unit"
    )
    kind = fields.Selection(
        [("lost", "Lost"), ("stolen", "Stolen"), ("damaged", "Damaged")],
        required=True,
        default="lost",
    )
    occurred_on = fields.Date(required=True, default=lambda self: _today(self.env))
    circumstances = fields.Text(required=True)
    police_report_ref = fields.Char(string="Police Report (GD) Ref")
    evidence_file = fields.Binary(string="Evidence", attachment=True, copy=False)
    evidence_filename = fields.Char(copy=False)
    reported_by_id = fields.Many2one("res.users", string="Reported By", readonly=True)
    reported_on = fields.Datetime(readonly=True)
    custodian_at_loss_id = fields.Many2one("hr.employee", string="Custodian at Loss", readonly=True)
    currency_id = fields.Many2one(related="equipment_id.currency_id")
    value_impact = fields.Monetary(currency_field="currency_id", readonly=True)
    recharge_employee_id = fields.Many2one("hr.employee", string="Recharge To")
    recharge_amount = fields.Monetary(currency_field="currency_id")
    # A07 ERP audit (2026-11-20) M45-05 / decision D9: a recharge is recovered
    # only on an HR-approved recovery decision; M56 deducts it within the
    # statutory limit HR records (S6 consumes equipment.recharge_requested).
    recharge_hr_decision = fields.Selection(
        [("approved", "Approved by HR"), ("rejected", "Rejected by HR")],
        string="HR Recovery Decision",
        readonly=True,
        copy=False,
    )
    recharge_hr_decided_by_id = fields.Many2one(
        "res.users", string="HR Decision By", readonly=True, copy=False
    )
    recharge_hr_decided_on = fields.Datetime(string="HR Decision On", readonly=True, copy=False)
    recharge_hr_note = fields.Text(string="HR Decision Note", readonly=True, copy=False)
    recharge_requested_on = fields.Datetime(
        string="Recharge Sent to Payroll",
        readonly=True,
        copy=False,
        help="When the approved recharge was handed to M52/M56 (once).",
    )
    state = fields.Selection(
        [
            ("reported", "Reported"),
            ("recovered", "Recovered"),
            ("repair", "Sent to Repair"),
            ("writeoff_requested", "Write-Off Requested"),
            ("written_off", "Written Off"),
        ],
        required=True,
        default="reported",
        tracking=True,
    )
    decision_note = fields.Text(readonly=True)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_on = fields.Datetime(readonly=True)
    repair_job_id = fields.Many2one("fix.equipment.pm", string="Repair Job", readonly=True)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | LOSS_STAMPS | RECHARGE_STAMPS
        if self:
            guarded |= {"equipment_id", "kind", "occurred_on"}
        if any(rec.recharge_hr_decision for rec in self):
            # HR decided on this employee and this amount: pinned
            guarded |= {"recharge_employee_id", "recharge_amount"}
        if any(rec.state != "reported" for rec in self):
            guarded |= {
                "circumstances",
                "police_report_ref",
                "evidence_file",
                "evidence_filename",
                "recharge_employee_id",
                "recharge_amount",
            }
        return guarded

    @api.constrains("recharge_amount", "recharge_employee_id")
    def _check_recharge(self):
        for rec in self:
            if rec.recharge_amount < 0:
                raise ValidationError("A recharge cannot be negative.")
            if rec.recharge_amount and not rec.recharge_employee_id:
                raise ValidationError("Name the employee the recharge is made to.")
            if rec.value_impact and rec.recharge_amount > rec.value_impact:
                raise ValidationError(
                    "The recharge (%.2f) exceeds the item's value (%.2f)."
                    % (rec.recharge_amount, rec.value_impact)
                )

    @api.model_create_multi
    def create(self, vals_list):
        today = _today(self.env)
        Equipment = self.env["fix.equipment"].sudo()
        for vals in vals_list:
            equipment = Equipment.browse(vals.get("equipment_id") or [])
            if not equipment:
                continue
            if equipment.operational_status == "retired":
                raise UserError("%s is retired: there is nothing to report." % equipment.name)
            occurred = fields.Date.to_date(vals.get("occurred_on")) or today
            if occurred > today:
                raise UserError("A loss cannot be dated in the future (%s)." % occurred)
            if self.sudo().search_count(
                [("equipment_id", "=", equipment.id), ("state", "in", OPEN_LOSS)]
            ):
                raise UserError(
                    "%s already has an open loss / damage report: decide it first." % equipment.name
                )
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.loss") or "ELOS/New"
                )
        records = super().create(vals_list)
        Issue = self.env["fix.equipment.issue"].sudo()
        Hold = self.env["fix.equipment.oos"]._guarded()
        for rec in records:
            equipment = rec.equipment_id.sudo()
            custodian = (
                Issue.search(
                    [("equipment_id", "=", equipment.id), ("state", "=", "issued")], limit=1
                ).custodian_id
                or equipment.custodian_id
            )
            rec.sudo()._guarded().write(
                {
                    "reported_by_id": self.env.uid,
                    "reported_on": fields.Datetime.now(),
                    "custodian_at_loss_id": custodian.id or False,
                    # D10: the write-off basis (M49 NBV when capitalised)
                    "value_impact": equipment._m45_writeoff_basis()[0],
                }
            )
            if rec.kind == "damaged":
                Hold.create(
                    {
                        "equipment_id": equipment.id,
                        "reason": "Damage reported (%s): %s" % (rec.name, rec.circumstances[:200]),
                        "hold_type": "damaged",
                    }
                )
            else:
                equipment._m45_sync_status()
            payload = {
                "equipment": equipment.code,
                "loss": rec.name,
                "kind": rec.kind,
                "custodian": custodian.name or None,
                "custodian_id": custodian.id or None,
                "value": equipment.acquisition_cost or 0.0,
            }
            # two literal event types: the registry scanner cannot resolve one
            # composed at run time (FF-28 registry guard)
            if rec.kind == "damaged":
                publish(self.env, "equipment.damaged", "fix.equipment.loss", rec.id, payload)
            else:
                publish(self.env, "equipment.lost", "fix.equipment.loss", rec.id, payload)
        return records

    def _m45_decide(self, state, note=None, **extra):
        vals = {
            "state": state,
            "decided_by_id": self.env.uid,
            "decided_on": fields.Datetime.now(),
            **extra,
        }
        if note:
            vals["decision_note"] = note
        self._guarded().write(vals)

    def _m45_check_not_pending(self):
        for rec in self:
            if rec.equipment_id.sudo().approval_state == "pending":
                raise UserError(
                    "The write-off of %s is waiting for approval: recall that request first."
                    % rec.equipment_id.name
                )

    def action_recover(self, note=None):
        """A lost or stolen item was found: it returns to the store."""
        m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), "Recording a lost item as found")
        self._m45_check_not_pending()
        for rec in self:
            if rec.kind == "damaged" or rec.state not in OPEN_LOSS:
                raise UserError("Only an open lost or stolen report can be recovered.")
            where = (note or "").strip()
            if not where:
                raise UserError("State where %s was found." % rec.equipment_id.name)
            rec._m45_decide("recovered", where)
            rec.equipment_id._m45_sync_status()
            publish(
                self.env,
                "equipment.recovered",
                "fix.equipment.loss",
                rec.id,
                {"equipment": rec.equipment_id.sudo().code, "loss": rec.name, "found": where},
            )
        return True

    def action_send_to_repair(self):
        """A damaged item is repaired, not returned to stock (BRU-EAM-10): a
        corrective job is raised from the report."""
        m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), "Sending a damaged item to repair")
        for rec in self:
            if rec.kind != "damaged" or rec.state != "reported":
                raise UserError("Only an open damage report is sent to repair.")
            job = (
                self.env["fix.equipment.pm"]
                .sudo()
                .create(
                    {
                        "equipment_id": rec.equipment_id.id,
                        "pm_type": "corrective",
                        "symptom": (rec.circumstances or "")[:250],
                        "description": "Repair of the damage reported in %s" % rec.name,
                    }
                )
            )
            rec._m45_decide("repair", "Corrective job %s raised." % job.name, repair_job_id=job.id)
        return True

    def action_hr_decide_recharge(self, decision="approved", note=None):
        """D9: HR approves or rejects the recovery of the recharge from the
        employee. Not the person who reported the loss, nor the employee
        recharged. An approved recharge reaches payroll once the write-off is
        approved (or at once if it already is)."""
        m45_require_role(self.env, ROLE_HR, "Deciding a staff recharge")
        if decision not in ("approved", "rejected"):
            raise UserError("The HR decision is approved or rejected.")
        text = note.strip() if isinstance(note, str) else ""
        for rec in self:
            if not (rec.recharge_employee_id and rec.recharge_amount > 0):
                raise UserError("%s proposes no recharge to decide." % rec.name)
            if rec.recharge_hr_decision:
                raise UserError("HR has already decided the recharge of %s." % rec.name)
            if rec.state in ("recovered",):
                raise UserError("%s was recovered: there is nothing to recharge." % rec.name)
            if not self.env.su:
                if rec.reported_by_id == self.env.user:
                    raise UserError(
                        "Segregation of duties: you reported %s, so another HR manager "
                        "decides its recharge." % rec.name
                    )
                if rec.recharge_employee_id.user_id == self.env.user:
                    raise UserError("You cannot decide a recharge made to yourself.")
            if decision == "rejected" and not text:
                raise UserError("State why HR rejects the recharge of %s." % rec.name)
            rec._guarded().write(
                {
                    "recharge_hr_decision": decision,
                    "recharge_hr_decided_by_id": self.env.uid,
                    "recharge_hr_decided_on": fields.Datetime.now(),
                    "recharge_hr_note": text or False,
                }
            )
            rec.message_post(
                body="HR %s the recharge of BDT %.2f to %s.%s"
                % (
                    decision,
                    rec.recharge_amount,
                    rec.recharge_employee_id.name,
                    (" %s" % text) if text else "",
                )
            )
            rec._m45_publish_recharge()
        return True

    def action_hr_approve_recharge(self, note=None):
        """D9: HR approves the recovery (the P03 button)."""
        return self.action_hr_decide_recharge("approved", note)

    def action_hr_reject_recharge(self, note=None):
        """D9: HR rejects the recovery, with the reason (the P03 button)."""
        return self.action_hr_decide_recharge("rejected", note)

    def _m45_publish_recharge(self):
        """equipment.recharge_requested, once, only for an HR-approved recharge
        on an approved write-off (D9). Carries what payroll / AR need."""
        for rec in self:
            if not (
                rec.state == "written_off"
                and rec.recharge_hr_decision == "approved"
                and rec.recharge_employee_id
                and rec.recharge_amount > 0
                and not rec.recharge_requested_on
            ):
                continue
            equipment = rec.equipment_id.sudo()
            rec.sudo()._guarded().write({"recharge_requested_on": fields.Datetime.now()})
            publish(
                self.env,
                "equipment.recharge_requested",
                "fix.equipment.loss",
                rec.id,
                {
                    "equipment": equipment.code,
                    "loss": rec.name,
                    "employee_id": rec.recharge_employee_id.id,
                    "employee": rec.recharge_employee_id.name,
                    "amount": rec.recharge_amount,
                    "currency": rec.currency_id.name or "BDT",
                    "hr_approved_by_id": rec.recharge_hr_decided_by_id.id,
                    "hr_approved_on": str(rec.recharge_hr_decided_on),
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id or None,
                    "value_impact": rec.value_impact or 0.0,
                    "kind": rec.kind,
                },
            )

    def action_request_writeoff(self):
        """Ask for the write-off within the authority matrix; the reporter of
        the loss never approves it (BRU-EAM-11/12)."""
        self._m45_check_not_pending()
        for rec in self:
            if rec.state not in ("reported", "repair", "writeoff_requested"):
                raise UserError("%s is decided already." % rec.name)
            reason = "%s (%s, %s): %s" % (
                dict(rec._fields["kind"].selection)[rec.kind],
                rec.name,
                rec.occurred_on,
                rec.circumstances,
            )
            rec.equipment_id.action_request_approval(justification=reason)
            rec._guarded().write({"state": "writeoff_requested"})
        return True


# ---------------------------------------------------------------------------
# Physical verification run (FR-EAM-038/039, AUT-EAM-12)
# ---------------------------------------------------------------------------
AUDIT_STAMPS = {
    "state",
    "reviewed_by_id",
    "reviewed_on",
    "expected_count",
    "found_count",
    "missing_count",
    "unexpected_count",
    "variance_value",
    "completed_by_id",
    "completed_on",
}


class FixEquipmentAudit(models.Model):
    _name = "fix.equipment.audit"
    _description = "Equipment Physical Verification Run"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "scheduled_for desc, id desc"

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True, index=True)
    scope = fields.Selection(
        [("all", "All equipment"), ("critical", "Measurement-critical only")],
        required=True,
        default="all",
    )
    scheduled_for = fields.Date(required=True, default=lambda self: _today(self.env))
    counter_id = fields.Many2one("hr.employee", string="Counter", required=True)
    line_ids = fields.One2many("fix.equipment.audit.line", "audit_id", string="Items Found")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("counting", "Counting"),
            # A07 ERP audit M45-16 / AC-14: a count with items not found is
            # final only once a reviewer accepts the discrepancy with a reason
            ("review", "Discrepancy Review"),
            ("done", "Done"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    discrepancy_reason = fields.Text(
        string="Discrepancy Reason",
        help="Why the items not found are missing (searched where, who was asked).",
    )
    reviewed_by_id = fields.Many2one("res.users", string="Discrepancy Approved By", readonly=True)
    reviewed_on = fields.Datetime(readonly=True)
    expected_count = fields.Integer(readonly=True)
    found_count = fields.Integer(readonly=True)
    missing_count = fields.Integer(readonly=True)
    unexpected_count = fields.Integer(string="Found Elsewhere-Registered", readonly=True)
    variance_value = fields.Monetary(currency_field="currency_id", readonly=True)
    completed_by_id = fields.Many2one("res.users", string="Completed By", readonly=True)
    completed_on = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | AUDIT_STAMPS | {"currency_id"}
        if self:
            guarded |= {"branch_id", "scope", "company_id"}
        if any(rec.state in ("review", "done") for rec in self):
            guarded |= {"scheduled_for", "counter_id", "line_ids"}
        if any(rec.state == "done" for rec in self):
            guarded |= {"discrepancy_reason"}
        return guarded

    @api.model_create_multi
    def create(self, vals_list):
        m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), "Scheduling a physical verification")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.audit") or "EAUD/New"
                )
        return super().create(vals_list)

    def _m45_expected(self):
        """What the register says is in the branch store: items out on issue or
        in transit are accounted for by their custody, not by this count."""
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("branch_id", "=", self.branch_id.id),
            ("operational_status", "in", ("available", "out_of_service", "missing")),
        ]
        if self.scope == "critical":
            domain.append(("measurement_critical", "=", True))
        items = self.env["fix.equipment"].sudo().search(domain)
        moving = (
            self.env["fix.equipment.transfer"]
            .sudo()
            .search([("equipment_id", "in", items.ids), ("state", "=", "dispatched")])
            .equipment_id
        )
        return items - moving

    def action_start(self):
        m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), "Starting a physical verification")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s has started already." % rec.name)
            rec._guarded().write({"state": "counting"})
        return True

    def _m45_check_counter_sod(self):
        """FR-EAM-038 / §13: the store keeper does not count their own store.
        Refused: the person who scheduled the count, the register custodian of
        any item of the branch, and an Equipment Custodian assigned to it."""
        for rec in self:
            counter = rec.counter_id.sudo()
            counter_user = counter.user_id
            if counter_user and counter_user == rec.create_uid:
                raise UserError(
                    "Segregation of duties: %s scheduled this count, so someone else counts."
                    % counter.name
                )
            held = (
                self.env["fix.equipment"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", rec.company_id.id),
                        ("branch_id", "=", rec.branch_id.id),
                        ("custodian_id", "=", counter.id),
                        ("operational_status", "!=", "retired"),
                    ],
                    limit=1,
                )
            )
            if held:
                raise UserError(
                    "Segregation of duties: %s is the custodian of %s, so another person "
                    "counts this branch." % (counter.name, held.name)
                )
            if (
                counter_user
                and "branch_id" in counter._fields
                and counter.branch_id == rec.branch_id
                and counter_user.has_group(ROLE_CUSTODIAN)
                and not counter_user.has_group(ROLE_QM)
            ):
                raise UserError(
                    "Segregation of duties: %s keeps the store of %s, so another person "
                    "counts it." % (counter.name, rec.branch_id.name)
                )

    def action_complete(self):
        """Close the count. It is blind: the counter scanned what was found, and
        every item the register expects but nobody found is recorded missing.
        The counter closes their own count and may not hold any of the items
        counted (SOD: the store keeper does not count their own store).

        A07 ERP audit M45-16: a count that did not find everything goes to
        Discrepancy Review; a reviewer other than the counter and the scheduler
        accepts it with a reason (action_approve_count) before the items are
        recorded missing."""
        for rec in self:
            if rec.state != "counting":
                raise UserError(
                    "%s is %s: only a count in progress (Start Count) is completed."
                    % (rec.name, dict(rec._fields["state"].selection)[rec.state])
                )
            expected = rec._m45_expected()
            if not self.env.su:
                counter_user = rec.counter_id.sudo().user_id
                if counter_user != self.env.user:
                    raise UserError(
                        "Only the counter (%s) closes this count: the person who counted "
                        "signs for it." % rec.counter_id.name
                    )
                rec._m45_check_counter_sod()
            found = rec.line_ids.equipment_id
            missing = expected - found
            if missing:
                rec._guarded().write(
                    {
                        "state": "review",
                        "expected_count": len(expected),
                        "found_count": len(found & expected),
                        "missing_count": len(missing),
                        "unexpected_count": len(found - expected),
                        "variance_value": sum(m._m45_writeoff_basis()[0] for m in missing),
                    }
                )
                rec.message_post(
                    body="Count closed by the counter with %d item(s) not found (%s): waiting "
                    "for the discrepancy review."
                    % (len(missing), ", ".join(missing.mapped("code")))
                )
                continue
            rec._m45_finalise(expected, found)
        return True

    def action_approve_count(self, reason=None):
        """AC-14: the discrepancy is accepted, with its reason, by a store keeper
        or Quality Manager who neither counted nor scheduled the count; the
        items not found are then recorded missing."""
        m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), "Approving a count discrepancy")
        text = reason.strip() if isinstance(reason, str) else ""
        for rec in self:
            if rec.state != "review":
                raise UserError("%s has no discrepancy waiting for review." % rec.name)
            if not self.env.su and self.env.user in (
                rec.counter_id.sudo().user_id | rec.create_uid
            ):
                raise UserError(
                    "Segregation of duties: you counted or scheduled %s, so another person "
                    "approves its discrepancy." % rec.name
                )
            if text:
                rec.write({"discrepancy_reason": text})
            if not (rec.discrepancy_reason or "").strip():
                raise UserError("State why the items of %s were not found." % rec.name)
            rec._guarded().write(
                {"reviewed_by_id": self.env.uid, "reviewed_on": fields.Datetime.now()}
            )
            rec._m45_finalise(rec._m45_expected(), rec.line_ids.equipment_id)
        return True

    def _m45_finalise(self, expected, found):
        """Record each verification (as the count run) and close the count."""
        self.ensure_one()
        rec = self
        Verification = self.env["fix.equipment.verification"].sudo()
        today = _today(self.env)
        missing = expected - found
        for item in expected | found:
            line = rec.line_ids.filtered(lambda line, e=item: line.equipment_id == e)[:1]
            Verification.create(
                {
                    "equipment_id": item.id,
                    "campaign_ref": rec.name,
                    "verified_on": today,
                    "found": item in found,
                    "location": (line.found_location or rec.branch_id.name or "")
                    if item in found
                    else False,
                    "condition": line.condition or False,
                    "verifier_id": rec.counter_id.id,
                }
            )
        rec._guarded().write(
            {
                "state": "done",
                "expected_count": len(expected),
                "found_count": len(found & expected),
                "missing_count": len(missing),
                "unexpected_count": len(found - expected),
                "variance_value": sum(m._m45_writeoff_basis()[0] for m in missing),
                "completed_by_id": self.env.uid,
                "completed_on": fields.Datetime.now(),
            }
        )
        publish(
            self.env,
            "equipment.audit_completed",
            "fix.equipment.audit",
            rec.id,
            {
                "branch": rec.branch_id.name,
                "expected": rec.expected_count,
                "found": rec.found_count,
                "missing": rec.missing_count,
                "variance": rec.variance_value,
            },
        )


class FixEquipmentAuditLine(models.Model):
    _name = "fix.equipment.audit.line"
    _description = "Equipment Count Line"
    _order = "audit_id, id"

    audit_id = fields.Many2one("fix.equipment.audit", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="audit_id.company_id", store=True, index=True)
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment Found", required=True, ondelete="restrict"
    )
    # M45-16 blind count: the counter scans the tag (or types the code / serial)
    # instead of picking from the register list
    scanned_code = fields.Char(string="Scanned Tag / Code / Serial")
    found_location = fields.Char(string="Found At")
    condition = fields.Char()

    _audit_equipment_unique = models.Constraint(
        "UNIQUE (audit_id, equipment_id)", "An item is counted once per verification."
    )

    def _m45_check_open(self, audits):
        if not self.env.su and any(a.state in ("review", "done") for a in audits):
            # M45-16: closed by the counter, the count is what the reviewer judges
            raise UserError("A closed verification is final: its count cannot change.")

    @api.model_create_multi
    def create(self, vals_list):
        audits = self.env["fix.equipment.audit"].browse([v.get("audit_id") for v in vals_list])
        self._m45_check_open(audits)
        Equipment = self.env["fix.equipment"].sudo()
        for vals in vals_list:
            code = (vals.get("scanned_code") or "").strip()
            if code and not vals.get("equipment_id"):
                audit = self.env["fix.equipment.audit"].sudo().browse(vals.get("audit_id"))
                company = audit.company_id.id or self.env.company.id
                item = Equipment.search(
                    [
                        ("company_id", "=", company),
                        "|",
                        "|",
                        ("asset_tag", "=ilike", code),
                        ("code", "=ilike", code),
                        ("serial_no", "=ilike", code),
                    ],
                    limit=2,
                )
                if len(item) != 1:
                    raise UserError(
                        "%s identifies %s registered item(s): scan the asset tag."
                        % (code, "no" if not item else "more than one")
                    )
                vals["equipment_id"] = item.id
        return super().create(vals_list)

    def write(self, vals):
        self._m45_check_open(self.audit_id)
        return super().write(vals)

    def unlink(self):
        self._m45_check_open(self.audit_id)
        return super().unlink()


# ---------------------------------------------------------------------------
# Retirement and disposal (FR-EAM-042/043, BRU-EAM-16, AUT-EAM-15/16)
# ---------------------------------------------------------------------------
RETIREMENT_STAMPS = {"state", "requested_by_id", "disposed_by_id", "disposed_on"}
DISPOSAL_ROUTES = [
    ("ewaste", "E-waste (M18)"),
    ("resale", "Resale"),
    ("scrap", "Scrap"),
    ("return_supplier", "Return to Supplier"),
]


class FixEquipmentRetirement(models.Model):
    _name = "fix.equipment.retirement"
    _description = "Equipment Retirement & Disposal"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", copy=False)
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(
        related="equipment_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="equipment_id.operating_unit_id", store=True, index=True, string="Operating Unit"
    )
    basis = fields.Selection(
        [
            ("age", "Age / end of life"),
            ("repair_cost", "Repair cost history"),
            ("calibration_failure", "Calibration failure history"),
            ("beyond_repair", "Beyond economic repair"),
            ("obsolete", "Obsolete"),
        ],
        required=True,
    )
    justification = fields.Text(required=True)
    replacement_required = fields.Boolean(string="Replacement Needed")
    replacement_note = fields.Char(string="Replacement Justification (M16)")
    data_bearing = fields.Boolean(related="equipment_id.data_bearing")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Approval Requested"),
            ("approved", "Retired"),
            ("disposed", "Disposed"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    disposal_route = fields.Selection(DISPOSAL_ROUTES)
    erasure_certificate_ref = fields.Char(string="M06 Erasure Certificate")
    disposal_ref = fields.Char(string="E-Waste Batch / Sale Reference")
    # A07 ERP audit M45-06 / D10: the sale proceeds M49 books the gain or loss
    # against (and M51 output VAT on); S6 consumes equipment.disposed
    currency_id = fields.Many2one(related="equipment_id.currency_id", string="Currency")
    sale_amount = fields.Monetary(currency_field="currency_id", string="Sale Proceeds")
    buyer_partner_id = fields.Many2one("res.partner", string="Buyer")
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True)
    disposed_by_id = fields.Many2one("res.users", string="Disposed By", readonly=True)
    disposed_on = fields.Date(readonly=True)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | RETIREMENT_STAMPS
        if self:
            guarded |= {"equipment_id"}
        if any(rec.state != "draft" for rec in self):
            guarded |= {"basis", "justification", "replacement_required", "replacement_note"}
        if any(rec.state == "disposed" for rec in self):
            guarded |= {
                "disposal_route",
                "erasure_certificate_ref",
                "disposal_ref",
                "sale_amount",
                "buyer_partner_id",
            }
        return guarded

    @api.constrains("sale_amount")
    def _check_sale_amount(self):
        for rec in self:
            if (rec.sale_amount or 0.0) < 0:
                raise ValidationError("Sale proceeds cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), "Recommending a retirement")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.retirement") or "ERET/New"
                )
            if self.sudo().search_count(
                [
                    ("equipment_id", "=", vals.get("equipment_id")),
                    ("state", "in", ("draft", "requested", "approved")),
                ]
            ):
                raise UserError("This item already has an open retirement record.")
        records = super().create(vals_list)
        for rec in records:
            # an item written off already (a loss) goes straight to disposal
            if rec.equipment_id.sudo().operational_status == "retired":
                rec._guarded().write({"state": "approved"})
        return records

    def action_request(self):
        """Ask for the retirement: the equipment's write-off approval decides it
        within the authority matrix (BRU-EAM-11)."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s has been requested already." % rec.name)
            basis = dict(rec._fields["basis"].selection)[rec.basis]
            rec.equipment_id.action_request_approval(
                justification="Retirement (%s, %s): %s" % (basis, rec.name, rec.justification)
            )
            rec._guarded().write({"state": "requested", "requested_by_id": self.env.uid})
        return True

    def action_dispose(self):
        """Record the disposal. A data-bearing item does not leave without its
        M06 erasure certificate (BRU-EAM-16, AUT-EAM-15)."""
        m45_require_role(self.env, (ROLE_QM,), "Disposing of retired equipment")
        for rec in self:
            equipment = rec.equipment_id.sudo()
            if rec.state != "approved" or equipment.operational_status != "retired":
                raise UserError(
                    "%s is not retired yet: its retirement must be approved first." % equipment.name
                )
            if not rec.disposal_route:
                raise UserError("Choose the disposal route of %s." % equipment.name)
            if rec.data_bearing and not (rec.erasure_certificate_ref or "").strip():
                raise UserError(
                    "%s holds data: it may not leave the company before M06 certifies its "
                    "erasure (BRU-EAM-16). Record the erasure certificate first." % equipment.name
                )
            if rec.disposal_route in ("ewaste", "resale") and not (rec.disposal_ref or "").strip():
                raise UserError(
                    "Record the e-waste batch or sale reference for %s." % equipment.name
                )
            if rec.disposal_route == "resale" and not (
                rec.buyer_partner_id and (rec.sale_amount or 0.0) > 0.0
            ):
                raise UserError(
                    "A resale of %s records the buyer and the sale proceeds: M49 books the "
                    "gain or loss against them." % equipment.name
                )
            rec._guarded().write(
                {
                    "state": "disposed",
                    "disposed_by_id": self.env.uid,
                    "disposed_on": _today(self.env),
                }
            )
            publish(
                self.env,
                "equipment.disposed",
                "fix.equipment.retirement",
                rec.id,
                {
                    "equipment": equipment.code,
                    "route": rec.disposal_route,
                    "reference": rec.disposal_ref or None,
                    "erasure_certificate": rec.erasure_certificate_ref or None,
                    "fixed_asset_id": equipment.fixed_asset_id.id
                    if "fixed_asset_id" in equipment._fields
                    else None,
                    # M45-06: the facts S6 books the disposal from
                    "sale_amount": rec.sale_amount or 0.0,
                    "buyer_partner_id": rec.buyer_partner_id.id or None,
                    "currency": rec.currency_id.name or "BDT",
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id or None,
                    "book_value": equipment._m45_writeoff_basis()[0],
                },
            )
        return True


# A QC result verifies conformity: only a calibration-controlled instrument
# may produce one (FR-EAM-026, BRU-EAM-02/15).
class FixEquipmentUsageConformity(models.Model):
    _inherit = "fix.equipment.usage"

    @api.model_create_multi
    def create(self, vals_list):
        Equipment = self.env["fix.equipment"].sudo()
        for vals in vals_list:
            if vals.get("qc_result") in ("pass", "fail"):
                equipment = Equipment.browse(vals.get("equipment_id") or [])
                if equipment and not equipment.measurement_critical:
                    raise UserError(
                        "%s is not a measurement-critical instrument (its class is outside "
                        "calibration control), so it cannot produce a QC result. Use a "
                        "calibrated instrument." % equipment.name
                    )
                # A07 ERP audit M45-24 / BRU-EAM-05: certified by a provider
                # without accreditation, it is restricted to non-conformity work
                if equipment and equipment._m45_latest_calibration().non_accredited:
                    raise UserError(
                        "%s holds a certificate from a provider that is not accredited: it is "
                        "restricted to non-conformity work and cannot produce a QC result."
                        % equipment.name
                    )
        return super().create(vals_list)
