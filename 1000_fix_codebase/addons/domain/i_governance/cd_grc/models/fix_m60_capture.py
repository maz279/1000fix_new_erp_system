# fix_m60_capture — M60 capture audit (2026-11-18): the records the M60
# sub-module pages could not capture because they did not exist.
#
# Page 1 Risk Register
#   * fix.risk.assessment (FR-GRC-003/005, T-01, BRU-GRC-02/03): a dated,
#     never-overwritten assessment. It carries the inherent and residual
#     scores and the next review date onto the risk; the history stays.
#     A risk is not scored before the appetite of its category is stated.
#   * fix.risk.treatment (FR-GRC-004): a treatment decision and its action,
#     with an owner and a date; completion needs the evidence note. A
#     transfer names its instrument (the insurance policy or contract term).
#   * fix.risk.event (FR-GRC-007): a realised event (loss, incident, claim,
#     non-conformance, breach) linked to the risk it realised; the risk
#     owner is asked to reassess.
# Page 2 Control Framework & Testing: key-control designation, nature and
#   objective on the control (FR-GRC-011/012) — fields on fix.control.
# Page 3 SoD & Authority: the M60 rule names the M29 control that enforces it
#   and shows that control's latest measured test (FR-GRC-018/019).
# Page 4 Compliance Obligations
#   * fix.compliance.obligation.occurrence (FR-GRC-024/025, BRU-GRC-12/13):
#     each due instance of an obligation, discharged with evidence — a
#     discharge without evidence is recorded as a control failure, never as
#     a discharge — verified by a Compliance Officer who did not discharge
#     it, and a missed one is recorded as a breach, never quietly closed.
#   * fix.grc.regulatory.change (FR-GRC-026): a regulatory change with its
#     impact assessment on obligations and controls.
# Page 5 Policy Governance
#   * fix.grc.policy.attestation (FR-GRC-030): an employee's own
#     acknowledgement of one version of an approved policy.
#   * fix.grc.policy.exception (FR-GRC-031): a time-boxed exception to a
#     policy, approved by a Compliance Officer who did not request it.
# Page 6 Legal & IP
#   * fix.grc.ip.asset (FR-GRC-028): trademarks, domains, software licences.
#   * the legal matter gains its provision and next action (FR-GRC-038).
# Page 7 PDPA Governance
#   * fix.grc.processing.activity (FR-GRC-033, BRU-GRC-16/17): the record of
#     processing activities; in force only with a lawful basis, retention
#     and safeguards (and an approved PIA when it is high-risk); never
#     deleted.
#   * fix.grc.data.transfer (FR-GRC-034, BRU-GRC-18): the cross-border
#     transfer register; approved only over an activity in force.
#   * fix.grc.data.breach (FR-GRC-036, BRU-GRC-20): the breach register, read
#     by the Compliance Officer and Legal Counsel only; closed only with the
#     assessment and the notification decision.
#   * fix.grc.privacy.impact (FR-GRC-037): the privacy impact assessment,
#     approved by a Compliance Officer who did not author it.
import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_grc import OFFICER_GROUP, RISK_CATEGORIES, RISK_OWNER_GROUP, _require_group

LEGAL_GROUP = "cd_grc.group_grc_legal"
SCORE = [(str(i), str(i)) for i in range(1, 6)]


def _employee(env):
    """The session user's employee, or a refusal: these records name people."""
    employee = env.user.employee_id
    if not employee:
        raise UserError(
            "%s has no employee record: this record is stamped with the employee "
            "who made it." % env.user.name
        )
    return employee


def _require_any(env, groups, why):
    if env.su or any(env.user.has_group(g) for g in groups):
        return
    raise UserError(why)


def _immutable(rec_or_model, vals, allowed=()):
    """A versioned record is never overwritten (BRU-GRC-03): only the named
    fields may change after creation, and only through the record's actions."""
    if rec_or_model.env.su or rec_or_model._fix_guard_has_token():
        return
    blocked = set(vals) - set(allowed)
    if blocked:
        raise UserError(
            "%s is kept as recorded — file a new one instead of changing %s."
            % (rec_or_model._description, ", ".join(sorted(blocked)))
        )


def _require_editor(records, owner_field, why):
    """Plain edits (outside the record's actions) are the owner's or a
    Compliance Officer's; the actions carry the guard token."""
    if records.env.su or records._fix_guard_has_token():
        return
    if records.env.user.has_group(OFFICER_GROUP) or records.env.user.has_group(RISK_OWNER_GROUP):
        return
    for rec in records:
        owner = rec[owner_field]
        if not (owner and owner.user_id == records.env.user):
            # a record not saved yet has no name: say what it is
            raise UserError(why % (rec.display_name or rec._description))


