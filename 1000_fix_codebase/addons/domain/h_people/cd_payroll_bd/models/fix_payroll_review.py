# fix_payroll_review — M56: the reviews that stand between a calculated run
# and its approval (A09 round 2).
#
#   * BRU-PAY-06 / FR-PAY-039/040 (M56-14): every calculation (and every trial
#     run) records each employee's net against the previous PAID period. Once
#     the business sets a threshold (company setting, 0 = off as today), the
#     run is refused at pre-validation - so neither requested nor approved -
#     while an employee over the threshold has no reviewer's acknowledgement.
#     The reviewer is a payroll user who did not calculate the run.
#   * M56-1: a salary account or wallet changed within the cool-off before the
#     run (company setting, 0 = off as today) is refused at pre-validation
#     until a second person - not whoever made the change, not the calculator,
#     not the employee - confirms it. The confirmation pins the account it
#     confirmed: a further change needs a further confirmation.
import hashlib
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

PAYROLL_OFFICER = "cd_payroll_bd.group_payroll_officer"
# The master's salary-channel fields (cd_hr_core BANK_FIELDS)
BANK_FIELDS = (
    "bank_name",
    "bank_branch_name",
    "routing_number",
    "bank_account_number",
    "bank_account_ids",
    "mfs_provider",
    "mfs_account_number",
)
BANK_PROPOSALS = (
    "proposed_bank_name",
    "proposed_bank_branch_name",
    "proposed_routing_number",
    "proposed_bank_account_number",
    "proposed_mfs_provider",
    "proposed_mfs_account_number",
)


def _require_payroll(env, what):
    if not (env.su or env.user.has_group(PAYROLL_OFFICER)):
        raise AccessError("Only payroll can %s." % what)


