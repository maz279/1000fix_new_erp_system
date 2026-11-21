# fix_equipment_ops — M45: kits, issue/return custody, transfers, physical
# verification, out-of-service enforcement, PM/corrective jobs and usage capture.
# The equipment register and calibration records live in fix_equipment.py.
#
# A07 audit (2026-11-03) D1: every workflow field below (issue, transfer,
# verification, out-of-service and PM state, and the equipment's operational
# status) was writable by any internal user, through the ORM and the P03 form.
# Each model now names its guarded fields (fix.guarded.mixin) and moves them
# only in its transition methods, through `_guarded()`. A record in a terminal
# state is frozen for users. Superuser code (seeds, data loads, sudo service
# calls) stays trusted.
#
# A07 P1 (2026-11-04): the ops rows carry their equipment's company and
# operating unit (record rules, M45-10); custody, out-of-service, loss and
# transfer changes publish events (T-08, M45-12); a nightly job escalates
# overdue custody; a kit is issued and returned as one unit.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_equipment import (
    ROLE_CUSTODIAN,
    ROLE_QM,
    m45_has_role,
    m45_require_role,
    m45_today,
)

# AUT-EAM-08: notify the holder when the return date passes, escalate to the
# branch manager at +3 days and to the Quality Manager at +7 (spec §11).
CUSTODY_ESCALATION_DAYS = ((7, 3), (3, 2), (1, 1))


def _ops_company(comodel="equipment_id"):
    return fields.Many2one(
        related="%s.company_id" % comodel, store=True, index=True, string="Company"
    )


def _ops_unit(comodel="equipment_id"):
    return fields.Many2one(
        related="%s.operating_unit_id" % comodel, store=True, index=True, string="Operating Unit"
    )


class FixEquipmentExtend(models.Model):
    _inherit = "fix.equipment"

    operational_status = fields.Selection(
        [
            ("available", "Available"),
            ("issued", "Issued"),
            ("out_of_service", "Out of Service"),
            # A07 P1 (2026-11-04) FR-EAM-039: not found at a physical count
            ("missing", "Lost / Missing"),
            ("retired", "Retired"),
        ],
        required=True,
        default="available",
        index=True,
    )

    def _m45_released_status(self):
        """The status an item returns to when a hold on it ends: missing while
        a count has not found it again, out of service while an out-of-service
        record is open, issued while an issue is open, otherwise available."""
        self.ensure_one()
        rec = self.sudo()
        if rec.missing_verification_id:
            return "missing"
        if rec.env["fix.equipment.oos"].search_count(
            [("equipment_id", "=", rec.id), ("state", "=", "open")]
        ):
            return "out_of_service"
        if rec.env["fix.equipment.issue"].search_count(
            [("equipment_id", "=", rec.id), ("state", "=", "issued")]
        ):
            return "issued"
        return "available"


class FixCalibrationExtend(models.Model):
    _inherit = "fix.calibration"

    certificate_ref = fields.Char(string="Certificate Reference")
    trace_no = fields.Char(string="Trace Number")


# A kit's member list is fixed while any member is out on a kit issue.
KIT_ISSUE_FIELDS = {"accountable_employee_id", "completeness_checked_at"}


