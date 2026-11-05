# fix_competency_consumers — M22: what happens downstream when a technician
# loses a certification, and the assessment attempt-limit escalation.
#
# A09 report "Still open" item 4 / M22-F11: certification.expired,
# .suspended and .revoked had no consumer. Dispatch eligibility reads the
# certification live, so a NEW assignment was already refused, but a job
# assigned before the lapse sat on the technician's list and nobody was told.
# The relay (fix.event.consumer, data/fix_a09_m22_r2_data.xml) now hands each
# of these events to consume_certification_lost: every open job of the
# technician that has not started (work orders pending/assigned; field orders
# up to "arrived") and that the technician no longer qualifies for gets one
# dispatcher to-do. Field-service states are not changed: starting the work
# is refused by the gate (fix.work.order here, fix.field.order in
# cd_field_service/models/fix_field_order_certification.py) until the job is
# reassigned or waived.
#
# BRU-LMS-09 / AUT-LMS-11: reaching a competency's attempt limit used only to
# refuse the next attempt. The attempt that reaches the limit now opens a
# to-do for the Training Managers; one of them (never the technician, nor
# the person who recorded the attempt) grants a retake with a reason.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_competency import TRAINING, group_users, open_activity_once, require_group

LOST_EVENTS = ("certification.expired", "certification.suspended", "certification.revoked")


class FixCertificationConsumers(models.Model):
    _inherit = "fix.certification"

    @api.model
    def consume_certification_lost(self, event):
        """certification.expired / .suspended / .revoked -> dispatcher to-dos
        on the technician's open, not-started jobs. Idempotent."""
        cert = self.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not cert:
            return False
        event_type = event.get("event_type") or "certification.lost"
        emp = cert.employee_id
        flagged = 0
        if "fix.work.order" in self.env:
            orders = (
                self.env["fix.work.order"]
                .sudo()
                .search([("technician_id", "=", emp.id), ("state", "in", ("pending", "assigned"))])
            )
            flagged += len(orders._fix_flag_certification_lost(cert, event_type))
        if "fix.field.order" in self.env:
            field_orders = self.env["fix.field.order"].sudo()
            if hasattr(field_orders, "_fix_flag_certification_lost"):
                orders = field_orders.search(
                    [
                        ("technician_id", "=", emp.id),
                        ("state", "in", field_orders._fix_not_started_states()),
                    ]
                )
                flagged += len(orders._fix_flag_certification_lost(cert, event_type))
        return flagged


class FixCompetencyAssessmentAttempts(models.Model):
    _name = "fix.competency.assessment"
    _inherit = ["fix.competency.assessment", "mail.thread", "mail.activity.mixin"]

    attempt_escalated = fields.Boolean(
        string="Attempt Limit Reached",
        readonly=True,
        help="This failed attempt used the last one the competency allows; the "
        "Training Managers were asked to decide a retake.",
    )
    retake_granted_by_id = fields.Many2one("res.users", string="Retake Granted By", readonly=True)
    retake_granted_at = fields.Datetime(string="Retake Granted At", readonly=True)
    retake_reason = fields.Char(string="Retake Reason", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "attempt_escalated",
            "retake_granted_by_id",
            "retake_granted_at",
            "retake_reason",
        }

    def _fix_attempts_since_retake(self, employee, competency, exclude=None):
        """Failed attempts since the last granted retake (or ever), and
        whether a pass exists (a passed competency has no limit)."""
        prior = self.sudo().search(
            [
                ("employee_id", "=", employee.id),
                ("competency_id", "=", competency.id),
                ("id", "not in", (exclude or self.browse()).ids),
            ],
            order="id",
        )
        if any(prior.mapped("passed")):
            return 0, True
        granted = prior.filtered("retake_granted_at")
        if granted:
            prior = prior.filtered(lambda a: a.id > granted[-1].id)
        return len(prior.filtered(lambda a: not a.passed)), False

    def _fix_check_attempts(self):
        """BRU-LMS-09: attempts are limited by the competency's policy. The
        attempt that reaches the limit is escalated (below); the next one is
        refused until a Training Manager grants a retake."""
        for rec in self:
            limit = rec.competency_id.attempt_limit
            if not limit:
                continue
            failed, passed = self._fix_attempts_since_retake(
                rec.employee_id, rec.competency_id, exclude=rec
            )
            if passed:
                continue
            if failed >= limit:
                raise UserError(
                    "%s has used the %d attempts allowed for %s. It was escalated to the "
                    "Training Managers: a retake needs one of them to grant it "
                    "(BRU-LMS-09, AUT-LMS-11)."
                    % (rec.employee_id.name, limit, rec.competency_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._fix_escalate_attempt_limit()
        return records

    def _fix_escalate_attempt_limit(self):
        for rec in self.sudo():
            limit = rec.competency_id.attempt_limit
            if not limit or rec.passed:
                continue
            failed, passed = self._fix_attempts_since_retake(rec.employee_id, rec.competency_id)
            if passed or failed != limit:
                continue
            rec._guarded().write({"attempt_escalated": True})
            excluded = rec.employee_id.user_id | rec.create_uid | rec.assessor_id.user_id
            summary = "Attempt limit reached: %s / %s" % (
                rec.employee_id.name,
                rec.competency_id.code,
            )
            for user in group_users(self.env, TRAINING, rec.company_id) - excluded:
                open_activity_once(
                    rec,
                    user,
                    summary,
                    "%s failed %s %d times (the limit). Decide with the manager and HR: "
                    "grant a retake (Grant Retake, with the reason) or plan retraining."
                    % (rec.employee_id.name, rec.competency_id.name, limit),
                )
        return True

    def action_grant_retake(self, reason=None):
        """A Training Manager who neither is the technician nor recorded the
        attempt grants one more round of attempts, with the reason."""
        require_group(self.env, TRAINING, "Granting a retake")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Give the reason for the retake.")
        for rec in self:
            if not rec.attempt_escalated or rec.retake_granted_at:
                raise UserError("%s is not an escalated attempt awaiting a decision." % rec.name)
            if not self.env.su and self.env.user in (
                rec.employee_id.sudo().user_id | rec.create_uid
            ):
                raise UserError(
                    "The technician and the person who recorded the attempt do not grant "
                    "its retake."
                )
            rec._guarded().write(
                {
                    "retake_granted_by_id": self.env.user.id,
                    "retake_granted_at": fields.Datetime.now(),
                    "retake_reason": reason,
                }
            )
            rec.sudo().activity_unlink(["mail.mail_activity_data_todo"])
            rec.message_post(body="Retake granted by %s: %s" % (self.env.user.name, reason))
        return True