class FixPayrollVariance(models.Model):
    _name = "fix.payroll.variance"
    _description = "Payroll Variance Review Line"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "period_id desc, kind, abs_variance_pct desc, id"

    period_id = fields.Many2one(
        "fix.payroll.period", required=True, ondelete="cascade", index=True, readonly=True
    )
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", readonly=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True, readonly=True)
    kind = fields.Selection(
        [("trial", "Trial Run"), ("run", "Calculated Run")], required=True, readonly=True
    )
    previous_period_id = fields.Many2one("fix.payroll.period", readonly=True)
    currency_id = fields.Many2one("res.currency", readonly=True)
    previous_net = fields.Monetary(currency_field="currency_id", readonly=True)
    current_net = fields.Monetary(currency_field="currency_id", readonly=True)
    variance = fields.Monetary(currency_field="currency_id", readonly=True)
    variance_pct = fields.Float(string="Variance %", readonly=True)
    abs_variance_pct = fields.Float(readonly=True)
    no_comparison = fields.Boolean(
        string="No Previous Net",
        readonly=True,
        help="The employee was not paid in the previous paid period (a joiner, a return).",
    )
    over_threshold = fields.Boolean(
        string="Over Threshold (at calculation)",
        readonly=True,
        help="Against the threshold set when the line was computed; the approval gate reads "
        "the company's threshold as it stands.",
    )
    acknowledged_by_id = fields.Many2one("res.users", string="Acknowledged By", readonly=True)
    acknowledged_on = fields.Datetime(readonly=True)
    acknowledgement_note = fields.Text(readonly=True)

    def _fix_guarded_fields(self) -> set:
        # every line is written by a calculation, a trial run or a review
        return super()._fix_guarded_fields() | {
            "period_id",
            "company_id",
            "operating_unit_id",
            "employee_id",
            "kind",
            "previous_period_id",
            "currency_id",
            "previous_net",
            "current_net",
            "variance",
            "variance_pct",
            "abs_variance_pct",
            "no_comparison",
            "over_threshold",
            "acknowledged_by_id",
            "acknowledged_on",
            "acknowledgement_note",
        }

    def _over(self, threshold):
        self.ensure_one()
        if threshold <= 0:
            return False
        return self.no_comparison or self.abs_variance_pct > threshold + 1e-9

    @api.model
    def _previous_paid_period(self, period):
        return (
            self.env["fix.payroll.period"]
            .sudo()
            .search(
                [
                    ("company_id", "=", period.company_id.id),
                    ("operating_unit_id", "=", period.operating_unit_id.id),
                    ("id", "!=", period.id),
                    ("state", "in", ("paid", "posted")),
                    ("period_start", "<", period.period_start),
                ],
                order="period_start desc, id desc",
                limit=1,
            )
        )

    @api.model
    def _refresh(self, period, kind, slips):
        """Replace `period`'s `kind` lines from `slips` (real or in-memory);
        returns how many are over the company threshold."""
        threshold = period.company_id.payroll_variance_threshold_pct or 0.0
        self.sudo().search([("period_id", "=", period.id), ("kind", "=", kind)])._guarded().unlink()
        previous = self._previous_paid_period(period)
        before = {}
        for slip in previous.sudo().payslip_ids:
            before[slip.employee_id.id] = before.get(slip.employee_id.id, 0.0) + slip.net
        now = {}
        for slip in slips:
            now[slip.employee_id.id] = now.get(slip.employee_id.id, 0.0) + slip.net
        vals_list = []
        for emp_id in sorted(set(before) | set(now)):
            prev, cur = before.get(emp_id, 0.0), now.get(emp_id, 0.0)
            missing = emp_id not in before or not previous
            pct = ((cur - prev) / prev * 100.0) if prev else 0.0
            vals_list.append(
                {
                    "period_id": period.id,
                    "company_id": period.company_id.id,
                    "employee_id": emp_id,
                    "kind": kind,
                    "previous_period_id": previous.id or False,
                    "currency_id": period.currency_id.id,
                    "previous_net": prev,
                    "current_net": cur,
                    "variance": round(cur - prev, 2),
                    "variance_pct": round(pct, 2),
                    "abs_variance_pct": round(abs(pct), 2),
                    "no_comparison": missing,
                }
            )
        lines = self.sudo()._guarded().create(vals_list)
        over = 0
        for line in lines:
            flag = line._over(threshold)
            over += int(flag)
            if flag:
                line._guarded().write({"over_threshold": True})
        return over

    @api.model
    def _variance_issues(self, period):
        """BRU-PAY-06: the employees of a calculated run whose net moved over
        the threshold with no reviewer's acknowledgement."""
        threshold = period.company_id.payroll_variance_threshold_pct or 0.0
        if threshold <= 0:
            return []
        lines = self.sudo().search([("period_id", "=", period.id), ("kind", "=", "run")])
        issues = []
        for line in lines.filtered(lambda r: r._over(threshold) and not r.acknowledged_by_id):
            if line.no_comparison:
                what = "has no net in the previous paid period (%.2f now)" % line.current_net
            else:
                what = "net moved %+.2f%% (%.2f -> %.2f)" % (
                    line.variance_pct,
                    line.previous_net,
                    line.current_net,
                )
            issues.append(
                "%s %s, over the %g%% variance threshold, and no reviewer has acknowledged it"
                % (line.employee_id.name, what, threshold)
            )
        return issues

    def action_acknowledge(self, note=None):
        """The reviewer's acknowledgement of a run's variance: a payroll user
        who neither calculated the run nor is the employee, with a reason."""
        _require_payroll(self.env, "acknowledge a payroll variance")
        if not (note or "").strip():
            raise UserError("State why the variance is right before acknowledging it.")
        user = self.env.user
        for rec in self:
            period = rec.period_id.sudo()
            if rec.kind != "run" or period.state != "calculated":
                raise UserError("Only a calculated run's variance is acknowledged.")
            if period.approval_state == "pending":
                raise UserError("Recall the approval request before reviewing its variance.")
            if not self.env.su and user in (period.calculator_id | period.create_uid):
                raise UserError(
                    "The variance of a run is acknowledged by a reviewer, not by whoever "
                    "prepared or calculated it."
                )
            if not self.env.su and rec.employee_id.sudo().user_id == user:
                raise UserError("Nobody acknowledges the variance of their own pay.")
            rec._guarded().write(
                {
                    "acknowledged_by_id": user.id,
                    "acknowledged_on": fields.Datetime.now(),
                    "acknowledgement_note": note.strip(),
                }
            )
        return True


