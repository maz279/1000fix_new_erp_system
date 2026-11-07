# fix.branch — operational branch, the OU isolation unit (P03-M04-T01).
# 51+ branches; every transactional model carries operating_unit_id (AS-03).
#
# A12 finish E19 (M30-7, BRU-ADM-01/06): one Platform Admin appointed himself
# manager and closed a branch by toggling `active`. A branch now has a lifecycle:
# provisioning -> live -> suspended -> closed. A closure takes a second Platform
# Admin; closures, manager and calendar changes leave an audit row.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_entity import PLATFORM_ADMIN_GROUP, audit_event, require_platform_admin

AUDITED_BRANCH_FIELDS = {"manager_id": "manager", "calendar_id": "working calendar"}


class FixBranch(models.Model):
    """An operational branch — the isolation unit for OU-based record rules."""

    _name = "fix.branch"
    _description = "Branch"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "entity_id, code"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_entity_unique = models.Constraint(
        "UNIQUE (code, entity_id)", "Branch code must be unique within an entity"
    )

    code = fields.Char(string="Branch Code", required=True, size=10, tracking=True)
    name = fields.Char(string="Branch Name", required=True, tracking=True)
    name_bn = fields.Char(string="Branch Name (Bengali)", help="Bengali branch name — DE-17")
    # AS-03: company_id (derived from entity's company)
    company_id = fields.Many2one(
        "res.company", related="entity_id.company_id", store=True, string="Company"
    )
    entity_id = fields.Many2one("fix.entity", string="Entity", required=True, ondelete="cascade")
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        required=True,
        ondelete="restrict",
        help="AS-03: every transactional model carries operating_unit_id. "
        "This is the isolation mechanism OCA operating-unit provides.",
    )
    zone_id = fields.Many2one(
        "fix.zone", string="Dispatch Zone", help="Consumed by M02 dispatch in Phase 5"
    )
    address_id = fields.Many2one(
        "fix.bd.address", string="Address", help="Bangladesh address hierarchy"
    )
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    # Layer rule (FF-17 / live-install finding): this PLATFORM module cannot
    # depend on Odoo hr, so the manager is the accountable LOGIN user here;
    # cd_employee_core extends fix.branch with the HR-grade employee pointer
    # (employee_manager_id -> hr.employee) where hr actually exists.
    manager_id = fields.Many2one("res.users", string="Branch Manager")
    active = fields.Boolean(default=True, tracking=True)
    calendar_id = fields.Many2one(
        "fix.working.calendar",
        string="Working Calendar",
        tracking=True,
        help="M02's W2 availability stub reads this",
    )
    state = fields.Selection(
        [
            ("provisioning", "Provisioning"),
            ("live", "Live"),
            ("suspended", "Suspended"),
            ("closed", "Closed"),
        ],
        required=True,
        default="provisioning",
        tracking=True,
        help="Existing branches were migrated from `active`: live, or closed if archived.",
    )
    closure_requested_by_id = fields.Many2one(
        "res.users", string="Closure Requested By", readonly=True, copy=False
    )
    closure_reason = fields.Char(string="Closure Reason", readonly=True, copy=False)
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        copy=False,
        help="MIG-03: permanent source system reference (FR-SRM-088)",
    )

    # A12 X4 / M30-7: entity_id and operating_unit_id are the branch's place
    # in the isolation structure. A clerk moved a branch into another
    # operating unit with a plain write, silently re-scoping every record rule
    # that resolves through it. On an EXISTING branch they change only through
    # superuser code (a governed migration / the M64 provisioning path);
    # create sets them, as it always did.
    def _fix_guarded_fields(self) -> set:
        # `active` follows the lifecycle: toggling it was how a branch was closed.
        return super()._fix_guarded_fields() | {
            "state",
            "active",
            "closure_requested_by_id",
            "closure_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            return locked | {"entity_id", "operating_unit_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        # A12 X4 / M30-7 (b01): the branch master feeds dispatch, queue-SLA
        # escalation and the public customer branch list; only Platform Admin.
        require_platform_admin(self.env, "The branch register")
        return super().create(vals_list)

    def write(self, vals):
        require_platform_admin(self.env, "The branch register")
        structural = {"entity_id", "operating_unit_id"} & set(vals)
        if structural and not self._fix_guard_open():
            for rec in self:
                for name in sorted(structural):
                    new = vals[name]
                    new = new.id if hasattr(new, "id") else (int(new) if new else False)
                    if new != rec[name].id:
                        raise UserError(
                            "A branch's %s is structural: %s (with every record "
                            "rule and OU default that resolves through it) "
                            "cannot be moved by an edit. Raise a governed "
                            "change (a new branch, or the M64 provisioning "
                            "path) instead." % (rec._fields[name].string, rec.display_name)
                        )
        if vals.get("manager_id") == self.env.uid and not self._fix_guard_open():
            raise UserError(
                "You cannot appoint yourself branch manager: another Platform Admin "
                "makes that change."
            )
        audited = set(AUDITED_BRANCH_FIELDS) & set(vals)
        before = {rec.id: {n: rec[n].id for n in audited} for rec in self} if audited else {}
        result = super().write(vals)
        for rec in self:
            for name in audited:
                if before[rec.id][name] != rec[name].id:
                    rec._branch_audit(
                        "branch.%s_changed" % name.removesuffix("_id"),
                        "%s changed to %s"
                        % (AUDITED_BRANCH_FIELDS[name], rec[name].display_name or "none"),
                    )
        # A12 finish E20 / BRU-ADM-05: a row whose stored company was lost cannot
        # be repaired through the structural entity field, so any edit re-derives it.
        lost = self.filtered(lambda b: not b.company_id and b.entity_id.company_id)
        if lost:
            self.env.add_to_compute(self._fields["company_id"], lost)
        return result

    def _branch_audit(self, event, detail):
        for rec in self:
            audit_event(
                rec.env,
                event,
                "fix.branch,%d" % rec.id,
                "%s (%s) by %s" % (detail, rec.code, rec.env.user.name),
            )

    def _set_branch_state(self, new_state, from_states, reason=None, **extra):
        for rec in self:
            require_platform_admin(rec.env, "The branch register")
            if rec.state not in from_states:
                raise UserError(
                    "Branch %s is %s and cannot move to %s."
                    % (rec.code, dict(rec._fields["state"].selection)[rec.state], new_state)
                )
            rec._guarded().write({"state": new_state, **extra})
            rec._branch_audit("branch.state_%s" % new_state, reason or new_state)
            if reason:
                rec.message_post(body="%s: %s" % (new_state, reason))

    def action_go_live(self):
        self._set_branch_state("live", ("provisioning", "suspended"), active=True)
        return True

    def action_suspend(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say why this branch is being suspended.")
        self._set_branch_state("suspended", ("live", "provisioning"), reason=reason.strip())
        return True

    def action_request_closure(self, reason=None):
        """First signature on a closure. The branch stays open until a second
        Platform Admin confirms."""
        if not (reason or "").strip():
            raise UserError("Say why this branch is being closed.")
        for rec in self:
            require_platform_admin(rec.env, "The branch register")
            if rec.state == "closed":
                raise UserError("Branch %s is already closed." % rec.code)
            rec._guarded().write(
                {"closure_requested_by_id": rec.env.uid, "closure_reason": reason.strip()[:250]}
            )
            rec._branch_audit("branch.closure_requested", reason.strip())
            rec.message_post(body="Closure requested: %s" % reason.strip())
        return True

    def action_confirm_closure(self):
        for rec in self:
            require_platform_admin(rec.env, "The branch register")
            if not rec.closure_requested_by_id:
                raise UserError("No closure has been requested for branch %s." % rec.code)
            if not rec.env.su and rec.env.user == rec.closure_requested_by_id:
                raise UserError(
                    "A second person confirms a branch closure: you requested this one."
                )
            if not (rec.env.su or rec.env.user.has_group(PLATFORM_ADMIN_GROUP)):
                raise UserError("Confirming a branch closure needs the 'Platform Admin' role.")
            rec._set_branch_state(
                "closed",
                ("provisioning", "live", "suspended"),
                reason=rec.closure_reason,
                active=False,
            )
        return True

    def unlink(self):
        # BRU-ADM-07: a branch is never deleted (the unlink ACL already
        # refuses non-admins; this keeps the promise at the ORM too).
        require_platform_admin(self.env, "The branch register")
        raise UserError(
            "A branch is never deleted (BRU-ADM-07). Suspend it or request its " "closure instead."
        )

    @api.onchange("entity_id")
    def _onchange_entity(self):
        if self.entity_id and self.entity_id.company_id:
            return {
                "domain": {"operating_unit_id": [("company_id", "=", self.entity_id.company_id.id)]}
            }