class FixEquipmentKit(models.Model):
    _name = "fix.equipment.kit"
    _description = "Equipment Kit"
    _inherit = ["fix.guarded.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    description = fields.Text()
    line_ids = fields.One2many("fix.equipment.kit.line", "kit_id", string="Equipment")
    active = fields.Boolean(default=True)
    # A07 P1 (2026-11-04) M45-13 / FR-EAM-007: a kit is issued and returned as
    # one unit, with one accountable holder and a completeness check.
    branch_id = fields.Many2one("fix.branch", string="Branch")
    accountable_employee_id = fields.Many2one(
        "hr.employee",
        string="Accountable Holder",
        readonly=True,
        help="Who holds the kit now; set by Issue Kit, cleared by Return Kit.",
    )
    issue_to_id = fields.Many2one(
        "hr.employee", string="Issue To", help="The holder the next Issue Kit hands it to."
    )
    issue_due_on = fields.Date(string="Return Due")
    return_condition = fields.Selection(
        [("good", "Serviceable"), ("damaged", "Damaged / Faulty")],
        string="Condition on Return",
        help="Recorded on every member when the kit is returned.",
    )
    completeness_checked_at = fields.Datetime(string="Completeness Checked", readonly=True)
    issue_ids = fields.One2many("fix.equipment.issue", "kit_id", string="Kit Issues")
    state = fields.Selection(
        [("available", "Available"), ("issued", "Issued"), ("partial", "Partly Issued")],
        compute="_compute_kit_state",
        store=True,
        string="Kit Status",
    )

    _code_unique = models.Constraint("UNIQUE (code)", "Kit code must be unique")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | KIT_ISSUE_FIELDS

    @api.depends("issue_ids.state", "issue_ids.equipment_id", "line_ids")
    def _compute_kit_state(self):
        for rec in self:
            open_issues = rec.sudo().issue_ids.filtered(lambda i: i.state == "issued")
            if not open_issues:
                rec.state = "available"
            elif len(open_issues.mapped("equipment_id")) >= len(rec.sudo().line_ids):
                rec.state = "issued"
            else:
                rec.state = "partial"

    def _m45_open_issues(self):
        self.ensure_one()
        return (
            self.env["fix.equipment.issue"]
            .sudo()
            .search([("kit_id", "=", self.id), ("state", "=", "issued")])
        )

    def action_issue_kit(self):
        """Issue every member to one holder, all or none (each member passes
        the issue checks: fit, available, not already out)."""
        for rec in self:
            if not rec.line_ids:
                raise UserError("Kit %s has no equipment to issue." % rec.name)
            if rec._m45_open_issues():
                raise UserError("Kit %s is already out; return it first." % rec.name)
            if not rec.issue_to_id:
                raise UserError("Choose who the kit is issued to (Issue To).")
            # the token lets Issue Kit set kit_id; every issue check still runs
            Issue = self.env["fix.equipment.issue"]._guarded()
            for line in rec.line_ids:
                Issue.create(
                    {
                        "equipment_id": line.equipment_id.id,
                        "custodian_id": rec.issue_to_id.id,
                        "due_on": rec.issue_due_on or False,
                        "reference": "Kit %s" % rec.code,
                        "kit_id": rec.id,
                    }
                )
            rec._guarded().write({"accountable_employee_id": rec.issue_to_id.id})
        return True

    def action_return_kit(self):
        """Return every member still out on the kit issue, with the kit's
        condition, and stamp the completeness check: every member is back."""
        # releasing the kit below is the system's; returning it is the role's
        self.check_access("write")
        for rec in self:
            open_issues = rec._m45_open_issues()
            if not open_issues:
                raise UserError("Kit %s is not out on issue." % rec.name)
            missing = rec.line_ids.mapped("equipment_id") - open_issues.mapped("equipment_id")
            stray = missing.filtered(lambda e: e.sudo().operational_status == "issued")
            if stray:
                raise UserError(
                    "Kit %s is incomplete: %s is out on another issue. Return it to the kit "
                    "first." % (rec.name, ", ".join(stray.mapped("name")))
                )
            # the last member back releases the kit (_m45_release_when_home)
            open_issues.with_env(self.env).action_return(condition=rec.return_condition or None)
        return True

    def _m45_release_when_home(self):
        """Once no member is out, the kit has no holder and every member is back,
        however they came back (Return Kit, or one by one on their own issues).
        The condition on return described that return: it is never reused."""
        for rec in self:
            if not rec._m45_open_issues():
                rec.sudo()._guarded().write(
                    {
                        "accountable_employee_id": False,
                        "completeness_checked_at": fields.Datetime.now(),
                        "return_condition": False,
                    }
                )


class FixEquipmentKitLine(models.Model):
    _name = "fix.equipment.kit.line"
    _description = "Kit Line"
    _order = "kit_id, id"

    kit_id = fields.Many2one("fix.equipment.kit", required=True, ondelete="cascade", index=True)
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="kit_id.company_id", store=True, index=True)

    _unique_equipment = models.Constraint(
        "UNIQUE (kit_id, equipment_id)", "An equipment item appears once per kit"
    )

    def _m45_check_kit_home(self, kits):
        if self.env.su:
            return
        for kit in kits:
            if kit._m45_open_issues():
                raise UserError(
                    "Kit %s is out on issue: its members change only once it is returned."
                    % kit.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        kits = self.env["fix.equipment.kit"].browse(
            [v.get("kit_id") for v in vals_list if v.get("kit_id")]
        )
        self._m45_check_kit_home(kits)
        return super().create(vals_list)

    def write(self, vals):
        self._m45_check_kit_home(self.mapped("kit_id"))
        return super().write(vals)

    def unlink(self):
        self._m45_check_kit_home(self.mapped("kit_id"))
        return super().unlink()


# An issue that has been returned is closed custody history.
ISSUE_RETURNED_FROZEN = {
    "equipment_id",
    "custodian_id",
    "reference",
    "issued_on",
    "due_on",
    "condition_out",
    "condition_in",
    "return_condition",
}


class FixEquipmentIssue(models.Model):
    _name = "fix.equipment.issue"
    _description = "Equipment Issue / Return"
    _inherit = ["fix.guarded.mixin"]
    _order = "issued_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    company_id = _ops_company()
    operating_unit_id = _ops_unit()
    custodian_id = fields.Many2one("hr.employee", string="Custodian", required=True)
    reference = fields.Char(string="Job / Ticket Ref")
    issued_on = fields.Date(required=True, default=lambda self: m45_today(self.env))
    due_on = fields.Date()
    returned_on = fields.Date(readonly=True)
    condition_out = fields.Char()
    condition_in = fields.Char(help="What the returner found: describe any damage.")
    # A07 audit (2026-11-03) M45-5, BRU-EAM-10: action_return took no condition,
    # so a damaged return went straight back to available. The returner states
    # the condition; a damaged item goes out of service, never to available.
    return_condition = fields.Selection(
        [("good", "Serviceable"), ("damaged", "Damaged / Faulty")],
        string="Condition on Return",
    )
    state = fields.Selection(
        [("issued", "Issued"), ("returned", "Returned")], required=True, default="issued"
    )
    # A07 audit (2026-11-03) M45-5 / D9: is_overdue was STORED and depended on
    # due_on/state only, so it never turned True as the due date passed (live
    # issues due 30 Oct still read False). It is computed at read time now,
    # with a search method so the overdue filters and KPIs keep working.
    is_overdue = fields.Boolean(compute="_compute_overdue", search="_search_is_overdue")
    # A07 P1 (2026-11-04): the kit this member went out with, and the
    # escalation level the nightly job reached (AUT-EAM-08)
    kit_id = fields.Many2one("fix.equipment.kit", string="Kit", readonly=True, index=True)
    overdue_level = fields.Integer(
        string="Overdue Escalation",
        readonly=True,
        help="0 none, 1 holder notified, 2 branch manager (+3 days), 3 Quality Manager (+7 days).",
    )
    # A07 ERP audit (2026-11-20) M45-01: the return date moves only through
    # Extend Due, by a store keeper / QM, with the reason and the first date kept
    due_original_on = fields.Date(string="Originally Due", readonly=True, copy=False)
    due_extension_count = fields.Integer(string="Extensions", readonly=True, copy=False)
    due_extension_note = fields.Text(string="Extension History", readonly=True, copy=False)
    due_extended_by_id = fields.Many2one(
        "res.users", string="Last Extended By", readonly=True, copy=False
    )
    proposed_due_on = fields.Date(
        string="New Return Date",
        copy=False,
        help="Set it, then Extend Due (the reason is asked for): the due date itself is "
        "fixed once issued.",
    )
    # M45-15: a holder's hand-in (no store keeper condition check)
    handed_in_by_holder = fields.Boolean(
        string="Handed In by Holder",
        readonly=True,
        copy=False,
        help="The holder handed it back without a store keeper's condition check: it waits "
        "out of service for one.",
    )

    def _fix_guarded_fields(self) -> set:
        # M45-5: an issue forged to "returned" by write left the item "issued"
        # with no return date; only action_return closes an issue.
        # A07 P1: only Issue Kit links a member to its kit
        guarded = super()._fix_guarded_fields() | {
            "state",
            "returned_on",
            "overdue_level",
            "kit_id",
            "due_original_on",
            "due_extension_count",
            "due_extension_note",
            "due_extended_by_id",
            "handed_in_by_holder",
        }
        if self:
            # A07 ERP audit M45-01: an OPEN issue was re-pointed to another
            # holder (exit clearance then passed), back-dated or extended by a
            # plain write. Who holds what since when is fixed once issued: a new
            # holder is a return and a new issue (or a transfer); the due date
            # moves only through action_extend_due.
            guarded |= {"equipment_id", "custodian_id", "issued_on", "due_on"}
        if any(rec.state == "returned" for rec in self):
            guarded |= ISSUE_RETURNED_FROZEN
        return guarded

    def action_extend_due(self, new_due=None, reason=None):
        """Move the expected return date (FR-EAM-015): a store keeper or the
        Quality Manager, with a reason; the first date and every change are
        kept, and the escalation starts again from the new date."""
        m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), "Extending a custody due date")
        try:
            typed = fields.Date.to_date(new_due) if new_due else False
        except (TypeError, ValueError):
            typed = False
        note = reason.strip() if isinstance(reason, str) else ""
        if not note:
            raise UserError("State why the return date is extended.")
        today = m45_today(self.env)
        for rec in self:
            new = typed or rec.proposed_due_on
            if not new:
                raise UserError("Give the new return date (New Return Date) first.")
            if rec.state != "issued":
                raise UserError("Only an open issue has a return date to extend.")
            if new < today or (rec.due_on and new <= rec.due_on):
                raise UserError(
                    "The new return date (%s) must be after the current one (%s) and not in "
                    "the past." % (new, rec.due_on or "none")
                )
            if not self.env.su and rec.custodian_id.user_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you hold %s, so another store keeper extends "
                    "its return date." % rec.equipment_id.name
                )
            line = "%s: %s -> %s by %s: %s" % (
                today,
                rec.due_on or "none",
                new,
                self.env.user.name,
                note,
            )
            rec._guarded().write(
                {
                    "due_original_on": rec.due_original_on or rec.due_on or False,
                    "due_on": new,
                    "due_extension_count": rec.due_extension_count + 1,
                    "due_extension_note": "\n".join(
                        part for part in (rec.due_extension_note, line) if part
                    ),
                    "due_extended_by_id": self.env.user.id,
                    "overdue_level": 0,
                    "proposed_due_on": False,
                }
            )
        return True

    @api.depends("due_on", "state")
    def _compute_overdue(self):
        today = m45_today(self.env)
        for rec in self:
            rec.is_overdue = bool(rec.due_on and rec.state == "issued" and rec.due_on < today)

    def _search_is_overdue(self, operator, value):
        # the ORM hands boolean conditions over as in / not in [True]; the
        # negative form is derived by the ORM from this positive one
        if operator != "in":
            return NotImplemented
        today = m45_today(self.env)
        overdue = [("state", "=", "issued"), ("due_on", "!=", False), ("due_on", "<", today)]
        if True in value:
            return overdue
        return ["!", "&", "&", *overdue]

    # A07 audit (2026-11-03) M45-4 / M45-5: issuing never looked at the
    # instrument. An overdue, failed or never-calibrated item was issued; an
    # OUT-OF-SERVICE item was issued and create() overwrote its status to
    # "issued", erasing the out-of-service state; a retired item was issued;
    # and the same item was issued to two custodians at once.
    def _m45_check_issuable(self):
        for rec in self:
            equipment = rec.equipment_id.sudo()
            if rec.state != "issued":
                continue
            # custody truth holds for every caller, superuser included: these
            # are facts about the item, not approvals
            if equipment.operational_status in ("out_of_service", "retired", "missing"):
                label = dict(equipment._fields["operational_status"].selection).get(
                    equipment.operational_status
                )
                raise UserError("%s is %s and cannot be issued" % (equipment.name, label.lower()))
            if (
                self.env["fix.equipment.transfer"]
                .sudo()
                .search_count([("equipment_id", "=", equipment.id), ("state", "=", "dispatched")])
            ):
                raise UserError(
                    "%s is in transit to another branch and cannot be issued until the "
                    "transfer is received" % equipment.name
                )
            # fitness: superuser code (seeds, data loads, sudo service calls)
            # stays trusted; every user path is checked. The item's own status
            # was checked above (a second open issue is the constraint below).
            if not self.env.su:
                problem = equipment._m45_calibration_problem()
                if problem:
                    raise UserError("Cannot issue: " + problem)

    @api.constrains("equipment_id", "state")
    def _check_one_open_issue(self):
        """BRU-EAM-07: exactly one named holder at a time."""
        for rec in self.filtered(lambda r: r.state == "issued"):
            others = self.sudo().search_count(
                [
                    ("equipment_id", "=", rec.equipment_id.id),
                    ("state", "=", "issued"),
                    ("id", "!=", rec.id),
                ]
            )
            if others:
                raise ValidationError(
                    "%s is already issued; return it before issuing it again"
                    % rec.equipment_id.name
                )

    def _m45_publish(self, event_type, **extra):
        for rec in self:
            payload = {
                "equipment": rec.equipment_id.code,
                "issue": rec.name,
                "custodian": rec.custodian_id.name,
                "custodian_id": rec.custodian_id.id,
                "due_on": str(rec.due_on) if rec.due_on else None,
                "reference": rec.reference or "",
                "kit": rec.kit_id.code or None,
            }
            payload.update(extra)
            publish(self.env, event_type, "fix.equipment.issue", rec.id, payload)

    @api.model_create_multi
    def create(self, vals_list):
        # A07 ERP audit M45-15 (spec §8.1 Available -> Issued "store keeper +
        # holder"): anyone issued any tool to anyone, themselves included
        if not self.env.su:
            m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), "Issuing equipment")
            mine = self.env.user.employee_ids
            if any(vals.get("custodian_id") in mine.ids for vals in vals_list):
                raise UserError(
                    "Segregation of duties: a store keeper does not issue equipment to "
                    "themselves; another store keeper issues it to you."
                )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.issue") or "EISS/New"
                )
        records = super().create(vals_list)
        for rec in records:
            if rec.state == "issued":
                rec._m45_check_issuable()
                rec.equipment_id._guarded().write({"operational_status": "issued"})
                rec._m45_publish("equipment.issued")
        return records

    def write(self, vals):
        if "equipment_id" not in vals:
            return super().write(vals)
        before = {rec.id: rec.equipment_id for rec in self}
        res = super().write(vals)
        for rec in self.filtered(lambda r: r.state == "issued"):
            old = before.get(rec.id)
            if old and old != rec.equipment_id:
                rec._m45_check_issuable()
                rec.equipment_id._guarded().write({"operational_status": "issued"})
                if old.operational_status == "issued":
                    old._guarded().write({"operational_status": old._m45_released_status()})
        return res

    def action_return(self, condition=None, detail=None):
        """Close the issue with the item's condition (BRU-EAM-10): a
        serviceable item goes back to available, a damaged one out of
        service. `condition` may be passed, or set on the issue first.

        A07 P1 (2026-11-04): a return with no condition stated no longer
        keeps the item out on custody (the holder could not hand it back);
        custody closes and the item waits out of service for a condition
        check by a store keeper (spec §8.1: Issued -> Available only with a
        passed condition check)."""
        conditions = dict(self._fields["return_condition"].selection)
        if condition is not None and condition not in conditions:
            raise UserError("Condition on return must be one of: %s" % ", ".join(conditions))
        # A07 ERP audit M45-15: the holder self-certified "serviceable" and the
        # item went straight to available. Only a store keeper / QM records the
        # condition check, never on their own custody; anyone else's return is
        # a hand-in that waits out of service for it (damage may be declared).
        checker = m45_has_role(self.env, ROLE_CUSTODIAN, ROLE_QM)
        # the return opens a damaged / inspection hold (system hold types)
        Hold = self.env["fix.equipment.oos"]._guarded()
        for rec in self:
            if rec.state != "issued":
                raise UserError("Return an issued item")
            cond = condition or rec.return_condition
            own = not self.env.su and rec.custodian_id.user_id == self.env.user
            vals = {"state": "returned", "returned_on": m45_today(self.env)}
            if (not checker or own) and cond != "damaged":
                vals["handed_in_by_holder"] = True
                if cond == "good":
                    detail = "Declared serviceable by the holder. %s" % (detail or "")
                cond = False
            if cond:
                vals["return_condition"] = cond
            # M45 capture audit (2026-11-16): the Return form carries the damage
            # detail with the condition (FR-EAM-014)
            if (detail or "").strip():
                vals["condition_in"] = detail.strip()
            rec._guarded().write(vals)
            equipment = rec.equipment_id
            detail = (rec.condition_in or "").strip() or "no detail recorded"
            if cond == "damaged":
                # the hold is opened by the returner, so the returner cannot
                # also resolve it (see fix.equipment.oos.action_resolve)
                Hold.create(
                    {
                        "equipment_id": equipment.id,
                        "reason": "Returned damaged (%s): %s" % (rec.name, detail),
                        "hold_type": "damaged",
                    }
                )
            elif not cond and (not self.env.su or vals.get("handed_in_by_holder")):
                Hold.create(
                    {
                        "equipment_id": equipment.id,
                        "reason": "Returned without a condition check (%s): %s"
                        % (rec.name, detail),
                        "hold_type": "inspection",
                    }
                )
            elif equipment.operational_status == "issued":
                # an item put out of service while it was out on issue stays out
                # of service; only the issued status is released (A07 M45-5)
                equipment._guarded().write({"operational_status": equipment._m45_released_status()})
            days = (rec.returned_on - rec.issued_on).days if rec.issued_on else None
            rec._m45_publish("equipment.returned", condition=cond or None, days_held=days)
            rec.kit_id._m45_release_when_home()
        return True

    # ---- A07 P1 (2026-11-04): custody queries and the nightly job -----------
    @api.model
    def m45_open_custody_for_employee(self, employees):
        """The open equipment custody of the given hr.employee records (M21
        exit clearance, BRU-EAM-09 / AUT-EAM-09): read as superuser, so HR
        sees every item an employee still holds, in any branch."""
        employees = employees if isinstance(employees, models.BaseModel) else None
        if not employees:
            return self.sudo().browse()
        return self.sudo().search([("custodian_id", "in", employees.ids), ("state", "=", "issued")])

    @api.model
    def cron_custody_overdue(self):
        """Daily (FR-EAM-015, AUT-EAM-08): escalate open issues past their
        expected return; one event per escalation level, so a re-run sends
        nothing new."""
        today = m45_today(self.env)
        escalated = 0
        for rec in self.sudo().search(self._search_is_overdue("in", [True])):
            days = (today - rec.due_on).days
            level = next((lvl for limit, lvl in CUSTODY_ESCALATION_DAYS if days >= limit), 0)
            if level <= rec.overdue_level:
                continue
            rec._guarded().write({"overdue_level": level})
            rec._m45_publish(
                "equipment.custody_overdue",
                days_overdue=days,
                escalation_level=level,
                # M45-23 (AUT-EAM-08): who is told at this level
                holder_user_id=rec.custodian_id.user_id.id or None,
                branch_manager_id=rec.equipment_id.sudo().branch_id.manager_id.id or None,
            )
            escalated += 1
        return escalated