class FixPayrollBankCheck(models.Model):
    _name = "fix.payroll.bank.check"
    _description = "Payroll Bank-Change Confirmation"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "period_id desc, id"

    period_id = fields.Many2one(
        "fix.payroll.period", required=True, ondelete="cascade", index=True, readonly=True
    )
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", readonly=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True, readonly=True)
    payment_digest = fields.Char(readonly=True)
    account_hint = fields.Char(string="Account (last digits)", readonly=True)
    changed_on = fields.Datetime(string="Changed On", readonly=True)
    changed_by_ids = fields.Many2many(
        "res.users",
        "fix_payroll_bank_check_changer_rel",
        "check_id",
        "user_id",
        string="Changed By",
        readonly=True,
    )
    state = fields.Selection(
        [("pending", "Awaiting Confirmation"), ("confirmed", "Confirmed")],
        required=True,
        default="pending",
        readonly=True,
    )
    confirmed_by_id = fields.Many2one("res.users", string="Confirmed By", readonly=True)
    confirmed_on = fields.Datetime(readonly=True)
    confirmation_note = fields.Text(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "period_id",
            "company_id",
            "operating_unit_id",
            "employee_id",
            "payment_digest",
            "account_hint",
            "changed_on",
            "changed_by_ids",
            "state",
            "confirmed_by_id",
            "confirmed_on",
            "confirmation_note",
        }

    # ---- what changed, and when -------------------------------------------------
    @staticmethod
    def _slip_digest(slip):
        if slip.payment_channel == "mfs":
            key = "mfs|%s|%s" % (slip.mfs_provider or "", (slip.mfs_wallet or "").strip())
        else:
            key = "bank|%s|%s" % (
                (slip.bank_account_no or "").strip(),
                (slip.routing_no or "").strip(),
            )
        return hashlib.sha256(key.encode()).hexdigest()

    @api.model
    def _last_change(self, employee):
        """(when, users) of the latest change to the employee's salary account
        or wallet: an applied master change, a tracked write on the master,
        or a bank account record created or edited."""
        env = self.env(su=True)
        events = []
        if "fix.hr.master.change" in env:
            domain = [("employee_id", "=", employee.id), ("state", "=", "applied")]
            domain += ["|"] * (len(BANK_PROPOSALS) - 1)
            domain += [(name, "!=", False) for name in BANK_PROPOSALS]
            for change in env["fix.hr.master.change"].search(domain):
                req = change.approval_request_id
                users = change.create_uid | change.applied_by_id | req.requested_by_id
                events.append((change.applied_on, users))
        tracked = env["mail.tracking.value"].search(
            [
                ("mail_message_id.model", "=", "hr.employee"),
                ("mail_message_id.res_id", "=", employee.id),
                ("field_id.name", "in", list(BANK_FIELDS)),
            ]
        )
        for value in tracked:
            msg = value.mail_message_id
            events.append((msg.date, msg.author_id.user_ids[:1]))
        for bank in employee.sudo().bank_account_ids:
            events.append((bank.write_date or bank.create_date, bank.create_uid | bank.write_uid))
        events = [(when, users) for when, users in events if when]
        if not events:
            return None, env["res.users"]
        latest = max(when for when, _u in events)
        users = env["res.users"]
        for when, who in events:
            if when == latest:
                users |= who
        return latest, users

    @api.model
    def _in_cooloff(self, period, employee):
        days = period.company_id.payroll_bank_cooloff_days or 0
        if days <= 0:
            return None, None
        when, users = self._last_change(employee)
        if when and when >= fields.Datetime.now() - timedelta(days=days):
            return when, users
        return None, None

    @api.model
    def _refresh(self, period):
        """One confirmation line per paid employee whose account changed
        inside the cool-off; a confirmation of the same account survives a
        recalculation, any other is replaced."""
        Check = self.sudo()._guarded()
        existing = Check.search([("period_id", "=", period.id)])
        if (period.company_id.payroll_bank_cooloff_days or 0) <= 0:
            existing.filtered(lambda c: c.state == "pending").unlink()
            return
        keep = Check.browse()
        for slip in period.sudo().payslip_ids.filtered(lambda s: s.net > 0):
            when, users = self._in_cooloff(period, slip.employee_id)
            if not when:
                continue
            digest = self._slip_digest(slip)
            same = existing.filtered(
                lambda c, e=slip.employee_id, d=digest: c.employee_id == e and c.payment_digest == d
            )
            if same:
                keep |= same
                continue
            account = (
                (slip.mfs_wallet or "")
                if slip.payment_channel == "mfs"
                else (slip.bank_account_no or "")
            ).strip()
            keep |= Check.create(
                {
                    "period_id": period.id,
                    "company_id": period.company_id.id,
                    "employee_id": slip.employee_id.id,
                    "payment_digest": digest,
                    "account_hint": ("..." + account[-4:]) if account else "(none)",
                    "changed_on": when,
                    "changed_by_ids": [(6, 0, users.ids)],
                }
            )
        (existing - keep).unlink()

    @api.model
    def _bank_check_issues(self, period):
        days = period.company_id.payroll_bank_cooloff_days or 0
        if days <= 0:
            return []
        lines = self.sudo().search([("period_id", "=", period.id)])
        issues = []
        for slip in period.sudo().payslip_ids.filtered(lambda s: s.net > 0):
            when, _users = self._in_cooloff(period, slip.employee_id)
            if not when:
                continue
            digest = self._slip_digest(slip)
            mine = lines.filtered(
                lambda c, e=slip.employee_id, d=digest: c.employee_id == e and c.payment_digest == d
            )
            if mine.filtered(lambda c: c.state == "confirmed"):
                continue
            issues.append(
                "%s's salary account changed on %s, inside the %d-day cool-off: a second person "
                "must confirm it before the run is approved%s"
                % (
                    slip.employee_id.name,
                    fields.Datetime.to_string(when)[:16],
                    days,
                    "" if mine else " (recalculate the run to raise its confirmation)",
                )
            )
        return issues

    def action_confirm(self, note=None):
        """The second person's confirmation (M56-1)."""
        _require_payroll(self.env, "confirm a bank-account change")
        user = self.env.user
        for rec in self:
            period = rec.period_id.sudo()
            if rec.state != "pending":
                raise UserError("This bank change is already confirmed.")
            if period.state != "calculated":
                raise UserError("A bank change is confirmed on a calculated run.")
            if not self.env.su:
                if user in rec.changed_by_ids:
                    raise UserError(
                        "You made this bank change: a second person confirms it (M56-1)."
                    )
                if user in (period.calculator_id | period.create_uid):
                    raise UserError(
                        "The run's preparer or calculator does not confirm its bank changes."
                    )
                if rec.employee_id.sudo().user_id == user:
                    raise UserError("Nobody confirms a change to their own salary account.")
            slip = period.payslip_ids.filtered(lambda s, e=rec.employee_id: s.employee_id == e)
            if not slip or self._slip_digest(slip[:1]) != rec.payment_digest:
                raise UserError(
                    "%s's payslip no longer pays the account this line was raised for; "
                    "recalculate the run." % rec.employee_id.name
                )
            rec._guarded().write(
                {
                    "state": "confirmed",
                    "confirmed_by_id": user.id,
                    "confirmed_on": fields.Datetime.now(),
                    "confirmation_note": (note or "").strip() or False,
                }
            )
        return True
