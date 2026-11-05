# hr.employee extension — the employee master W1 slice + JML events (P03-M08).
#
# MV-01 (AR-006 section 5.1): M29 has in-degree 53 and declared a dependency
# on a module arriving four waves later. This module IS the correction.
#
# The M21<->M29 interface break (AR-006 section 4.1 pair 17):
#   M21 EMITS events that M29 CONSUMES (joiner/left/role_changed)
#   M21 CALLS M29's published API for role assignment (sync one-way)
#   NEVER synchronous-both-ways
#
# The leaver path (KPI-090): zero orphaned accounts beyond 24 hours.
# M29's Keycloak deprovisioning triggers on employee.left within 1 hour.
import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError

logger = logging.getLogger(__name__)


class HrEmployeeExt(models.Model):
    """Extend hr.employee with the W1 employee-master slice.

    W1 scope ONLY: the master record and the JML (joiner/mover/leaver)
    event emission. Learning, payroll, performance and talent stay in W5.
    """

    _inherit = "hr.employee"

    # The employee is a PARTY (M33) with an employee role — not a separate master
    party_role_id = fields.Many2one(
        "fix.party.role",
        string="Party Role (Employee)",
        domain=[("role_type", "=", "employee")],
        help="The fix.party.role record linking this employee to the party "
        "kernel. An employee is a party with an employee role.",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Linked Party",
        related="party_role_id.partner_id",
        store=True,
        readonly=True,
        help="The res.partner this employee maps to through the party kernel",
    )

    # W1 slice fields
    employee_code = fields.Char(
        string="Employee Code",
        index=True,
        tracking=True,
        help="1000FiX employee identifier, e.g. E-00042",
    )
    branch_id = fields.Many2one(
        "fix.branch", string="Assigned Branch", help="The branch this employee reports to"
    )
    primary_role_id = fields.Many2one(
        "fix.role",
        string="Primary Business Role (M29)",
        help="The primary fix.role — drives M29's permission model",
    )
    additional_role_ids = fields.Many2many(
        "fix.role",
        string="Additional Roles",
        help="Secondary roles; SoD controls check for conflicts",
    )
    keycloak_user_id = fields.Char(
        string="Keycloak User ID",
        readonly=True,
        help="The Keycloak user UUID — provisioned on employee.joined, "
        "deprovisioned on employee.left within 1 hour (KPI-090)",
    )
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        copy=False,
        help="MIG-03: permanent source system reference (FR-SRM-088)",
    )

    # JML state
    employment_status = fields.Selection(
        [
            ("prospect", "Prospect"),
            ("joining", "Joining (Pre-Start)"),
            ("active", "Active"),
            ("notice_period", "Notice Period"),
            ("leaving", "Leaving"),
            ("left", "Left"),
        ],
        default="joining",
        required=True,
        tracking=True,
        compute="_compute_employment_status",
        store=False,
        help="Derived from Odoo's hr state + M21-core lifecycle tracking",
    )
    joined_date = fields.Date(string="Joined Date", tracking=True)
    left_date = fields.Date(string="Left Date", tracking=True)

    # Bengali name (DE-17)
    name_bn = fields.Char(string="Name (Bengali)")

    # -------------------------------------------------------------
    # JML event emission (P03-M08-T04, AS-08 via fix_events)
    # -------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        # A10 P1-3: an employee born holding a conflicting role pair is a
        # conflict, not a fresh start.
        for vals in vals_list:
            if vals.get("primary_role_id") or vals.get("additional_role_ids"):
                self.env["fix.sod.control"].gate_role_set(self._sod_final_role_set(vals))
        records = super().create(vals_list)
        for rec in records:
            if rec.employment_status in ("active", "joining"):
                rec._emit_jml(
                    "employee.joined",
                    {
                        "employee_id": rec.id,
                        "employee_code": rec.employee_code,
                        "branch_id": rec.branch_id.id if rec.branch_id else None,
                        "primary_role": rec.primary_role_id.code if rec.primary_role_id else None,
                        "joined_date": str(rec.joined_date) if rec.joined_date else None,
                        # M29 FR-SEC-027 creates the identity from this event: the
                        # account's display name and (password-setup) mail address
                        "name": rec.name,
                        "work_email": rec.work_email or None,
                    },
                )
        return records

    def write(self, vals):
        # The leaver set is decided on the status BEFORE the archive: after
        # the write every archived record derives to leaving/left.
        leavers = self.browse()
        if "active" in vals and not vals["active"]:
            leavers = self.filtered(lambda rec: rec.employment_status == "active")
        # A10 P1-3: the employee master is the real grant path for business
        # roles — a direct write must clear the same SoD gate assign_role
        # does, against the employee's FULL final set.
        if "primary_role_id" in vals or "additional_role_ids" in vals:
            for rec in self:
                self.env["fix.sod.control"].gate_role_set(rec._sod_final_role_set(vals))
        result = super().write(vals)
        # JML event emission on lifecycle changes
        for rec in leavers:
            rec._emit_leaver()
        if "primary_role_id" in vals or "additional_role_ids" in vals:
            for rec in self:
                rec._emit_jml(
                    "employee.role_changed",
                    {
                        "employee_id": rec.id,
                        "primary_role": rec.primary_role_id.code if rec.primary_role_id else None,
                    },
                )
        return result

    def action_mark_left(self):
        """Mark the employee as left and emit the leaver event (T05).

        M29 consumes employee.left and deprovisions Keycloak within 1 hour.
        KPI-090: zero orphaned accounts beyond 24 hours.
        """
        # A09 audit M21-6: a public method, so any internal user fired the
        # leaver event for a colleague and so deprovisioned their access.
        if not (self.env.su or self.env.user.has_group("hr.group_hr_user")):
            raise AccessError("Only HR may record that an employee has left.")
        for rec in self:
            rec.left_date = fields.Date.today()
            rec._emit_leaver()

    def _emit_leaver(self):
        self._emit_jml(
            "employee.left",
            {
                "employee_id": self.id,
                "employee_code": self.employee_code,
                "keycloak_user_id": self.keycloak_user_id,
                "left_date": str(self.left_date or fields.Date.today()),
            },
        )

    def _emit_jml(self, event_type: str, payload: dict):
        """Emit a JML event through the transactional outbox.

        M29's access-lifecycle consumer (P03-M02-T08) subscribes to these
        events and provisions/deprovisions Keycloak accordingly.
        """
        from libs.py.fix_events import publish

        publish(self.env, event_type, "hr.employee", self.id, payload)
        logger.info("M21-core: emitted %s for employee %s (id=%s)", event_type, self.name, self.id)

    @api.depends("active", "joined_date", "left_date")
    def _compute_employment_status(self):
        """Derive the employment status from Odoo's hr state."""
        for rec in self:
            if not rec.active:
                rec.employment_status = "left" if rec.left_date else "leaving"
            elif rec.joined_date and rec.joined_date <= fields.Date.today():
                rec.employment_status = "active"
            else:
                rec.employment_status = "joining"

    # -------------------------------------------------------------
    # M21 calls M29's published API (sync one-way) — P03-M08-T08
    # -------------------------------------------------------------
    def _sod_final_role_set(self, vals):
        """The employee's final business-role set once a vals dict lands:
        primary + additional (commands applied) + any register roles the
        linked user's Odoo groups already carry (A10 P1-3). Called on the
        record for a write, on the empty recordset for a create."""
        Sod = self.env["fix.sod.control"]
        primary = vals.get("primary_role_id") or self.primary_role_id.id
        additional = set(self.additional_role_ids.ids)
        for cmd in vals.get("additional_role_ids") or ():
            if isinstance(cmd, int):
                additional.add(cmd)
            elif cmd[0] == 3:
                additional.discard(cmd[1])
            elif cmd[0] == 4:
                additional.add(cmd[1])
            elif cmd[0] == 5:
                additional = set()
            elif cmd[0] == 6:
                additional = set(cmd[2])
        user_id = vals.get("user_id") or (self.user_id.id if self.user_id else False)
        final = {r for r in ({primary} | additional) if r}
        if user_id:
            final |= Sod._user_role_ids(self.env["res.users"].browse(user_id))
        return final

    def assign_role(self, role_code: str):
        """Call M29's published API to assign a business role (T08).

        This is the synchronous one-way call in the M21<->M29 break:
        M21 calls M29's API for role assignment; M29 consumes M21's
        events for lifecycle. NEVER the reverse (sync-both-ways = monolith).
        """
        role = self.env["fix.role"].search([("code", "=", role_code)], limit=1)
        if not role:
            raise ValueError(f"Role {role_code} not found in the reconciled register.")
        # SoD check before assignment (P03-M02-T04) — against the FULL final
        # set plus the user's register roles, not one hand-picked pair
        # (A10 P1-3: the pair-only check missed additional roles).
        self.env["fix.sod.control"].gate_role_set(
            self._sod_final_role_set({"additional_role_ids": [(4, role.id)]})
        )
        self.write({"additional_role_ids": [(4, role.id)]})
