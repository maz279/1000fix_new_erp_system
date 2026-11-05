# fix_certification_waiver — M22: the certification override as an approved,
# reasoned record (A09 audit M22-F3, report C4; BRU-LMS-02, FR-LMS-040).
#
# The waiver on fix.work.order was a bare Boolean that any internal user
# could tick through JSON-RPC, and the module's own test asserted that it let
# an uncertified technician through. An override now names ONE technician on
# ONE job, carries its reason and a validity date, and is decided from the
# approval inbox by the Dispatch Override Approver, never by the requester or
# the technician. The M31 workshop bench keeps its own supervisor waiver.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

from .fix_competency import changed_fields, guard_first

OVERRIDE = "cd_competency.group_dispatch_override"

TARGETS = [("fix.work.order", "Work Order"), ("fix.field.order", "Field Order")]


class FixCertificationWaiver(models.Model):
    _name = "fix.certification.waiver"
    _description = "Certification Waiver (Dispatch Override)"
    _inherit = ["mail.thread", "fix.people.approval.mixin"]
    _order = "id desc"

    _approval_domain = "hr_certification"
    _approval_apply_method = "action_approve"
    _approval_group = OVERRIDE

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", string="Technician", required=True, index=True)
    res_model = fields.Selection(TARGETS, string="Job Type", required=True)
    res_id = fields.Integer(string="Job ID", required=True, index=True)
    reason = fields.Text(string="Justification", required=True)
    valid_until = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    requester_id = fields.Many2one(
        "res.users",
        string="Requested By",
        readonly=True,
        default=lambda self: self.env.user,
        help="Who asked for the override. A dispatcher or supervisor asks from the job "
        "(action_request_certification_waiver), so plain users need no write access "
        "to this model; the requester never decides it.",
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(string="Approved At", readonly=True)

    _TERMS = frozenset(
        {"employee_id", "res_model", "res_id", "reason", "valid_until", "company_id"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requester_id",
            "approved_by_id",
            "approved_at",
        }

    def _approval_preparers(self):
        # A request raised from a job runs as the superuser; the person who
        # asked is still excluded from deciding it.
        return self.mapped("requester_id")

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" or rec.approval_state == "pending" for rec in self):
            locked = locked | self._TERMS
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.certification.waiver") or "CWV/New"
                )
        records = super().create(vals_list)
        records._fix_check_request()
        return records

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(
                self.filtered(lambda r: r.state != "draft" or r.approval_state == "pending"),
                vals,
                self._TERMS,
            )
            if frozen:
                raise UserError(
                    "A requested or decided waiver keeps its terms (%s); raise a new one."
                    % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def _fix_target(self):
        self.ensure_one()
        if self.res_model not in self.env:
            return None
        return self.env[self.res_model].sudo().browse(self.res_id).exists()

    def _fix_check_request(self):
        for rec in self:
            if len((rec.reason or "").strip()) < 10:
                raise UserError("State why the certification is waived (BRU-LMS-02).")
            asker = rec.requester_id | (
                self.env.user if not self.env.su else self.env.user.browse()
            )
            if rec.employee_id.sudo().user_id in asker:
                raise UserError("A technician cannot request a waiver for themself.")
            if not rec._fix_target():
                raise UserError("The job %s %s does not exist." % (rec.res_model, rec.res_id))
            if rec.valid_until < fields.Date.context_today(self):
                raise UserError("A waiver cannot be valid only in the past.")

    def _fix_covers_target(self, res_model, res_id, employee):
        """True when this approved waiver covers `employee` on that job today."""
        self.ensure_one()
        return (
            self.state == "approved"
            and self.res_model == res_model
            and self.res_id == res_id
            and employee
            and self.employee_id == employee
            and self.valid_until >= fields.Date.context_today(self)
        )

    @api.model
    def _fix_covers(self, res_model, res_id, employee):
        """An approved waiver covers this technician on this job today."""
        if not employee:
            return False
        waivers = self.sudo().search(
            [
                ("state", "=", "approved"),
                ("res_model", "=", res_model),
                ("res_id", "=", res_id),
                ("employee_id", "=", employee.id),
                ("valid_until", ">=", fields.Date.context_today(self)),
            ],
            limit=1,
        )
        return bool(waivers)

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft waiver is requested.")
        self._fix_check_request()
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """Run by the approval engine from the override approver's inbox task."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not awaiting a decision." % rec.name)
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": rec._people_decider().id,
                    "approved_at": fields.Datetime.now(),
                }
            )
            target = rec._fix_target()
            if rec.res_model == "fix.work.order" and target:
                if target.technician_id and target.technician_id != rec.employee_id:
                    raise UserError(
                        "%s is assigned to %s, not %s."
                        % (target.display_name, target.technician_id.name, rec.employee_id.name)
                    )
                target._guarded().write(
                    {
                        "certification_waiver": True,
                        "certification_waiver_reason": (rec.reason or "")[:250],
                        "certification_waiver_id": rec.id,
                    }
                )
            publish(
                self.env,
                "certification.waiver.approved",
                "fix.certification.waiver",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "res_model": rec.res_model,
                    "res_id": rec.res_id,
                    "reason": rec.reason,
                    "valid_until": str(rec.valid_until),
                },
            )
        return True

    def _approval_on_rejected(self, comment):
        self._guarded().write({"state": "rejected"})

    def action_cancel(self):
        """The requester withdraws a waiver, or an override approver ends it."""
        for rec in self:
            if rec.state not in ("draft", "approved"):
                raise UserError("%s is already closed." % rec.name)
            if not (
                self.env.su
                or self.env.user in (rec.requester_id | rec.create_uid)
                or self.env.user.has_group(OVERRIDE)
            ):
                raise AccessError("Only the requester or an override approver cancels a waiver.")
            if rec.approval_state == "pending":
                rec._approval_void("the waiver was cancelled")
            rec._guarded().write({"state": "cancelled"})
            target = rec._fix_target()
            if (
                rec.res_model == "fix.work.order"
                and target
                and target.certification_waiver_id == rec
            ):
                target._guarded().write(
                    {
                        "certification_waiver": False,
                        "certification_waiver_reason": False,
                        "certification_waiver_id": False,
                    }
                )
        return True

    @api.model
    def _fix_request_for(self, res_model, res_id, technician, reason, valid_until=None):
        """Raise and route a waiver for one technician on one job, on behalf of
        the calling user (the job's own action checks who may ask)."""
        if not technician:
            raise UserError("Name the technician the waiver is for.")
        if technician.sudo().user_id == self.env.user and not self.env.su:
            raise UserError("A technician cannot request a waiver for themself.")
        vals = {
            "employee_id": technician.id,
            "res_model": res_model,
            "res_id": res_id,
            "reason": (reason or "").strip(),
            "requester_id": self.env.user.id,
        }
        if valid_until:
            vals["valid_until"] = valid_until
        waiver = self.sudo()._guarded().create(vals)
        waiver.action_request_approval()
        return waiver