TRANSFER_STATES = [
    ("draft", "Draft"),
    ("dispatched", "Dispatched (in transit)"),
    ("received", "Received"),
    ("cancelled", "Cancelled"),
    # before the A07 P0 build a transfer was born "posted" and moved nothing;
    # those rows stay as they are, closed
    ("posted", "Posted (legacy, moved nothing)"),
]
TRANSFER_CLOSED = ("received", "cancelled", "posted")


class FixEquipmentTransfer(models.Model):
    """Inter-branch transfer (FR-EAM-016, BRU-EAM-22).

    A07 audit (2026-11-03) M45-8: a transfer was born "posted", changed
    neither the equipment's branch nor its custodian, took a typed from-branch
    and posted for issued or out-of-service items. It now runs draft ->
    dispatched -> received: the sender stays accountable until a different
    user confirms receipt, and only the receipt moves the equipment."""

    _name = "fix.equipment.transfer"
    _description = "Equipment Transfer"
    _inherit = ["fix.guarded.mixin"]
    _order = "transfer_date desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    company_id = _ops_company()
    operating_unit_id = _ops_unit()
    from_branch_id = fields.Many2one(
        "fix.branch", string="From Branch", help="Where the item sits: taken from the register."
    )
    to_branch_id = fields.Many2one("fix.branch", string="To Branch", required=True)
    from_custodian_id = fields.Many2one(
        "hr.employee", string="From Custodian", help="Taken from the register."
    )
    to_custodian_id = fields.Many2one("hr.employee", string="To Custodian")
    transfer_date = fields.Date(required=True, default=lambda self: m45_today(self.env))
    state = fields.Selection(TRANSFER_STATES, required=True, default="draft")
    notes = fields.Char()
    dispatched_by_id = fields.Many2one("res.users", string="Dispatched By", readonly=True)
    dispatched_on = fields.Date(readonly=True)
    received_by_id = fields.Many2one("res.users", string="Received By", readonly=True)
    received_on = fields.Date(readonly=True)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "state",
            "dispatched_by_id",
            "dispatched_on",
            "received_by_id",
            "received_on",
        }
        if self:
            # the origin is the register's, and the item is fixed once raised
            guarded |= {"equipment_id", "from_branch_id", "from_custodian_id"}
        if any(rec.state != "draft" for rec in self):
            # what was dispatched is what the receiver confirms
            guarded |= {"to_branch_id", "to_custodian_id", "transfer_date"}
        if any(rec.state in TRANSFER_CLOSED for rec in self):
            guarded |= {"notes"}
        return guarded

    def _m45_check_movable(self, equipment):
        """Custody truth, for every caller: an item out on issue, out of
        service or retired does not travel."""
        equipment = equipment.sudo()
        if equipment.operational_status != "available":
            label = dict(equipment._fields["operational_status"].selection).get(
                equipment.operational_status
            )
            raise UserError(
                "%s is %s and cannot be transferred: only an available item travels"
                % (equipment.name, label.lower())
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.transfer") or "ETRF/New"
                )
            equipment = self.env["fix.equipment"].sudo().browse(vals.get("equipment_id"))
            if not equipment.exists():
                continue
            self._m45_check_movable(equipment)
            # A07 P1 (2026-11-04): the origin is always the register's. A typed
            # origin was refused (P0); it is now simply replaced by where the
            # item is, so the record is true whatever the caller sent.
            origin = {
                "from_branch_id": equipment.branch_id.id or False,
                "from_custodian_id": equipment.custodian_id.id or False,
            }
            for key, actual in origin.items():
                if not self.env.su or key not in vals:
                    vals[key] = actual
        return super().create(vals_list)

    def _m45_check_store_keeper(self, what):
        # spec §13: transfers are store-keeper work (R18), or the Quality Manager's
        m45_require_role(self.env, (ROLE_CUSTODIAN, ROLE_QM), what)

    def action_dispatch(self):
        """The sender hands the item over; it stays theirs until receipt."""
        self._m45_check_store_keeper("Dispatching a transfer")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Dispatch a draft transfer")
            equipment = rec.equipment_id.sudo()
            rec._m45_check_movable(equipment)
            if self.sudo().search_count(
                [
                    ("equipment_id", "=", equipment.id),
                    ("state", "=", "dispatched"),
                    ("id", "!=", rec.id),
                ]
            ):
                raise UserError("%s is already in transit" % equipment.name)
            if (rec.to_branch_id or False) == (equipment.branch_id or False) and (
                rec.to_custodian_id or False
            ) == (equipment.custodian_id or False):
                raise UserError(
                    "%s is already at %s with that custodian: there is nothing to transfer"
                    % (equipment.name, equipment.branch_id.name or "no branch")
                )
            rec._guarded().write(
                {
                    "state": "dispatched",
                    "dispatched_by_id": self.env.user.id,
                    "dispatched_on": m45_today(self.env),
                    "from_branch_id": equipment.branch_id.id or False,
                    "from_custodian_id": equipment.custodian_id.id or False,
                }
            )
        return True

    def action_receive(self):
        """Receipt confirmed by someone other than the sender (BRU-EAM-22);
        only now do the equipment's branch and custodian move."""
        self._m45_check_store_keeper("Confirming receipt of a transfer")
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Confirm receipt of a dispatched transfer")
            if not self.env.su and rec.dispatched_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you dispatched %s, so its receipt must be "
                    "confirmed by someone at the receiving end." % rec.equipment_id.name
                )
            rec._guarded().write(
                {
                    "state": "received",
                    "received_by_id": self.env.user.id,
                    "received_on": m45_today(self.env),
                }
            )
            equipment = rec.equipment_id
            moved = {"branch_id": rec.to_branch_id.id}
            if rec.to_custodian_id:
                moved["custodian_id"] = rec.to_custodian_id.id
            equipment._guarded().write(moved)
            # A07 P1: M49 needs the transfer trigger (spec §10.2)
            publish(
                self.env,
                "equipment.transferred",
                "fix.equipment.transfer",
                rec.id,
                {
                    "equipment": equipment.sudo().code,
                    "transfer": rec.name,
                    "from_branch": rec.from_branch_id.name or None,
                    "to_branch": rec.to_branch_id.name,
                    "from_custodian_id": rec.from_custodian_id.id or None,
                    "to_custodian_id": rec.to_custodian_id.id or None,
                },
            )
        return True

    def action_cancel(self):
        """Withdraw a transfer that has not been received; nothing moves. Whoever
        raised a draft may withdraw it, since nothing has happened yet; anything
        else is store-keeper work, like the dispatch and the receipt."""
        for rec in self:
            if rec.state not in ("draft", "dispatched"):
                raise UserError("Only a draft or dispatched transfer can be cancelled")
            if rec.state != "draft" or rec.create_uid != self.env.user:
                rec._m45_check_store_keeper("Cancelling a transfer")
            rec._guarded().write({"state": "cancelled"})
        return True


