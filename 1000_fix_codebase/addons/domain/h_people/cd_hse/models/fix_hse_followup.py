# fix_hse_followup — M59: the HSE follow-up of a lapsed safety certification
# (A09 round 2; consumer of M22's `certification.safety_lapsed`).
#
# When a competency marked "Statutory / Safety" lapses, M22 publishes
# certification.safety_lapsed {employee_id, certification_id, competency,
# expired_on}. The consumer opens one follow-up per certification on the
# employee's HSE side, assigned to an HSE Officer with an activity. A second
# delivery of the same event (or a re-publication) finds the follow-up and
# does nothing: idempotent per certification.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_hse import _group_users, _require_hse


class FixHseSafetyFollowup(models.Model):
    _name = "fix.hse.safety.followup"
    _description = "HSE Follow-up: Lapsed Safety Certification"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True, readonly=True)
    certification_ref = fields.Integer(
        string="M22 Certification", required=True, readonly=True, index=True
    )
    competency = fields.Char(readonly=True)
    expired_on = fields.Date(readonly=True)
    assigned_to_id = fields.Many2one("res.users", string="HSE Officer", readonly=True)
    outcome = fields.Text(readonly=True, copy=False)
    closed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], required=True, default="open", tracking=True
    )

    _one_per_certification = models.Constraint(
        "UNIQUE (certification_ref)", "One HSE follow-up per lapsed certification"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "outcome",
            "closed_by_id",
            "assigned_to_id",
            "employee_id",
            "certification_ref",
            "expired_on",
            "competency",
        }

    @api.model
    def consume_certification_safety_lapsed(self, event):
        """Relay consumer of certification.safety_lapsed. Superuser; idempotent."""
        payload = event.get("payload") or {}
        cert_id = int(payload.get("certification_id") or event.get("aggregate_id") or 0)
        employee = (
            self.env["hr.employee"].sudo().browse(int(payload.get("employee_id") or 0)).exists()
        )
        if not cert_id or not employee:
            return False
        Followup = self.sudo().with_context(active_test=False)
        if Followup.search_count([("certification_ref", "=", cert_id)]):
            return False
        company = employee.company_id or self.env.company
        officers = _group_users(self.env, "cd_hse.group_hse_officer", company)
        officer = officers.sorted("id")[:1]
        rec = Followup._guarded().create(
            {
                "name": "Safety certification lapsed: %s (%s)"
                % (employee.name, payload.get("competency") or "?"),
                "company_id": company.id,
                "employee_id": employee.id,
                "certification_ref": cert_id,
                "competency": payload.get("competency") or False,
                "expired_on": payload.get("expired_on") or False,
                "assigned_to_id": officer.id or False,
            }
        )
        if officer:
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=fields.Date.context_today(rec),
                summary="Lapsed safety certification: %s" % employee.name,
                note="%s lapsed on %s. Keep %s off the work it covers until it is renewed."
                % (
                    payload.get("competency") or "A safety competency",
                    rec.expired_on,
                    employee.name,
                ),
                user_id=officer.id,
            )
        return True

    def action_close(self, outcome=None):
        _require_hse(self.env, "close an HSE follow-up")
        if not (outcome or "").strip():
            raise UserError("Record what was done (renewed, restricted, reassigned).")
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is closed." % rec.name)
            rec._guarded().write(
                {"state": "closed", "outcome": outcome.strip(), "closed_by_id": self.env.uid}
            )
        return True
