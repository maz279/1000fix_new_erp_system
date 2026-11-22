# cd_hr_core — employment contract controls (A09 workflow audit M21-8, B1-B5,
# C2, C5, P2 "contract versioning", "probation confirmation").
#
# The audit found every contract rule inside one button: a contract created
# already 'active' carried a 375-day probation, 72 h a week and a zero basic;
# probation was extended after activation; two active contracts per employee
# (21 live); active contracts edited in place, including an HR Officer's own
# basic; the legal sign-off approved by its drafter and never required. Here:
#
#   * the statutory limits are constraints, so no path (create, write, P03,
#     import) saves a contract past them;
#   * state, the sign-off and every stamp are guarded; the terms of a contract
#     that left draft are frozen: a change is a NEW VERSION (BRU-HCM-03);
#   * the legal sign-off is a routed M63 request decided by Legal Counsel,
#     never by the drafter, the requester or the employee; activation needs
#     it, and the terms it covered are pinned;
#   * one active contract per employee;
#   * probation is confirmed, extended (skilled workers, once) or deemed
#     confirmed by the cron at its end (BLA s.4(8)); fixed-term contracts
#     raise 90/60/30-day alerts and expire on their end date;
#   * a contract ends only through the employee's exit (I3), never by a
#     one-click "Terminate".
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_hr_controls_common import (
    LEGAL,
    OFFICER,
    PROBATION_MONTHS,
    PROBATION_SKILLED_EXTENSION_MONTHS,
    digest,
)

PAY_TERMS = (
    "basic_monthly",
    "house_rent",
    "medical_allowance",
    "conveyance_allowance",
    "technical_allowance",
    "other_allowance",
    "dearness_allowance",
    "adhoc_allowance",
)
# BLR 2015 r.19(4) particulars of the letter of appointment that are terms of
# the contract (A09 ERP audit M21-F2). Optional: a blank one is no term, so a
# sign-off requested before these fields existed stays valid (see _fix_terms).
R194_TERMS = ("wage_scale", "increment_rate", "other_facilities")
CONTRACT_TERMS = (
    "employee_id",
    "company_id",
    "contract_type",
    "joining_date",
    "effective_date",
    "probation_end",
    "probation_class",
    "weekly_hours",
    "currency_id",
    "date_end",
    *PAY_TERMS,
    *R194_TERMS,
)
EXPIRY_ALERT_DAYS = (90, 60, 30)  # AUT-HCM-06 fixed-term expiry alerts
PROBATION_ALERT_DAYS = 14


