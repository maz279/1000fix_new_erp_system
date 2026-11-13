# cd_hr_core — transfer / promotion controls (A09 workflow audit M21-3, B1-B5,
# C1, C3 "employee.moved / salary_structure.changed").
#
# The audit ran all six "approvals" as one HR Manager, wrote state and the
# executive approval directly and through /p03/model/write, raised the gross
# from 60,000 to 600,000 after executive approval, promoted the approver
# himself, skipped Finance and credited the MD for the officer's click. Here:
#
#   * every step has an owner: the origin line manager recommends, the
#     destination manager concurs, the named technical evaluator evaluates,
#     an HR Officer audits, Finance clears (mandatory when pay changes), and
#     the executive decision is a routed M63 approval (DOFA tier on the pay
#     delta once a ladder is ruled);
#   * nobody signs two steps, and the initiator and the employee sign none;
#   * the stamps are the acting user's, never typed; state, approvals, stamps
#     and custody ticks are guarded;
#   * the proposal is frozen once it leaves draft and pinned at approval:
#     apply refuses anything the approval did not cover;
#   * the custody ticks each have an owner (stores, finance, line manager);
#   * applying a pay change creates and activates a new contract version
#     (never an in-place edit) and publishes salary_structure.changed;
#   * an approved or applied movement never goes back to draft.
from odoo import fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

from .fix_hr_controls_common import CLEAR_ASSETS, EXECUTIVE, FINANCE, OFFICER, digest

# read from the employee master and the active contract at recommendation (T7)
SNAPSHOT_FIELDS = (
    "from_operating_unit_id",
    "from_department_id",
    "from_position_id",
    "from_job_title",
    "from_manager_id",
    "from_grade_band",
    "from_repair_tier",
)

PROPOSAL_FIELDS = (
    "employee_id",
    "movement_type",
    "movement_category",
    "movement_nature",
    "effective_date",
    "to_operating_unit_id",
    "to_department_id",
    "to_position_id",
    "to_job_title",
    "to_grade_band",
    "to_manager_id",
    "to_repair_tier",
    "to_tax_location",
    "current_basic",
    "proposed_basic",
    "current_gross",
    "proposed_gross",
    "proposed_house_rent",
    "proposed_medical",
    "proposed_conveyance",
    "proposed_skill_allowance",
    "deputation_allowance",
    "transfer_grant",
    "luggage_allowance",
    "travel_allowance",
    # who signs a step is part of the proposal: an HR officer could name
    # themselves the evaluator after the recommendation (M21 audit T6)
    "technical_evaluator_id",
    # the accreditations the movement grants reach the master that M02
    # dispatch matches skills on (they were captured and never applied)
    "esd_certified",
    "bga_license",
    "oem_brand_authorizations",
)
# The one-off relocation money a movement grants: Finance clears it and it is
# part of the amount the executive decides (it bypassed both, M21 audit T3).
RELOCATION_MONEY = (
    "transfer_grant",
    "luggage_allowance",
    "travel_allowance",
    "deputation_allowance",
)
# contract component -> the movement's proposal for it
COMPONENTS = (
    ("basic_monthly", "proposed_basic"),
    ("house_rent", "proposed_house_rent"),
    ("medical_allowance", "proposed_medical"),
    ("conveyance_allowance", "proposed_conveyance"),
    ("technical_allowance", "proposed_skill_allowance"),
    ("other_allowance", None),
    ("dearness_allowance", None),
    ("adhoc_allowance", None),
)
# hr.employee.job_band <-> the movement grade (band_7 "Head of Dept" was never reached)
BAND_MAP = {
    "L1": "band_2",
    "L2": "band_3",
    "L3": "band_4",
    "L4": "band_5",
    "M1": "band_6",
    "M2": "band_7",
    "EX": "band_8",
}
TIER_MAP = {
    "tier1_basic": "l1_modular",
    "tier2_component": "l2_subassembly",
    "tier3_board": "l3_component",
    "tier4_bga_micro": "l4_schematic",
}
OPEN_STATES = (
    "draft",
    "recommended",
    "concurred",
    "tech_evaluated",
    "hr_audited",
    "finance_approved",
    "approved",
    "handover_cleared",
)
PAY_PROPOSALS = (
    "proposed_basic",
    "proposed_gross",
    "proposed_house_rent",
    "proposed_medical",
    "proposed_conveyance",
    "proposed_skill_allowance",
)
# step -> (approval field, employee stamp, user stamp, date stamp)
STEPS = {
    "recommend": (
        "origin_manager_approval",
        "origin_manager_id",
        "origin_manager_user_id",
        "origin_manager_date",
    ),
    "concur": (
        "destination_manager_approval",
        "destination_manager_id",
        "destination_manager_user_id",
        "destination_manager_date",
    ),
    "tech": ("tech_head_approval", "tech_head_id", "tech_head_user_id", "tech_head_date"),
    "hr": ("hr_head_approval", "hr_head_id", "hr_head_user_id", "hr_head_date"),
    "finance": (
        "finance_head_approval",
        "finance_head_id",
        "finance_head_user_id",
        "finance_head_date",
    ),
    "executive": ("executive_approval", "executive_id", "executive_user_id", "executive_date"),
}
CUSTODY = {
    "open_jobs_audited": "line_manager",
    "toolkit_returned": CLEAR_ASSETS,
    "spare_parts_reconciled": CLEAR_ASSETS,
    "storekeeper_cleared": "storekeeper",
    "imprest_cash_settled": FINANCE,
}


