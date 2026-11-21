# m52_recovery — A07 ERP audit (2026-11-20): money owed back to the company
# from an A07 event reaches the GL as a receivable.
#
#   * D9 (FIN-10, M45-05, M46-14): a lost/damaged item recharged to a staff
#     member (equipment.recharge_requested), a traffic fine or an insurance
#     excess recovered from the driver (a cost entry naming the employee) is
#     an EMPLOYEE RECOVERY. HR approves it (an HR manager who did not raise
#     the source); approval books Dr 100049 Employee Recovery Receivable /
#     Cr the loss or expense account, on the source's branch. It is recovered
#     through M56 payroll within the statutory wage-deduction limit HR records
#     as a setting: nothing is sent to payroll until that limit exists.
#   * FIN-11 (M46-01c): an accident claim closed with a settlement is an
#     INSURER RECEIVABLE: Dr 100048 Insurance Claim Receivable (the insurer) /
#     Cr the insurance-recovery account, posted by an accountant.
# Accounts are account roles (cd_asset_finance_hse_bridge.account.<key>);
# unset, nothing posts.
from odoo import api, fields, models
from odoo.addons.cd_fixed_asset_ext.models.fix_asset_common import money
from odoo.exceptions import UserError

from .fix_bridge_exception import (
    ACCOUNTANT,
    ACCOUNTING_MANAGER,
    dhaka_today,
    event_source,
    require_role,
    role_account,
    run_hook,
)

HR_MANAGER = "hr.group_hr_manager"
# D9: the statutory wage-deduction limit HR records (BLA 2006). Unset = no
# deduction is ever sent to payroll.
DEDUCTION_LIMIT_PARAM = "cd_payroll_bd.recharge_deduction_limit_percent"
RECEIVABLE_ROLE = {
    "employee": "employee_recovery_receivable",
    "insurer": "insurance_claim_receivable",
}