class FixEmploymentContractControls(models.Model):
    _name = "fix.employment.contract"
    _inherit = [
        "fix.employment.contract",
        "fix.people.approval.mixin",
        "fix.hr.control.mixin",
    ]

    # The legal sign-off is the contract's routed approval (SOD-25: the
    # drafter, the requester and the employee never decide it).
    _approval_domain = "hr_contract"
    _approval_apply_method = "action_approve_legal_signoff"
    _approval_group = LEGAL

    state = fields.Selection(
        selection_add=[("superseded", "Superseded by a New Version")],
        ondelete={"superseded": "set default"},
    )
    legal_signoff_state = fields.Selection(
        selection_add=[("covered", "Covered by an Approved Movement")],
        ondelete={"covered": "set default"},
    )
    date_end = fields.Date(
        string="End Date",
        help="Fixed-term end, or the last working day set when the exit is settled (I3)",
    )
    effective_date = fields.Date(
        string="Terms Effective From",
        help="When this version's terms apply. The joining date stays the original "
        "one (payroll counts service from it).",
    )
    probation_class = fields.Selection(
        [
            ("clerical", "Clerical (6 months)"),
            ("skilled", "Skilled (3 months, extendable by 3)"),
            ("other", "Other (3 months)"),
        ],
        string="Probation Class (BLA s.4(8))",
        default="clerical",
        help="Sets the statutory probation cap. Default keeps the 6-month cap the code used.",
    )
    probation_extended = fields.Boolean(readonly=True, copy=False)
    probation_decision = fields.Selection(
        [
            ("confirmed", "Confirmed"),
            ("deemed", "Deemed Permanent (s.4(8))"),
            ("extended", "Extended"),
        ],
        readonly=True,
        copy=False,
    )
    probation_decided_on = fields.Date(readonly=True, copy=False)
    probation_decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    probation_alert_sent = fields.Boolean(readonly=True, copy=False)
    previous_contract_id = fields.Many2one(
        "fix.employment.contract", string="Previous Version", readonly=True, copy=False
    )
    superseded_by_id = fields.Many2one(
        "fix.employment.contract", string="Superseded By", readonly=True, copy=False
    )
    movement_id = fields.Many2one(
        "fix.hr.transfer", string="Approved Movement", readonly=True, copy=False
    )
    legal_signoff_by_id = fields.Many2one(
        "res.users", string="Signed Off By", readonly=True, copy=False
    )
    legal_signoff_on = fields.Datetime(string="Signed Off On", readonly=True, copy=False)
    signoff_digest = fields.Char(readonly=True, copy=False)
    activated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    activated_on = fields.Datetime(readonly=True, copy=False)
    expiry_alert_days = fields.Integer(
        readonly=True, copy=False, help="Smallest expiry alert sent (90/60/30)"
    )
    termination_exit_id = fields.Many2one(
        "fix.hr.exit", string="Ended By Exit", readonly=True, copy=False
    )

    # ---- guard --------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "legal_signoff_state",
            "signed_by_legal_counsel",
            "legal_signoff_by_id",
            "legal_signoff_on",
            "signoff_digest",
            "document_id",
            "probation_extended",
            "probation_decision",
            "probation_decided_on",
            "probation_decided_by_id",
            "probation_alert_sent",
            "previous_contract_id",
            "superseded_by_id",
            "movement_id",
            "activated_by_id",
            "activated_on",
            "expiry_alert_days",
            "termination_exit_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(CONTRACT_TERMS)
        return locked

    def _approval_amount(self) -> float:
        return sum(self[f] or 0.0 for f in PAY_TERMS)

    def _fix_terms(self):
        self.ensure_one()
        out = {}
        for name in CONTRACT_TERMS:
            value = self[name]
            if name in R194_TERMS and not str(value or "").strip():
                continue
            out[name] = value.id if isinstance(value, models.BaseModel) else value
        return out

    def _fix_terms_digest(self):
        return digest(self._fix_terms())

    def write(self, vals):
        voided = self.browse()
        if not self._fix_guard_open():
            terms = set(vals) & set(CONTRACT_TERMS)
            for rec in self.filtered("id") if terms else self.browse():
                changed = [n for n in terms if rec._fix_guard_differs(n, vals[n], rec[n])]
                if not changed:
                    continue
                if rec.state != "draft":
                    raise UserError(
                        "%s is %s: a contract's terms are never edited after it leaves "
                        "draft (BRU-HCM-03). Create a new version." % (rec.name, rec.state)
                    )
                if rec.approval_state in ("pending", "approved") or rec.legal_signoff_state in (
                    "approved",
                    "covered",
                ):
                    voided |= rec
        result = super().write(vals)
        for rec in voided:
            rec._approval_void("the contract terms changed after the legal sign-off")
            rec._guarded().write(
                {
                    "legal_signoff_state": "pending",
                    "signed_by_legal_counsel": False,
                    "legal_signoff_by_id": False,
                    "legal_signoff_on": False,
                    "signoff_digest": False,
                }
            )
        return result

    # ---- statutory limits (constraints: every path) --------------------------
    def _fix_probation_cap(self):
        self.ensure_one()
        months = PROBATION_MONTHS.get(self.probation_class or "clerical", 6)
        if self.probation_class == "skilled" and self.probation_extended:
            months += PROBATION_SKILLED_EXTENSION_MONTHS
        return months

    def _fix_statutory_errors(self):
        self.ensure_one()
        errors = []
        if (self.basic_monthly or 0.0) <= 0:
            errors.append("Basic salary must be positive")
        cap = (self.company_id or self.env.company).fix_hr_contract_weekly_hours_cap or 48.0
        if (self.weekly_hours or 0.0) > cap:
            errors.append("s.102: weekly hours may not exceed %g" % cap)
        joining = self.joining_date
        if self.probation_end and joining:
            if self.probation_end < joining:
                errors.append("Probation cannot end before the joining date")
            months = self._fix_probation_cap()
            if self.probation_end > joining + relativedelta(months=months):
                errors.append(
                    "Probation exceeds the %d-month statutory cap for a %s worker (BLA s.4(8))"
                    % (months, self.probation_class or "clerical")
                )
        if self.date_end and joining and self.date_end < joining:
            errors.append("The contract cannot end before the joining date")
        if self.effective_date and joining and self.effective_date < joining:
            errors.append("A version's terms cannot take effect before the joining date")
        if self.state == "active" and self.contract_type == "probation" and not self.probation_end:
            errors.append("An active probation contract needs its probation end date (s.4(8))")
        return errors

    @api.constrains(
        "basic_monthly",
        "weekly_hours",
        "probation_end",
        "probation_class",
        "probation_extended",
        "joining_date",
        "effective_date",
        "date_end",
        "contract_type",
        "state",
    )
    def _check_statutory_terms(self):
        for rec in self:
            errors = rec._fix_statutory_errors()
            if errors:
                raise ValidationError(errors[0])

    @api.constrains("state", "employee_id")
    def _check_one_active_contract(self):
        for rec in self.filtered(lambda r: r.state == "active"):
            others = self.sudo().search_count(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("state", "=", "active"),
                    ("id", "!=", rec.id),
                ]
            )
            if others:
                raise ValidationError(
                    "%s already has an active contract: one active contract per employee "
                    "(payroll reads exactly one). Version it instead." % rec.employee_id.name
                )

    def _validate_statutory(self):
        for rec in self:
            errors = rec._fix_statutory_errors()
            if errors:
                raise ValidationError(errors[0])

    # ---- legal sign-off (routed) ----------------------------------------------
    def action_request_legal_signoff(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Legal sign-off is requested for a draft contract.")
            rec._hr_require(OFFICER, "Requesting a legal sign-off")
            rec._validate_statutory()
            rec._guarded().write(
                {"legal_signoff_state": "pending", "signoff_digest": rec._fix_terms_digest()}
            )
            rec.action_request_approval()
        return True

    def action_approve_legal_signoff(self):
        """Legal Counsel's decision, run from the approval inbox only."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft contract is signed off.")
            if not rec.signoff_digest or rec.signoff_digest != rec._fix_terms_digest():
                raise UserError(
                    "%s changed after the sign-off was requested; request it again." % rec.name
                )
            decider = rec._people_decider()
            rec._guarded().write(
                {
                    "legal_signoff_state": "approved",
                    "signed_by_legal_counsel": decider.name,
                    "legal_signoff_by_id": decider.id,
                    "legal_signoff_on": fields.Datetime.now(),
                }
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec._guarded().write({"legal_signoff_state": "rejected"})
            rec.message_post(body="Legal sign-off rejected: %s" % (comment or ""))

    # ---- activation -------------------------------------------------------------
    def action_activate(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft contract can be activated.")
            rec._hr_require(OFFICER, "Activating a contract")
            if not self.env.su and self.env.user in rec._hr_subject_users():
                raise UserError("You cannot activate your own contract (SOD-25).")
            if rec.legal_signoff_state == "covered":
                if rec.movement_id.state not in ("handover_cleared", "applied"):
                    raise UserError("The movement covering %s is not approved." % rec.name)
            elif rec.legal_signoff_state != "approved" or rec.approval_state != "approved":
                raise UserError(
                    "%s needs Legal Counsel's sign-off before activation. Request it." % rec.name
                )
            elif rec.signoff_digest != rec._fix_terms_digest():
                raise UserError("%s changed after its legal sign-off." % rec.name)
            if rec.contract_type == "fixed_term" and not rec.date_end:
                raise UserError("A fixed-term contract needs its end date.")
            if rec.contract_type == "probation" and not rec.probation_end:
                raise UserError("A probation contract needs its probation end date (s.4(8)).")
            effective = rec.effective_date or rec.joining_date
            if rec.previous_contract_id and effective > fields.Date.context_today(self):
                raise UserError(
                    "This version takes effect on %s; the daily contract cron activates it "
                    "then." % effective
                )
            rec._validate_statutory()
            rec._fix_activate()
        return True

    def _fix_activate(self):
        """Activate this contract, superseding the version it replaces."""
        for rec in self:
            previous = rec.previous_contract_id
            if previous and previous.state == "active":
                effective = rec.effective_date or rec.joining_date
                previous._guarded().write(
                    {
                        "state": "superseded",
                        "date_end": max(effective - relativedelta(days=1), previous.joining_date),
                        "superseded_by_id": rec.id,
                    }
                )
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_on": fields.Datetime.now(),
                }
            )
            # A version made before the probation was confirmed copied the
            # probation terms; activating it re-ran the probation and the cron
            # deemed the worker permanent a second time (M21 audit F10).
            if (
                previous
                and rec.contract_type == "probation"
                and previous.probation_decision
                and previous.contract_type == "permanent"
            ):
                rec._guarded().write(
                    {
                        "contract_type": "permanent",
                        "probation_decision": previous.probation_decision,
                        "probation_decided_on": previous.probation_decided_on,
                    }
                )
            rec._fix_sync_employee_terms()
            publish(
                self.env,
                "employment.contract.activated",
                "fix.employment.contract",
                rec.id,
                {
                    "employee": rec.employee_id.name,
                    "contract_type": rec.contract_type,
                    "joining": str(rec.joining_date),
                },
            )
            if previous:
                publish(
                    self.env,
                    "contract.versioned",
                    "fix.employment.contract",
                    rec.id,
                    {
                        "employee_id": rec.employee_id.id,
                        "contract": rec.name,
                        "previous_contract_id": previous.id,
                        "effective_date": str(rec.effective_date or rec.joining_date),
                    },
                )
                if any(abs((rec[f] or 0.0) - (previous[f] or 0.0)) > 0.005 for f in PAY_TERMS):
                    publish(
                        self.env,
                        "salary_structure.changed",
                        "fix.employment.contract",
                        rec.id,
                        {
                            "employee_id": rec.employee_id.id,
                            "contract_id": rec.id,
                            "previous_contract_id": previous.id,
                            "previous_basic": previous.basic_monthly,
                            "basic": rec.basic_monthly,
                            "previous_gross": previous._approval_amount(),
                            "gross": rec._approval_amount(),
                            "effective_date": str(rec.effective_date or rec.joining_date),
                        },
                    )

    def _fix_sync_employee_terms(self):
        """The active contract is the employee's terms: the master's wage
        fields, joining date and employment nature follow it. Nothing kept
        them in step, so Form 6/7 and the Form 6(a) register printed zeros and
        stale natures (M21 audit F2)."""
        nature = {
            "permanent": "permanent",
            "probation": "probationary",
            "fixed_term": "contractual",
        }
        for rec in self:
            emp = rec.employee_id.sudo()
            gross = sum(rec[f] or 0.0 for f in PAY_TERMS if f in rec._fields)
            vals = {
                "basic_wage": rec.basic_monthly or 0.0,
                "house_rent": rec.house_rent or 0.0,
                "medical_allowance": rec.medical_allowance or 0.0,
                "conveyance_allowance": rec.conveyance_allowance or 0.0,
                "technical_allowance": rec.technical_allowance or 0.0,
                "wage": gross,
            }
            if rec.contract_type in nature:
                vals["employment_type"] = nature[rec.contract_type]
            first = self.sudo().search(
                [("employee_id", "=", emp.id), ("state", "in", ("active", "superseded"))],
                order="joining_date asc",
                limit=1,
            )
            if first and not emp.joining_date:
                vals["joining_date"] = first.joining_date
            emp.with_context(fix_movement_event=True)._guarded().write(vals)

    # ---- versioning (BRU-HCM-03) -------------------------------------------------
    def _fix_version_vals(self, effective_date, **changes):
        self.ensure_one()
        vals = {k: v for k, v in self._fix_terms().items() if k != "date_end"}
        vals.update(
            {
                "operating_unit_id": self.operating_unit_id.id,
                "template_id": self.template_id.id,
                "effective_date": effective_date,
                "previous_contract_id": self.id,
            }
        )
        vals.update(changes)
        return vals

    def action_new_version(self, effective_date=None):
        """A change to an active contract: a draft copy that, once signed off
        and activated, supersedes this one."""
        self.ensure_one()
        self._hr_require(OFFICER, "Versioning a contract")
        if self.state != "active":
            raise UserError("Only the active contract is versioned.")
        if self.search_count([("previous_contract_id", "=", self.id), ("state", "=", "draft")]):
            raise UserError("%s already has a draft version." % self.name)
        effective = fields.Date.to_date(effective_date) if effective_date else None
        effective = effective or fields.Date.context_today(self)
        new = self._guarded().create(self._fix_version_vals(effective))
        return {"res_model": self._name, "res_id": new.id}

    # ---- ending a contract --------------------------------------------------------
    def action_terminate(self):
        raise UserError(
            "An employment ends through its Exit (Exit & Settlement): the settlement "
            "ends the contract on the last working day and records the leaver. A "
            "contract is never terminated on its own."
        )

    def _fix_end_for_exit(self, exit_rec):
        """I3: the settled exit ends the employee's contract on the last working day."""
        lwd = exit_rec.last_working_day
        for rec in self:
            vals = {"termination_exit_id": exit_rec.id}
            if rec.state == "active":
                vals.update({"state": "terminated", "date_end": lwd})
            elif rec.state == "draft":
                vals.update({"state": "terminated"})
            elif rec.state == "expired" and not rec.date_end:
                vals.update({"date_end": lwd})
            rec._guarded().write(vals)
            publish(
                self.env,
                "employment.contract.terminated",
                "fix.employment.contract",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "contract": rec.name,
                    "date_end": str(lwd),
                    "exit": exit_rec.name,
                },
            )

    # ---- probation (BLA s.4(8)) -----------------------------------------------------
    def _fix_check_probation_decider(self, what):
        for rec in self:
            rec._hr_require(OFFICER, what)
            if not self.env.su and self.env.user in rec._hr_subject_users():
                raise UserError("You cannot decide your own probation.")
            if rec.state != "active" or rec.contract_type != "probation":
                raise UserError("%s is not an active probation contract." % rec.name)

    def action_confirm_probation(self):
        self._fix_check_probation_decider("Confirming a probation")
        self._fix_confirm_probation("confirmed")
        return True

    def action_extend_probation(self):
        """A skilled worker's probation may be extended once by 3 months (s.4(8))."""
        self._fix_check_probation_decider("Extending a probation")
        for rec in self:
            if rec.probation_class != "skilled":
                raise UserError("Only a skilled worker's probation may be extended (BLA s.4(8)).")
            if rec.probation_extended:
                raise UserError("%s was already extended once." % rec.name)
            if rec.probation_end and rec.probation_end < fields.Date.context_today(self):
                raise UserError(
                    "The probation already ended: the worker is deemed permanent (s.4(8))."
                )
            months = PROBATION_MONTHS["skilled"] + PROBATION_SKILLED_EXTENSION_MONTHS
            rec._guarded().write(
                {
                    "probation_extended": True,
                    "probation_end": rec.joining_date + relativedelta(months=months),
                    "probation_decision": "extended",
                    "probation_decided_on": fields.Date.context_today(self),
                    "probation_decided_by_id": self.env.uid,
                }
            )
        return True

    def _fix_confirm_probation(self, decision):
        today = fields.Date.context_today(self)
        for rec in self:
            confirmed_on = (
                rec.probation_end + relativedelta(days=1)
                if decision == "deemed" and rec.probation_end
                else today
            )
            rec._guarded().write(
                {
                    "contract_type": "permanent",
                    "probation_decision": decision,
                    "probation_decided_on": today,
                    "probation_decided_by_id": self.env.uid,
                }
            )
            rec.employee_id.sudo()._guarded().write(
                {"confirmation_date": confirmed_on, "employment_type": "permanent"}
            )
            publish(
                self.env,
                "employee.confirmed",
                "hr.employee",
                rec.employee_id.id,
                {
                    "employee_id": rec.employee_id.id,
                    "contract": rec.name,
                    "confirmation_date": str(confirmed_on),
                    "deemed": decision == "deemed",
                },
            )

    def _fix_activity(self, summary, note):
        self.ensure_one()
        officer = self.env.ref(OFFICER, raise_if_not_found=False)
        users = officer.sudo().all_user_ids.filtered(lambda u: u.active and not u.share)
        self.activity_schedule(
            "mail.mail_activity_data_todo",
            summary=summary,
            note=note,
            user_id=(users[:1] or self.env.user).id,
        )

    @api.model
    def _cron_probation_review(self):
        """Daily: deem permanent every probation past its end with no decision
        (s.4(8), second proviso), and warn HR 14 days before an end."""
        today = fields.Date.context_today(self)
        Contract = self.sudo()
        ended = Contract.search(
            [
                ("state", "=", "active"),
                ("contract_type", "=", "probation"),
                ("probation_end", "<", today),
            ]
        )
        ended._fix_confirm_probation("deemed")
        due = Contract.search(
            [
                ("state", "=", "active"),
                ("contract_type", "=", "probation"),
                ("probation_end", ">=", today),
                ("probation_end", "<=", today + relativedelta(days=PROBATION_ALERT_DAYS)),
                ("probation_alert_sent", "=", False),
            ]
        )
        for rec in due:
            rec._fix_activity(
                "Probation decision due: %s" % rec.employee_id.name,
                "Probation ends on %s. Confirm, extend (skilled) or end it; otherwise the "
                "worker is deemed permanent (BLA s.4(8))." % rec.probation_end,
            )
            rec._guarded().write({"probation_alert_sent": True})
        return len(ended)

    @api.model
    def _cron_contract_expiry(self):
        """Daily: activate versions that took effect, warn 90/60/30 days before
        a fixed-term end, and expire contracts past their end."""
        today = fields.Date.context_today(self)
        Contract = self.sudo()
        due_versions = Contract.search(
            [
                ("state", "=", "draft"),
                ("previous_contract_id", "!=", False),
                ("legal_signoff_state", "in", ("approved", "covered")),
                ("effective_date", "<=", today),
            ]
        )
        for rec in due_versions:
            ready = (
                rec.legal_signoff_state == "covered"
                and rec.movement_id.state in ("handover_cleared", "applied")
            ) or (
                rec.approval_state == "approved" and rec.signoff_digest == rec._fix_terms_digest()
            )
            if rec.contract_type == "fixed_term" and not rec.date_end:
                # action_activate refuses this; the cron activated it and the
                # fixed-term version never expired (M21 audit F11)
                rec._fix_activity(
                    "Version %s has no end date" % rec.name,
                    "A fixed-term contract needs its end date before it takes effect.",
                )
                continue
            if ready and rec.previous_contract_id.state == "active":
                rec._fix_activate()
        running = Contract.search([("state", "=", "active"), ("date_end", "!=", False)])
        expired = running.filtered(lambda c: c.date_end < today)
        for rec in expired:
            rec._guarded().write({"state": "expired"})
            publish(
                self.env,
                "employment.contract.expired",
                "fix.employment.contract",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "contract": rec.name,
                    "date_end": str(rec.date_end),
                },
            )
            rec._fix_activity(
                "Contract expired: %s" % rec.employee_id.name,
                "The contract ended on %s. Record the exit (contract end) or a renewal."
                % rec.date_end,
            )
        for rec in running - expired:
            left = (rec.date_end - today).days
            reached = [t for t in EXPIRY_ALERT_DAYS if left <= t]
            if not reached:
                continue
            threshold = min(reached)
            if rec.expiry_alert_days and threshold >= rec.expiry_alert_days:
                continue  # this alert (or a later one) was already sent
            rec._fix_activity(
                "Contract ends in %d days: %s" % (left, rec.employee_id.name),
                "Fixed-term contract %s ends on %s." % (rec.name, rec.date_end),
            )
            rec._guarded().write({"expiry_alert_days": threshold})
        return len(expired)
