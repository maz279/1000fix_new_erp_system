# cd_hr_core — exit, clearance and final settlement (A09 workflow audit M21-7,
# B1-B5, C1-C3, C5, P2 "exits").
#
# The audit settled an exit with a typed 9,999,999, wrote a draft exit to
# 'settled', had one HR Manager tick IT, Finance, HR and Assets, accepted 0
# days' notice, kept the contract active (the next payroll paid the leaver)
# and never revoked access. Here:
#
#   * the exit is confirmed against the statutory notice (s.26 employer, s.20
#     retrenchment, s.27 resignation via company settings); a shortfall needs
#     a treatment (pay in lieu or a waiver); a dismissal needs a decided
#     disciplinary case (s.23/24);
#   * each clearance tick has one owning role (IT, Finance, HR, Assets) and is
#     stamped with who ticked it; the subject and the exit's creator tick none;
#   * the settlement figure comes from payroll (I1 _fix_settlement_breakdown),
#     is pinned with its lines, routed to Finance (preparer excluded) and
#     re-computed at approval: a typed figure is never accepted;
#   * the s.30 / s.123(2) clock: due 30 working days after the last working
#     day, flagged by a cron when overdue;
#   * on the last working day the cron records the leaver (left_date,
#     employee.left: M29 deprovisions, the relay consumer archives the Odoo
#     login); settling ends the contract on that day (I3).
import json

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_hr_controls_common import (
    CLEAR_ASSETS,
    CLEAR_IT,
    FINANCE,
    OFFICER,
    RETRENCHMENT_NOTICE_DAYS,
    SETTLEMENT_WORKING_DAYS,
    TERMINATION_NOTICE_DAYS,
    add_working_days,
    digest,
)

TICKS = {
    "clearance_it": CLEAR_IT,
    "clearance_finance": FINANCE,
    "clearance_hr": OFFICER,
    "clearance_assets": CLEAR_ASSETS,
}
OPEN_STATES = ("draft", "notice", "cleared")
EXIT_TERMS = (
    "employee_id",
    "exit_type",
    "notice_date",
    "last_working_day",
    "notice_shortfall_treatment",
    "disciplinary_case_id",
)


