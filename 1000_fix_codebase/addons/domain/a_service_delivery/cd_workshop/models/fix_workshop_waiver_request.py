# fix.workshop.waiver.request — the M22 certification waiver as a routed
# M63 approval (CD-M31-01).
#
# A02 workflow audit (2026-11-03) B1, M31 step 4: in P0 the waiver became a
# supervisor-only action, but it was still a button the supervisor pressed on
# the job: no request, no named approver, no deadline, no delegate and no
# history. A waiver is now requested on the job (Request Certification Waiver)
# and granted from a Workshop Supervisor's M63 inbox. The requester, the job's
# creator and the repairing technician never decide it, and it covers only the
# technician it was requested for.
#
# The waiver lifts the M22 certification gate at repair start and nothing
# else: the QC gate's test-instrument check (A07 M45-14) still runs.
from odoo import api, fields, models
from odoo.exceptions import UserError

GROUP_SUPERVISOR = "cd_workshop.group_fix_workshop_manager"
# the job states in which a waiver can still matter (before the bench work)
WAIVABLE_JOB_STATES = ("draft", "intake", "diagnostic", "waiting_parts", "qc_failed")

WAIVER_STATES = [
    ("pending", "Awaiting Supervisor"),
    ("granted", "Granted"),
    ("rejected", "Rejected"),
]


class FixWorkshopWaiverRequest(models.Model):
    _name = "fix.workshop.waiver.request"
    _description = "Workshop Certification Waiver Request"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "id desc"

    _approval_domain = "workshop_cert_waiver"
    _approval_apply_method = "action_grant"
    _approval_group = GROUP_SUPERVISOR
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "job_id",
            "technician_id",
            "requested_by_id",
            "granted_by_id",
            "granted_at",
        }

    name = fields.Char(compute="_compute_name", store=True)
    job_id = fields.Many2one(
        "fix.workshop.job", string="Workshop Job", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="job_id.company_id", store=True, string="Company")
    operating_unit_id = fields.Many2one(
        related="job_id.operating_unit_id", store=True, string="Operating Unit"
    )
    technician_id = fields.Many2one(
        "hr.employee", string="Technician Waived", required=True, readonly=True
    )
    reason = fields.Text(string="Justification", required=True, readonly=True)
    state = fields.Selection(WAIVER_STATES, default="pending", required=True, readonly=True)
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True)
    granted_by_id = fields.Many2one("res.users", string="Granted By", readonly=True)
    granted_at = fields.Datetime(string="Granted At", readonly=True)

    @api.depends("job_id.name", "technician_id.name")
    def _compute_name(self):
        for rec in self:
            rec.name = "Waiver %s / %s" % (rec.job_id.name or "?", rec.technician_id.name or "?")

    def _approval_excluded(self):
        """The repairing technician never decides a waiver of his own gate,
        on top of the requester, the creator and the amount changer."""
        excluded = super()._approval_excluded()
        return excluded | self.sudo().technician_id.user_id

    def action_grant(self):
        """The M63 apply method: a Workshop Supervisor grants the waiver from
        his inbox. A direct press is refused (routed)."""
        self._approval_assert_routed()
        trusted = self.env.su and not self._approval_task()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for rec in self:
            if rec.state != "pending":
                raise UserError("Waiver request %s is %s." % (rec.name, rec.state))
            job = rec.job_id
            if not trusted:
                if not authority.has_group(GROUP_SUPERVISOR):
                    raise UserError(
                        "A certification waiver is granted by a Workshop Supervisor, which %s "
                        "is not." % authority.name
                    )
                if acting & (rec.requested_by_id | rec.sudo().technician_id.user_id):
                    raise UserError(
                        "Segregation of duties: the requester and the repairing technician "
                        "cannot grant this waiver."
                    )
            if job.technician_id != rec.technician_id:
                raise UserError(
                    "Job %s was reassigned from %s; this waiver was requested for %s only."
                    % (job.name, rec.technician_id.name, rec.technician_id.name)
                )
            if job.state not in WAIVABLE_JOB_STATES:
                raise UserError(
                    "Job %s is %s: a waiver is granted before the repair starts."
                    % (job.name, job.state)
                )
            now = fields.Datetime.now()
            job._guarded().write(
                {
                    "certification_waiver": True,
                    "certification_waiver_reason": rec.reason,
                    "certification_waiver_by_id": self.env.user.id,
                    "certification_waiver_at": now,
                    "certification_waiver_technician_id": rec.technician_id.id,
                }
            )
            rec._guarded().write(
                {"state": "granted", "granted_by_id": self.env.user.id, "granted_at": now}
            )
            job.message_post(
                body="M22 certification waiver granted by %s for %s: %s"
                % (self.env.user.name, rec.technician_id.name, rec.reason)
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self.filtered(lambda r: r.state == "pending"):
            rec.sudo()._guarded().write({"state": "rejected"})
            rec.job_id.sudo().message_post(
                body="Certification waiver for %s rejected: %s"
                % (rec.technician_id.name, comment or "-")
            )


class FixApprovalMatrixWorkshop(models.Model):
    """M31 decision domains on the DoA register (A02 audit B1)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("workshop_ber", "Workshop BER / Scrap Write-Off"),
            ("workshop_extra_parts", "Workshop Parts Beyond the Estimate"),
            ("workshop_cert_waiver", "Workshop Certification Waiver"),
        ],
        ondelete={
            "workshop_ber": "cascade",
            "workshop_extra_parts": "cascade",
            "workshop_cert_waiver": "cascade",
        },
    )
