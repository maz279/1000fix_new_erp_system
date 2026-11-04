# fix_equipment — M45: test equipment + the deferred calibration (P08-M08).
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

# A07 P1 (2026-11-04) D7: the spec's M45 roles (§13). The Quality Manager owns
# calibration, fitness and the impact assessment (R32); the Calibration
# Technician records calibrations; the Equipment Custodian is the branch store
# keeper (R18) who registers, transfers and condition-checks items. The groups
# ship with the dev admin only: appointing people is decision B1.
ROLE_QM = "cd_equipment_register.group_quality_manager"
ROLE_CALIBRATION = "cd_equipment_register.group_calibration_technician"
ROLE_CUSTODIAN = "cd_equipment_register.group_equipment_custodian"

# A pass, or an adjustment that left every point within tolerance, certifies.
CERTIFYING_RESULTS = ("pass", "adjusted")

# Business switches (A07 P1). Each is off by default because turning it on
# before decision B1 (appointing the role holders) would stop live work:
# - only a Calibration Technician / Quality Manager records a calibration;
PARAM_CALIBRATION_ROLE = "cd_equipment_register.calibration_requires_role"
# - a calibration certifies only once a second person has accepted it.
PARAM_USAGE_DECISION = "cd_equipment_register.usage_decision_required"
# An instrument with no calibration profile may not be certified for longer
# than this many months by a typed next-due (probe 09: 100 years). The spec
# leaves the interval per instrument class open (Q-05); 24 months is a
# plausibility ceiling, not a calibration interval. Business to confirm (B2).
PARAM_MAX_INTERVAL = "cd_equipment_register.max_calibration_interval_months"
MAX_INTERVAL_DEFAULT = 24
# AUT-EAM-02: alerts at 60, 30, 15 and 7 days before the due date.
DUE_ALERT_DAYS = (60, 30, 15, 7)
# what a Calibration Technician may write on a profile: the change request
PROFILE_REQUEST_FIELDS = {"proposed_interval_months", "interval_change_reason"}


def m45_param_on(env, key) -> bool:
    raw = env["ir.config_parameter"].sudo().get_param(key)
    return str(raw or "").strip().lower() in ("1", "true", "yes")


def m45_has_role(env, *xmlids) -> bool:
    return env.su or any(env.user.has_group(x) for x in xmlids)