# ====================================================================== page 1
class FixRiskAssessment(models.Model):
    _name = "fix.risk.assessment"
    _description = "Risk Assessment"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "assessed_on desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    risk_id = fields.Many2one("fix.risk.register", required=True, index=True, ondelete="cascade")
    category = fields.Selection(related="risk_id.category", store=True)
    assessed_on = fields.Date(required=True, default=fields.Date.context_today, readonly=True)
    assessed_by_id = fields.Many2one("hr.employee", string="Assessed By", readonly=True)
    likelihood = fields.Selection(SCORE, string="Inherent Likelihood", required=True)
    impact = fields.Selection(SCORE, string="Inherent Impact", required=True)
    inherent_score = fields.Integer(compute="_compute_scores", store=True)
    residual_likelihood = fields.Selection(SCORE, string="Residual Likelihood")
    residual_impact = fields.Selection(SCORE, string="Residual Impact")
    residual_score = fields.Integer(compute="_compute_scores", store=True)
    controls_relied_on = fields.Char(
        string="Controls Relied On", compute="_compute_controls", store=True
    )
    rationale = fields.Text(required=True, help="Why the scores are what they are.")
    next_review_date = fields.Date(string="Next Review Due", required=True)
    previous_residual = fields.Integer(string="Previous Residual Score", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "assessed_on",
            "assessed_by_id",
            "previous_residual",
        }

    @api.depends("risk_id", "assessed_on")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s · %s" % (rec.risk_id.name or "Risk", rec.assessed_on or "")

    @api.depends("likelihood", "impact", "residual_likelihood", "residual_impact")
    def _compute_scores(self):
        for rec in self:
            rec.inherent_score = int(rec.likelihood or 0) * int(rec.impact or 0)
            rec.residual_score = int(rec.residual_likelihood or 0) * int(rec.residual_impact or 0)

    @api.depends("risk_id")
    def _compute_controls(self):
        for rec in self:
            active = rec.risk_id.control_ids.filtered(lambda c: c.state == "active")
            rec.controls_relied_on = ", ".join(active.mapped("name"))[:250] or "—"

    @api.constrains("assessed_on", "next_review_date")
    def _check_review_ahead(self):
        for rec in self:
            if rec.next_review_date and rec.next_review_date <= rec.assessed_on:
                raise ValidationError(
                    "The next review of '%s' must fall after the assessment (FR-GRC-005)."
                    % rec.risk_id.name
                )

    @api.constrains("residual_likelihood", "residual_impact")
    def _check_residual_pair(self):
        for rec in self:
            if bool(rec.residual_likelihood) != bool(rec.residual_impact):
                raise ValidationError("Assess the residual likelihood and impact together.")

    @api.model_create_multi
    def create(self, vals_list):
        _require_any(
            self.env,
            (RISK_OWNER_GROUP, OFFICER_GROUP),
            "Only a Risk Owner or a Compliance Officer assesses a risk (BRU-GRC-01).",
        )
        employee = _employee(self.env) if not self.env.su else self.env.user.employee_id
        Appetite = self.env["fix.risk.appetite"].sudo()
        for vals in vals_list:
            risk = self.env["fix.risk.register"].browse(vals.get("risk_id"))
            if risk.state == "closed":
                raise UserError("'%s' is closed — reopen it before assessing it." % risk.name)
            if not Appetite.search_count(
                [("category", "=", risk.category), ("company_id", "=", risk.company_id.id)]
            ):
                raise UserError(
                    "The appetite of the '%s' category is not stated: a risk is not "
                    "scored before the appetite is declared (BRU-GRC-02). Ask the "
                    "Compliance Officer to state it on the Risk Appetite register."
                    % dict(RISK_CATEGORIES).get(risk.category, risk.category)
                )
            vals["company_id"] = risk.company_id.id
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write(
                {
                    "assessed_by_id": employee.id if employee else False,
                    "previous_residual": rec.risk_id.residual_score or 0,
                }
            )
            rec._apply_to_risk()
        return recs

    def write(self, vals):
        _immutable(self, vals)
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A risk assessment is history (BRU-GRC-03): it is never deleted.")
        return super().unlink()

    def _apply_to_risk(self):
        """The latest assessment is the risk's current position; earlier ones
        stay as they were (T-01)."""
        for rec in self:
            vals = {
                "likelihood": rec.likelihood,
                "impact": rec.impact,
                "review_date": rec.next_review_date,
            }
            if rec.residual_likelihood:
                vals.update(
                    residual_likelihood=rec.residual_likelihood,
                    residual_impact=rec.residual_impact,
                )
            rec.risk_id.sudo().write(vals)
            rec.risk_id.message_post(
                body="Assessed by %s on %s: inherent %d, residual %s (was %s). Next review %s."
                % (
                    rec.assessed_by_id.name or self.env.user.name,
                    rec.assessed_on,
                    rec.inherent_score,
                    rec.residual_score or "not assessed",
                    rec.previous_residual or "not assessed",
                    rec.next_review_date,
                )
            )


