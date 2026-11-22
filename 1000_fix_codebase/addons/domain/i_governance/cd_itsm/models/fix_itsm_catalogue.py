# M66 ITSM depth — service catalogue, problem management, licence register and
# the CMDB configuration items. Tickets, changes and assets live in fix_itsm.py /
# fix_itsm_ops.py.
#
# A12 workflow audit (2026-11-04) M66-10/11/13 and the finish audit (2026-11-07)
# M66-9, M66-11, M66-12:
#   - the catalogue keeps a trail, and only a Change Manager switches its approval
#     policy off; requires_approval gates fulfilment on the ticket;
#   - a problem goes investigating -> known error -> resolved -> verifying ->
#     closed, links its incidents and its fix change, and closes only on verified
#     absence of recurrence (BRU-ITS-03/04/05);
#   - seat assignments are records. Utilisation and state are measured, a daily
#     cron follows the clock, and over-use is a compliance exception that the
#     person who caused it cannot close (BRU-ITS-16/17).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_itsm import itsm_activity, itsm_param_float, itsm_require_superuser, itsm_resolve_employee

LICENCE_EXPIRING_DAYS = 30
AGENT_GROUP = "cd_itsm.group_itsm_agent"
CHANGE_MANAGER_GROUP = "cd_itsm.group_itsm_change_manager"
CAB_GROUP = "cd_itsm.group_itsm_cab_member"
PROBLEM_VERIFY_DAYS_PARAM = "cd_itsm.problem_verify_days"
PROBLEM_VERIFY_DAYS_DEFAULT = 30
LICENCE_REMEDIATION_DAYS_PARAM = "cd_itsm.licence_exception_days"
LICENCE_REMEDIATION_DAYS_DEFAULT = 30
SEATS_MIGRATED_PARAM = "cd_itsm.licence_seats_migrated"
_PROBLEM_FROZEN = {
    "title",
    "description",
    "root_cause",
    "workaround",
    "severity",
    "opened_on",
    "owner_id",
    "fix_change_id",
}