class FixEquipmentVerification(models.Model):
    _name = "fix.equipment.verification"
    _description = "Equipment Physical Verification"
    _inherit = ["fix.guarded.mixin"]
    _order = "verified_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    company_id = _ops_company()
    operating_unit_id = _ops_unit()
    campaign_ref = fields.Char(string="Campaign", required=True)
    verified_on = fields.Date(required=True, default=lambda self: m45_today(self.env))
    location = fields.Char()
    found = fields.Boolean(default=True)
    condition = fields.Char()
    verifier_id = fields.Many2one("hr.employee", string="Verifier")
    state = fields.Selection(
        [("verified", "Verified"), ("missing", "Missing")], required=True, default="verified"
    )

    def _fix_guarded_fields(self) -> set:
        # A07 audit (2026-11-03) M45-6: a "missing" result (the recorded loss)
        # was rewritten to verified/found by any user. The result follows
        # `found`, and a missing result is final for users.
        guarded = super()._fix_guarded_fields() | {"state"}
        if self:
            guarded |= {"equipment_id", "verified_on"}
        if any(rec.state == "missing" for rec in self):
            guarded |= {"found", "campaign_ref", "location", "condition", "verifier_id"}
        return guarded

    def _m45_check_counter(self):
        """A07 ERP audit M45-14 (spec §8.1 Any -> Lost is a branch manager /
        store keeper action, FR-EAM-038 a designated counter): a technician
        recorded "not found" on any item, which blocked it and sent a write-off
        request to M49 and a risk to M60. The blind count run records its
        results as the system; a single verification is a store keeper's."""
        if not self.env.su:
            m45_require_role(
                self.env, (ROLE_CUSTODIAN, ROLE_QM), "Recording a physical verification"
            )

    @api.model_create_multi
    def create(self, vals_list):
        self._m45_check_counter()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.verification") or "EVER/New"
                )
            # the result is derived from what was found, never typed: anything
            # falsy is stored as not found, so it must read as missing too
            vals["state"] = "verified" if vals.get("found", True) else "missing"
        records = super(FixEquipmentVerification, self._guarded()).create(vals_list)
        records = records.with_env(self.env)
        records.filtered(lambda r: r.state == "missing")._m45_mark_missing()
        records.filtered(lambda r: r.state == "verified")._m45_recover()
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            self._m45_check_counter()
        res = super().write(vals)
        if "found" in vals and not vals["found"]:
            # found -> not found after the count: the result follows (M45 D2)
            lost = self.filtered(lambda r: not r.found and r.state == "verified")
            lost._guarded().write({"state": "missing"})
            lost._m45_mark_missing()
        return res

    def _m45_mark_missing(self):
        """A07 P1 (2026-11-04) FR-EAM-039 / AUT-EAM-13: not found at the count
        = the item is missing: unusable, not issuable, not transferable, and
        the loss is published for M49 / M21 / M23."""
        for rec in self:
            equipment = rec.equipment_id.sudo()
            if equipment.operational_status == "retired":
                continue
            custodian = (
                self.env["fix.equipment.issue"]
                .sudo()
                .search([("equipment_id", "=", equipment.id), ("state", "=", "issued")], limit=1)
                .custodian_id
            ) or equipment.custodian_id
            equipment._guarded().write({"missing_verification_id": rec.id})
            equipment._m45_sync_status()
            publish(
                self.env,
                "equipment.lost",
                "fix.equipment.verification",
                rec.id,
                {
                    "equipment": equipment.code,
                    "verification": rec.name,
                    "campaign": rec.campaign_ref,
                    "custodian": custodian.name or None,
                    "custodian_id": custodian.id or None,
                    "value": equipment.acquisition_cost or 0.0,
                },
            )

    def _m45_recover(self):
        """A count that finds a missing item recovers it (spec §8.1 Lost ->
        Available, branch manager / store keeper)."""
        for rec in self:
            equipment = rec.equipment_id.sudo()
            if not equipment.missing_verification_id:
                continue
            m45_require_role(
                self.env, (ROLE_CUSTODIAN, ROLE_QM), "Recording a missing item as found"
            )
            # the Found box is ticked by default: leaving a form alone must not
            # clear a recorded loss
            if not self.env.su and not (rec.location or "").strip():
                raise UserError(
                    "%s is recorded as missing. To record it as found, state where it was "
                    "found (Location). If it is still missing, untick Found." % equipment.name
                )
            lost = equipment.missing_verification_id
            equipment._guarded().write({"missing_verification_id": False})
            equipment._m45_sync_status()
            publish(
                self.env,
                "equipment.recovered",
                "fix.equipment.verification",
                rec.id,
                {"equipment": equipment.code, "verification": rec.name, "missing_since": lost.name},
            )


