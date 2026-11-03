# fix_equipment — M45: test equipment + the deferred calibration (P08-M08).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

# A07 audit (2026-11-03) M45-6, spec §9 BRU-EAM-11/12: a write-off or retirement
# is decided within the authority matrix, on the amount written off: up to
# BDT 25,000 the Quality Manager, above that the CFO. No Quality Manager group
# exists yet (P1), so the rungs map to the DOFA tier groups by label:
#   Quality Manager -> tier_2 "Branch / Operations Manager" (the manager-level
#                      tier; tier_1 is a team lead / supervisor);
#   CFO             -> tier_4 "CFO / CCO / COO".
# One ladder, here; a fix.dofa.ladder ruling for fix.equipment overrides it
# without code.
WRITEOFF_DOFA_THRESHOLDS = [
    (25000.0, "tier_2"),
    (float("inf"), "tier_4"),
]

# A retired item is terminal: its register facts are frozen for users.
RETIRED_FROZEN = {
    "code",
    "name",
    "category",
    "acquisition_cost",
    "retirement_reason",
    "maintenance_equipment_id",
    "company_id",
    "operating_unit_id",
}

# A07 audit (2026-11-03) M45-2: a calibration is evidence. After create only
# the notes may change; a correction is a new row that supersedes this one.
CALIBRATION_EVIDENCE = {
    "equipment_id",
    "calibrated_on",
    "standard_ref",
    "result",
    "next_due",
    "performed_by",
    "certificate_ref",
    "trace_no",
    "company_id",
    "operating_unit_id",
    "supersedes_id",
}