class FixItsmCatalogue(models.Model):
    _name = "fix.itsm.catalogue"
    _description = "IT Service Catalogue Item"
    _inherit = ["mail.thread"]
    _order = "category, name"

    code = fields.Char(required=True, index=True, tracking=True)
    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    category = fields.Selection(
        [
            ("access", "Access & Accounts"),
            ("hardware", "Hardware"),
            ("software", "Software"),
            ("network", "Network & Connectivity"),
            ("support", "Support & Advice"),
        ],
        required=True,
        default="support",
        tracking=True,
    )
    description = fields.Text()
    fulfilment_team = fields.Char(tracking=True)
    target_hours = fields.Float(string="Target fulfilment (hours)", default=8.0, tracking=True)
    calendar_id = fields.Many2one(
        "fix.working.calendar",
        string="SLA Calendar",
        tracking=True,
        help="BRU-ITS-19: the target hours count on this working calendar. Empty: "
        "cd_itsm.sla_calendar_id, else wall-clock hours.",
    )
    cost_per_request = fields.Monetary(
        string="Cost per request", currency_field="currency_id", tracking=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    requires_approval = fields.Boolean(
        default=False,
        tracking=True,
        help="M66-12: a request against this item cannot be fulfilled until the "
        "approver signs it off. Only a Change Manager or CAB member turns this off.",
    )
    active = fields.Boolean(default=True, tracking=True)

    _code_unique = models.Constraint("UNIQUE (code, company_id)", "Catalogue code is unique")

    def write(self, vals):
        if "requires_approval" in vals and not vals["requires_approval"] and not self.env.su:
            user = self.env.user
            if any(rec.requires_approval for rec in self) and not (
                user.has_group(CHANGE_MANAGER_GROUP) or user.has_group(CAB_GROUP)
            ):
                raise UserError(
                    "The approval policy of a catalogue item is switched off by a Change "
                    "Manager or a CAB member, not by the agent who fulfils its requests (M66-12)."
                )
        return super().write(vals)


class FixItsmProblem(models.Model):
    _name = "fix.itsm.problem"
    _description = "IT Problem"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "opened_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    title = fields.Char(required=True)
    description = fields.Text()
    root_cause = fields.Text()
    workaround = fields.Text()
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        required=True,
        default="medium",
        tracking=True,
    )
    opened_on = fields.Date(required=True, default=fields.Date.context_today)
    owner_id = fields.Many2one("res.users", string="Problem Owner")
    known_error = fields.Boolean(help="A documented cause + workaround exists.")
    state = fields.Selection(
        [
            ("open", "Open"),
            ("investigating", "Investigating"),
            ("known_error", "Known Error"),
            ("resolved", "Resolved"),
            ("verifying", "Verifying"),
            ("closed", "Closed"),
        ],
        required=True,
        default="open",
        tracking=True,
    )
    resolved_on = fields.Datetime(readonly=True)
    ticket_ids = fields.One2many("fix.itsm.ticket", "problem_id", string="Incidents")
    incident_count = fields.Integer(compute="_compute_incident_count", string="Incidents")
    fix_change_id = fields.Many2one(
        "fix.itsm.change",
        string="Fix Change",
        index=True,
        tracking=True,
        help="The change that removes the cause. A problem with a fix change "
        "resolves only once that change is implemented.",
    )
    verify_started_on = fields.Datetime(readonly=True, copy=False)
    verify_until = fields.Date(
        string="Verify Until",
        readonly=True,
        copy=False,
        help="BRU-ITS-05: the problem closes only after this date with no recurring "
        "incident (cd_itsm.problem_verify_days, default 30).",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "known_error",
            "resolved_on",
            "verify_started_on",
            "verify_until",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state == "closed" for rec in self):
            locked |= _PROBLEM_FROZEN
        return locked

    @api.depends("ticket_ids")
    def _compute_incident_count(self):
        for rec in self:
            rec.incident_count = len(rec.sudo().ticket_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.itsm.problem") or "PRB/New"
        return super().create(vals_list)

    def write(self, vals):
        frozen = self and not self._fix_guard_open() and _PROBLEM_FROZEN & set(vals)
        if frozen and any(rec.state == "closed" for rec in self):
            raise UserError("A closed problem stands as the record (M66-9).")
        return super().write(vals)

    def action_investigate(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Investigate an open problem.")
            rec._guarded().write({"state": "investigating"})

    def action_known_error(self):
        """A known error is a DOCUMENTED cause + workaround, reached by
        investigating (M66-9). Both texts are required."""
        for rec in self:
            if rec.state != "investigating":
                raise UserError(
                    "Mark a problem as known error while it is under investigation (M66-9)."
                )
            if not (rec.root_cause or "").strip():
                raise UserError("A known error needs its root cause documented first")
            if not (rec.workaround or "").strip():
                raise UserError(
                    "A known error needs its workaround documented (M66-10): the "
                    "register exists so the service desk can work around the fault."
                )
            rec._guarded().write({"state": "known_error", "known_error": True})

    def action_resolve(self):
        for rec in self:
            if rec.state not in ("investigating", "known_error"):
                raise UserError("Resolve a problem that is being investigated")
            if not (rec.root_cause or "").strip():
                raise UserError(
                    "A resolved problem names its root cause (M66-10): without it the "
                    "resolution cannot prevent recurrence."
                )
            change = rec.sudo().fix_change_id
            if change and change.state not in ("implemented", "reviewed"):
                raise UserError(
                    "The fix change %s is %s: the cause is not removed until it is implemented."
                    % (change.name, change.state)
                )
            rec._guarded().write({"state": "resolved", "resolved_on": fields.Datetime.now()})

    def action_verify(self):
        """Start the recurrence window (BRU-ITS-05)."""
        days = int(
            itsm_param_float(self.env, PROBLEM_VERIFY_DAYS_PARAM, PROBLEM_VERIFY_DAYS_DEFAULT)
        )
        for rec in self:
            if rec.state != "resolved":
                raise UserError("Verify a resolved problem.")
            rec._guarded().write(
                {
                    "state": "verifying",
                    "verify_started_on": fields.Datetime.now(),
                    "verify_until": fields.Date.add(fields.Date.context_today(rec), days=days),
                }
            )
            rec.message_post(body="Verifying: no recurrence allowed until %s." % rec.verify_until)

    def _recurrences(self):
        """Incidents linked to this problem since the window opened."""
        self.ensure_one()
        start = self.verify_started_on
        return self.sudo().ticket_ids.filtered(
            lambda t: t.ticket_type == "incident" and start and t.create_date >= start
        )

    def action_close(self):
        """BRU-ITS-05: closes only on verified absence of recurrence over the
        whole window."""
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "verifying":
                raise UserError(
                    "Close a problem after verifying it stayed fixed: start verification first "
                    "(BRU-ITS-05)."
                )
            if rec.verify_until and today < rec.verify_until:
                raise UserError(
                    "%s is being verified until %s: it closes on verified absence of "
                    "recurrence, not before (BRU-ITS-05)." % (rec.name, rec.verify_until)
                )
            if rec._recurrences():
                raise UserError(
                    "%s recurred during verification (%s)."
                    % (rec.name, ", ".join(rec._recurrences().mapped("name")))
                )
            rec._guarded().write({"state": "closed"})

    def _on_incident_linked(self):
        """An incident during the window is the recurrence the window watches
        for: the problem goes back to investigation (BRU-ITS-03/05)."""
        for rec in self.sudo().filtered(lambda p: p.state == "verifying"):
            if rec._recurrences():
                rec._guarded().write(
                    {"state": "investigating", "verify_started_on": False, "verify_until": False}
                )
                rec.message_post(body="Recurrence during verification: back to investigation.")
                itsm_activity(
                    rec,
                    rec.owner_id,
                    "Problem recurred: %s" % rec.name,
                    "A linked incident arrived during the verification window.",
                )

    @api.model
    def cron_problem_verification(self):
        """Daily: tell the owner a clean verification window has ended. A person
        still closes it; nothing is closed on his behalf."""
        itsm_require_superuser(self.env, "Problem verification")
        today = fields.Date.context_today(self)
        due = self.sudo().search([("state", "=", "verifying"), ("verify_until", "<=", today)])
        for rec in due:
            if rec._recurrences():
                rec._on_incident_linked()
                continue
            itsm_activity(
                rec,
                rec.owner_id or rec.create_uid,
                "Ready to close: %s" % rec.name,
                "No incident recurred during the verification window.",
            )
        return len(due)


class FixItsmLicence(models.Model):
    _name = "fix.itsm.licence"
    _description = "Software Licence"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "renewal_on, id"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    vendor = fields.Char(required=True)
    licence_type = fields.Selection(
        [
            ("per_user", "Per User"),
            ("per_device", "Per Device"),
            ("site", "Site / Enterprise"),
            ("subscription", "Subscription"),
        ],
        required=True,
        default="per_user",
    )
    seats_owned = fields.Integer(required=True, default=0, tracking=True)
    seat_ids = fields.One2many("fix.itsm.licence.seat", "licence_id", string="Seat Assignments")
    seats_assigned = fields.Integer(
        compute="_compute_seats_assigned",
        store=True,
        help="M66-11: counted from the seat assignment records, never typed.",
    )
    seats_declared = fields.Integer(
        string="Seats Declared (unverified)",
        readonly=True,
        default=0,
        help="The figure typed into the register before seats became records. It is "
        "not evidence: no named person stands behind it. It counts towards "
        "utilisation until the seats are recorded by name.",
    )
    unit_cost = fields.Monetary(
        string="Unit cost", currency_field="currency_id", groups=AGENT_GROUP
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    annual_cost = fields.Monetary(
        compute="_compute_cost", store=True, currency_field="currency_id", groups=AGENT_GROUP
    )
    purchased_on = fields.Date()
    renewal_on = fields.Date()
    utilisation_pct = fields.Float(compute="_compute_utilisation", store=True)
    compliance_state = fields.Selection(
        [("ok", "Within Entitlement"), ("over", "Over-Allocated")],
        compute="_compute_utilisation",
        store=True,
    )
    exception_ids = fields.One2many(
        "fix.itsm.licence.exception", "licence_id", string="Compliance Exceptions"
    )
    state = fields.Selection(
        [("active", "Active"), ("expiring", "Expiring"), ("expired", "Expired")],
        required=True,
        default="active",
        compute="_compute_state",
        store=True,
        tracking=True,
        help="M66-11: the licence status is the renewal date, not an opinion — "
        "expired once the renewal date passes, expiring within %d days of it. A daily "
        "cron follows the clock." % LICENCE_EXPIRING_DAYS,
    )

    def init(self):
        # Once: rows from before the seat records keep their typed figure as a
        # declared, unverified one. It is neither thrown away nor shown as measured.
        Params = self.env["ir.config_parameter"].sudo()
        if not Params.get_param(SEATS_MIGRATED_PARAM):
            self.env.cr.execute(
                "UPDATE fix_itsm_licence SET seats_declared = seats_assigned, seats_assigned = 0 "
                "WHERE COALESCE(seats_declared, 0) = 0 AND COALESCE(seats_assigned, 0) > 0"
            )
            Params.set_param(SEATS_MIGRATED_PARAM, "1")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "seats_assigned",
            "seats_declared",
            "utilisation_pct",
            "compliance_state",
        }

    @api.depends("seat_ids.state")
    def _compute_seats_assigned(self):
        for rec in self:
            rec.seats_assigned = len(rec.seat_ids.filtered(lambda s: s.state == "active"))

    @api.depends("seats_owned", "unit_cost", "licence_type")
    def _compute_cost(self):
        for rec in self:
            if rec.licence_type == "subscription":
                rec.annual_cost = rec.unit_cost or 0.0
            else:
                rec.annual_cost = (rec.seats_owned or 0) * (rec.unit_cost or 0.0)

    @api.depends("seats_owned", "seats_assigned", "seats_declared")
    def _compute_utilisation(self):
        for rec in self:
            used = max(rec.seats_assigned or 0, rec.seats_declared or 0)
            rec.utilisation_pct = (
                round(100.0 * used / rec.seats_owned, 1) if rec.seats_owned else 0.0
            )
            rec.compliance_state = "over" if used > (rec.seats_owned or 0) else "ok"

    def _state_for_today(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        if self.renewal_on and self.renewal_on < today:
            return "expired"
        if self.renewal_on and self.renewal_on <= fields.Date.add(
            today, days=LICENCE_EXPIRING_DAYS
        ):
            return "expiring"
        return "active"

    @api.depends("renewal_on")
    def _compute_state(self):
        for rec in self:
            rec.state = rec._state_for_today()

    @api.constrains("seats_owned", "seats_declared")
    def _check_seats(self):
        """M66-11: the register owns and declares a non-negative count. Real
        over-use is NOT refused here: it has to be recordable to be an exception."""
        for rec in self:
            if rec.seats_owned < 0:
                raise ValidationError("A licence owns a non-negative number of seats.")
            if rec.seats_declared < 0:
                raise ValidationError("A licence has a non-negative number of seats assigned.")

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.su:
            # Server-side loaders still speak the old typed figure; keep it as
            # what it is, a declared figure.
            for vals in vals_list:
                if vals.get("seats_assigned"):
                    vals["seats_declared"] = vals.pop("seats_assigned")
        return super().create(vals_list)

    # ---- seat assignments ----------------------------------------------------
    def _assert_agent(self):
        if not self.env.su and not self.env.user.has_group(AGENT_GROUP):
            raise UserError("Seats are assigned by the service desk.")

    def _seat_create(self, employee, over_entitlement, device_note=None):
        self.ensure_one()
        return (
            self.env["fix.itsm.licence.seat"]
            .sudo()
            .create(
                {
                    "licence_id": self.id,
                    "employee_id": employee.id,
                    "assigned_by_id": self.env.uid,
                    "over_entitlement": over_entitlement,
                    "note": device_note or False,
                }
            )
        )

    def action_assign_seat(self, employee=None):
        """BRU-ITS-16: a seat is assigned only from an available entitlement."""
        self._assert_agent()
        person = itsm_resolve_employee(self.env, employee)
        if not person:
            raise UserError("Name the employee who takes the seat.")
        for rec in self:
            if rec.state == "expired":
                raise UserError("%s has expired: renew it before assigning seats." % rec.name)
            held = rec.seat_ids.filtered(
                lambda s: s.state == "active" and s.employee_id == person
            )
            if held:
                # M66-2: one person, one active seat per licence — a second
                # assignment would silently eat an entitlement and inflate
                # the utilisation figure.
                raise UserError(
                    "%s already holds an active seat on %s (since %s)."
                    % (person.name, rec.name, held[0].create_date.date() if held[0].create_date else "earlier")
                )
            used = max(rec.seats_assigned, rec.seats_declared)
            if used >= rec.seats_owned:
                raise UserError(
                    "%s has no free seat (%d of %d in use): buy more, or record what was found "
                    "installed as over-use (BRU-ITS-16)." % (rec.name, used, rec.seats_owned)
                )
            rec._seat_create(person, False)
            rec.message_post(body="Seat assigned to %s." % person.name)

    def action_record_overuse(self, employee=None):
        """BRU-ITS-17: an installation found beyond the entitlement is recorded,
        and that opens a compliance exception."""
        self._assert_agent()
        person = itsm_resolve_employee(self.env, employee)
        if not person:
            raise UserError("Name the employee on whose device it was found.")
        for rec in self:
            rec._seat_create(person, True)
            rec.message_post(body="Over-use recorded for %s." % person.name)

    def _sync_compliance(self):
        """Open one exception while a licence is over, naming who caused it."""
        Exception_ = self.env["fix.itsm.licence.exception"].sudo()
        days = int(
            itsm_param_float(
                self.env, LICENCE_REMEDIATION_DAYS_PARAM, LICENCE_REMEDIATION_DAYS_DEFAULT
            )
        )
        for rec in self.sudo():
            if rec.compliance_state != "over":
                continue
            if rec.exception_ids.filtered(lambda e: e.state == "open"):
                continue
            last = rec.seat_ids.filtered(lambda s: s.state == "active").sorted("id")[-1:]
            Exception_.create(
                {
                    "licence_id": rec.id,
                    "seats_over": max(rec.seats_assigned, rec.seats_declared) - rec.seats_owned,
                    "installer_id": last.assigned_by_id.id or False,
                    "remediation_due": fields.Date.add(fields.Date.context_today(rec), days=days),
                }
            )
            rec.message_post(body="Over-allocated: a compliance exception is open (BRU-ITS-17).")

    @api.model
    def cron_refresh_licences(self):
        """Daily (M66-11): the state follows the clock, over-use opens its
        exception, and an exception past its remediation date is chased."""
        itsm_require_superuser(self.env, "The licence refresh")
        changed = 0
        licences = self.sudo().search([])
        for rec in licences:
            wanted = rec._state_for_today()
            if rec.state != wanted:
                rec._guarded().write({"state": wanted})
                changed += 1
        licences._sync_compliance()
        today = fields.Date.context_today(self)
        late = (
            self.env["fix.itsm.licence.exception"]
            .sudo()
            .search([("state", "=", "open"), ("remediation_due", "<", today)])
        )
        group = self.env.ref(CHANGE_MANAGER_GROUP, raise_if_not_found=False)
        managers = group.sudo().all_user_ids.filtered("active") if group else self.env["res.users"]
        for exception in late:
            for user in managers:
                itsm_activity(
                    exception,
                    user,
                    "Licence exception overdue: %s" % exception.licence_id.name,
                    "Remediate or buy: the remediation date has passed.",
                )
        return changed


class FixItsmLicenceSeat(models.Model):
    """One seat held by one person: utilisation is counted from these, not typed."""

    _name = "fix.itsm.licence.seat"
    _description = "Licence Seat Assignment"
    _inherit = ["fix.guarded.mixin"]
    _order = "id desc"

    licence_id = fields.Many2one(
        "fix.itsm.licence", required=True, index=True, ondelete="cascade", string="Licence"
    )
    company_id = fields.Many2one(
        "res.company", related="licence_id.company_id", store=True, index=True
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True, string="Employee")
    assigned_by_id = fields.Many2one("res.users", string="Assigned By", readonly=True)
    assigned_on = fields.Date(default=fields.Date.context_today, readonly=True)
    revoked_on = fields.Date(readonly=True)
    revoked_by_id = fields.Many2one("res.users", string="Revoked By", readonly=True)
    over_entitlement = fields.Boolean(string="Over Entitlement", readonly=True)
    note = fields.Char()
    state = fields.Selection(
        [("active", "Active"), ("revoked", "Revoked")], required=True, default="active"
    )

    @api.depends("licence_id", "employee_id")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s - %s" % (
                rec.sudo().licence_id.name or "",
                rec.sudo().employee_id.name or "",
            )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "assigned_by_id",
            "assigned_on",
            "revoked_on",
            "revoked_by_id",
            "over_entitlement",
            "licence_id",
            "employee_id",
        }

    @api.constrains("employee_id")
    def _check_active_employee(self):
        for rec in self:
            if not rec.employee_id.active:
                raise ValidationError("A seat is held by an active employee.")

    @api.model_create_multi
    def create(self, vals_list):
        seats = super().create(vals_list)
        seats.mapped("licence_id")._sync_compliance()
        return seats

    def action_revoke(self):
        if not self.env.su and not self.env.user.has_group(AGENT_GROUP):
            raise UserError("Seats are revoked by the service desk.")
        for rec in self:
            if rec.state != "active":
                raise UserError("This seat is already revoked.")
            rec.sudo()._guarded().write(
                {
                    "state": "revoked",
                    "revoked_on": fields.Date.context_today(rec),
                    "revoked_by_id": self.env.uid,
                }
            )


class FixItsmLicenceException(models.Model):
    """BRU-ITS-17: over-use is an exception to remediate within a defined period.
    SoD: the person who created the installation cannot close it."""

    _name = "fix.itsm.licence.exception"
    _description = "Licence Compliance Exception"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True)
    licence_id = fields.Many2one(
        "fix.itsm.licence", required=True, index=True, ondelete="cascade", string="Licence"
    )
    company_id = fields.Many2one(
        "res.company", related="licence_id.company_id", store=True, index=True
    )
    seats_over = fields.Integer(string="Seats Over", readonly=True)
    installer_id = fields.Many2one("res.users", string="Installed By", readonly=True)
    raised_on = fields.Date(default=fields.Date.context_today, readonly=True)
    remediation_due = fields.Date(string="Remediate By")
    closure_note = fields.Text(string="Closure Note", readonly=True)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)
    closed_on = fields.Date(readonly=True)
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], required=True, default="open", tracking=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "seats_over",
            "installer_id",
            "raised_on",
            "closure_note",
            "closed_by_id",
            "closed_on",
            "licence_id",
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.itsm.licence.exception") or "LCE/New"
                )
        return super().create(vals_list)

    def action_close_exception(self, closure_note=None):
        """Closes only when the measured count is back inside the entitlement,
        and never by the person who installed it."""
        if not self.env.su and not self.env.user.has_group(AGENT_GROUP):
            raise UserError("A licence exception is closed by the service desk.")
        if not (closure_note or "").strip():
            raise UserError("Say how it was remediated: the closure note is required.")
        for rec in self:
            if rec.state != "open":
                raise UserError("This exception is already closed.")
            if not self.env.su and rec.installer_id == self.env.user:
                raise UserError(
                    "You created this installation: another person closes its compliance "
                    "exception (segregation of duties)."
                )
            if rec.licence_id.compliance_state == "over":
                raise UserError(
                    "%s is still over-allocated: revoke seats or buy more first."
                    % rec.licence_id.name
                )
            rec._guarded().write(
                {
                    "state": "closed",
                    "closure_note": closure_note,
                    "closed_by_id": self.env.uid,
                    "closed_on": fields.Date.context_today(rec),
                }
            )