OOS_HOLD_TYPES = [
    ("fault", "Fault raised"),
    ("calibration", "Calibration (failed, overdue or rejected)"),
    ("damaged", "Returned damaged"),
    ("inspection", "Returned without a condition check"),
]


class FixEquipmentOutOfService(models.Model):
    _name = "fix.equipment.oos"
    _description = "Out-of-Service Record"
    _inherit = ["fix.guarded.mixin"]
    _order = "started_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    company_id = _ops_company()
    operating_unit_id = _ops_unit()
    reason = fields.Char(required=True)
    # A07 P1 (2026-11-04): why the item is held decides how it returns: a
    # condition check (inspection, store keeper) or an accepted re-calibration
    # (everything else, Quality Manager).
    hold_type = fields.Selection(OOS_HOLD_TYPES, required=True, default="fault")
    calibration_id = fields.Many2one(
        "fix.calibration", string="Triggering Calibration", readonly=True, ondelete="restrict"
    )
    started_on = fields.Date(required=True, default=lambda self: m45_today(self.env))
    resolved_on = fields.Date(readonly=True)
    resolved_by_id = fields.Many2one("res.users", string="Resolved By", readonly=True)
    resolution_calibration_id = fields.Many2one(
        "fix.calibration",
        string="Re-calibration",
        readonly=True,
        help="The passing calibration, recorded after the item went out of service, that "
        "returned it to service.",
    )
    state = fields.Selection(
        [("open", "Open"), ("resolved", "Resolved")], required=True, default="open"
    )

    def _fix_guarded_fields(self) -> set:
        # A07 audit (2026-11-03) M45-7: the OOS state was forged to "resolved"
        # through P03, and a back-dated start would let an older pass count as
        # the re-calibration.
        guarded = super()._fix_guarded_fields() | {
            "state",
            "started_on",
            "resolved_on",
            "resolved_by_id",
            "resolution_calibration_id",
            "calibration_id",
        }
        if self:
            guarded |= {"equipment_id", "hold_type"}
        if any(rec.state == "resolved" for rec in self):
            guarded |= {"reason"}
        return guarded

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.oos") or "EOOS/New"
                )
            if not self._fix_guard_open() and vals.get("hold_type") not in (None, "fault"):
                # the other hold types are opened by the system (calibration,
                # return); a user raises a fault
                self._fix_guard_refuse(["hold_type"])
        records = super().create(vals_list)
        for rec in records:
            equipment = rec.equipment_id.sudo()
            if equipment.operational_status == "retired":
                raise UserError("%s is retired: it is out of use for good" % rec.equipment_id.name)
            rec.equipment_id._m45_sync_status()
            publish(
                self.env,
                "equipment.out_of_service",
                "fix.equipment.oos",
                rec.id,
                {
                    "equipment": equipment.code,
                    "hold": rec.name,
                    "hold_type": rec.hold_type,
                    "reason": rec.reason,
                    "effective_from": str(rec.started_on),
                    "branch": equipment.branch_id.name or None,
                },
            )
        return records

    def _m45_recalibration(self):
        """The passing calibration that returns the item to service: the
        latest one, current, dated on or after the start and recorded after
        the hold was opened. None when there is no such calibration."""
        self.ensure_one()
        equipment = self.equipment_id.sudo()
        latest = equipment._m45_latest_calibration()
        # the certificate's own state: an item whose class was taken out of
        # calibration control reads "not required", which is not a re-calibration
        state = equipment._m45_certificate_state(latest, m45_today(self.env))
        if (
            latest
            and state in ("current", "pending")
            and latest.calibrated_on >= self.started_on
            and latest.create_date >= self.create_date
        ):
            return latest
        return None

    def action_resolve(self):
        """Back to service only with a re-calibration, by someone other than
        the person who opened the hold (spec §8.1, SOD-07).

        A07 P1/P2 (2026-11-04): returning an item to service is the Quality
        Manager's decision (a store keeper's for a condition check), and the
        re-calibration is accepted by a second person: the resolver may not be
        whoever recorded it, unless another Quality Manager has already
        accepted it at its usage decision. Resolving records that acceptance."""
        for rec in self:
            if rec.state != "open":
                raise UserError("Resolve an open out-of-service record")
            equipment = rec.equipment_id
            if equipment.sudo().operational_status == "retired":
                raise UserError("%s is retired and cannot return to service" % equipment.name)
            inspection = rec.hold_type == "inspection"
            # M45 capture audit (2026-11-16), spec §8.1: an item is re-calibrated
            # before it returns "where measurement-critical"; a tool outside
            # calibration control returns on its repair / condition check.
            # A07 ERP audit M45-04: switching the class's calibration control
            # off no longer lets a store keeper clear an open calibration or
            # recall hold without a re-calibration (BRU-EAM-01: no override)
            needs_recal = not inspection and (
                equipment.sudo().measurement_critical or rec.hold_type in ("calibration", "recall")
            )
            recal = rec._m45_recalibration() if needs_recal else None
            if not self.env.su:
                if inspection or not needs_recal:
                    m45_require_role(
                        self.env,
                        (ROLE_CUSTODIAN, ROLE_QM),
                        "The condition check of a returned item",
                    )
                else:
                    m45_require_role(self.env, (ROLE_QM,), "Returning an item to service")
                if rec.create_uid == self.env.user:
                    raise UserError(
                        "Segregation of duties: you opened %s, so another person must "
                        "accept the re-calibration and return the item to service." % rec.name
                    )
                if inspection:
                    problem = equipment.sudo()._m45_calibration_problem()
                    if problem:
                        raise UserError(
                            "%s passed its condition check but stays out of service: %s"
                            % (equipment.name, problem)
                        )
                elif needs_recal and not recal:
                    raise UserError(
                        "%s cannot return to service without a passing calibration "
                        "recorded after it went out of service (on or after %s)."
                        % (equipment.name, rec.started_on)
                    )
                elif (
                    recal
                    and recal.decision_state != "accepted"
                    and recal.create_uid == self.env.user
                ):
                    raise UserError(
                        "Segregation of duties: you recorded the re-calibration of %s, so "
                        "another Quality Manager accepts it and returns the item to service."
                        % equipment.name
                    )
            if recal and recal.decision_state == "pending":
                recal.sudo()._guarded().write(
                    {
                        "decision_state": "accepted",
                        "decided_by_id": self.env.user.id,
                        "decided_on": fields.Datetime.now(),
                    }
                )
            rec._guarded().write(
                {
                    "state": "resolved",
                    "resolved_on": m45_today(self.env),
                    "resolved_by_id": self.env.user.id,
                    "resolution_calibration_id": recal.id if recal else False,
                }
            )
            equipment._m45_sync_status()
            publish(
                self.env,
                "equipment.returned_to_service",
                "fix.equipment.oos",
                rec.id,
                {
                    "equipment": equipment.sudo().code,
                    "hold": rec.name,
                    "calibration_id": recal.id if recal else None,
                    "effective_from": str(rec.resolved_on),
                    "status": equipment.sudo().operational_status,
                },
            )
        return True


