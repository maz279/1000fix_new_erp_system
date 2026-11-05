# fix_hse_investigation — M59: the investigation team, root causes and CAPA
# actions as child records (A09 round 2, M59-F8; BRU-HSE-05/06).
#
# The incident carried one typed root cause, one typed corrective action, one
# owner and one due date, and one HSE Officer "verified" it all. Now:
#   * the investigation team and the root causes are rows, kept by HSE;
#   * every CAPA action has an owner and a due date; its owner marks it done
#     with what was done; an HSE Officer who is neither the owner nor the
#     person who marked it done verifies it effective;
#   * the incident closes only when every live CAPA is verified (lost-time
#     and reportable incidents) or done (the rest) (fix_hse.py).
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from .fix_hse import _is_hse, _require_hse


def guard_first(records, vals):
    """Refuse a changing write of a guarded field with the guard's own
    message, before any role check speaks (the control suite reads it)."""
    if records._fix_guard_open():
        return
    touched = records._fix_guarded_fields() & set(vals)
    changed = {n for r in records for n in touched if r._fix_guard_differs(n, vals[n], r[n])}
    if changed:
        records._fix_guard_refuse(changed)


class _IncidentChild(models.AbstractModel):
    _name = "fix.hse.incident.child"
    _description = "HSE Incident Child Record"

    incident_id = fields.Many2one("fix.hse.incident", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="incident_id.company_id", store=True, string="Company")

    def _fix_check_open(self, incident_ids):
        if self.env.su:
            return
        incidents = self.env["fix.hse.incident"].sudo().browse([i for i in incident_ids if i])
        if incidents.filtered(lambda i: i.state == "closed"):
            raise UserError("A closed incident's investigation is a record.")


class FixHseInvestigationMember(models.Model):
    _name = "fix.hse.investigation.member"
    _description = "Incident Investigation Team Member"
    _inherit = ["fix.hse.incident.child"]
    _order = "incident_id, role, id"

    employee_id = fields.Many2one("hr.employee", required=True)
    role = fields.Selection(
        [("lead", "Lead Investigator"), ("member", "Member"), ("specialist", "Specialist")],
        required=True,
        default="member",
    )

    _member_once = models.Constraint(
        "UNIQUE (incident_id, employee_id)", "An employee sits on an investigation once"
    )

    @api.model_create_multi
    def create(self, vals_list):
        _require_hse(self.env, "name the investigation team")
        self._fix_check_open([v.get("incident_id") for v in vals_list])
        return super().create(vals_list)

    def write(self, vals):
        _require_hse(self.env, "change the investigation team")
        self._fix_check_open([*self.mapped("incident_id").ids, vals.get("incident_id")])
        return super().write(vals)

    def unlink(self):
        _require_hse(self.env, "change the investigation team")
        self._fix_check_open(self.mapped("incident_id").ids)
        return super().unlink()