class FixRiskTreatment(models.Model):
    _name = "fix.risk.treatment"
    _description = "Risk Treatment Action"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "due_on, id"

    name = fields.Char(string="Action", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    risk_id = fields.Many2one("fix.risk.register", required=True, index=True, ondelete="cascade")
    strategy = fields.Selection(
        [
            ("mitigate", "Mitigate"),
            ("transfer", "Transfer (insurance / contract)"),
            ("avoid", "Avoid (activity ceases)"),
            ("accept", "Accept"),
        ],
        required=True,
        default="mitigate",
    )
    rationale = fields.Text(required=True)
    transfer_instrument = fields.Char(
        string="Transfer Instrument",
        help="The insurance policy number or contract clause that carries the risk.",
    )
    owner_id = fields.Many2one("hr.employee", string="Action Owner", required=True)
    due_on = fields.Date(string="Due", required=True)
    target_residual_score = fields.Integer(string="Target Residual Score")
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("in_progress", "In Progress"),
            ("done", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="planned",
        tracking=True,
    )
    completion_note = fields.Text(readonly=True)
    completed_on = fields.Date(readonly=True)
    completed_by_id = fields.Many2one("res.users", readonly=True)
    overdue = fields.Boolean(compute="_compute_overdue")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "completion_note",
            "completed_on",
            "completed_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and set(self.mapped("state")) & {"done", "cancelled"}:
            locked |= {"name", "risk_id", "strategy", "rationale", "owner_id", "due_on"}
        return locked

    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.overdue = rec.state in ("planned", "in_progress") and bool(
                rec.due_on and rec.due_on < today
            )

    @api.constrains("strategy", "transfer_instrument")
    def _check_transfer_instrument(self):
        for rec in self:
            if rec.strategy == "transfer" and not (rec.transfer_instrument or "").strip():
                raise ValidationError(
                    "A transfer names its instrument — the insurance policy or the "
                    "contract term that carries the risk (M60 §8.1)."
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require_any(
            self.env,
            (RISK_OWNER_GROUP, OFFICER_GROUP),
            "A treatment decision is the Risk Owner's (or a Compliance Officer's) — M60 §8.1.",
        )
        recs = super().create(vals_list)
        for rec in recs:
            rec.company_id = rec.risk_id.company_id
            if rec.strategy in ("mitigate", "transfer", "avoid") and rec.risk_id.state == "open":
                rec.risk_id._guarded().write({"state": "mitigating"})
            if rec.owner_id.user_id:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=rec.due_on,
                    summary="Risk treatment: %s" % rec.name,
                    user_id=rec.owner_id.user_id.id,
                )
            rec.risk_id.message_post(
                body="Treatment planned (%s): %s — owner %s, due %s."
                % (rec.strategy, rec.name, rec.owner_id.name, rec.due_on)
            )
        return recs

    def write(self, vals):
        _require_editor(
            self,
            "owner_id",
            "Only the action owner, a Risk Owner or a Compliance Officer edits '%s'.",
        )
        return super().write(vals)

    def _require_owner_or_officer(self, rec):
        if self.env.su or self.env.user.has_group(OFFICER_GROUP):
            return
        if rec.owner_id.user_id != self.env.user:
            raise UserError(
                "Only the action owner (%s) or a Compliance Officer works '%s'."
                % (rec.owner_id.name, rec.name)
            )

    def action_start(self):
        for rec in self:
            self._require_owner_or_officer(rec)
            if rec.state != "planned":
                raise UserError("'%s' is not planned." % rec.name)
            rec._guarded().write({"state": "in_progress"})
        return True

    def action_complete(self, note=None):
        if not (note or "").strip():
            raise UserError("Say what was done and where the evidence is — it is the record.")
        for rec in self:
            self._require_owner_or_officer(rec)
            if rec.state not in ("planned", "in_progress"):
                raise UserError("'%s' is already %s." % (rec.name, rec.state))
            rec._guarded().write(
                {
                    "state": "done",
                    "completion_note": note.strip(),
                    "completed_on": fields.Date.context_today(rec),
                    "completed_by_id": self.env.uid,
                }
            )
            rec.activity_ids.action_done()
            rec.risk_id.message_post(
                body="Treatment completed by %s: %s — reassess the residual."
                % (self.env.user.name, rec.name)
            )
        return True

    def action_cancel(self, reason=None):
        _require_group(
            self.env, OFFICER_GROUP, "Only a Compliance Officer cancels a treatment action."
        )
        if not (reason or "").strip():
            raise UserError("State why the action is cancelled.")
        for rec in self:
            if rec.state in ("done", "cancelled"):
                raise UserError("'%s' is already %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "cancelled", "completion_note": reason.strip()})
            rec.activity_ids.unlink()
        return True


class FixRiskEvent(models.Model):
    _name = "fix.risk.event"
    _description = "Risk Event"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "occurred_on desc, id desc"

    name = fields.Char(string="What Happened", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    risk_id = fields.Many2one("fix.risk.register", required=True, index=True, ondelete="cascade")
    event_type = fields.Selection(
        [
            ("loss", "Loss"),
            ("incident", "Incident"),
            ("claim", "Claim"),
            ("nonconformance", "Non-Conformance"),
            ("breach", "Breach"),
            ("near_miss", "Near Miss"),
        ],
        required=True,
        default="incident",
    )
    occurred_on = fields.Date(required=True, default=fields.Date.context_today)
    source_module = fields.Char(string="Source Module (e.g. M59, M23)")
    source_ref = fields.Char(string="Source Reference")
    loss_amount = fields.Monetary(currency_field="currency_id", string="Loss Amount")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    description = fields.Text(required=True)
    reported_by_id = fields.Many2one("res.users", readonly=True)
    reassessment_due = fields.Boolean(
        string="Challenges the Assessment",
        compute="_compute_reassessment_due",
        store=True,
        help="True when the event is a loss, claim or breach on a risk scored "
        "below the Major impact — the assumed impact is challenged.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"reported_by_id"}

    @api.depends("event_type", "risk_id.impact")
    def _compute_reassessment_due(self):
        for rec in self:
            rec.reassessment_due = (
                rec.event_type in ("loss", "claim", "breach") and int(rec.risk_id.impact or 0) < 4
            )

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write(
                {"reported_by_id": self.env.uid, "company_id": rec.risk_id.company_id.id}
            )
            risk = rec.risk_id
            risk.message_post(
                body="Realised %s on %s: %s%s."
                % (
                    rec.event_type,
                    rec.occurred_on,
                    rec.name,
                    " — the assumed impact is challenged, reassess" if rec.reassessment_due else "",
                )
            )
            owner = risk.owner_id.user_id
            if owner:
                risk.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Reassess after event: %s" % rec.name,
                    user_id=owner.id,
                )
        return recs

    def write(self, vals):
        _immutable(self, vals)
        return super().write(vals)


# ====================================================================== page 4
class FixComplianceObligationOccurrence(models.Model):
    _name = "fix.compliance.obligation.occurrence"
    _description = "Obligation Occurrence"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "due_on, id"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    obligation_id = fields.Many2one(
        "fix.compliance.obligation", required=True, index=True, ondelete="cascade"
    )
    period = fields.Char(required=True, help="The period this instance discharges (e.g. 2026-Q4).")
    due_on = fields.Date(required=True)
    owner_id = fields.Many2one(related="obligation_id.owner_id", store=True)
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Evidence of Discharge", ondelete="restrict"
    )
    evidence_ref = fields.Char(string="Evidence Reference (filing no., certificate no.)")
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("discharged", "Discharged"),
            ("failed", "Control Failure (no evidence)"),
            ("verified", "Verified"),
            ("breached", "Breached"),
            ("not_applicable", "Not Applicable"),
        ],
        required=True,
        default="scheduled",
        tracking=True,
    )
    overdue = fields.Boolean(compute="_compute_overdue")
    discharged_on = fields.Date(readonly=True)
    discharged_by_id = fields.Many2one("res.users", readonly=True)
    verified_by_id = fields.Many2one("res.users", readonly=True)
    verified_on = fields.Date(readonly=True)
    decision_note = fields.Text(readonly=True)

    _one_per_period = models.Constraint(
        "UNIQUE (obligation_id, period)", "One occurrence per obligation and period."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "discharged_on",
            "discharged_by_id",
            "verified_by_id",
            "verified_on",
            "decision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and set(self.mapped("state")) - {"scheduled"}:
            locked |= {
                "obligation_id",
                "period",
                "due_on",
                "evidence_attachment_id",
                "evidence_ref",
            }
        return locked

    @api.depends("obligation_id", "period")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s · %s" % (rec.obligation_id.name or "Obligation", rec.period or "")

    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.overdue = rec.state == "scheduled" and bool(rec.due_on and rec.due_on < today)

    @api.model_create_multi
    def create(self, vals_list):
        _require_group(
            self.env,
            OFFICER_GROUP,
            "A Compliance Officer schedules the occurrences of an obligation (AUT-GRC-11).",
        )
        recs = super().create(vals_list)
        for rec in recs:
            rec.company_id = rec.obligation_id.company_id
            user = rec.owner_id.user_id
            if user:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=rec.due_on,
                    summary="Discharge %s" % rec.name,
                    user_id=user.id,
                )
        return recs

    def write(self, vals):
        _require_editor(
            self, "owner_id", "Only the obligation owner or a Compliance Officer edits '%s'."
        )
        return super().write(vals)

    def _require_discharger(self, rec):
        if self.env.su or self.env.user.has_group(OFFICER_GROUP):
            return
        if rec.owner_id.user_id != self.env.user:
            raise UserError(
                "Only the obligation owner (%s) or a Compliance Officer discharges '%s'."
                % (rec.owner_id.name or "none named", rec.name)
            )

    def action_discharge(self, note=None):
        """BRU-GRC-12: a discharge without evidence is recorded as a control
        failure, not as a discharge (AUT-GRC-12)."""
        for rec in self:
            self._require_discharger(rec)
            if rec.state != "scheduled":
                raise UserError("'%s' is %s, not scheduled." % (rec.name, rec.state))
            evidenced = bool(rec.evidence_attachment_id or (rec.evidence_ref or "").strip())
            rec._guarded().write(
                {
                    "state": "discharged" if evidenced else "failed",
                    "discharged_on": fields.Date.context_today(rec),
                    "discharged_by_id": self.env.uid,
                    "decision_note": (note or "").strip() or False,
                }
            )
            rec.message_post(
                body="Discharged by %s%s."
                % (
                    self.env.user.name,
                    ""
                    if evidenced
                    else " WITHOUT evidence — recorded as a control failure (BRU-GRC-12)",
                )
            )
        return True

    def action_verify(self):
        _require_group(self.env, OFFICER_GROUP, "Only a Compliance Officer verifies a discharge.")
        for rec in self:
            if rec.state != "discharged":
                raise UserError(
                    "'%s' is %s: only an evidenced discharge is verified." % (rec.name, rec.state)
                )
            if rec.discharged_by_id == self.env.user and not self.env.su:
                raise UserError("The person who discharged '%s' does not verify it." % rec.name)
            rec._guarded().write(
                {
                    "state": "verified",
                    "verified_by_id": self.env.uid,
                    "verified_on": fields.Date.context_today(rec),
                }
            )
        return True

    def action_record_breach(self, reason=None):
        """BRU-GRC-13: a missed obligation is recorded, assessed and escalated."""
        _require_group(self.env, OFFICER_GROUP, "Only a Compliance Officer records a breach.")
        if not (reason or "").strip():
            raise UserError("Assess the breach: its consequence is the record (BRU-GRC-13).")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state not in ("scheduled", "failed"):
                raise UserError("'%s' is %s." % (rec.name, rec.state))
            if rec.state == "scheduled" and rec.due_on >= today:
                raise UserError("'%s' is not yet due (%s)." % (rec.name, rec.due_on))
            rec._guarded().write({"state": "breached", "decision_note": reason.strip()})
            rec.obligation_id.message_post(
                body="BREACHED (%s): %s — escalated to the CFO." % (rec.period, reason.strip())
            )
        return True

    def action_not_applicable(self, reason=None):
        _require_group(
            self.env,
            OFFICER_GROUP,
            "Only a Compliance Officer declares an occurrence not applicable.",
        )
        if not (reason or "").strip():
            raise UserError("Justify why the occurrence does not apply.")
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("'%s' is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "not_applicable", "decision_note": reason.strip()})
        return True


class FixComplianceObligationOwner(models.Model):
    """FR-GRC-023: the obligation's owner, source, recurrence, lead time and
    consequence of breach."""

    _inherit = "fix.compliance.obligation"

    owner_id = fields.Many2one("hr.employee", string="Obligation Owner", tracking=True)
    source_type = fields.Selection(
        [
            ("statutory", "Statutory"),
            ("regulatory", "Regulatory"),
            ("contractual", "Contractual"),
            ("certification", "Certification"),
            ("licence", "Licence"),
        ],
        string="Source",
        default="statutory",
    )
    recurrence = fields.Selection(
        [
            ("once", "Once"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
        ],
        default="annual",
    )
    lead_days = fields.Integer(string="Advance Notice (days)", default=15)
    consequence = fields.Text(string="Consequence of Breach")
    occurrence_ids = fields.One2many("fix.compliance.obligation.occurrence", "obligation_id")


class FixGrcRegulatoryChange(models.Model):
    _name = "fix.grc.regulatory.change"
    _description = "Regulatory Change"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "effective_on desc, id desc"

    name = fields.Char(string="Change", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    source = fields.Char(string="Source (gazette, SRO, circular, counsel)", required=True)
    published_on = fields.Date()
    effective_on = fields.Date(required=True)
    description = fields.Text(required=True)
    obligation_ids = fields.Many2many("fix.compliance.obligation", string="Affected Obligations")
    control_ids = fields.Many2many("fix.control", string="Affected Controls")
    impact_assessment = fields.Text(readonly=True)
    assessed_by_id = fields.Many2one("res.users", readonly=True)
    state = fields.Selection(
        [("logged", "Logged"), ("assessed", "Impact Assessed"), ("closed", "Actions Closed")],
        required=True,
        default="logged",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "impact_assessment", "assessed_by_id"}

    def action_assess(self, impact=None):
        _require_group(
            self.env, OFFICER_GROUP, "Only a Compliance Officer assesses a regulatory change."
        )
        if not (impact or "").strip():
            raise UserError("Write the impact on obligations, controls and processes.")
        for rec in self:
            if rec.state != "logged":
                raise UserError("'%s' is already assessed." % rec.name)
            rec._guarded().write(
                {
                    "state": "assessed",
                    "impact_assessment": impact.strip(),
                    "assessed_by_id": self.env.uid,
                }
            )
        return True

    def action_close(self):
        _require_group(self.env, OFFICER_GROUP, "Only a Compliance Officer closes a change.")
        for rec in self:
            if rec.state != "assessed":
                raise UserError("Assess the impact of '%s' before closing it." % rec.name)
            rec._guarded().write({"state": "closed"})
        return True


# ====================================================================== page 5
class FixGrcPolicyAttestation(models.Model):
    _name = "fix.grc.policy.attestation"
    _description = "Policy Attestation"
    _inherit = ["fix.guarded.mixin"]
    _order = "acknowledged_at desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    policy_id = fields.Many2one("fix.grc.policy", required=True, index=True, ondelete="cascade")
    version = fields.Char(readonly=True)
    employee_id = fields.Many2one("hr.employee", readonly=True, index=True)
    acknowledged_at = fields.Datetime(readonly=True)
    method = fields.Selection(
        [("workspace", "Read and Acknowledged in the Workspace"), ("paper", "Signed Paper Copy")],
        required=True,
        default="workspace",
    )
    paper_employee_id = fields.Many2one(
        "hr.employee",
        string="Employee (paper copy)",
        help="For a signed paper copy only: the Compliance Officer records whose it is.",
    )
    recorded_by_id = fields.Many2one("res.users", readonly=True)

    _one_per_version = models.Constraint(
        "UNIQUE (policy_id, version, employee_id)",
        "An employee acknowledges each version of a policy once.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "version",
            "employee_id",
            "acknowledged_at",
            "recorded_by_id",
        }

    @api.depends("policy_id", "employee_id")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s · %s" % (rec.policy_id.code or "", rec.employee_id.name or "")

    @api.model_create_multi
    def create(self, vals_list):
        stamped = []
        for vals in vals_list:
            policy = self.env["fix.grc.policy"].browse(vals.get("policy_id"))
            if policy.state != "approved":
                raise UserError(
                    "Only an approved policy is acknowledged — %s is %s."
                    % (policy.code, policy.state)
                )
            if not policy.attestation_required:
                raise UserError("%s does not require attestation." % policy.code)
            if vals.get("method") == "paper":
                _require_group(
                    self.env,
                    OFFICER_GROUP,
                    "A signed paper copy is recorded by a Compliance Officer.",
                )
                employee = self.env["hr.employee"].browse(vals.get("paper_employee_id"))
                if not employee:
                    raise UserError("Name the employee whose signed copy this is.")
            else:
                vals.pop("paper_employee_id", None)
                employee = _employee(self.env) if not self.env.su else self.env.user.employee_id
            vals["company_id"] = policy.company_id.id
            stamped.append(
                {
                    "version": policy.version,
                    "employee_id": employee.id,
                    "acknowledged_at": fields.Datetime.now(),
                    "recorded_by_id": self.env.uid,
                }
            )
        recs = (
            super(FixGrcPolicyAttestation, self._guarded())
            .create([dict(v, **s) for v, s in zip(vals_list, stamped, strict=True)])
            .with_env(self.env)
        )
        return recs

    def write(self, vals):
        _immutable(self, vals)
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("An acknowledgement is evidence: it is never deleted.")
        return super().unlink()


class FixGrcPolicyAttestationLink(models.Model):
    _inherit = "fix.grc.policy"

    attestation_ids = fields.One2many("fix.grc.policy.attestation", "policy_id")
    attested_count = fields.Integer(
        string="Acknowledged (this version)", compute="_compute_attested_count"
    )
    document_id = fields.Many2one("fix.document", string="Controlled Document (M24)")

    def _compute_attested_count(self):
        for rec in self:
            rec.attested_count = len(
                rec.attestation_ids.filtered(lambda a, v=rec.version: a.version == v)
            )


class FixGrcPolicyException(models.Model):
    _name = "fix.grc.policy.exception"
    _description = "Policy Exception"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    policy_id = fields.Many2one("fix.grc.policy", required=True, index=True, ondelete="cascade")
    justification = fields.Text(required=True)
    compensating_control = fields.Text(string="Compensating Control", required=True)
    control_id = fields.Many2one("fix.control", string="Compensating Control (register)")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date(required=True)
    requested_by_id = fields.Many2one("res.users", readonly=True)
    decided_by_id = fields.Many2one("res.users", readonly=True)
    decided_on = fields.Date(readonly=True)
    decision_note = fields.Text(readonly=True)
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("expired", "Expired"),
        ],
        required=True,
        default="requested",
        tracking=True,
    )

    MAX_DAYS = 365

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "decided_by_id",
            "decided_on",
            "decision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and set(self.mapped("state")) - {"requested"}:
            locked |= {
                "policy_id",
                "justification",
                "compensating_control",
                "valid_from",
                "valid_to",
            }
        return locked

    @api.constrains("valid_from", "valid_to")
    def _check_window(self):
        for rec in self:
            if rec.valid_to < rec.valid_from:
                raise ValidationError("The exception ends after it starts.")
            if (rec.valid_to - rec.valid_from).days > self.MAX_DAYS:
                raise ValidationError(
                    "A policy exception is time-boxed: at most %d days (FR-GRC-031)."
                    % self.MAX_DAYS
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.grc.policy.exception") or "PEX/New"
                )
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write(
                {"requested_by_id": self.env.uid, "company_id": rec.policy_id.company_id.id}
            )
        return recs

    def _decide(self, state, note):
        _require_group(
            self.env, OFFICER_GROUP, "Only a Compliance Officer decides a policy exception."
        )
        for rec in self:
            if rec.state != "requested":
                raise UserError("'%s' is already %s." % (rec.name, rec.state))
            if rec.requested_by_id == self.env.user and not self.env.su:
                raise UserError("The requester of '%s' does not decide it." % rec.name)
            rec._guarded().write(
                {
                    "state": state,
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Date.context_today(rec),
                    "decision_note": (note or "").strip() or False,
                }
            )
            rec.policy_id.message_post(
                body="Exception %s %s by %s (%s to %s)."
                % (rec.name, state, self.env.user.name, rec.valid_from, rec.valid_to)
            )
        return True

    def action_approve(self):
        return self._decide("approved", "")

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why the exception is rejected.")
        return self._decide("rejected", reason)

    @api.model
    def cron_expire(self):
        """An exception ends on its date; it is never extended silently."""
        # the Dhaka day, not the UTC one: a cron runs with no user timezone,
        # and for six hours a day the UTC date is still yesterday's
        today = fields.Date.context_today(
            self.with_context(tz=self.env.context.get("tz") or "Asia/Dhaka")
        )
        due = self.search([("state", "=", "approved"), ("valid_to", "<", today)])
        for rec in due:
            rec._guarded().write({"state": "expired"})
            rec.message_post(body="Expired on %s." % rec.valid_to)
        return len(due)


# ====================================================================== page 3
class FixGrcSodRuleEnforcement(models.Model):
    """FR-GRC-018/019: M60 defines and tests, M29 enforces (BRU-GRC-11). The
    rule names the M29 control that enforces it and shows that control's
    latest measured run — a rule nothing enforces says so."""

    _inherit = "fix.grc.sod.rule"

    enforced_by_id = fields.Many2one(
        "fix.sod.control",
        string="Enforced By (M29 control)",
        help="The access-engine control that blocks or flags this conflict.",
    )
    test_method = fields.Selection(
        [
            ("measured", "Measured run over every user (M29 SoD test)"),
            ("violation", "Controlled violation attempt"),
            ("review", "Access review sample"),
        ],
        default="measured",
    )
    last_test_result = fields.Char(string="Latest Test", compute="_compute_last_test")

    @api.depends("enforced_by_id")
    def _compute_last_test(self):
        Test = self.env["fix.sod.test"].sudo()
        for rec in self:
            if not rec.enforced_by_id:
                rec.last_test_result = "Not enforced — no M29 control named"
                continue
            last = Test.search(
                [("control_id", "=", rec.enforced_by_id.id), ("result", "!=", False)],
                order="tested_on desc, id desc",
                limit=1,
            )
            rec.last_test_result = (
                "%s on %s (%d violation(s))"
                % (last.result.upper(), last.tested_on, last.violations_found)
                if last
                else "Never tested"
            )


# ====================================================================== page 2
class FixControlKey(models.Model):
    """FR-GRC-011/012: objective, nature and key-control designation."""

    _inherit = "fix.control"

    objective = fields.Text(string="Control Objective")
    nature = fields.Selection(
        [("manual", "Manual"), ("automated", "Automated"), ("hybrid", "Hybrid")],
        default="manual",
    )
    is_key = fields.Boolean(
        string="Key Control",
        help="Key controls are the testing programme's scope (KPI-C60-02).",
    )


# ====================================================================== page 6
class FixGrcLegalNextAction(models.Model):
    """FR-GRC-038: provision and next action on the legal matter."""

    _inherit = "fix.grc.legal"

    provision = fields.Monetary(currency_field="currency_id", string="Provision")
    next_action = fields.Char(string="Next Action")
    next_action_on = fields.Date(string="Next Action Due")
    hold_note = fields.Char(
        string="Legal Hold Scope",
        help="What M24 must preserve for this matter (FR-GRC-039). Place the hold on "
        "each document with Place Legal Hold.",
    )


class FixGrcIpAsset(models.Model):
    _name = "fix.grc.ip.asset"
    _description = "Intellectual Property Asset"
    _inherit = ["mail.thread"]
    _order = "renews_on, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    ip_type = fields.Selection(
        [
            ("trademark", "Trademark"),
            ("domain", "Domain Name"),
            ("software", "Software Licence Held"),
            ("copyright", "Copyright"),
            ("patent", "Patent / Design"),
        ],
        required=True,
        default="trademark",
    )
    identifier = fields.Char(string="Registration No. / Domain / Licence Key Ref", required=True)
    jurisdiction = fields.Char(default="Bangladesh")
    registered_on = fields.Date()
    renews_on = fields.Date(string="Renews / Expires On")
    owner_id = fields.Many2one("hr.employee", string="Responsible")
    infringement_note = fields.Text(string="Infringement Watch")
    renewal_due = fields.Boolean(compute="_compute_renewal_due")

    _identifier_unique = models.Constraint(
        "UNIQUE (ip_type, identifier, company_id)", "This IP asset is already registered."
    )

    def _compute_renewal_due(self):
        horizon = fields.Date.context_today(self) + datetime.timedelta(days=60)
        for rec in self:
            rec.renewal_due = bool(rec.renews_on and rec.renews_on <= horizon)