class FixEquipmentPm(models.Model):
    _name = "fix.equipment.pm"
    _description = "Equipment PM / Corrective Job"
    _inherit = ["fix.guarded.mixin"]
    _order = "scheduled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    company_id = _ops_company()
    operating_unit_id = _ops_unit()
    pm_type = fields.Selection(
        [("preventive", "Preventive"), ("corrective", "Corrective")],
        required=True,
        default="preventive",
    )
    scheduled_on = fields.Date(required=True, default=lambda self: m45_today(self.env))
    done_on = fields.Date(readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cost = fields.Monetary(currency_field="currency_id")
    technician_id = fields.Many2one("hr.employee", string="Technician")
    state = fields.Selection([("open", "Open"), ("done", "Done")], required=True, default="open")
    notes = fields.Char()

    def _fix_guarded_fields(self) -> set:
        # A07 audit (2026-11-03) M45-11: a PM job was forged to "done" by write;
        # a done job is the maintenance record and is frozen.
        guarded = super()._fix_guarded_fields() | {"state", "done_on"}
        if any(rec.state == "done" for rec in self):
            guarded |= {
                "equipment_id",
                "pm_type",
                "scheduled_on",
                "currency_id",
                "cost",
                "technician_id",
                "notes",
            }
        return guarded

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.equipment.pm") or "EPM/New"
        return super().create(vals_list)

    def action_done(self):
        """A07 audit (2026-11-03) M45-11: completion needed no evidence. A job
        is done with what was found and done (notes) and who did it."""
        for rec in self:
            if rec.state != "open":
                raise UserError("Complete an open job")
            if not self.env.su:
                missing = [
                    label
                    for ok, label in (
                        ((rec.notes or "").strip(), "completion notes"),
                        (rec.technician_id, "the technician"),
                    )
                    if not ok
                ]
                if missing:
                    raise UserError(
                        "Record %s on %s before marking it done."
                        % (" and ".join(missing), rec.name)
                    )
            rec._guarded().write({"state": "done", "done_on": m45_today(self.env)})
        return True


# What the system stamps on a use: never typed.
USAGE_SYSTEM_FIELDS = {
    "calibration_id",
    "fitness_state_at_use",
    "used_by_id",
    "source_model",
    "source_res_id",
}


class FixEquipmentUsage(models.Model):
    _name = "fix.equipment.usage"
    _description = "Equipment Usage per Job"
    _inherit = ["fix.guarded.mixin"]
    _order = "used_on desc, id desc"

    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    company_id = _ops_company()
    operating_unit_id = _ops_unit()
    job_ref = fields.Char(string="Job / Work Order", required=True)
    service_order_ref = fields.Char(string="Service Order")
    used_on = fields.Date(required=True, default=lambda self: m45_today(self.env))
    uses = fields.Integer(string="Uses", default=1)
    qc_result = fields.Selection(
        [("pass", "Pass"), ("fail", "Fail"), ("na", "Not a QC use")],
        required=True,
        default="na",
    )
    notes = fields.Char()
    # A07 P1 (2026-11-04) spec §10.1: which calibration certified the
    # instrument at the moment of use, and who used it. M31 QC writes its own
    # rows (source = the workshop job), so the impact assessment sees them.
    calibration_id = fields.Many2one(
        "fix.calibration", string="Calibration at Use", readonly=True, ondelete="restrict"
    )
    fitness_state_at_use = fields.Char(string="Calibration Status at Use", readonly=True)
    used_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)
    source_model = fields.Char(readonly=True)
    source_res_id = fields.Integer(readonly=True)

    _uses_positive = models.Constraint("CHECK (uses > 0)", "Usage count must be positive")

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | USAGE_SYSTEM_FIELDS
        if self:
            # the date decides which certificate covered the use, and the impact
            # assessment reads it and the QC result: fixed once recorded
            guarded |= {"used_on", "qc_result"}
        if any(rec.source_model for rec in self):
            # a use written by another module's record is that record's evidence
            guarded |= {
                "equipment_id",
                "job_ref",
                "service_order_ref",
                "used_on",
                "uses",
                "qc_result",
            }
        return guarded

    # A07 audit (2026-11-03) M45-4 (BRU-EAM-02): usage was recorded on overdue
    # and out-of-service instruments; the fitness gate was only a button. A use
    # is the instrument being put to work, so the gate runs on every user path.
    # Superuser code (seeds, sudo service calls) stays trusted. A use dated today
    # meets today's status; a late entry is judged at its own date, so an honest
    # entry written after a later fail is accepted (and joins the impact below).
    def _m45_check_fit_for_use(self):
        if self.env.su:
            return
        today = m45_today(self.env)
        for rec in self:
            if rec.used_on > today:
                raise UserError(
                    "A use cannot be dated in the future (%s): record it once the instrument "
                    "has been used." % rec.used_on
                )
            if rec.used_on == today:
                rec.equipment_id.action_assert_usable()
                continue
            problem = rec.equipment_id._m45_fitness_problem_on(rec.used_on)
            if problem:
                raise UserError(problem)

    def _m45_stamp(self):
        for rec in self:
            equipment = rec.equipment_id.sudo()
            calibration = equipment._m45_calibration_at(rec.used_on)
            rec.sudo()._guarded().write(
                {
                    "calibration_id": calibration.id or False,
                    "fitness_state_at_use": equipment._m45_certificate_state(
                        calibration, rec.used_on
                    ),
                    "used_by_id": self.env.uid,
                }
            )

    def _m45_join_impact_assessments(self):
        """A use recorded after the assessment was raised, dated inside its suspect
        window, is as suspect as the ones it already lists. A closed assessment
        lists it too and says so, for the Quality Manager who closed it."""
        Impact = self.env["fix.calibration.impact"].sudo()
        for rec in self:
            for impact in Impact.search(
                [
                    ("equipment_id", "=", rec.equipment_id.id),
                    ("period_to", ">=", rec.used_on),
                    "|",
                    ("period_from", "=", False),
                    ("period_from", "<=", rec.used_on),
                ]
            ):
                if rec in impact.usage_ids:
                    continue
                impact._guarded().write({"usage_ids": [(4, rec.id)]})
                if impact.state == "closed":
                    impact.message_post(
                        body="A use dated %s (%s) was recorded after this assessment was "
                        "closed. Review it against the disposition." % (rec.used_on, rec.job_ref)
                    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._m45_check_fit_for_use()
        records._m45_stamp()
        records._m45_join_impact_assessments()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "equipment_id" in vals:
            self._m45_check_fit_for_use()
            self._m45_stamp()
            self._m45_join_impact_assessments()
        return res

    @api.model
    def m45_record_qc_use(self, equipment, job_ref, qc_result, source=None, service_order_ref=None):
        """The service another module calls after its own fitness check (M31
        QC): write the usage row as superuser, stamped with the calibration at
        use. `source` is the record the measurement belongs to."""
        equipment = equipment.sudo()
        if not equipment:
            return self.browse()
        vals = {
            "equipment_id": equipment.id,
            "job_ref": job_ref,
            "qc_result": qc_result,
            "service_order_ref": service_order_ref or False,
        }
        if source is not None:
            vals.update({"source_model": source._name, "source_res_id": source.id})
        return self.sudo().create([vals])