def m45_require_role(env, xmlids, what):
    """Refuse a non-superuser without one of the roles (A07 P1 D7)."""
    if m45_has_role(env, *xmlids):
        return
    names = []
    for xmlid in xmlids:
        group = env.ref(xmlid, raise_if_not_found=False)
        names.append(group.sudo().name if group else xmlid)
    raise UserError("%s needs the %s role." % (what, " or ".join(names)))


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
        selection_add=[
            ("equipment_writeoff", "Equipment Write-Off / Retirement"),
            # A07 P2 (2026-11-04) BRU-EAM-13: an interval change is approved
            ("calibration_interval", "Calibration Interval Change"),
        ],
        ondelete={"equipment_writeoff": "cascade", "calibration_interval": "cascade"},
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
            ("rejected", "Rejected at Usage Decision"),
            ("pending", "Awaiting Usage Decision"),
            ("overdue", "Overdue"),
            ("current", "Current"),
        ],
        compute="_compute_calibration",
        string="Calibration Status",
        help="From the LATEST calibration only (by date, then record): current = it "
        "passed and its next-due is not past.",
    )
    # A07 P2 (2026-11-04) FR-EAM-019: what "calibrated" means for this
    # instrument: interval, measurement points and tolerance bands.
    calibration_profile_ids = fields.One2many(
        "fix.calibration.profile", "equipment_id", string="Calibration Profiles"
    )
    calibration_profile_id = fields.Many2one(
        "fix.calibration.profile",
        compute="_compute_calibration_profile",
        string="Calibration Profile",
    )
    # A07 P1 (2026-11-04) FR-EAM-039 / AUT-EAM-13: an item not found at a
    # physical verification is missing until a later count finds it.
    missing_verification_id = fields.Many2one(
        "fix.equipment.verification",
        string="Missing Since Verification",
        readonly=True,
        copy=False,
    )
    # AUT-EAM-02 bookkeeping for the nightly job: the smallest alert horizon
    # already sent for the current due date, so each alert goes once.
    calibration_alert_due = fields.Date(readonly=True, copy=False)
    calibration_alert_days = fields.Integer(readonly=True, copy=False)

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
            # A07 P1: set by the verification and the nightly job only
            "missing_verification_id",
            "calibration_alert_due",
            "calibration_alert_days",
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
        "calibration_ids.decision_state",
    )
    def _compute_calibration(self):
        # A07 P1: the business day (Asia/Dhaka), not the server's UTC date: the
        # midnight job runs at 00:05 Dhaka, still "yesterday" in UTC
        today = fields.Date.context_today(self)
        # A07 P2: with the switch on, a calibration certifies only once a
        # second person has accepted it (the usage decision)
        decision_required = m45_param_on(self.env, PARAM_USAGE_DECISION)
        for rec in self:
            latest = rec._m45_latest_calibration()
            rec.last_calibration = latest.calibrated_on if latest else False
            certifies = latest.result in CERTIFYING_RESULTS and latest.decision_state != "rejected"
            # a failed calibration certifies nothing, so it gives no due date
            rec.next_calibration = latest.next_due if certifies else False
            if not latest:
                state = "never"
            elif latest.result not in CERTIFYING_RESULTS:
                state = "failed"
            elif latest.decision_state == "rejected":
                state = "rejected"
            elif latest.next_due < today:
                state = "overdue"
            elif decision_required and latest.decision_state != "accepted":
                state = "pending"
            else:
                state = "current"
            rec.calibration_state = state
            rec.calibration_overdue = state == "overdue"

    def _compute_calibration_profile(self):
        for rec in self:
            rec.calibration_profile_id = rec.sudo().calibration_profile_ids[:1].with_env(self.env)

    @api.constrains("code", "company_id")
    def _check_unique_code(self):
        """A07 P1 (2026-11-04) M45-13, FR-EAM-001: the equipment code is the
        permanent ID; live fix_dev holds E2E-EQ-001 twice. Compared trimmed and
        case-insensitively within the company. Rows already duplicated stay as
        they are until one is renamed; a new duplicate is refused."""
        for rec in self:
            code = (rec.code or "").strip()
            if not code:
                continue
            dupes = (
                self.sudo()
                .with_context(active_test=False)
                .search(
                    [
                        ("id", "!=", rec.id),
                        ("company_id", "=", rec.company_id.id),
                        ("code", "ilike", code),
                    ]
                )
                .filtered(lambda r, key=code.lower: (r.code or "").strip().lower() == key())
            )
            if dupes:
                raise ValidationError(
                    "Equipment code %s is already used by %s: an equipment code is "
                    "unique within the company." % (code, dupes[0].name)
                )

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
        if state == "rejected":
            return (
                "The latest calibration of %s was rejected at its usage decision: it "
                "certifies nothing until a new calibration is accepted" % rec.name
            )
        if state == "pending":
            return (
                "The latest calibration of %s awaits its usage decision: a Quality "
                "Manager other than the person who recorded it must accept it first" % rec.name
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
            # A07 P1: a missing item is written off through the same approval
            # (spec §8.1 Lost -> Retired, within the authority matrix)
            if equipment.operational_status not in ("available", "out_of_service", "missing"):
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
            # A07 P1 (2026-11-04) AUT-EAM-14: M49 disposal accounting consumes it
            publish(
                self.env,
                "equipment.written_off",
                "fix.equipment",
                rec.id,
                {
                    "equipment": rec.code,
                    "approver": self.env.user.name,
                    "approver_id": self.env.user.id,
                    "value": rec.acquisition_cost or 0.0,
                    "basis": rec.retirement_reason or "",
                    "was_missing": bool(rec.missing_verification_id),
                },
            )
        return True

    # ---- A07 P1 (2026-11-04): status and the nightly job ----------------------
    def _m45_sync_status(self):
        """Write the status the open holds and custody give (retired stays)."""
        for rec in self:
            equipment = rec.sudo()
            if equipment.operational_status == "retired":
                continue
            status = equipment._m45_released_status()
            if status != equipment.operational_status:
                rec._guarded().write({"operational_status": status})

    def _m45_has_calibration_hold(self):
        self.ensure_one()
        return bool(
            self.env["fix.equipment.oos"]
            .sudo()
            .search_count(
                [
                    ("equipment_id", "=", self.id),
                    ("state", "=", "open"),
                    ("hold_type", "=", "calibration"),
                ]
            )
        )

    def _m45_open_calibration_hold(self, reason, calibration=None):
        """Put the instrument out of service for a calibration reason, once:
        an open calibration hold already covers it."""
        self.ensure_one()
        equipment = self.sudo()
        if equipment.operational_status == "retired":
            return self.env["fix.equipment.oos"]
        Hold = self.env["fix.equipment.oos"].sudo()
        held = Hold.search(
            [
                ("equipment_id", "=", equipment.id),
                ("state", "=", "open"),
                ("hold_type", "=", "calibration"),
            ],
            limit=1,
        )
        if held:
            return held
        vals = {"equipment_id": equipment.id, "reason": reason, "hold_type": "calibration"}
        if calibration:
            # unfit since the calibration that found it so
            vals.update({"calibration_id": calibration.id, "started_on": calibration.calibrated_on})
        return Hold.create(vals)

    @api.model
    def cron_calibration_status(self):
        """Nightly (AUT-EAM-03, BRU-EAM-01): an instrument whose latest
        calibration is past due, failed or rejected goes out of service, with
        no override; and the 60/30/15/7-day due alerts go out (AUT-EAM-02).
        Idempotent: an open calibration hold is not opened twice and each alert
        is sent once per due date."""
        today = fields.Date.context_today(self)
        Equipment = self.sudo().with_context(active_test=False)
        held = 0
        for rec in Equipment.search([("operational_status", "!=", "retired")]):
            state = rec.calibration_state
            if state in ("overdue", "failed", "rejected"):
                reason = {
                    "overdue": "Calibration due %s has passed (automatic, AUT-EAM-03)"
                    % rec._m45_latest_calibration().next_due,
                    "failed": "Latest calibration failed (automatic)",
                    "rejected": "Latest calibration rejected at its usage decision (automatic)",
                }[state]
                if not rec._m45_has_calibration_hold():
                    rec._m45_open_calibration_hold(reason)
                    held += 1
                continue
            if state != "current" or not rec.next_calibration:
                continue
            days = (rec.next_calibration - today).days
            due_horizons = [d for d in DUE_ALERT_DAYS if days <= d]
            if not due_horizons:
                continue
            horizon = min(due_horizons)
            if rec.calibration_alert_due == rec.next_calibration and (
                rec.calibration_alert_days and rec.calibration_alert_days <= horizon
            ):
                continue
            rec._guarded().write(
                {"calibration_alert_due": rec.next_calibration, "calibration_alert_days": horizon}
            )
            publish(
                self.env,
                "equipment.calibration_due",
                "fix.equipment",
                rec.id,
                {
                    "equipment": rec.code,
                    "due_date": str(rec.next_calibration),
                    "branch": rec.branch_id.name or "",
                    "days_remaining": days,
                    "horizon_days": horizon,
                },
            )
        return held


class FixCalibration(models.Model):
    """The M31-deferred capability, delivered (P08-M08-T02)."""

    _name = "fix.calibration"
    _description = "Calibration"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "calibrated_on desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    # A07 P2 (2026-11-04) BRU-EAM-06: "cascade" let deleting the register row
    # delete every certificate; a calibrated item is never deleted.
    equipment_id = fields.Many2one("fix.equipment", required=True, ondelete="restrict", index=True)
    calibrated_on = fields.Date(required=True, default=fields.Date.today)
    standard_ref = fields.Char(
        string="Standard Reference",
        help="The traceable standard (ISO 9001 7.1.5: measurement traceability)",
        required=True,
    )
    # A07 audit (2026-11-03) M45-1: the default was "pass", so a calibration
    # saved without a result certified the instrument. The result is chosen.
    # A07 P2 (2026-11-04) FR-EAM-022: with readings it is derived from them
    # (T-10), and "adjusted" = adjusted, with every point within tolerance.
    result = fields.Selection(
        [("pass", "Pass"), ("adjusted", "Adjusted and Passed"), ("fail", "Fail")], required=True
    )
    next_due = fields.Date(
        required=True,
        help="With a calibration profile it is calibrated-on + the profile interval when "
        "left empty, and may not exceed it.",
    )
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
    # ---- A07 P2 (2026-11-04): profile, readings, usage decision, impact ------
    profile_id = fields.Many2one(
        "fix.calibration.profile",
        string="Calibration Profile",
        readonly=True,
        ondelete="restrict",
        help="The instrument's profile when it was calibrated: its interval and "
        "tolerance bands were applied to this record.",
    )
    reading_ids = fields.One2many(
        "fix.calibration.reading", "calibration_id", string="As-Found / As-Left Readings"
    )
    as_found_out_of_tolerance = fields.Boolean(
        string="As-Found Out of Tolerance",
        readonly=True,
        help="Derived from the readings: at least one point was found outside its "
        "tolerance band. This raises the retrospective impact assessment.",
    )
    decision_state = fields.Selection(
        [
            ("pending", "Awaiting Usage Decision"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            ("na", "Not Applicable (failed)"),
        ],
        string="Usage Decision",
        default="pending",
        required=True,
        readonly=True,
        copy=False,
        help="A Quality Manager other than the person who recorded the calibration "
        "accepts or rejects it (SOD-07).",
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Datetime(string="Decided On", readonly=True, copy=False)
    decision_note = fields.Text(
        string="Usage Decision Note",
        help="Why the calibration is accepted or rejected. Required to reject.",
    )
    impact_id = fields.Many2one(
        "fix.calibration.impact", string="Impact Assessment", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        # A07 audit (2026-11-03) M45-2: a plain user rewrote a FAIL to PASS and
        # extended next_due to revive an overdue instrument (ORM and P03).
        # A07 P2 (2026-11-04) T-03: the record is insert-only. After create
        # nothing changes except the usage decision (through its actions) and
        # its note while the decision is pending.
        guarded = super()._fix_guarded_fields() | {
            "superseded_by_id",
            "profile_id",
            "as_found_out_of_tolerance",
            "decision_state",
            "decided_by_id",
            "decided_on",
            "impact_id",
        }
        if self:
            guarded |= CALIBRATION_EVIDENCE | {"notes", "reading_ids"}
            if any(rec.decision_state != "pending" for rec in self):
                guarded |= {"decision_note"}
        return guarded

    # ---- create-time evidence rules ---------------------------------------
    def _m45_max_interval_months(self) -> int:
        raw = self.env["ir.config_parameter"].sudo().get_param(PARAM_MAX_INTERVAL)
        try:
            return int(raw) if raw not in (None, False, "") else MAX_INTERVAL_DEFAULT
        except (TypeError, ValueError):
            return MAX_INTERVAL_DEFAULT

    def _m45_check_new_evidence(self, vals_list):
        """A07 audit (2026-11-03) M45-2: any user recorded a PASS with no
        certificate or performer, dated in the future. Superuser code (seeds,
        data loads) stays trusted."""
        today = fields.Date.context_today(self)
        if m45_param_on(self.env, PARAM_CALIBRATION_ROLE):
            m45_require_role(self.env, (ROLE_CALIBRATION, ROLE_QM), "Recording a calibration")
        for vals in vals_list:
            on = fields.Date.to_date(vals.get("calibrated_on")) or today
            if on > today:
                raise UserError(
                    "A calibration cannot be dated in the future (%s): record it once it "
                    "has been performed." % on
                )
            if vals.get("result") in CERTIFYING_RESULTS:
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

    def _m45_prepare_vals(self, vals_list):
        """A07 P2 (2026-11-04) FR-EAM-019/022, T-10. Applied to every caller:
        - the instrument's profile is stamped on the record; its interval sets
          next-due when none is given and caps a typed one (no profile: the
          plausibility ceiling, probe 09/10: 100-year and 3-years-back);
        - readings take their tolerance band from the profile point, never
          from what was typed, and the result is derived from them.
        A superuser (seed, migration) may load history beyond the cap."""
        su = self.env.su
        Equipment = self.env["fix.equipment"].sudo()
        Point = self.env["fix.calibration.profile.point"].sudo()
        today = fields.Date.context_today(self)
        for vals in vals_list:
            equipment = Equipment.browse(vals.get("equipment_id") or []).exists()
            profile = equipment.calibration_profile_ids[:1] if equipment else None
            if not su or "profile_id" not in vals:
                vals["profile_id"] = profile.id if profile else False
            on = fields.Date.to_date(vals.get("calibrated_on")) or today
            if profile:
                ceiling = on + relativedelta(months=profile.interval_months)
                basis = "its calibration profile interval of %d months" % profile.interval_months
                if not vals.get("next_due"):
                    vals["next_due"] = ceiling
            else:
                months = self._m45_max_interval_months()
                ceiling = on + relativedelta(months=months) if months > 0 else None
                basis = (
                    "%d months, the longest validity allowed without a calibration "
                    "profile (%s)" % (months, PARAM_MAX_INTERVAL)
                )
            due = fields.Date.to_date(vals.get("next_due"))
            if not su and due and ceiling and due > ceiling:
                raise UserError(
                    "Next-due %s is beyond %s from the calibration on %s (latest allowed "
                    "%s). Record the interval in the instrument's calibration profile; "
                    "an interval change is approved by the Quality Manager."
                    % (due, basis, on, ceiling)
                )
            readings = [cmd[2] for cmd in vals.get("reading_ids") or [] if cmd and cmd[0] == 0]
            if readings:
                vals.update(self._m45_evaluate_readings(readings, profile, Point, su, vals))
            elif not su and profile and profile.point_ids and not profile.verification_only:
                raise UserError(
                    "Record the as-found reading of each measurement point of %s's "
                    "calibration profile: the result is derived from them." % equipment.name
                )
            elif not su and vals.get("result") == "adjusted":
                raise UserError(
                    "Adjusted and Passed is derived from as-found / as-left readings; record "
                    "the readings."
                )
            if vals.get("result") == "fail":
                vals["decision_state"] = "na"

    def _m45_evaluate_readings(self, readings, profile, Point, su, vals):
        """Fill each reading's band from its profile point and derive the
        result: every point found in tolerance = pass (adjusted if any point
        was adjusted and left in tolerance); a point found out of tolerance
        and not adjusted back within it = fail."""
        points = profile.point_ids if profile else Point.browse()
        seen = set()
        found_out = left_out = adjusted = False
        for rv in readings:
            point = Point.browse(rv.get("point_id") or []).exists()
            if not su:
                if not point or point not in points:
                    raise UserError(
                        "Each reading names a measurement point of the instrument's "
                        "calibration profile: tolerance bands are never typed (T-10)."
                    )
                if point.id in seen:
                    raise UserError("Measurement point %s is read twice." % point.name)
            if point:
                seen.add(point.id)
                if not su or "tolerance_low" not in rv:
                    rv.update(
                        {
                            "name": point.name,
                            "unit": point.unit,
                            "nominal": point.nominal,
                            "tolerance_low": point.tolerance_low,
                            "tolerance_high": point.tolerance_high,
                        }
                    )
            low, high = rv.get("tolerance_low") or 0.0, rv.get("tolerance_high") or 0.0
            found_in = low <= (rv.get("as_found") or 0.0) <= high
            if not found_in:
                found_out = True
            if rv.get("adjusted"):
                adjusted = True
                if not low <= (rv.get("as_left") or 0.0) <= high:
                    left_out = True
            elif not found_in:
                left_out = True
        if not su and points and len(seen) != len(points):
            missing = ", ".join((points - Point.browse(list(seen))).mapped("name"))
            raise UserError("Record the as-found reading of every measurement point: %s." % missing)
        derived = "fail" if left_out else ("adjusted" if adjusted else "pass")
        typed = vals.get("result")
        if not su and typed and typed != derived:
            raise UserError(
                "The readings give the result %s, not %s: the result is derived from the "
                "readings against the profile's tolerance bands (T-10)."
                % (dict(self._fields["result"].selection)[derived], typed)
            )
        return {"result": derived, "as_found_out_of_tolerance": found_out}

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
            if old.result == "fail" and rec.result in CERTIFYING_RESULTS:
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
            # the system-set fields are refused when typed, before the create
            # below (which sets them itself) obtains the guard token
            typed = self._fix_guarded_fields() & {k for vals in vals_list for k in vals}
            defaults = {"decision_state": "pending"}
            forged = sorted(
                name
                for name in typed
                for vals in vals_list
                if name in vals and (vals[name] or False) != defaults.get(name, False)
            )
            if forged:
                self._fix_guard_refuse(forged)
            self._m45_check_new_evidence(vals_list)
        self._m45_prepare_vals(vals_list)
        # the readings are created with their calibration, never afterwards
        recs = super(FixCalibration, self._guarded().with_context(m45_calibration_create=True))
        recs = recs.create(vals_list).with_env(self.env)
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
        recs._m45_after_record()
        return recs

    def unlink(self):
        """BRU-EAM-06: a calibration certificate is never deleted by a user.
        The ACL already grants no unlink; this holds even if one is added."""
        if not self.env.su:
            self.check_access("unlink")
            raise UserError("A calibration record is retained evidence and cannot be deleted.")
        return super().unlink()

    @api.constrains("calibrated_on", "next_due")
    def _check_due_after(self):
        for rec in self:
            if rec.next_due < rec.calibrated_on:
                raise UserError("Next-due precedes the calibration date")

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    # ---- A07 P2: what a failure sets in motion -----------------------------
    def _m45_after_record(self):
        """BRU-EAM-03 / AUT-EAM-05: an as-found out-of-tolerance result raises
        the retrospective impact assessment (every measurement since the last
        pass), a quality event and an NCR; a failed latest calibration puts
        the instrument out of service (spec §8.1)."""
        for rec in self:
            if rec.result == "fail" or rec.as_found_out_of_tolerance:
                rec._m45_raise_impact()
            equipment = rec.equipment_id.sudo()
            if rec.result == "fail" and equipment._m45_latest_calibration() == rec.sudo():
                equipment.with_env(self.env)._m45_open_calibration_hold(
                    "Failed calibration on %s (%s)" % (rec.calibrated_on, rec.display_name),
                    calibration=rec,
                )

    def _m45_last_good_before(self):
        """The last certifying calibration before this one: the start of the
        suspect window."""
        self.ensure_one()
        key = (self.calibrated_on, self.id)
        prior = self.equipment_id.sudo().calibration_ids.filtered(
            lambda c: (
                c.id != self.id
                and not c.superseded_by_id
                and c.result in CERTIFYING_RESULTS
                and c.decision_state != "rejected"
                and (c.calibrated_on, c.id) < key
            )
        )
        return prior.sorted(lambda c: (c.calibrated_on, c.id))[-1:]

    def _m45_raise_impact(self):
        self.ensure_one()
        rec = self.sudo()
        last_good = rec._m45_last_good_before()
        since = last_good.calibrated_on if last_good else False
        domain = [("equipment_id", "=", rec.equipment_id.id), ("used_on", "<=", rec.calibrated_on)]
        if since:
            domain.append(("used_on", ">=", since))
        usages = self.env["fix.equipment.usage"].sudo().search(domain)
        impact = (
            self.env["fix.calibration.impact"]
            .sudo()
            .create(
                {
                    "calibration_id": rec.id,
                    "equipment_id": rec.equipment_id.id,
                    "last_good_calibration_id": last_good.id or False,
                    "period_from": since,
                    "period_to": rec.calibrated_on,
                    "usage_ids": [(6, 0, usages.ids)],
                }
            )
        )
        rec._guarded().write({"impact_id": impact.id})
        impact._m45_raise_ncr()
        readings_out = [
            {
                "point": r.name,
                "as_found": r.as_found,
                "low": r.tolerance_low,
                "high": r.tolerance_high,
            }
            for r in rec.reading_ids.filtered(lambda r: not r.in_tolerance_found)
        ]
        publish(
            self.env,
            "equipment.out_of_tolerance",
            "fix.calibration",
            rec.id,
            {
                "equipment": rec.equipment_id.code,
                "calibration_id": rec.id,
                "result": rec.result,
                "period_from": str(since) if since else None,
                "period_to": str(rec.calibrated_on),
                "readings_out": readings_out,
            },
        )
        publish(
            self.env,
            "equipment.impact_assessment_raised",
            "fix.calibration.impact",
            impact.id,
            {
                "impact": impact.name,
                "equipment": rec.equipment_id.code,
                "calibration_id": rec.id,
                "period_from": str(since) if since else None,
                "period_to": str(rec.calibrated_on),
                "affected_uses": len(usages),
                "job_refs": usages.mapped("job_ref"),
                "source_refs": [
                    {"model": u.source_model, "id": u.source_res_id}
                    for u in usages
                    if u.source_model
                ],
                "ncr": impact.ncr_ref or None,
            },
        )
        return impact

    # ---- A07 P2: the usage decision by a second person (SOD-07) -------------
    def _m45_check_decider(self):
        m45_require_role(self.env, (ROLE_QM,), "The usage decision on a calibration")
        for rec in self:
            if rec.decision_state != "pending":
                raise UserError(
                    "The usage decision on %s has already been taken." % rec.display_name
                )
            if rec.result not in CERTIFYING_RESULTS:
                raise UserError(
                    "A failed calibration certifies nothing: there is nothing to accept."
                )
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you recorded %s, so another Quality Manager takes "
                    "its usage decision." % rec.display_name
                )

    def _m45_decide(self, decision):
        for rec in self:
            rec._guarded().write(
                {
                    "decision_state": decision,
                    "decided_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Usage decision: %s by %s.%s"
                % (
                    dict(rec._fields["decision_state"].selection)[decision],
                    self.env.user.name,
                    (" %s" % rec.decision_note) if rec.decision_note else "",
                )
            )
            publish(
                self.env,
                "equipment.calibration_decided",
                "fix.calibration",
                rec.id,
                {
                    "equipment": rec.equipment_id.code,
                    "calibration_id": rec.id,
                    "decision": decision,
                    "decided_by_id": self.env.user.id,
                },
            )

    def action_accept_calibration(self):
        """Accept the calibration: the instrument is certified by it."""
        self._m45_check_decider()
        self._m45_decide("accepted")
        return True

    def action_reject_calibration(self):
        """Reject the calibration (e.g. certificate not traceable, provider not
        accredited): it certifies nothing and, as the latest, it puts the
        instrument out of service."""
        self._m45_check_decider()
        for rec in self:
            if not (rec.decision_note or "").strip():
                raise UserError(
                    "State why %s is rejected (Usage Decision Note)." % rec.display_name
                )
        self._m45_decide("rejected")
        for rec in self:
            equipment = rec.equipment_id.sudo()
            if equipment._m45_latest_calibration() == rec.sudo():
                equipment.with_env(self.env)._m45_open_calibration_hold(
                    "Calibration of %s rejected at its usage decision: %s"
                    % (rec.calibrated_on, rec.decision_note.strip()),
                    calibration=rec,
                )
        return True


class FixCalibrationReading(models.Model):
    """A07 P2 (2026-11-04) FR-EAM-022: as-found / as-left per measurement point.
    Insert-only: created with its calibration, never edited or deleted."""

    _name = "fix.calibration.reading"
    _description = "Calibration Reading"
    _inherit = ["fix.guarded.mixin"]
    _order = "calibration_id, id"

    calibration_id = fields.Many2one(
        "fix.calibration", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="calibration_id.company_id", store=True, index=True)
    point_id = fields.Many2one(
        "fix.calibration.profile.point", string="Measurement Point", ondelete="restrict"
    )
    name = fields.Char(string="Point", required=True)
    unit = fields.Char()
    nominal = fields.Float(digits=(16, 6))
    tolerance_low = fields.Float(string="Lower Limit", digits=(16, 6))
    tolerance_high = fields.Float(string="Upper Limit", digits=(16, 6))
    as_found = fields.Float(string="As Found", digits=(16, 6))
    adjusted = fields.Boolean(help="The instrument was adjusted at this point.")
    as_left = fields.Float(string="As Left", digits=(16, 6))
    in_tolerance_found = fields.Boolean(
        compute="_compute_in_tolerance", store=True, string="Found In Tolerance"
    )
    in_tolerance_left = fields.Boolean(
        compute="_compute_in_tolerance", store=True, string="Left In Tolerance"
    )

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields()
        if self:
            guarded |= {
                "calibration_id",
                "point_id",
                "name",
                "unit",
                "nominal",
                "tolerance_low",
                "tolerance_high",
                "as_found",
                "adjusted",
                "as_left",
            }
        return guarded

    @api.depends("as_found", "as_left", "adjusted", "tolerance_low", "tolerance_high")
    def _compute_in_tolerance(self):
        for rec in self:
            low, high = rec.tolerance_low, rec.tolerance_high
            rec.in_tolerance_found = low <= rec.as_found <= high
            rec.in_tolerance_left = (
                low <= rec.as_left <= high if rec.adjusted else rec.in_tolerance_found
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and not self.env.context.get("m45_calibration_create"):
            raise UserError(
                "Readings are recorded with their calibration: record a new calibration "
                "(a correction names the record it corrects)."
            )
        return super().create(vals_list)

    def unlink(self):
        if not self.env.su:
            raise UserError("A calibration reading is retained evidence and cannot be deleted.")
        return super().unlink()


class FixCalibrationProfile(models.Model):
    """A07 P2 (2026-11-04) FR-EAM-019: per instrument, the calibration
    interval, the measurement points with their tolerance bands, the required
    traceability and provider type. The interval changes only through an
    approved request (BRU-EAM-13, FR-EAM-030)."""

    _name = "fix.calibration.profile"
    _description = "Calibration Profile"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "equipment_id"
    _rec_name = "equipment_id"

    _approval_domain = "calibration_interval"
    _approval_apply_method = "action_apply_interval_change"
    _approval_group = ROLE_QM
    _approval_routed = True

    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="equipment_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="equipment_id.operating_unit_id", store=True, index=True
    )
    interval_months = fields.Integer(
        string="Calibration Interval (months)",
        required=True,
        help="Next-due = calibrated-on + this interval. Set when the profile is created; "
        "changed only by an approved interval change.",
    )
    point_ids = fields.One2many(
        "fix.calibration.profile.point", "profile_id", string="Measurement Points"
    )
    required_traceability = fields.Char(
        help="e.g. ISO/IEC 17025 accredited laboratory, traceable to BSTI national standards"
    )
    provider_requirement = fields.Selection(
        [("accredited", "Accredited provider only"), ("any", "Any provider")],
        default="accredited",
        required=True,
    )
    verification_only = fields.Boolean(
        help="Verified, not calibrated: no measurement points are read."
    )
    proposed_interval_months = fields.Integer(string="Proposed Interval (months)", copy=False)
    interval_change_reason = fields.Text(
        string="Interval Change Justification",
        copy=False,
        help="The documented stability history that supports the change (BRU-EAM-13).",
    )

    _equipment_unique = models.Constraint(
        "UNIQUE (equipment_id)", "An instrument has one calibration profile"
    )
    _interval_positive = models.Constraint(
        "CHECK (interval_months > 0)", "The calibration interval must be at least one month"
    )

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields()
        if self:
            guarded |= {"equipment_id", "interval_months"}
        if any(rec.approval_state == "pending" for rec in self):
            # the request is pinned to what was asked for
            guarded |= {"proposed_interval_months", "interval_change_reason"}
        return guarded

    @api.model_create_multi
    def create(self, vals_list):
        m45_require_role(self.env, (ROLE_QM,), "A calibration profile")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_has_token():
            if set(vals) - PROFILE_REQUEST_FIELDS:
                m45_require_role(self.env, (ROLE_QM,), "Changing a calibration profile")
            else:
                m45_require_role(
                    self.env, (ROLE_CALIBRATION, ROLE_QM), "Proposing a calibration interval"
                )
        return super().write(vals)

    def action_request_approval(self, justification=None):
        """Ask for the proposed interval. Routed to a Quality Manager who is
        neither the requester nor the profile's creator."""
        m45_require_role(self.env, (ROLE_CALIBRATION, ROLE_QM), "Requesting an interval change")
        for rec in self:
            new = rec.proposed_interval_months
            if not new or new <= 0:
                raise UserError("Propose the new interval (months) first.")
            if new == rec.interval_months:
                raise UserError("The proposed interval equals the current one.")
            reason = (justification or rec.interval_change_reason or "").strip()
            if not reason:
                raise UserError(
                    "Justify the interval change with the instrument's stability history "
                    "(BRU-EAM-13)."
                )
            if not (rec.interval_change_reason or "").strip():
                rec.write({"interval_change_reason": reason})
            super(FixCalibrationProfile, rec).action_request_approval(justification=reason)
        return True

    def action_apply_interval_change(self):
        """The approver's decision, from the inbox task (engine-routed)."""
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for rec in self:
            if not self.env.su:
                if not authority.has_group(ROLE_QM):
                    raise UserError("Approving an interval change needs the Quality Manager role.")
                # spec §13: whoever calibrates the instrument does not approve
                # a change to its interval
                performers = rec.equipment_id.sudo().calibration_ids.mapped("create_uid")
                if acting & performers:
                    raise UserError(
                        "Segregation of duties: you recorded a calibration of %s, so you "
                        "cannot approve a change to its interval." % rec.equipment_id.name
                    )
            old = rec.interval_months
            new = rec.proposed_interval_months
            rec._guarded().write({"interval_months": new, "proposed_interval_months": 0})
            rec.message_post(
                body="Calibration interval changed from %d to %d months, approved by %s."
                % (old, new, self.env.user.name)
            )
            publish(
                self.env,
                "equipment.calibration_interval_changed",
                "fix.calibration.profile",
                rec.id,
                {
                    "equipment": rec.equipment_id.code,
                    "old_months": old,
                    "new_months": new,
                    "approved_by_id": self.env.user.id,
                },
            )
        return True


class FixCalibrationProfilePoint(models.Model):
    _name = "fix.calibration.profile.point"
    _description = "Calibration Measurement Point"
    _order = "profile_id, sequence, id"

    profile_id = fields.Many2one(
        "fix.calibration.profile", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="profile_id.company_id", store=True, index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Measurement Point", required=True, help="e.g. DC V 10 V range")
    unit = fields.Char()
    nominal = fields.Float(digits=(16, 6))
    tolerance_low = fields.Float(string="Lower Limit", digits=(16, 6), required=True)
    tolerance_high = fields.Float(string="Upper Limit", digits=(16, 6), required=True)

    @api.constrains("tolerance_low", "tolerance_high")
    def _check_band(self):
        for rec in self:
            if rec.tolerance_high < rec.tolerance_low:
                raise ValidationError("The upper limit of %s is below its lower limit." % rec.name)

    @api.model_create_multi
    def create(self, vals_list):
        m45_require_role(self.env, (ROLE_QM,), "A calibration measurement point")
        return super().create(vals_list)

    def write(self, vals):
        m45_require_role(self.env, (ROLE_QM,), "Changing a tolerance band")
        return super().write(vals)

    def unlink(self):
        m45_require_role(self.env, (ROLE_QM,), "Removing a measurement point")
        return super().unlink()


IMPACT_DISPOSITIONS = [
    ("valid", "Results remain valid (documented)"),
    ("retested", "Affected results re-tested"),
    ("recalled", "Affected jobs / claims recalled"),
]


class FixCalibrationImpact(models.Model):
    """A07 P2 (2026-11-04) BRU-EAM-03, FR-EAM-027, ISO 9001 7.1.5.2: the
    retrospective impact assessment. Raised by the system when a calibration
    finds the instrument out of tolerance; lists every recorded use since the
    last good calibration; closed by a Quality Manager who did not record the
    failing calibration."""

    _name = "fix.calibration.impact"
    _description = "Calibration Impact Assessment"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    calibration_id = fields.Many2one(
        "fix.calibration", string="Calibration", required=True, ondelete="restrict", index=True
    )
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(related="equipment_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="equipment_id.operating_unit_id", store=True, index=True
    )
    last_good_calibration_id = fields.Many2one(
        "fix.calibration", string="Last Good Calibration", ondelete="restrict"
    )
    period_from = fields.Date(
        string="Suspect From", help="The last good calibration; empty = since first use."
    )
    period_to = fields.Date(string="Suspect To", help="The out-of-tolerance calibration.")
    usage_ids = fields.Many2many("fix.equipment.usage", string="Affected Uses")
    affected_uses = fields.Integer(
        compute="_compute_affected", store=True, string="Affected Use Count"
    )
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], default="open", required=True
    )
    disposition = fields.Selection(IMPACT_DISPOSITIONS)
    disposition_note = fields.Text(help="What was checked and decided for the affected uses.")
    decided_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)
    decided_on = fields.Datetime(string="Closed On", readonly=True)
    # fix.ncr lives in cd_qms_process, which is not a dependency: a soft link
    ncr_res_id = fields.Integer(string="NCR id", readonly=True)
    ncr_ref = fields.Char(string="NCR", readonly=True)

    _calibration_unique = models.Constraint(
        "UNIQUE (calibration_id)", "One impact assessment per calibration"
    )

    @api.depends("usage_ids")
    def _compute_affected(self):
        for rec in self:
            rec.affected_uses = len(rec.usage_ids)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "name",
            "calibration_id",
            "equipment_id",
            "last_good_calibration_id",
            "period_from",
            "period_to",
            "usage_ids",
            "state",
            "decided_by_id",
            "decided_on",
            "ncr_res_id",
            "ncr_ref",
        }
        if any(rec.state == "closed" for rec in self):
            guarded |= {"disposition", "disposition_note"}
        return guarded

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError(
                "An impact assessment is raised by the system when a calibration finds "
                "the instrument out of tolerance."
            )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.calibration.impact") or "EIMP/New"
                )
        return super().create(vals_list)

    def unlink(self):
        if not self.env.su:
            raise UserError("An impact assessment is retained evidence and cannot be deleted.")
        return super().unlink()

    def _m45_raise_ncr(self):
        """The quality event to M23: an NCR when the QMS module is installed
        (it is not a dependency of M45; the event carries the rest)."""
        for rec in self:
            if "fix.ncr" not in self.env:
                continue
            ncr = (
                self.env["fix.ncr"]
                .sudo()
                .create(
                    {
                        "source": "qc",
                        "severity": "major",
                        "company_id": rec.company_id.id or self.env.company.id,
                        "description": "Test instrument %s found out of tolerance at calibration "
                        "%s on %s. Impact assessment %s lists %d use(s) since %s."
                        % (
                            rec.equipment_id.code,
                            rec.calibration_id.display_name,
                            rec.period_to,
                            rec.name,
                            rec.affected_uses,
                            rec.period_from or "first use",
                        ),
                    }
                )
            )
            rec.sudo()._guarded().write({"ncr_res_id": ncr.id, "ncr_ref": ncr.name})

    def action_close_impact(self):
        """The disposition of the affected measurements, decided by a Quality
        Manager who did not record the failing calibration."""
        m45_require_role(self.env, (ROLE_QM,), "Closing an impact assessment")
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is already closed." % rec.name)
            if not rec.disposition or not (rec.disposition_note or "").strip():
                raise UserError(
                    "Record the disposition and what was checked before closing %s." % rec.name
                )
            if not self.env.su and rec.calibration_id.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you recorded the failing calibration, so another "
                    "Quality Manager closes %s." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "closed",
                    "decided_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "equipment.impact_assessment_closed",
                "fix.calibration.impact",
                rec.id,
                {
                    "impact": rec.name,
                    "equipment": rec.equipment_id.code,
                    "disposition": rec.disposition,
                    "affected_uses": rec.affected_uses,
                    "decided_by_id": self.env.user.id,
                    "ncr": rec.ncr_ref or None,
                },
            )
        return True