class FixApprovalMatrixEquipment(models.Model):
    """M45 decision domain on the DoA register (A07 audit 2026-11-03)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("equipment_writeoff", "Equipment Write-Off / Retirement")],
        ondelete={"equipment_writeoff": "cascade"},
    )


class FixEquipment(models.Model):
    _name = "fix.equipment"
    _description = "Test Equipment"
    # fix.dofa.mixin carries the routed engine (cd_workflow_engine extends it
    # with fix.approvable.mixin); listing the approvable mixin in front of it
    # here gives Python no consistent method order.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "code"

    # A07 audit (2026-11-03) M45-6: retirement was a plain write of
    # operational_status, by anyone, with no approval. It is now a write-off
    # request routed by the approval engine (M63) on the acquisition cost; the
    # approve method runs only from the approver's inbox task.
    _approval_domain = "equipment_writeoff"
    _approval_apply_method = "action_approve_writeoff"
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    category = fields.Char(
        string="Equipment Category", help="e.g. multimeter, thermal camera, OTP programmer"
    )
    maintenance_equipment_id = fields.Many2one(
        "maintenance.equipment",
        string="Maintenance Equipment",
        help="The Odoo maintenance link stays authoritative for work orders",
    )
    custodian_id = fields.Many2one("hr.employee", string="Custodian")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    calibration_ids = fields.One2many("fix.calibration", "equipment_id", string="Calibrations")
    last_calibration = fields.Date(compute="_compute_calibration", string="Last Calibration")
    next_calibration = fields.Date(compute="_compute_calibration", string="Next Calibration")
    calibration_overdue = fields.Boolean(
        compute="_compute_calibration", string="Calibration Overdue"
    )
    calibration_state = fields.Selection(
        [
            ("never", "Never Calibrated"),
            ("failed", "Failed"),
            ("overdue", "Overdue"),
            ("current", "Current"),
        ],
        compute="_compute_calibration",
        string="Calibration Status",
        help="From the LATEST calibration only (by date, then record): current = it "
        "passed and its next-due is not past.",
    )

    # ---- write-off / retirement (M45-6) -------------------------------------
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        readonly=True,
        default=lambda self: self.env.ref("base.BDT"),
        help="The write-off ladder is in BDT.",
    )
    acquisition_cost = fields.Monetary(
        currency_field="currency_id",
        string="Acquisition Cost",
        help="What the item cost. A write-off is approved on this amount (BRU-EAM-11); "
        "M45 holds no depreciation (BRU-EAM-19).",
    )
    retirement_reason = fields.Text(
        string="Write-Off Reason",
        help="Why the item is written off or retired. Required to request approval; "
        "it becomes the approval justification.",
    )
    retired_on = fields.Date(readonly=True, copy=False)
    retired_by_id = fields.Many2one(
        "res.users", string="Write-Off Approved By", readonly=True, copy=False
    )

    # ---- guard ----------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        # A07 audit (2026-11-03) M45-6/M45-7: operational_status was writable by
        # any user, so an item was retired, or an open out-of-service hold was
        # cleared, by a plain write. It changes only through issue, return,
        # out-of-service open/resolve and the approved write-off.
        guarded = super()._fix_guarded_fields() | {
            "operational_status",
            "retired_on",
            "retired_by_id",
            "currency_id",
        }
        if self:
            # M45-8: once registered, the branch and custodian move only on a
            # received transfer; a typed branch made the transfer decorative.
            guarded |= {"branch_id", "custodian_id"}
        if any(rec.approval_state in ("pending", "approved") for rec in self):
            # the approved terms are pinned: a change to them is refused while
            # the write-off is pending or once it is approved
            guarded |= {"acquisition_cost", "retirement_reason"}
        if any(rec.operational_status == "retired" for rec in self):
            guarded |= RETIRED_FROZEN
        return guarded

    # ---- DOFA -------------------------------------------------------------------
    def _dofa_thresholds(self):
        return WRITEOFF_DOFA_THRESHOLDS

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.acquisition_cost or 0.0

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (acquisition cost written off)" % self._dofa_amount()

    @api.depends("acquisition_cost")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _dofa_current_tier(self) -> str:
        """A write-off is never below the lowest rung of its ladder (BRU-EAM-11):
        the mixin reads a nil amount as tier 0, "nothing to approve"."""
        tier = super()._dofa_current_tier()
        if tier == "tier_0" and not (self.acquisition_cost or 0.0) > 0.0:
            return self._dofa_tier_for_amount(0.0)
        return tier

    # A07 audit (2026-11-03) M45-1: fitness was the max next_due of PASSING rows,
    # so a fail recorded after an earlier pass changed nothing, and an
    # instrument never calibrated (or whose only calibration failed) had no due
    # date and was "fit". The latest calibration now decides: a later fail
    # withdraws the earlier pass, and no calibration means no certificate.
    @api.depends(
        "calibration_ids.calibrated_on",
        "calibration_ids.next_due",
        "calibration_ids.result",
        "calibration_ids.superseded_by_id",
    )
    def _compute_calibration(self):
        today = fields.Date.today()
        for rec in self:
            latest = rec._m45_latest_calibration()
            rec.last_calibration = latest.calibrated_on if latest else False
            # a failed calibration certifies nothing, so it gives no due date
            rec.next_calibration = latest.next_due if latest.result == "pass" else False
            if not latest:
                state = "never"
            elif latest.result != "pass":
                state = "failed"
            elif latest.next_due < today:
                state = "overdue"
            else:
                state = "current"
            rec.calibration_state = state
            rec.calibration_overdue = state == "overdue"

    def _m45_latest_calibration(self):
        """The calibration that decides fitness: the latest by calibrated_on,
        then by record, among rows no correction has superseded. Read as
        superuser so the gate never depends on which calibration rows the
        acting user may see."""
        self.ensure_one()
        cals = self.sudo().calibration_ids.filtered(lambda c: not c.superseded_by_id)
        return cals.sorted(lambda c: (c.calibrated_on, c._origin.id or 0))[-1:]

    def _m45_calibration_problem(self):
        """The calibration half of fitness: why the latest calibration does
        not certify the instrument, or None."""
        self.ensure_one()
        rec = self.sudo()
        state = rec.calibration_state
        if state == "never":
            return (
                "%s has never been calibrated: there is no certificate, so it is not "
                "fit for use (ISO 9001 7.1.5)" % rec.name
            )
        if state == "failed":
            return (
                "%s failed its latest calibration (%s): it is not usable until it is "
                "recalibrated and passes" % (rec.name, rec.last_calibration)
            )
        if state == "overdue":
            return (
                "Calibration overdue on %s (due %s) — the instrument is not usable until "
                "recalibrated" % (rec.name, rec.next_calibration)
            )
        return None

    def _m45_fitness_problem(self, holder=None):
        """Why this instrument may not be used now, or None when it is fit.

        Fit = the latest calibration passed AND its next-due is not past AND
        the instrument is in service. `issued` counts as in service only for
        its holder: `holder` is the hr.employee recordset of the people using
        it (default: the acting user's employees); an instrument issued to
        someone else is in that person's custody, not on this bench."""
        self.ensure_one()
        rec = self.sudo()
        problem = rec._m45_calibration_problem()
        if problem:
            return problem
        status = rec.operational_status
        if status == "issued":
            # only server code passes a holder recordset; anything typed by an
            # RPC caller (P03 /p03/model/action kwargs) falls back to the actor
            if not isinstance(holder, models.BaseModel) or holder._name != "hr.employee":
                holder = self.env.user.sudo().employee_ids
            custodian = (
                self.env["fix.equipment.issue"]
                .sudo()
                .search([("equipment_id", "=", rec.id), ("state", "=", "issued")], limit=1)
                .custodian_id
            )
            if custodian and custodian in holder.sudo():
                return None
            return "%s is issued to %s: only its holder may use it" % (
                rec.name,
                custodian.name or "another custodian",
            )
        if status != "available":
            label = dict(rec._fields["operational_status"].selection).get(status, status)
            return "%s is %s and may not be used" % (rec.name, label)
        return None

    def action_assert_usable(self, holder=None):
        """ISO 9001 7.1.5: only a fit instrument is usable (see
        _m45_fitness_problem). Issue, usage capture and M31 QC call this."""
        for rec in self:
            problem = rec._m45_fitness_problem(holder=holder)
            if problem:
                raise UserError(problem)
        # Every instrument in the recordset is checked before declaring it usable.
        return True

    # ---- write-off / retirement (M45-6) -------------------------------------
    def _m45_check_retirable(self):
        """Only an item back in the store can be written off: not one out on
        issue or in transit, and not one already retired."""
        for rec in self:
            equipment = rec.sudo()
            if equipment.operational_status not in ("available", "out_of_service"):
                label = dict(equipment._fields["operational_status"].selection).get(
                    equipment.operational_status
                )
                raise UserError(
                    "%s is %s: only an available or out-of-service item can be written "
                    "off (return it first)" % (equipment.name, label.lower())
                )
            if (
                self.env["fix.equipment.transfer"]
                .sudo()
                .search_count([("equipment_id", "=", equipment.id), ("state", "=", "dispatched")])
            ):
                raise UserError(
                    "%s is in transit: confirm or cancel the transfer before writing it off"
                    % equipment.name
                )

    def action_request_approval(self, justification=None):
        """Request the write-off. The reason is the approval's justification;
        the engine routes it on the acquisition cost and never to the
        requester, the item's registrar or whoever last changed the cost."""
        for rec in self:
            rec._m45_check_retirable()
            reason = (justification or rec.retirement_reason or "").strip()
            if not reason:
                raise UserError(
                    "State why %s is written off (Write-Off Reason) before requesting "
                    "approval." % rec.name
                )
            if not (rec.acquisition_cost or 0.0) > 0.0:
                raise UserError(
                    "Record the acquisition cost of %s first: the write-off authority "
                    "(Quality Manager up to BDT 25,000, CFO above) is decided by it." % rec.name
                )
            if not (rec.retirement_reason or "").strip():
                rec.write({"retirement_reason": reason})
            super(FixEquipment, rec).action_request_approval(justification=reason)
        return True

    def action_approve_writeoff(self):
        """The approver's decision, run by the engine from the inbox task: the
        DOFA tier, segregation of duties and justification apply, then the
        item is retired."""
        for rec in self:
            rec._m45_check_retirable()
            requester = rec.approval_request_id.sudo().requested_by_id
            if not self.env.su and requester and requester in rec._dofa_acting_users():
                # BRU-EAM-12: the reporter may not approve the write-off
                raise UserError(
                    "Segregation of duties: you requested the write-off of %s and cannot "
                    "approve it." % rec.name
                )
            rec.action_dofa_approve()
            rec._dofa_assert_approved("Equipment write-off")
            rec._guarded().write(
                {
                    "operational_status": "retired",
                    "retired_on": fields.Date.context_today(self),
                    "retired_by_id": self.env.user.id,
                }
            )
            rec.message_post(
                body="Written off and retired (%s), approved by %s."
                % (rec._dofa_amount_label(), self.env.user.name)
            )
        return True


class FixCalibration(models.Model):
    """The M31-deferred capability, delivered (P08-M08-T02)."""

    _name = "fix.calibration"
    _description = "Calibration"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "calibrated_on desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    equipment_id = fields.Many2one("fix.equipment", required=True, ondelete="cascade", index=True)
    calibrated_on = fields.Date(required=True, default=fields.Date.today)
    standard_ref = fields.Char(
        string="Standard Reference",
        help="The traceable standard (ISO 9001 7.1.5: measurement traceability)",
        required=True,
    )
    # A07 audit (2026-11-03) M45-1: the default was "pass", so a calibration
    # saved without a result certified the instrument. The result is chosen.
    result = fields.Selection([("pass", "Pass"), ("fail", "Fail")], required=True)
    next_due = fields.Date(required=True)
    performed_by = fields.Char(string="Performed By")
    notes = fields.Text()
    supersedes_id = fields.Many2one(
        "fix.calibration",
        string="Corrects",
        ondelete="restrict",
        help="The calibration record this one corrects. The corrected record stays on "
        "file, marked superseded, and no longer decides fitness.",
    )
    superseded_by_id = fields.Many2one(
        "fix.calibration",
        string="Superseded By",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )

    def _fix_guarded_fields(self) -> set:
        # A07 audit (2026-11-03) M45-2: a plain user rewrote a FAIL to PASS and
        # extended next_due to revive an overdue instrument (ORM and P03).
        # After create, only the notes may change.
        guarded = super()._fix_guarded_fields() | {"superseded_by_id"}
        if self:
            guarded |= CALIBRATION_EVIDENCE
        return guarded

    def _m45_check_new_evidence(self, vals_list):
        """A07 audit (2026-11-03) M45-2: any user recorded a PASS with no
        certificate or performer, dated in the future. Superuser code (seeds,
        data loads) stays trusted."""
        today = fields.Date.context_today(self)
        for vals in vals_list:
            on = fields.Date.to_date(vals.get("calibrated_on")) or today
            if on > today:
                raise UserError(
                    "A calibration cannot be dated in the future (%s): record it once it "
                    "has been performed." % on
                )
            if vals.get("result") == "pass":
                missing = [
                    label
                    for key, label in (
                        ("certificate_ref", "the certificate reference"),
                        ("performed_by", "who performed it"),
                    )
                    if not (vals.get(key) or "").strip()
                ]
                if missing:
                    raise UserError(
                        "A passing calibration certifies the instrument, so it must name "
                        "%s." % " and ".join(missing)
                    )

    def _m45_link_supersession(self):
        """A correction is a new row: mark the row it corrects as superseded."""
        for rec in self.filtered("supersedes_id"):
            old = rec.supersedes_id.sudo()
            if old.equipment_id != rec.equipment_id:
                raise UserError(
                    "A correction must be for the same equipment as the record it corrects"
                )
            if old.superseded_by_id:
                raise UserError(
                    "Calibration of %s on %s is already superseded; correct the latest "
                    "record instead" % (old.equipment_id.name, old.calibrated_on)
                )
            if old.result == "fail" and rec.result == "pass":
                # the as-found fail is the evidence the retrospective impact
                # reads; a re-calibration that passes is a new record, not a
                # correction that erases the fail
                raise UserError(
                    "A failed calibration cannot be corrected into a pass. Recalibrate "
                    "and record the new passing calibration as its own record."
                )
            old.with_env(self.env)._guarded().write({"superseded_by_id": rec.id})

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            self._m45_check_new_evidence(vals_list)
        recs = super().create(vals_list)
        recs._m45_link_supersession()
        for rec in recs:
            publish(
                self.env,
                "equipment.calibration.recorded",
                "fix.calibration",
                rec.id,
                {
                    "equipment": rec.equipment_id.code,
                    "result": rec.result,
                    "next_due": str(rec.next_due),
                },
            )
            if rec.next_due < fields.Date.today():
                publish(
                    self.env,
                    "equipment.calibration.overdue",
                    "fix.calibration",
                    rec.id,
                    {"equipment": rec.equipment_id.code},
                )
        return recs

    @api.constrains("calibrated_on", "next_due")
    def _check_due_after(self):
        for rec in self:
            if rec.next_due < rec.calibrated_on:
                raise UserError("Next-due precedes the calibration date")

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