# ====================================================================== page 7
# A10 deep audit (2026-11-22, A3-F04): legitimate_interest is REMOVED — under
# the Bangladesh PDPA 2026 (which repealed the PDPO 2025 draft regime) it is
# not an available lawful basis, and offering it in the register invited
# recording processing that the Act does not permit. No row on any estate
# used it (verified fix_real + fix_dev before removal).
LAWFUL_BASES = [
    ("consent", "Consent"),
    ("contract", "Performance of a Contract"),
    ("legal_obligation", "Legal Obligation"),
    ("vital_interest", "Vital Interest"),
    ("public_task", "Public Task"),
]


class FixGrcProcessingActivity(models.Model):
    _name = "fix.grc.processing.activity"
    _description = "Record of Processing Activity"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "name"

    name = fields.Char(string="Processing Activity", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    purpose = fields.Text(required=True)
    lawful_basis = fields.Selection(LAWFUL_BASES, required=True)
    data_categories = fields.Char(string="Personal Data Categories", required=True)
    subject_categories = fields.Char(string="Data Subjects", required=True)
    recipients = fields.Char()
    retention_months = fields.Integer(string="Retention (months)")
    safeguards = fields.Text()
    systems = fields.Char(string="Systems / Modules")
    owner_id = fields.Many2one("hr.employee", string="Process Owner")
    high_risk = fields.Boolean(
        string="High-Risk Processing",
        help="Sensitive data, large scale or profiling: needs an approved privacy "
        "impact assessment before it is in force (FR-GRC-037).",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "In Force"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    activated_by_id = fields.Many2one("res.users", readonly=True)
    activated_on = fields.Date(readonly=True)
    transfer_ids = fields.One2many("fix.grc.data.transfer", "activity_id")
    pia_ids = fields.One2many("fix.grc.privacy.impact", "activity_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "activated_by_id", "activated_on"}

    def action_activate(self):
        """BRU-GRC-16: processing begins only with its lawful basis recorded."""
        _require_group(
            self.env, OFFICER_GROUP, "Only a Compliance Officer puts a processing record in force."
        )
        for rec in self:
            if rec.state != "draft":
                raise UserError("'%s' is %s." % (rec.name, rec.state))
            missing = [
                label
                for label, ok in (
                    ("retention", rec.retention_months > 0),
                    ("safeguards", bool((rec.safeguards or "").strip())),
                )
                if not ok
            ]
            if missing:
                raise UserError(
                    "'%s' is not in force without its %s (FR-GRC-033)."
                    % (rec.name, " and ".join(missing))
                )
            if rec.high_risk and not rec.pia_ids.filtered(lambda p: p.state == "approved"):
                raise UserError(
                    "'%s' is high-risk processing: it needs an approved privacy impact "
                    "assessment first (FR-GRC-037)." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_on": fields.Date.context_today(rec),
                }
            )
        return True

    def action_retire(self):
        _require_group(
            self.env, OFFICER_GROUP, "Only a Compliance Officer retires a processing record."
        )
        for rec in self:
            if rec.state != "active":
                raise UserError("'%s' is not in force." % rec.name)
            rec._guarded().write({"state": "retired"})
        return True

    def unlink(self):
        if not self.env.su:
            raise UserError(
                "Records of processing are kept at least five years (BRU-GRC-17): retire it."
            )
        return super().unlink()


class FixGrcDataTransfer(models.Model):
    _name = "fix.grc.data.transfer"
    _description = "Cross-Border Data Transfer"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    activity_id = fields.Many2one(
        "fix.grc.processing.activity", string="Processing Activity", required=True, index=True
    )
    destination_country_id = fields.Many2one("res.country", string="Destination", required=True)
    recipient = fields.Char(required=True)
    basis = fields.Selection(
        [
            ("adequacy", "Adequacy / Government Approval"),
            ("contract_clauses", "Contractual Clauses"),
            ("consent", "Explicit Consent"),
            ("intra_group", "Intra-Group Agreement"),
            ("necessity", "Necessity for a Contract"),
        ],
        required=True,
    )
    safeguards = fields.Text(required=True)
    volume_class = fields.Selection(
        [("low", "Occasional"), ("medium", "Regular"), ("high", "Bulk / Continuous")],
        default="medium",
    )
    effective_from = fields.Date()
    requested_by_id = fields.Many2one("res.users", readonly=True)
    approved_by_id = fields.Many2one("res.users", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("suspended", "Suspended")],
        required=True,
        default="draft",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "requested_by_id", "approved_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and set(self.mapped("state")) - {"draft"}:
            locked |= {"activity_id", "destination_country_id", "recipient", "basis", "safeguards"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.grc.data.transfer") or "XBT/New"
                )
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"requested_by_id": self.env.uid})
        return recs

    def action_approve(self):
        """BRU-GRC-18: a transfer needs a registered basis and safeguards over
        a processing activity that is in force."""
        _require_group(
            self.env, OFFICER_GROUP, "Only a Compliance Officer approves a cross-border transfer."
        )
        for rec in self:
            if rec.state != "draft":
                raise UserError("'%s' is %s." % (rec.name, rec.state))
            if rec.activity_id.state != "active":
                raise UserError(
                    "'%s' transfers data of '%s', which is not in force (BRU-GRC-18)."
                    % (rec.name, rec.activity_id.name)
                )
            if rec.requested_by_id == self.env.user and not self.env.su:
                raise UserError("The requester of '%s' does not approve it." % rec.name)
            rec._guarded().write({"state": "approved", "approved_by_id": self.env.uid})
        return True

    def action_suspend(self, reason=None):
        _require_group(self.env, OFFICER_GROUP, "Only a Compliance Officer suspends a transfer.")
        if not (reason or "").strip():
            raise UserError("State why the transfer is suspended.")
        for rec in self:
            if rec.state != "approved":
                raise UserError("'%s' is not approved." % rec.name)
            rec._guarded().write({"state": "suspended"})
            rec.message_post(body="Suspended by %s: %s" % (self.env.user.name, reason.strip()))
        return True