class FixHseRootCause(models.Model):
    _name = "fix.hse.root.cause"
    _description = "Incident Root Cause"
    _inherit = ["fix.hse.incident.child"]
    _order = "incident_id, id"

    category = fields.Selection(
        [
            ("people", "People / Behaviour"),
            ("procedure", "Procedure / Method"),
            ("equipment", "Equipment / Tool"),
            ("material", "Material / Substance"),
            ("environment", "Work Environment"),
            ("management", "Supervision / Management"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    description = fields.Text(required=True)

    @api.model_create_multi
    def create(self, vals_list):
        _require_hse(self.env, "record a root cause")
        self._fix_check_open([v.get("incident_id") for v in vals_list])
        return super().create(vals_list)

    def write(self, vals):
        _require_hse(self.env, "change a root cause")
        self._fix_check_open([*self.mapped("incident_id").ids, vals.get("incident_id")])
        return super().write(vals)

    def unlink(self):
        _require_hse(self.env, "remove a root cause")
        self._fix_check_open(self.mapped("incident_id").ids)
        return super().unlink()


class FixHseCapa(models.Model):
    _name = "fix.hse.capa"
    _description = "Corrective / Preventive Action"
    _inherit = ["fix.hse.incident.child", "mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "due_date, id"

    _PLAN = ("name", "action_type", "owner_id", "due_date")

    name = fields.Char(string="Action", required=True)
    action_type = fields.Selection(
        [("corrective", "Corrective"), ("preventive", "Preventive")],
        required=True,
        default="corrective",
    )
    owner_id = fields.Many2one("hr.employee", string="Owner", index=True, tracking=True)
    owner_user_id = fields.Many2one(
        related="owner_id.user_id", store=True, index=True, string="Owner User"
    )
    due_date = fields.Date(tracking=True)
    overdue = fields.Boolean(compute="_compute_overdue")
    completion_note = fields.Text(readonly=True, copy=False)
    completed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    completed_on = fields.Datetime(readonly=True, copy=False)
    verification_note = fields.Text(readonly=True, copy=False)
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_on = fields.Datetime(readonly=True, copy=False)
    cancel_reason = fields.Char(readonly=True, copy=False)
    migrated = fields.Boolean(
        readonly=True, copy=False, help="Moved from the incident's former single CAPA fields."
    )
    state = fields.Selection(
        [
            ("open", "Open"),
            ("done", "Done"),
            ("verified", "Verified Effective"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="open",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "completion_note",
            "completed_by_id",
            "completed_on",
            "verification_note",
            "verified_by_id",
            "verified_on",
            "cancel_reason",
            "migrated",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"incident_id"}
        if any(r.state != "open" for r in self):
            locked |= set(self._PLAN)
        return locked

    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.overdue = bool(rec.state == "open" and rec.due_date and rec.due_date < today)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            _require_hse(self.env, "raise a CAPA action")
            self._fix_check_open([v.get("incident_id") for v in vals_list])
            guarded = self._fix_guarded_fields()
            for vals in vals_list:
                touched = guarded & set(vals)
                if touched:
                    self._fix_guard_refuse(touched)
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            if not _is_hse(self.env):
                raise AccessError("HSE plans a CAPA action; its owner marks it done.")
            self._fix_check_open(self.mapped("incident_id").ids)
            if "incident_id" in vals and any(
                r._fix_guard_differs("incident_id", vals["incident_id"], r.incident_id)
                for r in self
            ):
                raise UserError("A CAPA action stays with its incident.")
            plan = set(self._PLAN) & set(vals)
            for rec in self:
                if (
                    plan
                    and rec.state != "open"
                    and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in plan)
                ):
                    raise UserError(
                        "CAPA %s is %s; it is no longer replanned." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A CAPA action is cancelled with a reason, never deleted.")
        return super().unlink()

    def action_mark_done(self, note=None):
        """The owner (or an HSE Officer for them) records what was done."""
        if not (note or "").strip():
            raise UserError("Say what was done.")
        for rec in self:
            if not (self.env.su or _is_hse(self.env) or rec.owner_user_id == self.env.user):
                raise AccessError("Only the owner of %s marks it done." % rec.name)
            if rec.state != "open":
                raise UserError("%s is not open." % rec.name)
            rec._fix_check_open(rec.incident_id.ids)
            rec.sudo()._guarded().write(
                {
                    "state": "done",
                    "completion_note": note.strip(),
                    "completed_by_id": self.env.uid,
                    "completed_on": fields.Datetime.now(),
                }
            )
        return True

    def action_verify(self, note=None):
        """BRU-HSE-06: an HSE Officer who neither owns the action nor marked
        it done verifies it effective."""
        _require_hse(self.env, "verify a CAPA action")
        if not (note or "").strip():
            raise UserError("Record how the action was verified effective.")
        for rec in self:
            if rec.state != "done":
                raise UserError("Verify a CAPA action that is done.")
            if not self.env.su and self.env.user in (rec.owner_user_id | rec.completed_by_id):
                raise UserError(
                    "You own or completed %s; another HSE Officer verifies it." % rec.name
                )
            rec._fix_check_open(rec.incident_id.ids)
            rec._guarded().write(
                {
                    "state": "verified",
                    "verification_note": note.strip(),
                    "verified_by_id": self.env.uid,
                    "verified_on": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self, reason=None):
        _require_hse(self.env, "cancel a CAPA action")
        if not (reason or "").strip():
            raise UserError("Say why the action is cancelled.")
        for rec in self:
            if rec.state in ("verified", "cancelled"):
                raise UserError("%s is %s." % (rec.name, rec.state))
            rec._fix_check_open(rec.incident_id.ids)
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason.strip()})
        return True