class FixHrTransferControls(models.Model):
    _name = "fix.hr.transfer"
    _inherit = [
        "fix.hr.transfer",
        "mail.thread",
        "mail.activity.mixin",
        "fix.people.approval.mixin",
        "fix.hr.control.mixin",
    ]

    _approval_domain = "hr_movement"
    _approval_apply_method = "action_approve"
    _approval_group = EXECUTIVE

    origin_manager_user_id = fields.Many2one(
        "res.users", string="Recommended By", readonly=True, copy=False
    )
    destination_manager_user_id = fields.Many2one(
        "res.users", string="Concurred By", readonly=True, copy=False
    )
    tech_head_user_id = fields.Many2one(
        "res.users", string="Technically Evaluated By", readonly=True, copy=False
    )
    hr_head_user_id = fields.Many2one(
        "res.users", string="HR Audited By", readonly=True, copy=False
    )
    finance_head_user_id = fields.Many2one(
        "res.users", string="Finance Cleared By", readonly=True, copy=False
    )
    executive_user_id = fields.Many2one(
        "res.users", string="Executive Approved By", readonly=True, copy=False
    )
    open_jobs_audited_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    toolkit_returned_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    spare_parts_reconciled_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    storekeeper_cleared_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    imprest_cash_settled_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_digest = fields.Char(readonly=True, copy=False)
    applied_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    new_contract_id = fields.Many2one(
        "fix.employment.contract", string="Contract Version", readonly=True, copy=False
    )

    # ---- guard -----------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        stamps = {name for step in STEPS.values() for name in step}
        ticks = set(CUSTODY) | {"%s_by_id" % t for t in CUSTODY}
        return (
            super()._fix_guarded_fields()
            | stamps
            | ticks
            | {
                "state",
                "initiator_user_id",
                "approved_digest",
                "applied_by_id",
                "new_contract_id",
                "rejection_reason",
            }
        )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(PROPOSAL_FIELDS) | set(SNAPSHOT_FIELDS)
        if self and self.tech_head_approval == "approved":
            locked.add("technical_assessment_score")
        if self and self.storekeeper_cleared:
            locked.add("storekeeper_id")
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self.filtered("id"):
                if (
                    "technical_assessment_score" in vals
                    and rec.tech_head_approval == "approved"
                    and rec._fix_guard_differs(
                        "technical_assessment_score",
                        vals["technical_assessment_score"],
                        rec.technical_assessment_score,
                    )
                ):
                    raise UserError("The technical evaluation is signed: its score is frozen.")
                if (
                    "storekeeper_id" in vals
                    and rec.storekeeper_cleared
                    and (vals["storekeeper_id"] or False) != rec.storekeeper_id.id
                ):
                    raise UserError("The storekeeper signed the clearance: it is never re-named.")
                snap = set(vals) & set(SNAPSHOT_FIELDS)
                if (
                    snap
                    and rec.state != "draft"
                    and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in snap)
                ):
                    raise UserError(
                        "%s: the current position, branch and pay are read from the employee "
                        "master when it is recommended, never typed." % rec.name
                    )
            frozen = set(vals) & set(PROPOSAL_FIELDS)
            for rec in self.filtered("id") if frozen else self.browse():
                if rec.state != "draft" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen
                ):
                    raise UserError(
                        "%s left draft: its proposal is frozen. Reset it to draft (before "
                        "approval) or raise a new movement." % rec.name
                    )
        return super().write(vals)

    # ---- approval hooks ----------------------------------------------------------
    def _approval_amount(self) -> float:
        """The monthly pay delta read from the employee's ACTIVE contract plus
        the one-off relocation money. It was proposed_gross - current_gross,
        both typed by the maker: equal figures routed a raise at amount 0 and
        picked the lowest DOFA tier (M21 audit T2)."""
        self.ensure_one()
        delta = 0.0
        if self._fix_pay_changes():
            current = self._fix_active_contract()
            now = self._fix_contract_gross(current) if current else (self.current_gross or 0.0)
            delta = abs(self._fix_new_gross() - now)
        return delta + sum(self[f] or 0.0 for f in RELOCATION_MONEY)

    def _approval_preparers(self):
        return self.mapped("initiator_user_id")

    def _fix_pay_changes(self):
        self.ensure_one()
        return any(self[f] for f in PAY_PROPOSALS)

    def _fix_needs_finance(self):
        """Finance clears a pay change AND any relocation money (T3)."""
        self.ensure_one()
        return self._fix_pay_changes() or any(self[f] for f in RELOCATION_MONEY)

    def _fix_tech_eval_required(self):
        """A technical promotion, a tier change or a named evaluator needs the
        technical evaluation; other movements may go from concurrence to HR."""
        self.ensure_one()
        return bool(
            self.movement_category == "technical_promotion"
            or self.to_repair_tier
            or self.technical_evaluator_id
        )

    # ---- the employee's contract (what payroll pays) -----------------------------
    def _fix_active_contract(self):
        self.ensure_one()
        return (
            self.env["fix.employment.contract"]
            .sudo()
            .search([("employee_id", "=", self.employee_id.id), ("state", "=", "active")], limit=1)
        )

    @staticmethod
    def _fix_contract_gross(contract):
        return sum((contract[c] or 0.0) for c, _p in COMPONENTS if c in contract._fields)

    def _fix_new_gross(self):
        """The gross the new contract version will carry: each proposed
        component, else the active contract's."""
        self.ensure_one()
        current = self._fix_active_contract()
        total = 0.0
        for comp, prop in COMPONENTS:
            if prop and self[prop]:
                total += self[prop]
            elif current and comp in current._fields:
                total += current[comp] or 0.0
        return total

    def _fix_check_pay_terms(self):
        """Payroll pays the CONTRACT components. A gross-only raise reached the
        employee master's wage and an unchanged contract version, so payroll
        kept paying the old figure (M21 audit T1)."""
        self.ensure_one()
        if not self._fix_pay_changes():
            return
        current = self._fix_active_contract()
        if not current:
            raise UserError(
                "%s changes pay but %s has no active employment contract: payroll pays from "
                "the contract, so activate the hire contract first (Hire / Onboard)."
                % (self.name, self.employee_id.name)
            )
        has_component = any(self[p] for _c, p in COMPONENTS if p)
        if self.proposed_gross and not has_component:
            raise UserError(
                "%s proposes a gross of %.2f with no component: state the basic and the "
                "allowances that make it up (payroll pays the contract components)."
                % (self.name, self.proposed_gross)
            )
        new_gross = self._fix_new_gross()
        if self.proposed_gross and abs(self.proposed_gross - new_gross) > 0.5:
            raise UserError(
                "%s: the proposed gross %.2f does not equal its components (%.2f: basic and "
                "allowances, unchanged ones from the active contract)."
                % (self.name, self.proposed_gross, new_gross)
            )

    def _fix_refuse_second_open(self):
        """One open movement per employee: a second one applied on top of the
        first from stale figures and versioned the contract twice (T10)."""
        for rec in self:
            other = self.sudo().search_count(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("state", "in", OPEN_STATES),
                    ("id", "!=", rec.id),
                ]
            )
            if other:
                raise UserError(
                    "%s already has an open movement: finish or cancel it before raising "
                    "another." % rec.employee_id.name
                )

    def _fix_snapshot_current(self):
        """The 'from' side is the employee master and the active contract at
        recommendation, never typed (T7): the employee.moved event and the
        M29 mover review read it."""
        for rec in self:
            emp = rec.employee_id.sudo()
            band_back = {v: k for k, v in BAND_MAP.items() if k != "M1"}
            band_back["band_6"] = "M1"
            tier_back = {v: k for k, v in TIER_MAP.items()}
            contract = rec._fix_active_contract()
            vals = {
                "from_operating_unit_id": emp.operating_unit_id.id or False,
                "from_department_id": emp.department_id.id or False,
                "from_position_id": emp.position_id.id or False,
                "from_job_title": emp.job_title or False,
                "from_manager_id": emp.parent_id.id or False,
                "from_grade_band": band_back.get(emp.job_band) or False,
                "from_repair_tier": tier_back.get(emp.repair_tier) or False,
            }
            if contract:
                vals["current_basic"] = contract.basic_monthly or 0.0
                vals["current_gross"] = rec._fix_contract_gross(contract)
            rec.sudo()._guarded().write(vals)

    def _fix_proposal_digest(self):
        self.ensure_one()
        out = {}
        for name in PROPOSAL_FIELDS:
            value = self[name]
            out[name] = value.id if isinstance(value, models.BaseModel) else value
        return digest(out)

    def _fix_signers(self):
        self.ensure_one()
        users = self.env["res.users"]
        for step in STEPS.values():
            users |= self[step[2]]
        return users

    def _fix_barred(self, rec):
        return rec._fix_signers() | rec.initiator_user_id

    def _fix_sign(self, step, state):
        approval, emp_stamp, user_stamp, date_stamp = STEPS[step]
        for rec in self:
            rec._hr_refuse_conflicted("sign this step of", extra=rec._fix_barred)
            user = self.env.user
            # the owner was checked above; a line manager holds no write ACL
            rec.sudo()._guarded().write(
                {
                    "state": state,
                    approval: "approved",
                    emp_stamp: user.employee_id.id or False,
                    user_stamp: user.id,
                    date_stamp: fields.Date.context_today(self),
                }
            )
            rec.sudo().message_post(
                body="%s: %s by %s." % (rec.name, approval.replace("_", " "), user.name)
            )

    def _fix_owner(self, users, fallback_group, what, barred=None):
        """The acting user must be one of `users`; when there is nobody (or
        only a conflicted person) the role in `fallback_group` acts."""
        for rec in self:
            if self.env.su:
                continue
            excluded = barred(rec) if barred else rec._fix_barred(rec)
            owners = users(rec) - excluded - rec._hr_subject_users() - rec.sudo().create_uid
            if owners:
                if self.env.user not in owners:
                    raise UserError(
                        "%s is decided by %s." % (what, ", ".join(owners.mapped("name")))
                    )
            elif not self.env.user.has_group(fallback_group):
                raise UserError("%s needs the %s role here." % (what, fallback_group))

    # ---- the steps ---------------------------------------------------------------
    def action_recommend(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft movement requisition can be recommended.")
            if rec.effective_date and rec.effective_date < fields.Date.context_today(self):
                raise UserError(
                    "%s takes effect on %s, a date already past: a movement is never "
                    "back-dated (payroll runs already paid the old terms)."
                    % (rec.name, rec.effective_date)
                )
        self._fix_refuse_second_open()
        self._fix_snapshot_current()
        for rec in self:
            rec._fix_check_pay_terms()
        self._fix_owner(
            lambda r: r.employee_id.sudo().parent_id.user_id, OFFICER, "The recommendation"
        )
        self._fix_sign("recommend", "recommended")
        return True

    def action_concur(self):
        for rec in self:
            if rec.state != "recommended":
                raise UserError(
                    "Movement must be recommended by Origin Manager before Destination Concurrence."
                )
        self._fix_owner(lambda r: r.to_manager_id.sudo().user_id, OFFICER, "The concurrence")
        self._fix_sign("concur", "concurred")
        return True

    def action_tech_eval(self):
        for rec in self:
            # after the destination's concurrence: evaluating straight from
            # "recommended" skipped the receiving manager altogether (T4)
            if rec.state != "concurred":
                raise UserError(
                    "Movement must be concurred by the destination manager before Technical "
                    "Evaluation."
                )
            if not 0 <= (rec.technical_assessment_score or 0.0) <= 100:
                raise UserError("The technical assessment score is a 0-100 figure.")
        self._fix_owner(
            lambda r: r.technical_evaluator_id.sudo().user_id, OFFICER, "The technical evaluation"
        )
        self._fix_sign("tech", "tech_evaluated")
        return True

    def action_hr_audit(self):
        for rec in self:
            if rec.state not in ("concurred", "tech_evaluated"):
                raise UserError(
                    "Movement must pass Destination Concurrence or Technical Evaluation before HR Audit."
                )
            if rec.state == "concurred" and rec._fix_tech_eval_required():
                raise UserError(
                    "%s needs its technical evaluation before the HR audit (technical "
                    "promotion, tier change or a named evaluator)." % rec.name
                )
        self._hr_require(OFFICER, "The HR audit")
        self._fix_sign("hr", "hr_audited")
        return True

    def action_finance_approve(self):
        for rec in self:
            if rec.state != "hr_audited":
                raise UserError("Movement must pass HR Compliance Audit before Finance Clearance.")
        self._hr_require(FINANCE, "The finance clearance")
        self._fix_sign("finance", "finance_approved")
        return True

    def action_request_approval(self, justification=None):
        """Route the movement to the executive (M63)."""
        for rec in self:
            needed = (
                "finance_approved"
                if rec._fix_needs_finance()
                else ("hr_audited", "finance_approved")
            )
            if rec.state not in (needed if isinstance(needed, tuple) else (needed,)):
                raise UserError(
                    "%s needs %s before the executive decision."
                    % (
                        rec.name,
                        "Finance clearance (pay or relocation money changes)"
                        if rec._fix_needs_finance()
                        else "the HR audit",
                    )
                )
            rec._fix_check_pay_terms()
            if rec.to_position_id:
                rec._fix_check_seat()
            rec._guarded().write({"approved_digest": rec._fix_proposal_digest()})
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """The executive decision, run from the approval inbox only."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state not in ("finance_approved", "hr_audited"):
                raise UserError(
                    "Movement must be Finance Cleared (or HR Audited) before Executive Approval."
                )
            if rec._fix_needs_finance() and rec.state != "finance_approved":
                raise UserError("A pay change or relocation money needs Finance clearance first.")
            if rec.approved_digest != rec._fix_proposal_digest():
                raise UserError("%s changed after it was routed; route it again." % rec.name)
            decider = rec._people_decider()
            if not self.env.su and decider in rec._fix_signers():
                raise UserError("You already signed another step of %s." % rec.name)
            rec._guarded().write(
                {
                    "state": "approved",
                    "executive_approval": "approved",
                    "executive_id": decider.employee_id.id or False,
                    "executive_user_id": decider.id,
                    "executive_date": fields.Date.context_today(self),
                }
            )
        return True

    def _approval_on_rejected(self, comment):
        self._guarded().write(
            {"state": "rejected", "executive_approval": "rejected", "rejection_reason": comment}
        )

    # ---- custody ticks: one owner each ---------------------------------------------
    def _fix_tick(self, tick):
        owner = CUSTODY[tick]
        for rec in self:
            if rec.state != "approved":
                raise UserError("Custody is cleared after the executive approval.")
            rec._hr_refuse_conflicted("clear custody on", extra=lambda r: r.initiator_user_id)
            if owner == "line_manager":
                rec._fix_owner(
                    lambda r: r.employee_id.sudo().parent_id.user_id,
                    CLEAR_ASSETS,
                    "This clearance",
                    barred=lambda r: r.initiator_user_id,
                )
            elif owner == "storekeeper":
                rec._fix_owner(
                    lambda r: r.storekeeper_id.sudo().user_id,
                    CLEAR_ASSETS,
                    "This clearance",
                    barred=lambda r: r.initiator_user_id,
                )
            else:
                rec._hr_require(owner, "This clearance")
            rec.sudo()._guarded().write({tick: True, "%s_by_id" % tick: self.env.uid})
        return True

    def action_tick_open_jobs(self):
        return self._fix_tick("open_jobs_audited")

    def action_tick_toolkit(self):
        return self._fix_tick("toolkit_returned")

    def action_tick_spare_parts(self):
        return self._fix_tick("spare_parts_reconciled")

    def action_tick_storekeeper(self):
        return self._fix_tick("storekeeper_cleared")

    def action_tick_imprest(self):
        return self._fix_tick("imprest_cash_settled")

    def action_clear_handover(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError(
                    "Movement must be Executive Approved before clearing handover custody."
                )
            rec._hr_require(OFFICER, "Clearing the handover")
            # the subject and the initiator never clear their own handover (T17)
            rec._hr_refuse_conflicted("clear the handover of", extra=lambda r: r.initiator_user_id)
            rec._check_custody_gate()
            rec._guarded().write({"state": "handover_cleared"})
        return True

    # ---- apply -----------------------------------------------------------------------
    def _fix_check_seat(self):
        self.ensure_one()
        position = self.to_position_id.sudo()
        holders = position.employee_ids - self.employee_id
        if (
            self.to_operating_unit_id
            and position.operating_unit_id
            and position.operating_unit_id != self.to_operating_unit_id
        ):
            raise UserError(
                "Position %s belongs to %s, not the destination branch %s."
                % (position.name, position.operating_unit_id.name, self.to_operating_unit_id.name)
            )
        # 0 sanctioned seats is a full position, as the hr.employee seat
        # constraint reads it; treating 0 as unlimited let routing pass and
        # the apply fail after every approval (T12)
        if len(holders) >= (position.headcount or 0):
            raise UserError(
                "Position %s is full (%d of %d sanctioned seats): no dual occupancy (BRU-HCM-10)."
                % (position.name, len(holders), position.headcount)
            )

    def action_apply(self):
        for rec in self:
            if rec.state != "handover_cleared":
                raise UserError(
                    "Movement must be approved and handover cleared before applying to employee master."
                )
            rec._hr_require(OFFICER, "Applying a movement")
            rec._hr_refuse_conflicted("apply")
            if rec.approval_state != "approved" or rec.executive_approval != "approved":
                raise UserError("%s has no executive approval." % rec.name)
            if rec.approved_digest != rec._fix_proposal_digest():
                raise UserError("%s differs from what was approved." % rec.name)
            if rec.effective_date and rec.effective_date > fields.Date.context_today(self):
                # the master moved at once whatever the date: payroll costed the
                # new branch and M29 reviewed access weeks early (T5)
                raise UserError(
                    "%s takes effect on %s: apply it on or after that date."
                    % (rec.name, rec.effective_date)
                )
            rec._fix_apply_to_master()
        return True

    def _fix_apply_to_master(self):
        self.ensure_one()
        rec = self
        vals = {"form7_last_event_date": rec.effective_date or fields.Date.context_today(self)}
        if rec.to_position_id:
            rec._fix_check_seat()
            vals["position_id"] = rec.to_position_id.id
        if rec.to_operating_unit_id:
            vals["operating_unit_id"] = rec.to_operating_unit_id.id
        if rec.to_department_id:
            vals["department_id"] = rec.to_department_id.id
        if rec.to_job_title:
            vals["job_title"] = rec.to_job_title
        if rec.to_manager_id:
            vals["parent_id"] = rec.to_manager_id.id
        if rec.to_grade_band:
            vals["job_band"] = BAND_MAP.get(rec.to_grade_band, rec.to_grade_band)
        if rec.to_repair_tier:
            vals["repair_tier"] = TIER_MAP.get(rec.to_repair_tier, rec.to_repair_tier)
        if rec.esd_certified:
            vals["esd_certified"] = True
        if rec.bga_license:
            vals["bga_rework_capable"] = True
        if rec.oem_brand_authorizations:
            vals["oem_brand_certs"] = rec.oem_brand_authorizations
        # the master's gross is the new contract's gross (the components),
        # never a typed total payroll would not pay (T1)
        if rec._fix_pay_changes():
            vals["wage"] = rec._fix_new_gross()
        pay_map = {
            "proposed_basic": "basic_wage",
            "proposed_house_rent": "house_rent",
            "proposed_medical": "medical_allowance",
            "proposed_conveyance": "conveyance_allowance",
            "proposed_skill_allowance": "technical_allowance",
        }
        for src, dst in pay_map.items():
            if rec[src]:
                vals[dst] = rec[src]
        if rec.to_tax_location:
            tax_map = {"dhaka_chittagong": "dhaka_chattogram"}
            vals["minimum_tax_location"] = tax_map.get(rec.to_tax_location, rec.to_tax_location)
        rec.employee_id.sudo().with_context(fix_movement_event=True)._guarded().write(vals)
        # BRU-HCM-03: a pay change is a new contract version, never an edit.
        contract = self.env["fix.employment.contract"]
        if rec._fix_pay_changes():
            active = contract.sudo().search(
                [("employee_id", "=", rec.employee_id.id), ("state", "=", "active")], limit=1
            )
            if active:
                changes = {
                    "legal_signoff_state": "covered",
                    "movement_id": rec.id,
                }
                for src, dst in (
                    ("proposed_basic", "basic_monthly"),
                    ("proposed_house_rent", "house_rent"),
                    ("proposed_medical", "medical_allowance"),
                    ("proposed_conveyance", "conveyance_allowance"),
                    ("proposed_skill_allowance", "technical_allowance"),
                ):
                    if rec[src]:
                        changes[dst] = rec[src]
                effective = rec.effective_date or fields.Date.context_today(self)
                contract = active._guarded().create(active._fix_version_vals(effective, **changes))
        rec._guarded().write(
            {"state": "applied", "applied_by_id": self.env.uid, "new_contract_id": contract.id}
        )
        if contract and (
            contract.effective_date or contract.joining_date
        ) <= fields.Date.context_today(self):
            contract._fix_activate()
        publish(
            self.env,
            "employee.moved",
            "fix.hr.transfer",
            rec.id,
            {
                "employee_id": rec.employee_id.id,
                "employee_code": rec.employee_id.employee_code or "",
                "department": (
                    rec.to_department_id.name or rec.employee_id.department_id.name or ""
                ),
                "from_branch": rec.from_operating_unit_id.name or "",
                "to_branch": rec.to_operating_unit_id.name or "",
                "from_position": rec.from_position_id.name or "",
                "to_position": rec.to_position_id.name or "",
                "from_tier": rec.from_repair_tier or "",
                "to_tier": rec.to_repair_tier or "",
                "effective_date": str(rec.effective_date or ""),
                "movement_type": rec.movement_type,
            },
        )

    # ---- cancel / reset ----------------------------------------------------------------
    def action_cancel(self):
        for rec in self:
            if rec.state in ("applied", "cancelled"):
                raise UserError("An applied or cancelled movement cannot be cancelled.")
            if not (
                self.env.su
                or self.env.user.has_group(OFFICER)
                or rec.initiator_user_id == self.env.user
            ):
                raise UserError("Only HR or the initiator cancels a movement.")
            req = rec.approval_request_id.sudo()
            if rec.approval_state == "pending" and req.state == "pending":
                req._finish("recalled", "recalled", self.env.user, record_state="none")
            rec._guarded().write({"state": "cancelled"})
        return True

    def action_reset_draft(self):
        """Back to draft only BEFORE the executive decision; the signatures go."""
        for rec in self:
            if rec.state in ("approved", "handover_cleared", "applied") or (
                rec.executive_approval == "approved"
            ):
                raise UserError(
                    "%s was approved: it never returns to draft. Cancel it or raise a new one."
                    % rec.name
                )
            if rec.approval_state == "pending":
                raise UserError(
                    "%s is awaiting the executive decision; recall it first." % rec.name
                )
            rec._hr_require(OFFICER, "Resetting a movement")
            vals = {"state": "draft", "approved_digest": False}
            for approval, emp_stamp, user_stamp, date_stamp in STEPS.values():
                vals.update(
                    {approval: "pending", emp_stamp: False, user_stamp: False, date_stamp: False}
                )
            rec._guarded().write(vals)
        return True