class FixGrcDataBreach(models.Model):
    _name = "fix.grc.data.breach"
    _description = "Personal Data Breach"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "detected_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    detected_on = fields.Datetime(required=True, default=fields.Datetime.now)
    description = fields.Text(required=True)
    data_categories = fields.Char(string="Data Categories Affected")
    subjects_affected = fields.Integer(string="Subjects Affected (estimate)")
    activity_id = fields.Many2one("fix.grc.processing.activity", string="Processing Activity")
    containment = fields.Text(string="Containment")
    assessment = fields.Text(string="Risk Assessment")
    notification_decision = fields.Selection(
        [
            ("none", "No Notification Required"),
            ("subjects", "Notify Data Subjects"),
            ("contractual", "Notify Contractual Parties"),
            ("regulator", "Notify Regulator"),
            ("all", "Notify Subjects, Parties and Regulator"),
        ],
        string="Notification Decision",
    )
    notified_parties = fields.Char(string="Notified Parties")
    reported_by_id = fields.Many2one("res.users", readonly=True)
    closed_by_id = fields.Many2one("res.users", readonly=True)
    closed_on = fields.Date(readonly=True)
    state = fields.Selection(
        [("open", "Open"), ("contained", "Contained"), ("closed", "Closed")],
        required=True,
        default="open",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "reported_by_id",
            "closed_by_id",
            "closed_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and set(self.mapped("state")) == {"closed"}:
            locked |= {
                "description",
                "containment",
                "assessment",
                "notification_decision",
                "notified_parties",
                "detected_on",
            }
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.grc.data.breach") or "BRCH/New"
                )
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"reported_by_id": self.env.uid})
        return recs

    def action_contain(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("'%s' is %s." % (rec.name, rec.state))
            if not (rec.containment or "").strip():
                raise UserError("Record what was done to contain '%s'." % rec.name)
            rec._guarded().write({"state": "contained"})
        return True

    def action_close(self):
        """Closed only with the assessment and the notification decision —
        contractual notifications included where statute is silent."""
        _require_group(self.env, OFFICER_GROUP, "Only a Compliance Officer closes a breach.")
        for rec in self:
            if rec.state != "contained":
                raise UserError("Contain '%s' before closing it." % rec.name)
            if not (rec.assessment or "").strip() or not rec.notification_decision:
                raise UserError(
                    "Record the assessment and the notification decision of '%s' "
                    "before closing it (FR-GRC-036)." % rec.name
                )
            if rec.notification_decision != "none" and not (rec.notified_parties or "").strip():
                raise UserError("Name who was notified about '%s'." % rec.name)
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_by_id": self.env.uid,
                    "closed_on": fields.Date.context_today(rec),
                }
            )
        return True

    def unlink(self):
        if not self.env.su:
            raise UserError("A breach record is never deleted.")
        return super().unlink()