class FixHrExitControls(models.Model):
    _name = "fix.hr.exit"
    _inherit = [
        "fix.hr.exit",
        "mail.thread",
        "mail.activity.mixin",
        "fix.people.approval.mixin",
        "fix.hr.control.mixin",
    ]

    # The settlement payment is prepared by payroll and approved by Finance.
    _approval_domain = "hr_exit"
    _approval_apply_method = "action_settle"
    _approval_group = FINANCE

    state = fields.Selection(
        selection_add=[("notice", "Notice Confirmed"), ("cleared",)],
        ondelete={"notice": "set default"},
    )
    exit_type = fields.Selection(
        selection_add=[
            ("retrenchment", "Retrenchment (s.20)"),
            ("dismissal", "Dismissal for Misconduct (s.23)"),
        ],
        ondelete={"retrenchment": "set default", "dismissal": "set default"},
    )
    contract_id = fields.Many2one(
        "fix.employment.contract", string="Contract", readonly=True, copy=False
    )
    notice_required_days = fields.Integer(
        compute="_compute_notice", string="Statutory Notice (days)"
    )
    notice_served_days = fields.Integer(compute="_compute_notice", string="Notice Served (days)")
    notice_shortfall_days = fields.Integer(compute="_compute_notice", string="Notice Shortfall")
    notice_basis = fields.Char(compute="_compute_notice", string="Statutory Basis")
    notice_shortfall_treatment = fields.Selection(
        [
            ("pay_in_lieu", "Wages in Lieu of Notice"),
            ("waived", "Waived by the Employer"),
        ],
        string="Notice Shortfall Treatment",
    )
    chief_inspector_notified_on = fields.Date(
        string="Chief Inspector / CBA Copy Sent On", help="s.20(2)(b): retrenchment notice copy"
    )
    disciplinary_case_id = fields.Many2one(
        "fix.hr.disciplinary.case", string="Disciplinary Case (dismissal)"
    )
    clearance_it_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    clearance_finance_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    clearance_hr_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    clearance_assets_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    settlement_lines = fields.Text(readonly=True, copy=False, help="Payroll's breakdown (JSON)")
    settlement_basis = fields.Char(readonly=True, copy=False)
    settlement_digest = fields.Char(readonly=True, copy=False)
    settlement_computed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    settlement_computed_at = fields.Datetime(readonly=True, copy=False)
    settled_on = fields.Date(readonly=True, copy=False)
    settlement_due_date = fields.Date(
        compute="_compute_settlement_due",
        store=True,
        string="Settlement Due (s.30 / s.123(2))",
        help="30 working days after the last working day",
    )
    settlement_overdue = fields.Boolean(readonly=True, copy=False)
    leaver_processed = fields.Boolean(readonly=True, copy=False)

    # ---- guard -------------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return (
            super()._fix_guarded_fields()
            | set(TICKS)
            | {"%s_by_id" % t for t in TICKS}
            | {
                "state",
                "contract_id",
                "settlement_amount",
                "settlement_lines",
                "settlement_basis",
                "settlement_digest",
                "settlement_computed_by_id",
                "settlement_computed_at",
                "settled_on",
                "settlement_overdue",
                "leaver_processed",
            }
        )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(EXIT_TERMS) | {"chief_inspector_notified_on"}
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = set(vals) & (set(EXIT_TERMS) | {"chief_inspector_notified_on"})
            for rec in self.filtered("id") if frozen else self.browse():
                if rec.state != "draft" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen
                ):
                    raise UserError(
                        "%s is confirmed: its terms (type, dates, notice) are frozen." % rec.name
                    )
        return super().write(vals)

    @api.constrains("employee_id", "state")
    def _check_one_open_exit(self):
        for rec in self.filtered(lambda r: r.state in OPEN_STATES):
            if self.sudo().search_count(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("state", "in", OPEN_STATES),
                    ("id", "!=", rec.id),
                ]
            ):
                raise ValidationError("%s already has an open exit." % rec.employee_id.name)

    @api.constrains("notice_date", "last_working_day")
    def _check_dates(self):
        for rec in self:
            if rec.notice_date and rec.last_working_day and rec.notice_date > rec.last_working_day:
                raise ValidationError("The notice date cannot be after the last working day.")

    # ---- notice (s.20, s.26, s.27) ---------------------------------------------------
    def _fix_active_contract(self):
        self.ensure_one()
        return (
            self.env["fix.employment.contract"]
            .sudo()
            .search(
                [("employee_id", "=", self.employee_id.id), ("state", "=", "active")],
                limit=1,
            )
        )

    @api.depends("exit_type", "notice_date", "last_working_day", "employee_id", "contract_id")
    def _compute_notice(self):
        for rec in self:
            contract = rec.contract_id or (rec._fix_active_contract() if rec.employee_id else None)
            permanent = bool(contract) and contract.contract_type == "permanent"
            company = rec.company_id or self.env.company
            required, basis = 0, "No statutory notice"
            if rec.exit_type == "termination":
                required = TERMINATION_NOTICE_DAYS["permanent" if permanent else "other"]
                basis = "BLA s.26 (employer termination, %s worker)" % (
                    "permanent" if permanent else "temporary"
                )
            elif rec.exit_type == "retrenchment":
                required, basis = RETRENCHMENT_NOTICE_DAYS, "BLA s.20(2)(a) (retrenchment)"
            elif rec.exit_type == "resignation":
                required = (
                    company.fix_hr_resign_notice_permanent_days
                    if permanent
                    else company.fix_hr_resign_notice_temporary_days
                )
                basis = "BLA s.27 (resignation; company setting)"
            elif rec.exit_type == "dismissal":
                basis = "BLA s.23 (dismissal after enquiry): no notice"
            elif rec.exit_type == "retirement":
                basis = "BLA s.28 (retirement)"
            elif rec.exit_type == "abandonment":
                basis = "BLA s.27(3A) (absence without leave)"
            served = (
                (rec.last_working_day - rec.notice_date).days
                if rec.notice_date and rec.last_working_day
                else 0
            )
            rec.notice_required_days = required
            rec.notice_served_days = max(served, 0)
            rec.notice_shortfall_days = max(required - max(served, 0), 0)
            rec.notice_basis = basis

    @api.depends("last_working_day", "company_id")
    def _compute_settlement_due(self):
        for rec in self:
            if not rec.last_working_day:
                rec.settlement_due_date = False
                continue
            calendar = (
                rec.employee_id.sudo().resource_calendar_id
                or (rec.company_id or self.env.company).resource_calendar_id
            )
            rec.settlement_due_date = add_working_days(
                self.env, rec.last_working_day, SETTLEMENT_WORKING_DAYS, calendar
            )

    def action_confirm_notice(self):
        """Confirm the exit against its statutory notice (draft -> notice)."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Confirm a draft exit.")
            rec._hr_require(OFFICER, "Confirming an exit")
            rec._hr_refuse_conflicted("confirm")
            if rec.notice_required_days and not rec.notice_date:
                raise UserError(
                    "%s requires %d days' notice (%s): enter the notice date."
                    % (rec.name, rec.notice_required_days, rec.notice_basis)
                )
            if rec.notice_shortfall_days and not rec.notice_shortfall_treatment:
                raise UserError(
                    "The notice is %d days short of the %d required (%s): record wages in "
                    "lieu of notice or the employer's waiver."
                    % (rec.notice_shortfall_days, rec.notice_required_days, rec.notice_basis)
                )
            if rec.notice_shortfall_treatment == "waived" and rec.exit_type in (
                "termination",
                "retrenchment",
            ):
                raise UserError(
                    "The employer cannot waive its own notice: pay wages in lieu (s.20/s.26)."
                )
            if rec.exit_type == "retirement":
                born = rec.employee_id.sudo().birthday
                if not born or born + relativedelta(years=60) > rec.last_working_day:
                    raise UserError(
                        "Retirement is on completing 60 years of age (BLA s.28): record the "
                        "date of birth, or use the exit type that applies."
                    )
            if rec.exit_type == "retrenchment" and not rec.chief_inspector_notified_on:
                raise UserError(
                    "Retrenchment: send the notice copy to the Chief Inspector and the CBA "
                    "(s.20(2)(b)) and record the date."
                )
            if rec.exit_type == "dismissal":
                case = rec.disciplinary_case_id
                if (
                    not case
                    or case.employee_id != rec.employee_id
                    or case.state != "decided"
                    or case.outcome != "dismissal"
                ):
                    raise UserError(
                        "A dismissal needs a disciplinary case for this employee decided "
                        "'dismissal' (BLA s.23/24)."
                    )
            rec._guarded().write({"state": "notice", "contract_id": rec._fix_active_contract().id})
            rec.message_post(
                body="Exit confirmed: %s; notice %d of %d days%s."
                % (
                    rec.notice_basis,
                    rec.notice_served_days,
                    rec.notice_required_days,
                    ", shortfall %s" % rec.notice_shortfall_treatment
                    if rec.notice_shortfall_days
                    else "",
                )
            )
        return True

    # ---- clearance: one owner per tick -----------------------------------------------
    def _fix_tick(self, tick):
        for rec in self:
            if rec.state != "notice":
                raise UserError("Clearance is ticked on a confirmed exit.")
            rec._hr_require(TICKS[tick], "This clearance")
            rec._hr_refuse_conflicted("clear")
            if (
                tick == "clearance_assets"
                and rec.employee_id.sudo().toolkit_custody_ref
                and not (rec.asset_return_receipt_no or rec.asset_return_receipt_file)
            ):
                raise UserError(
                    "Employee holds assigned toolkit custody (%s): Asset Return Receipt reference "
                    "or scan is required." % rec.employee_id.sudo().toolkit_custody_ref
                )
            if tick == "clearance_assets":
                rec._fix_refuse_outstanding_itsm_assets()
                # X-F2: a leaver cannot clear while they still hold work.
                rec._fix_refuse_open_work()
            rec._guarded().write({tick: True, "%s_by_id" % tick: self.env.uid})
        return True

    def _fix_refuse_outstanding_itsm_assets(self):
        """BRU-ITS-13: a leaver with an outstanding IT asset blocks final settlement
        until it is recovered or its write-off is approved. Read by name and as sudo:
        cd_itsm loads after this module, and the clearing officer has no register
        access."""
        self.ensure_one()
        if "fix.itsm.asset" not in self.env:
            return
        employee = self.employee_id
        assets = (
            self.env["fix.itsm.asset"]
            .sudo()
            .search(
                [
                    ("state", "in", ("in_service", "repair", "recovery_due")),
                    "|",
                    ("assigned_to_id", "=", employee.id),
                    ("recovery_from_id", "=", employee.id),
                ]
            )
        )
        if assets:
            raise UserError(
                "%s still holds IT asset(s) %s: recover them or get the write-off approved "
                "before the assets clearance (BRU-ITS-13)."
                % (employee.sudo().name, ", ".join(assets.mapped("asset_tag")))
            )

    def _fix_refuse_open_work(self):
        """X-F2 (exit-clearance side): a leaver cannot clear while they still
        hold work — open work orders and field orders still assigned to them
        (M02) and a booked vehicle assignment (M46). The models belong to
        other areas and may be absent: each is read defensively, by name and
        as sudo (the clearing officer has no register access). The consumers
        that reassign or block those records when the leaver event fires live
        in their own areas (a_service_delivery, e_supply_chain,
        f_asset_facilities — A09 X-F2)."""
        self.ensure_one()
        employee = self.employee_id
        problems = []
        if "fix.work.order" in self.env:
            wos = (
                self.env["fix.work.order"]
                .sudo()
                .search(
                    [
                        ("technician_id", "=", employee.id),
                        ("state", "in", ("pending", "assigned", "in_progress")),
                    ]
                )
            )
            if wos:
                problems.append("open work order(s) %s" % ", ".join(wos.mapped("name")))
        if "fix.field.order" in self.env:
            fos = (
                self.env["fix.field.order"]
                .sudo()
                .search(
                    [
                        ("technician_id", "=", employee.id),
                        ("state", "not in", ("completed", "cancelled", "declined")),
                    ]
                )
            )
            if fos:
                problems.append("open field order(s) %s" % ", ".join(fos.mapped("name")))
        if "fix.vehicle.assignment" in self.env:
            vas = (
                self.env["fix.vehicle.assignment"]
                .sudo()
                .search([("technician_id", "=", employee.id), ("active", "=", True)])
            )
            if vas:
                problems.append("vehicle booking(s) %s" % ", ".join(vas.mapped("name")))
        if problems:
            raise UserError(
                "%s still holds work and cannot clear: %s. Reassign or release it first "
                "(A09 X-F2: a leaver does not clear while holding work)."
                % (employee.sudo().name, "; ".join(problems))
            )

    def action_clear_it(self):
        return self._fix_tick("clearance_it")

    def action_clear_finance(self):
        return self._fix_tick("clearance_finance")

    def action_clear_hr(self):
        return self._fix_tick("clearance_hr")

    def action_clear_assets(self):
        return self._fix_tick("clearance_assets")

    def action_clear(self):
        for rec in self:
            if rec.state != "notice":
                raise UserError("Clear a confirmed exit (confirm its notice first).")
            rec._hr_require(OFFICER, "Clearing an exit")
            if not rec._all_cleared():
                raise UserError("Every clearance line must be ticked by its owner before clearing")
            # An asset allocated after the tick still blocks (BRU-ITS-13).
            rec._fix_refuse_outstanding_itsm_assets()
            # Work assigned after the tick still blocks (X-F2).
            rec._fix_refuse_open_work()
            rec.employee_id.sudo().write(
                {"form7_last_event_date": rec.last_working_day or fields.Date.context_today(self)}
            )
            rec._guarded().write({"state": "cleared"})
            publish(
                self.env,
                "clearance.completed",
                "fix.hr.exit",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "exit": rec.name,
                    "last_working_day": str(rec.last_working_day),
                    "cleared_by": {t: rec["%s_by_id" % t].id for t in TICKS},
                },
            )
        return True

    # ---- settlement (I1, pinned, routed) ---------------------------------------------
    def _fix_breakdown(self):
        self.ensure_one()
        result = self._fix_settlement_breakdown()
        lines = [[str(label), round(float(amount), 2)] for label, amount in result["lines"]]
        net = round(float(result["net"]), 2)
        basis = str(result.get("basis") or "")
        pin = digest(
            {
                "lines": lines,
                "net": net,
                "basis": basis,
                "employee": self.employee_id.id,
                "lwd": self.last_working_day,
                "type": self.exit_type,
            }
        )
        return lines, net, basis, pin

    def action_compute_settlement(self):
        for rec in self:
            if rec.state != "cleared":
                raise UserError("The settlement is computed after clearance (BRU-HCM-09).")
            rec._hr_require(OFFICER, "Computing a settlement")
            if rec.approval_state == "pending":
                raise UserError("The settlement is awaiting Finance; recall it first.")
            lines, net, basis, pin = rec._fix_breakdown()
            if rec.approval_state == "approved" and pin != rec.settlement_digest:
                rec._approval_void("the settlement was recomputed to a different figure")
            rec._guarded().write(
                {
                    "settlement_lines": json.dumps(lines),
                    "settlement_amount": net,
                    "settlement_basis": basis,
                    "settlement_digest": pin,
                    "settlement_computed_by_id": self.env.uid,
                    "settlement_computed_at": fields.Datetime.now(),
                }
            )
        return True

    def _approval_amount(self) -> float:
        return self.settlement_amount or 0.0

    def _approval_preparers(self):
        return self.mapped("settlement_computed_by_id")

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "cleared" or not rec.settlement_digest:
                raise UserError("Compute the settlement (payroll) before routing it to Finance.")
        return super().action_request_approval(justification=justification)

    def action_settle(self):
        """Finance's decision (approval inbox only). Re-computes payroll's
        figure and settles only what was approved."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "cleared":
                raise UserError("Settle a cleared exit")
            _lines, net, _basis, pin = rec._fix_breakdown()
            if pin != rec.settlement_digest or abs(net - (rec.settlement_amount or 0.0)) > 0.005:
                raise UserError(
                    "Payroll's settlement for %s is now %.2f, not the %.2f routed: recompute "
                    "and route it again." % (rec.employee_id.name, net, rec.settlement_amount)
                )
            today = fields.Date.context_today(self)
            rec._guarded().write({"state": "settled", "settled_on": today})
            # The employment ends ON the last working day (I3). A settlement
            # approved earlier (dues prepared ahead) waits for that day: ending
            # it now terminated the contract, dropped the worker from the
            # running payroll and revoked their access while they still worked
            # (M21 audit E2). The daily leaver cron ends it on the day.
            if not rec.last_working_day or rec.last_working_day <= today:
                rec._fix_end_employment()
            else:
                rec.message_post(
                    body="Settled ahead of the last working day: the contract ends and the "
                    "leaver is recorded on %s." % rec.last_working_day
                )
            publish(
                self.env,
                "exit.settled",
                "fix.hr.exit",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "exit": rec.name,
                    "net": net,
                    "last_working_day": str(rec.last_working_day),
                    "due_date": str(rec.settlement_due_date),
                    "within_s30": bool(
                        rec.settlement_due_date and today <= rec.settlement_due_date
                    ),
                },
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec.message_post(body="Settlement rejected by Finance: %s" % (comment or ""))

    def _fix_end_employment(self):
        """I3: contract terminated on the last working day; left_date set;
        the leaver event published once."""
        for rec in self:
            emp = rec.employee_id.sudo()
            contracts = (
                self.env["fix.employment.contract"]
                .sudo()
                .search(
                    [
                        ("employee_id", "=", emp.id),
                        ("state", "in", ("active", "draft", "expired")),
                    ]
                )
            )
            contracts._fix_end_for_exit(rec)
            rec._fix_record_leaver()

    def _fix_record_leaver(self):
        for rec in self:
            emp = rec.employee_id.sudo()
            if emp.left_date != rec.last_working_day:
                emp.write({"left_date": rec.last_working_day})
            if not emp.left_at:
                emp._emit_leaver()
            if not rec.leaver_processed:
                rec._guarded().write({"leaver_processed": True})

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "notice"):
                raise UserError("Only an exit before clearance can be cancelled.")
            if rec.leaver_processed:
                raise UserError("The leaver was already recorded for %s." % rec.name)
            rec._hr_require(OFFICER, "Cancelling an exit")
            rec._hr_refuse_conflicted("cancel")
            rec._guarded().write({"state": "cancelled"})
        return True

    # ---- crons -----------------------------------------------------------------------
    @api.model
    def _cron_process_last_working_days(self):
        """Daily: on the last working day the leaver is recorded (employee.left)."""
        today = fields.Date.context_today(self)
        due = self.sudo().search(
            [
                ("state", "in", ("notice", "cleared", "settled")),
                ("last_working_day", "<=", today),
                ("leaver_processed", "=", False),
            ]
        )
        # an exit settled ahead of its last working day ends the contract today
        settled = due.filtered(lambda r: r.state == "settled")
        settled._fix_end_employment()
        (due - settled)._fix_record_leaver()
        return len(due)

    @api.model
    def _cron_flag_overdue_settlements(self):
        """Daily: flag exits whose dues pass the s.30 / s.123(2) 30-working-day limit."""
        today = fields.Date.context_today(self)
        late = self.sudo().search(
            [
                ("state", "in", ("notice", "cleared")),
                ("settlement_due_date", "<", today),
                ("settlement_overdue", "=", False),
            ]
        )
        for rec in late:
            rec._guarded().write({"settlement_overdue": True})
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Final settlement overdue: %s" % rec.employee_id.name,
                note="Dues were due by %s (BLA s.30 / s.123(2))." % rec.settlement_due_date,
            )
            publish(
                self.env,
                "exit.settlement.overdue",
                "fix.hr.exit",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "exit": rec.name,
                    "due_date": str(rec.settlement_due_date),
                },
            )
        return len(late)