class FixItsmCi(models.Model):
    _name = "fix.itsm.ci"
    _description = "Configuration Item (CMDB)"
    _order = "ci_class, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    ci_class = fields.Selection(
        [
            ("server", "Server"),
            ("network", "Network Device"),
            ("endpoint", "Endpoint"),
            ("application", "Application"),
            ("database", "Database"),
            ("service", "Business Service"),
        ],
        required=True,
        default="server",
    )
    ci_key = fields.Char(required=True, help="Stable identifier (hostname, app key, service code).")
    environment_id = fields.Many2one("fix.platform.environment", string="Environment")
    owner_id = fields.Many2one("res.users", string="Owner")
    depends_on = fields.Many2many(
        "fix.itsm.ci",
        "fix_itsm_ci_depends_rel",
        "ci_id",
        "depends_on_id",
        string="Depends On",
        help="M66-12: the upstream configuration items this one depends on, as "
        "relations rather than typed keys.",
    )
    criticality = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        required=True,
        default="medium",
    )
    support_hours = fields.Selection(
        [("business", "Business hours"), ("extended", "Extended (07:00-23:00)"), ("24x7", "24x7")],
        required=True,
        default="business",
    )
    life_status = fields.Selection(
        [("in_service", "In Service"), ("maintenance", "Maintenance"), ("retired", "Retired")],
        required=True,
        default="in_service",
    )
    asset_id = fields.Many2one("fix.itsm.asset", string="Linked Asset")

    _ci_unique = models.Constraint("UNIQUE (ci_key, company_id)", "CI key is unique per company")

    @api.constrains("life_status", "asset_id")
    def _check_asset_life(self):
        """M66-13: nothing runs in service on retired hardware — the CMDB must
        not describe service the asset register has already ended."""
        for rec in self:
            if rec.life_status == "in_service" and rec.asset_id and rec.asset_id.state == "retired":
                raise ValidationError(
                    "CI %s is in service but its asset %s is retired (M66-13). Retire "
                    "the CI or relink it to live hardware." % (rec.ci_key, rec.asset_id.asset_tag)
                )

    @api.constrains("depends_on")
    def _check_depends_on(self):
        if self._has_cycle("depends_on"):
            raise ValidationError("A configuration item cannot depend on itself, even indirectly.")