class FixGrcPrivacyImpact(models.Model):
    _name = "fix.grc.privacy.impact"
    _description = "Privacy Impact Assessment"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    activity_id = fields.Many2one(
        "fix.grc.processing.activity", string="Processing Activity", required=True, index=True
    )
    risk_summary = fields.Text(string="Risks to Data Subjects", required=True)
    mitigations = fields.Text(required=True)
    residual_risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")], required=True, default="medium"
    )
    author_id = fields.Many2one("res.users", readonly=True)
    approved_by_id = fields.Many2one("res.users", readonly=True)
    approved_on = fields.Date(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("rejected", "Rejected")],
        required=True,
        default="draft",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "author_id",
            "approved_by_id",
            "approved_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and set(self.mapped("state")) - {"draft"}:
            locked |= {"activity_id", "risk_summary", "mitigations", "residual_risk"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.grc.privacy.impact") or "PIA/New"
                )
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"author_id": self.env.uid})
        return recs

    def action_approve(self):
        _require_group(self.env, OFFICER_GROUP, "Only a Compliance Officer approves a PIA.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("'%s' is %s." % (rec.name, rec.state))
            if rec.author_id == self.env.user and not self.env.su:
                raise UserError("The author of '%s' does not approve it." % rec.name)
            if rec.residual_risk == "high":
                raise UserError(
                    "'%s' leaves a HIGH residual risk: reduce it before approval." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_on": fields.Date.context_today(rec),
                }
            )
        return True

    def action_reject(self, reason=None):
        _require_group(self.env, OFFICER_GROUP, "Only a Compliance Officer rejects a PIA.")
        if not (reason or "").strip():
            raise UserError("State why the assessment is rejected.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("'%s' is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "rejected"})
            rec.message_post(body="Rejected by %s: %s" % (self.env.user.name, reason.strip()))
        return True