class FixAssetRecovery(models.Model):
    _name = "fix.asset.recovery"
    _description = "A07 Recovery Receivable (Employee / Insurer)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, id desc"

    _key_unique = models.Constraint("UNIQUE (key)", "One recovery per source.")

    name = fields.Char(required=True, readonly=True, default="New", copy=False)
    key = fields.Char(required=True, readonly=True, index=True, copy=False)
    kind = fields.Selection(
        [("employee", "Employee Recovery (D9)"), ("insurer", "Insurance Claim Receivable")],
        required=True,
        readonly=True,
    )
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Branch", index=True, readonly=True
    )
    source_model = fields.Char(required=True, readonly=True)
    source_res_id = fields.Integer(required=True, readonly=True, index=True)
    source_ref = fields.Char(string="Source", readonly=True)
    cost_entry_id = fields.Many2one("fix.asset.cost.entry", string="Cost Entry", readonly=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Debtor", readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, readonly=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Amount to Recover", readonly=True)
    credit_role = fields.Char(readonly=True, help="Account role credited by the recovery")
    credit_account_id = fields.Many2one("account.account", string="Credited Account", readonly=True)
    basis = fields.Text(readonly=True)
    state = fields.Selection(
        [
            ("pending", "Pending Approval"),
            ("approved", "Booked (Receivable)"),
            ("in_payroll", "Sent to Payroll"),
            ("rejected", "Rejected"),
        ],
        default="pending",
        required=True,
        index=True,
        tracking=True,
    )
    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True, copy=False)
    payroll_ref = fields.Char(string="Payroll Recovery", readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    decision_note = fields.Text()

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            n
            for n, f in self._fields.items()
            if f.store
            and n != "decision_note"
            and n not in ("id", "create_uid", "create_date", "write_uid", "write_date")
            and not n.startswith(("message_", "activity_"))
            and f.type not in ("one2many", "many2many")
        }
        if any(rec.state != "pending" for rec in self):
            guarded.add("decision_note")
        return guarded

    def unlink(self):
        if not self.env.su:
            raise UserError("A recovery is part of the record: reject it instead.")
        return super().unlink()

    # ---- raising -----------------------------------------------------------
    @api.model
    def _recovery_queue(self, source, vals):
        key = "recovery:%s:%s:%s" % (vals["kind"], source._name, source.id)
        Rec = self.sudo()._guarded()
        existing = Rec.search([("key", "=", key)], limit=1)
        if existing:
            pinned = {k: vals[k] for k in ("amount", "employee_id", "partner_id") if k in vals}
            changed = {
                k: v
                for k, v in pinned.items()
                if (existing[k].id if k != "amount" else existing[k]) != v
            }
            if changed and existing.state == "pending":
                existing.write(changed)
                existing.message_post(body="The source changed: figures refreshed.")
            elif changed:
                existing.message_post(
                    body="The source changed (%s) after the decision: finance and HR review it."
                    % ", ".join(sorted(changed))
                )
            return existing
        vals = dict(
            vals,
            key=key,
            source_model=source._name,
            source_res_id=source.id,
            source_ref=source.display_name,
            name=self.env["ir.sequence"].sudo().next_by_code("fix.asset.recovery") or "REC/New",
        )
        rec = Rec.create(vals)
        rec.message_post(
            body="Raised: %s approves it (%s)."
            % ("an HR manager" if rec.kind == "employee" else "an accountant", rec.basis or "-")
        )
        return rec

    @api.model
    def _recovery_from_cost(self, entry):
        """A cost the employee bears (a recovered fine, an excess borne by the
        driver): the recovery credits the cost's own account."""
        entry = entry.sudo()
        if not entry.recovery_employee_id or entry.amount <= 0:
            return self.browse()
        return self._recovery_queue(
            entry,
            {
                "kind": "employee",
                "company_id": entry.company_id.id,
                "operating_unit_id": entry.operating_unit_id.id,
                "cost_entry_id": entry.id,
                "employee_id": entry.recovery_employee_id.id,
                "amount": entry.amount,
                "credit_account_id": entry.account_id.id,
                "basis": "%s (%s), decided to be recovered from %s."
                % (entry.source_ref, entry.detail or "-", entry.recovery_employee_id.name),
            },
        )

    @api.model
    def consume_equipment_recharge_requested(self, event):
        """equipment.recharge_requested (M45: an approved write-off recharges
        the loss to a staff member) -> one employee recovery, read from the
        loss record itself (the approved amount and employee)."""
        loss = event_source(self.env, event, "fix.equipment.loss")
        if not loss or not loss.recharge_employee_id or (loss.recharge_amount or 0.0) <= 0:
            return False
        equipment = loss.equipment_id.sudo()
        payload = event.get("payload") or {}
        rec = self._recovery_queue(
            loss,
            {
                "kind": "employee",
                "company_id": (equipment.company_id or self.env.company).id,
                "operating_unit_id": (
                    equipment.operating_unit_id or equipment.branch_id.operating_unit_id
                ).id,
                "employee_id": loss.recharge_employee_id.id,
                "amount": loss.recharge_amount,
                "credit_role": "recovery.equipment_loss",
                "basis": "Write-off %s of %s recharged to %s."
                % (loss.name, equipment.code, loss.recharge_employee_id.name),
            },
        )
        # S2 (M45): the recharge is published only once HR approved it in M45
        # (D9's HR-approved recovery decision): it is booked at once, stamped
        # with that HR approver. A booking that cannot be made (an account role
        # unset) leaves it pending with the reason, for HR to approve here.
        hr_user = self.env["res.users"].sudo().browse(int(payload.get("hr_approved_by_id") or 0))
        if rec.state == "pending" and hr_user.exists():
            try:
                with self.env.cr.savepoint():
                    rec.sudo().action_approve(
                        note="Approved by HR in M45 (%s, %s)."
                        % (hr_user.name, payload.get("hr_approved_on") or "-")
                    )
                    rec.sudo()._guarded().write({"decided_by_id": hr_user.id})
            except UserError as exc:
                rec.message_post(body="Not booked yet: %s" % exc)
        return rec

    @api.model
    def _recovery_from_claim(self, accidents):
        for acc in accidents.sudo():
            if acc.state != "closed" or (acc.settlement_amount or 0.0) <= 0:
                continue
            vehicle = acc.vehicle_id
            self._recovery_queue(
                acc,
                {
                    "kind": "insurer",
                    "company_id": (vehicle.company_id or self.env.company).id,
                    "operating_unit_id": (
                        vehicle.operating_unit_id or vehicle.branch_id.operating_unit_id
                    ).id,
                    "partner_id": acc.insurer_id.id,
                    "amount": acc.settlement_amount,
                    "credit_role": "recovery.insurance",
                    "basis": "Claim %s closed with a settlement of %.2f from %s."
                    % (acc.name, acc.settlement_amount, acc.insurer_id.name or "-"),
                },
            )

    def _recovery_outstanding(self):
        """What the debtor still owes on a booked recovery (R2a, BRU-EAM-09:
        the M21 exit clearance reads it). The receivable line of its entry: its
        open residual when the account is reconciled, else its whole balance
        (nothing proves it was collected). Pending or rejected owes nothing."""
        self.ensure_one()
        if self.state not in ("approved", "in_payroll"):
            return 0.0
        lines = self.sudo().move_id.line_ids.filtered(lambda ln: ln.debit > 0)
        if not lines:
            return money(self.amount)
        if all(ln.account_id.reconcile for ln in lines):
            return money(sum(lines.mapped("amount_residual")))
        return money(sum(lines.mapped("balance")))

    def _recovery_source(self):
        self.ensure_one()
        if self.source_model not in self.env:
            return None
        return self.env[self.source_model].sudo().browse(self.source_res_id).exists()

    # ---- decision ----------------------------------------------------------
    def action_approve(self, note=None):
        """Approve and book the receivable: an HR manager for an employee
        recovery (D9), an accountant for an insurer's settlement. The person
        who recorded the source does not approve it."""
        from odoo.addons.cd_ap_ext.models.ap_gl import ap_journal, post_ap_move

        for rec in self:
            if rec.state != "pending":
                raise UserError("%s is already decided." % rec.name)
            if rec.kind == "employee":
                require_role(self.env, [HR_MANAGER], "Approving an employee recovery")
            else:
                require_role(
                    self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Booking a claim receivable"
                )
            source = rec._recovery_source()
            if not self.env.su and source and source.create_uid == self.env.user:
                raise UserError("Segregation of duties: you recorded %s." % rec.source_ref)
            if not rec.operating_unit_id:
                raise UserError(
                    "%s has no branch: the receivable is booked on the source's branch." % rec.name
                )
            company = rec.company_id
            receivable = role_account(
                self.env, company, RECEIVABLE_ROLE[rec.kind], required_for=rec.name
            )
            credit = rec.credit_account_id or role_account(
                self.env, company, rec.credit_role or "", required_for=rec.name
            )
            if not credit:
                raise UserError("%s names no account to credit." % rec.name)
            debtor = rec.partner_id
            if rec.kind == "employee":
                employee = rec.employee_id.sudo()
                debtor = employee.work_contact_id or employee.user_id.partner_id
            label = "%s %s" % (rec.name, rec.source_ref or "")
            move = post_ap_move(
                rec.env(su=True),
                company,
                ap_journal(rec.env(su=True), company, "purchase"),
                dhaka_today(self.env),
                label,
                [
                    (receivable, label, money(rec.amount), 0.0, debtor or None),
                    (credit, label, 0.0, money(rec.amount), None),
                ],
                rec.operating_unit_id,
            )
            rec.sudo()._guarded().write(
                {
                    "state": "approved",
                    "credit_account_id": credit.id,
                    "move_id": move.id,
                    "decision_note": (note or rec.decision_note or "").strip() or False,
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Booked %s: Dr %s / Cr %s." % (move.name, receivable.code, credit.code)
            )
        return True

    def action_reject(self, reason=None):
        for rec in self:
            require_role(
                self.env,
                [HR_MANAGER] if rec.kind == "employee" else [ACCOUNTANT, ACCOUNTING_MANAGER],
                "Rejecting a recovery",
            )
            if rec.state != "pending":
                raise UserError("%s is already decided." % rec.name)
            note = (reason or rec.decision_note or "").strip()
            if not note:
                raise UserError("Say why %s is not recovered (Decision Note)." % rec.name)
            rec.sudo()._guarded().write(
                {
                    "state": "rejected",
                    "decision_note": note,
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Rejected: %s" % note)
        return True

    def action_send_to_payroll(self):
        """D9: the booked recovery is deducted by M56 within the statutory
        limit HR records. Without the limit, or without the payroll API, it is
        refused (fail closed) and stays a receivable."""
        require_role(self.env, [HR_MANAGER], "Sending a recovery to payroll")
        raw = self.env["ir.config_parameter"].sudo().get_param(DEDUCTION_LIMIT_PARAM)
        try:
            limit = float(raw) if raw not in (None, False, "") else 0.0
        except ValueError:
            limit = 0.0
        for rec in self:
            if rec.kind != "employee" or rec.state != "approved":
                raise UserError("%s is not a booked employee recovery." % rec.name)
            if limit <= 0:
                raise UserError(
                    "HR has not recorded the statutory wage-deduction limit (system parameter "
                    "%s): no deduction is sent to payroll." % DEDUCTION_LIMIT_PARAM
                )
            Payroll = self.env.get("fix.payroll.recovery", None)
            api_call = (
                getattr(Payroll, "_fix_recovery_from_source", None) if Payroll is not None else None
            )
            if not api_call:
                raise UserError(
                    "M56 payroll has no recovery API for asset recharges yet "
                    "(fix.payroll.recovery._fix_recovery_from_source): %s stays a receivable."
                    % rec.name
                )
            recovery = api_call(rec, rec.employee_id, rec.amount, limit, rec.basis or rec.name)
            rec.sudo()._guarded().write(
                {"state": "in_payroll", "payroll_ref": recovery.display_name if recovery else False}
            )
        return True


class FixVehicleAccidentRecovery(models.Model):
    _inherit = "fix.vehicle.accident"

    def action_close(self, settlement=None):
        result = super().action_close(settlement=settlement)
        Rec = self.env["fix.asset.recovery"].sudo()
        run_hook(self.env, "m52_claim_receivable", Rec._recovery_from_claim, self)
        return result
