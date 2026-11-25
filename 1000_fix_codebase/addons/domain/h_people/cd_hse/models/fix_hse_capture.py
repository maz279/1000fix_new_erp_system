# fix_hse_capture — M59 sub-module capture audit (2026-11-18).
#
# Six things the spec owns had no record, so their sub-module pages could not
# capture them:
#   * page 2 "Procedures & Permits" held only the JSA: no safe work procedure
#     (FR-HSE-006) and no permit to work (FR-HSE-007);
#   * page 3 had no witness statement (FR-HSE-012, T-09 verbatim account);
#   * page 6 had no right-to-stop-work refusal (FR-HSE-026, BRU-HSE-10 H) and
#     no customer-premises hazard (FR-HSE-025, AUT-HSE-17);
#   * page 7 had no site emergency plan (FR-HSE-035).
# Every decision here is taken by someone other than the person who raised
# it, every stamp moves only through its action (fix.guarded.mixin), and a
# record that is evidence is never deleted.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_hse import _group_users, _int_param, _is_hse, _require_hse
from .fix_hse_investigation import guard_first

HSE_GROUP = "cd_hse.group_hse_officer"


def _todo(record, users, summary, note=""):
    """One to-do per active internal user (record needs mail.activity.mixin)."""
    for user in users.filtered(lambda u: u.active and not u.share):
        record.sudo().activity_schedule(
            "mail.mail_activity_data_todo",
            date_deadline=fields.Date.context_today(record),
            summary=summary,
            note=note,
            user_id=user.id,
        )


def _locked_change(records, vals, names, message):
    """Refuse a CHANGING write of `names` on a saved record (the P03 form
    re-posts unchanged values on save, which is allowed)."""
    touched = set(names) & set(vals)
    if not touched or records._fix_guard_open():
        return
    for rec in records:
        if rec.id and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in touched):
            raise UserError(message % rec.display_name)


# ---------------------------------------------------------------------------
# Page 2 - safe work procedure (FR-HSE-006)
# ---------------------------------------------------------------------------
PROCEDURE_CATEGORIES = [
    ("general", "General Workshop"),
    ("electrical", "Electrical Safety & Isolation"),
    ("battery", "Lithium Battery Handling"),
    ("chemical", "Chemical / Solvent"),
    ("height", "Work at Height"),
    ("road", "Road / Driving"),
    ("manual_handling", "Manual Handling"),
    ("fire", "Fire & Emergency"),
    ("other", "Other"),
]


class FixHseProcedure(models.Model):
    """A published safe work procedure, versioned. Prepared and submitted by
    an HSE Officer, approved by another, frozen once approved; a change is a
    new version, and approving it supersedes the one in force."""

    _name = "fix.hse.procedure"
    _description = "Safe Work Procedure"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "code, version desc, id desc"

    _CONTENT = (
        "code",
        "name",
        "category",
        "job_type",
        "scope",
        "content",
        "hazard_ids",
        "document",
        "document_name",
        "effective_from",
        "company_id",
    )

    code = fields.Char(required=True, tracking=True)
    name = fields.Char(string="Title", required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    category = fields.Selection(PROCEDURE_CATEGORIES, required=True, default="general")
    job_type = fields.Char(
        string="Task Type", help="The field or workshop task type it applies to (as on the JSA)."
    )
    scope = fields.Text()
    content = fields.Text(string="Procedure Steps")
    hazard_ids = fields.Many2many(
        "fix.hse.hazard",
        "fix_hse_procedure_hazard_rel",
        "procedure_id",
        "hazard_id",
        string="Hazards Controlled",
    )
    document = fields.Binary(string="Procedure Document", attachment=True)
    document_name = fields.Char()
    version = fields.Integer(default=1, readonly=True, copy=False)
    previous_id = fields.Many2one(
        "fix.hse.procedure", string="Supersedes", readonly=True, copy=False
    )
    effective_from = fields.Date()
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", readonly=True, default=lambda self: self.env.user
    )
    submitted_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    submitted_on = fields.Datetime(readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_on = fields.Date(readonly=True, copy=False)
    review_due_on = fields.Date(string="Review Due", readonly=True, copy=False)
    rejection_reason = fields.Char(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved (in force)"),
            ("superseded", "Superseded"),
            ("retired", "Retired"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )

    _code_version = models.Constraint(
        "UNIQUE (company_id, code, version)", "A procedure code has one row per version"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "version",
            "previous_id",
            "prepared_by_id",
            "submitted_by_id",
            "submitted_on",
            "approved_by_id",
            "approved_on",
            "review_due_on",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" for r in self):
            locked |= set(self._CONTENT)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            _require_hse(self.env, "prepare a safe work procedure")
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            _require_hse(self.env, "change a safe work procedure")
            for rec in self:
                if rec.id and rec.state != "draft":
                    _locked_change(
                        rec,
                        vals,
                        self._CONTENT,
                        "%s is no longer a draft; a change is a new version.",
                    )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and self.filtered(lambda r: r.state != "draft"):
            raise UserError("A submitted or published procedure is retired, never deleted.")
        return super().unlink()

    def action_submit(self):
        _require_hse(self.env, "submit a safe work procedure")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Submit a draft procedure.")
            if not ((rec.content or "").strip() and (rec.scope or "").strip()):
                raise UserError("Procedure %s needs its scope and its steps." % rec.code)
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by_id": self.env.uid,
                    "submitted_on": fields.Datetime.now(),
                    "rejection_reason": False,
                }
            )
        return True

    def _fix_assert_other_officer(self, what):
        for rec in self:
            if not self.env.su and self.env.user in (rec.prepared_by_id | rec.submitted_by_id):
                raise UserError(
                    "You prepared or submitted %s; another HSE Officer %s it." % (rec.code, what)
                )

    def action_approve(self):
        _require_hse(self.env, "approve a safe work procedure")
        self._fix_assert_other_officer("approves")
        days = _int_param(self.env, "cd_hse.procedure_review_days", 365)
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Approve a submitted procedure.")
            live = self.sudo().search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("code", "=", rec.code),
                    ("state", "=", "approved"),
                    ("id", "!=", rec.id),
                ]
            )
            live._guarded().write({"state": "superseded"})
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_on": today,
                    "review_due_on": today + timedelta(days=days) if days else False,
                    "effective_from": rec.effective_from or today,
                }
            )
        return True

    def action_reject(self, reason=None):
        _require_hse(self.env, "return a safe work procedure")
        if not (reason or "").strip():
            raise UserError("Say what must change before it is approved.")
        self._fix_assert_other_officer("returns")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Return a submitted procedure.")
            rec._guarded().write({"state": "draft", "rejection_reason": reason.strip()})
        return True

    def action_revise(self):
        _require_hse(self.env, "revise a safe work procedure")
        new = self.browse()
        for rec in self:
            if rec.state != "approved":
                raise UserError("Revise the procedure in force.")
            new |= rec._guarded().copy(
                {
                    "version": rec.version + 1,
                    "previous_id": rec.id,
                    "state": "draft",
                    "prepared_by_id": self.env.uid,
                    "effective_from": False,
                }
            )
        return {"ids": new.ids}

    def action_retire(self):
        _require_hse(self.env, "retire a safe work procedure")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Retire the procedure in force.")
            rec._guarded().write({"state": "retired"})
        return True


# ---------------------------------------------------------------------------
# Page 2 - permit to work (FR-HSE-007)
# ---------------------------------------------------------------------------
PERMIT_TYPES = [
    ("hot_work", "Hot Work (soldering, brazing, welding)"),
    ("electrical", "Electrical Isolation / Live Work"),
    ("height", "Work at Height"),
    ("confined", "Confined Space"),
    ("battery", "Damaged Battery Handling"),
    ("refrigerant", "Refrigerant / Pressurised Gas"),
    ("other", "Other High-Risk Activity"),
]


class FixHsePermit(models.Model):
    """A permit to work for a defined high-risk activity. Requested by the
    person doing the work (or HSE for them), authorised by an HSE Officer who
    neither requested it nor does the work, valid for a bounded window, and
    closed with the area left safe. An authorised permit past its window
    expires by itself and HSE is told."""

    _name = "fix.hse.permit"
    _description = "Permit to Work"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "valid_from desc, id desc"

    _TERMS = (
        "permit_type",
        "activity",
        "location",
        "branch_id",
        "operating_unit_id",
        "field_order_id",
        "performer_id",
        "procedure_id",
        "jsa_id",
        "precautions",
        "isolation_points",
        "valid_from",
        "valid_to",
        "company_id",
    )

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    permit_type = fields.Selection(PERMIT_TYPES, required=True, default="hot_work")
    activity = fields.Text(required=True)
    location = fields.Char(required=True)
    field_order_id = fields.Many2one("fix.field.order", string="Field Order", index=True)
    performer_id = fields.Many2one(
        "hr.employee",
        string="Work Done By",
        required=True,
        index=True,
        default=lambda self: self.env.user.employee_id,
    )
    procedure_id = fields.Many2one("fix.hse.procedure", string="Safe Work Procedure")
    jsa_id = fields.Many2one("fix.hse.jsa", string="Job Safety Analysis")
    precautions = fields.Text(string="Precautions in Place")
    isolation_points = fields.Text(string="Isolation Points (electrical)")
    valid_from = fields.Datetime(required=True, default=fields.Datetime.now)
    valid_to = fields.Datetime(required=True)
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", readonly=True, default=lambda self: self.env.user
    )
    requested_on = fields.Datetime(readonly=True, copy=False)
    authorised_by_id = fields.Many2one(
        "res.users", string="Authorised By", readonly=True, copy=False
    )
    authorised_on = fields.Datetime(readonly=True, copy=False)
    authorisation_note = fields.Text(readonly=True, copy=False)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    closed_on = fields.Datetime(readonly=True, copy=False)
    closure_note = fields.Text(readonly=True, copy=False)
    cancel_reason = fields.Char(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Requested"),
            ("authorised", "Authorised"),
            ("closed", "Closed"),
            ("expired", "Expired (not closed)"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "requested_on",
            "authorised_by_id",
            "authorised_on",
            "authorisation_note",
            "closed_by_id",
            "closed_on",
            "closure_note",
            "cancel_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" for r in self):
            locked |= set(self._TERMS)
        return locked

    @api.constrains("valid_from", "valid_to")
    def _check_window(self):
        hours = _int_param(self.env, "cd_hse.permit_max_hours", 12)
        for rec in self:
            if not rec.valid_to or rec.valid_to <= rec.valid_from:
                raise ValidationError("A permit is valid until a time after it starts.")
            if hours and rec.valid_to - rec.valid_from > timedelta(hours=hours):
                raise ValidationError(
                    "A permit is valid for at most %d hours; raise a new one for the next "
                    "shift." % hours
                )

    @api.constrains("procedure_id", "jsa_id")
    def _check_references(self):
        for rec in self:
            if rec.procedure_id and rec.procedure_id.sudo().state != "approved":
                raise ValidationError("Name a safe work procedure that is in force.")
            if rec.jsa_id and rec.jsa_id.sudo().state != "approved":
                raise ValidationError("Name an approved JSA.")

    @api.model_create_multi
    def create(self, vals_list):
        own = self.env.user.employee_id
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.hse.permit") or "PTW/New"
            if (
                not self._fix_guard_open()
                and not _is_hse(self.env)
                and vals.get("performer_id", own.id) != own.id
            ):
                raise AccessError("You request a permit for work you do yourself.")
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            for rec in self:
                if rec.id and rec.state != "draft":
                    _locked_change(
                        rec,
                        vals,
                        self._TERMS,
                        "%s has been requested; its terms are fixed (cancel and raise a new one).",
                    )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and self.filtered(lambda r: r.state != "draft"):
            raise UserError("A requested permit is cancelled, never deleted.")
        return super().unlink()

    def _fix_is_party(self, rec):
        return self.env.user in (rec.requested_by_id | rec.performer_id.user_id)

    def action_request(self):
        for rec in self:
            if not (_is_hse(self.env) or self._fix_is_party(rec)):
                raise AccessError("The person doing the work, or HSE, requests the permit.")
            if rec.state != "draft":
                raise UserError("Request a draft permit.")
            if not (rec.precautions or "").strip():
                raise UserError("State the precautions in place for %s." % rec.name)
            if rec.permit_type == "electrical" and not (rec.isolation_points or "").strip():
                raise UserError("An electrical permit names its isolation points.")
            if rec.valid_to <= fields.Datetime.now():
                raise UserError("The window of %s has already ended." % rec.name)
            rec._guarded().write({"state": "requested", "requested_on": fields.Datetime.now()})
            _todo(
                rec,
                _group_users(self.env, HSE_GROUP, rec.company_id)
                - rec.requested_by_id
                - rec.performer_id.user_id,
                "Permit to authorise: %s" % rec.name,
                "%s at %s." % (dict(PERMIT_TYPES)[rec.permit_type], rec.location),
            )
        return True

    def action_authorise(self, note=None):
        _require_hse(self.env, "authorise a permit to work")
        for rec in self:
            if rec.state != "requested":
                raise UserError("Authorise a requested permit.")
            if not self.env.su and self._fix_is_party(rec):
                raise UserError(
                    "You requested %s or do the work; another HSE Officer authorises it." % rec.name
                )
            if rec.valid_to <= fields.Datetime.now():
                raise UserError("The window of %s has ended; it cannot be authorised." % rec.name)
            rec._guarded().write(
                {
                    "state": "authorised",
                    "authorised_by_id": self.env.uid,
                    "authorised_on": fields.Datetime.now(),
                    "authorisation_note": (note or "").strip() or False,
                }
            )
        return True

    def action_close(self, note=None):
        if not (note or "").strip():
            raise UserError("Say how the work area was left (isolations removed, area safe).")
        for rec in self:
            if not (_is_hse(self.env) or self._fix_is_party(rec)):
                raise AccessError("The person doing the work, or HSE, closes the permit.")
            if rec.state not in ("authorised", "expired"):
                raise UserError("Close an authorised permit.")
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_by_id": self.env.uid,
                    "closed_on": fields.Datetime.now(),
                    "closure_note": note.strip(),
                }
            )
        return True

    def action_cancel(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say why the permit is cancelled.")
        for rec in self:
            if not (_is_hse(self.env) or self._fix_is_party(rec)):
                raise AccessError("The requester, the person doing the work or HSE cancels it.")
            if rec.state in ("closed", "cancelled", "expired"):
                raise UserError("%s is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason.strip()})
        return True

    @api.model
    def cron_expire_permits(self):
        """An authorised permit past its window expires; HSE is told to
        confirm the area is safe and close it. Idempotent; superuser."""
        due = self.sudo().search(
            [("state", "=", "authorised"), ("valid_to", "<", fields.Datetime.now())]
        )
        for rec in due:
            rec._guarded().write({"state": "expired"})
            _todo(
                rec,
                _group_users(self.env, HSE_GROUP, rec.company_id) | rec.performer_id.user_id,
                "Permit expired without closure: %s" % rec.name,
                "Confirm the area at %s is safe and close the permit." % rec.location,
            )
        return len(due)


# ---------------------------------------------------------------------------
# Page 3 - witness statement (FR-HSE-012, T-09)
# ---------------------------------------------------------------------------
class FixHseWitnessStatement(models.Model):
    """A witness's account, taken by HSE and kept verbatim: once recorded it
    is never edited or deleted; a correction is a further statement."""

    _name = "fix.hse.witness.statement"
    _description = "Incident Witness Statement"
    _inherit = ["fix.hse.incident.child", "fix.guarded.mixin"]
    _order = "incident_id, taken_on, id"

    _ACCOUNT = (
        "incident_id",
        "witness_employee_id",
        "witness_name",
        "witness_contact",
        "statement",
        "statement_file",
        "statement_filename",
    )

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    witness_employee_id = fields.Many2one("hr.employee", string="Witness (employee)")
    witness_name = fields.Char(string="Witness (not an employee)")
    witness_contact = fields.Char()
    statement = fields.Text(required=True, string="Statement (verbatim)")
    statement_file = fields.Binary(string="Signed Statement", attachment=True)
    statement_filename = fields.Char()
    taken_by_id = fields.Many2one(
        "res.users", string="Taken By", readonly=True, default=lambda self: self.env.user
    )
    taken_on = fields.Datetime(readonly=True, default=fields.Datetime.now)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"taken_by_id", "taken_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= set(self._ACCOUNT)
        return locked

    @api.constrains("witness_employee_id", "witness_name")
    def _check_witness(self):
        for rec in self:
            if not (rec.witness_employee_id or (rec.witness_name or "").strip()):
                raise ValidationError("Name the witness.")

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            _require_hse(self.env, "take a witness statement")
            self._fix_check_open([v.get("incident_id") for v in vals_list])
            for vals in vals_list:
                touched = self._fix_guarded_fields() & set(vals)
                if touched:
                    self._fix_guard_refuse(touched)
        for vals in vals_list:
            # @api.constrains runs only for fields present in the values, so a
            # statement naming no witness at all would pass it: check here too
            if not (vals.get("witness_employee_id") or (vals.get("witness_name") or "").strip()):
                raise ValidationError("Name the witness.")
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.hse.witness.statement") or "WIT/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        _locked_change(
            self,
            vals,
            self._ACCOUNT,
            "%s is a witness's account as given; add a further statement instead.",
        )
        if not self._fix_guard_open():
            _require_hse(self.env, "change a witness statement")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A witness statement is evidence; it is never deleted.")
        return super().unlink()


# ---------------------------------------------------------------------------
# Page 6 - right to stop work (FR-HSE-026, BRU-HSE-10)
# ---------------------------------------------------------------------------
REFUSAL_GROUNDS = [
    ("unsafe_premises", "Unsafe customer premises"),
    ("no_ppe", "Required PPE not available"),
    ("equipment", "Unsafe tool or equipment"),
    ("electrical", "Live or unsafe electrical supply"),
    ("height", "Unsafe work at height"),
    ("battery_chemical", "Battery / chemical hazard"),
    ("threat", "Threat or violence"),
    ("weather", "Weather / extreme heat"),
    ("fatigue", "Unwell or fatigued"),
    ("other", "Other"),
]
REFUSAL_OUTCOMES = [
    ("upheld", "Upheld: the work was unsafe and stays stopped until made safe"),
    ("made_safe", "Made safe: the hazard was removed and the work resumed"),
    ("not_substantiated", "Not substantiated (no penalty)"),
]


class FixHseWorkRefusal(models.Model):
    """A technician declines work they judge unsafe. The refusal is recorded
    as given and never edited or deleted; HSE and the line manager are told;
    an HSE Officer who neither refused nor recorded it reviews it. Whatever
    the outcome, it carries no penalty (BRU-HSE-10): the record has no field
    for one, and the register is read for patterns."""

    _name = "fix.hse.work.refusal"
    _description = "Work Refusal (Right to Stop Work)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "recorded_at desc, id desc"

    _ACCOUNT = (
        "employee_id",
        "field_order_id",
        "job_description",
        "location",
        "ground",
        "detail",
        "company_id",
    )

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Refused By",
        required=True,
        index=True,
        default=lambda self: self.env.user.employee_id,
    )
    field_order_id = fields.Many2one("fix.field.order", string="Field Order", index=True)
    job_description = fields.Char(string="Work Declined")
    location = fields.Char()
    ground = fields.Selection(REFUSAL_GROUNDS, required=True, default="unsafe_premises")
    detail = fields.Text(string="What Made It Unsafe", required=True)
    recorded_by_id = fields.Many2one(
        "res.users", string="Recorded By", readonly=True, default=lambda self: self.env.user
    )
    recorded_at = fields.Datetime(readonly=True, default=fields.Datetime.now)
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True, copy=False)
    reviewed_on = fields.Datetime(readonly=True, copy=False)
    outcome = fields.Selection(REFUSAL_OUTCOMES, readonly=True, copy=False)
    review_note = fields.Text(readonly=True, copy=False)
    state = fields.Selection(
        [("recorded", "Recorded"), ("reviewed", "Reviewed")],
        required=True,
        default="recorded",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "recorded_by_id",
            "recorded_at",
            "reviewed_by_id",
            "reviewed_on",
            "outcome",
            "review_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= set(self._ACCOUNT)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        own = self.env.user.employee_id
        if not self._fix_guard_open():
            for vals in vals_list:
                if not _is_hse(self.env) and vals.get("employee_id", own.id) != own.id:
                    raise AccessError("You record your own refusal; HSE records one for you.")
                touched = self._fix_guarded_fields() & set(vals)
                if touched:
                    self._fix_guard_refuse(touched)
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.hse.work.refusal") or "WRF/New"
                )
        recs = super().create(vals_list)
        for rec in recs:
            manager = rec.employee_id.sudo().parent_id.user_id
            _todo(
                rec,
                (_group_users(self.env, HSE_GROUP, rec.company_id) | manager)
                - rec.employee_id.user_id,
                "Work refused on safety grounds: %s" % rec.employee_id.name,
                "Review the refusal with %s. A refusal carries no penalty (BRU-HSE-10)."
                % rec.employee_id.name,
            )
        return recs

    def write(self, vals):
        guard_first(self, vals)
        _locked_change(
            self, vals, self._ACCOUNT, "%s is recorded as given; it is reviewed, never rewritten."
        )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A work refusal is a record; it is never deleted.")
        return super().unlink()

    def _fix_review(self, outcome, note):
        _require_hse(self.env, "review a work refusal")
        if not (note or "").strip():
            raise UserError("Record what the review found and what was done.")
        for rec in self:
            if rec.state != "recorded":
                raise UserError("%s has been reviewed." % rec.name)
            if not self.env.su and self.env.user in (rec.employee_id.user_id | rec.recorded_by_id):
                raise UserError(
                    "You refused or recorded %s; another HSE Officer reviews it." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "reviewed",
                    "outcome": outcome,
                    "review_note": note.strip(),
                    "reviewed_by_id": self.env.uid,
                    "reviewed_on": fields.Datetime.now(),
                }
            )
            rec.sudo().message_post(
                body="Reviewed: %s. No penalty attaches to a refusal."
                % dict(REFUSAL_OUTCOMES)[outcome]
            )
        return True

    def action_uphold(self, note=None):
        return self._fix_review("upheld", note)

    def action_made_safe(self, note=None):
        return self._fix_review("made_safe", note)

    def action_not_substantiated(self, note=None):
        return self._fix_review("not_substantiated", note)


# ---------------------------------------------------------------------------
# Page 6 - customer premises hazard (FR-HSE-025, AUT-HSE-17)
# ---------------------------------------------------------------------------
SITE_HAZARD_TYPES = [
    ("electrical", "Unsafe electrical supply / wiring"),
    ("structural", "Structural / access (stairs, roof, ladder)"),
    ("animal", "Aggressive animal"),
    ("person", "Threatening person"),
    ("chemical", "Chemicals / fumes"),
    ("confined", "Confined or very hot space"),
    ("other", "Other"),
]


class FixHseLocationHazard(models.Model):
    """A hazard at a customer's premises, reported by whoever met it and
    confirmed by HSE with the precautions the next technician takes. While it
    is live, every field order for that customer shows it."""

    _name = "fix.hse.location.hazard"
    _description = "Customer Premises Hazard"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "reported_on desc, id desc"

    _REPORT = ("partner_id", "address", "hazard_type", "description", "field_order_id")

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    address = fields.Text(string="Premises Address")
    hazard_type = fields.Selection(SITE_HAZARD_TYPES, required=True, default="electrical")
    description = fields.Text(string="Hazard Found", required=True)
    precautions = fields.Text(string="Precautions for the Next Visit")
    field_order_id = fields.Many2one("fix.field.order", string="Found on Field Order")
    reported_by_id = fields.Many2one(
        "hr.employee",
        string="Reported By",
        readonly=True,
        default=lambda self: self.env.user.employee_id,
    )
    reported_on = fields.Datetime(readonly=True, default=fields.Datetime.now)
    confirmed_by_id = fields.Many2one("res.users", string="Confirmed By", readonly=True, copy=False)
    confirmed_on = fields.Datetime(readonly=True, copy=False)
    retired_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    retire_reason = fields.Char(readonly=True, copy=False)
    state = fields.Selection(
        [("reported", "Reported"), ("confirmed", "Confirmed (live)"), ("retired", "Retired")],
        required=True,
        default="reported",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "reported_by_id",
            "reported_on",
            "confirmed_by_id",
            "confirmed_on",
            "retired_by_id",
            "retire_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= set(self._REPORT)
        if any(r.state != "reported" for r in self):
            locked |= {"precautions"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        Partner = self.env["res.partner"].sudo()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.hse.location.hazard") or "LHZ/New"
                )
            if not vals.get("address") and vals.get("partner_id"):
                partner = Partner.browse(vals["partner_id"])
                vals["address"] = partner._display_address(without_company=True) or False
        recs = super().create(vals_list)
        for rec in recs:
            _todo(
                rec,
                _group_users(self.env, HSE_GROUP, rec.company_id) - self.env.user,
                "Customer site hazard to confirm: %s" % rec.partner_id.display_name,
                "Confirm it and record the precautions the next technician takes.",
            )
        return recs

    def write(self, vals):
        guard_first(self, vals)
        _locked_change(self, vals, self._REPORT, "%s is reported as found; it is not rewritten.")
        if not self._fix_guard_open():
            if not _is_hse(self.env) and self.filtered(
                lambda r: r.state != "reported" or r.reported_by_id.user_id != self.env.user
            ):
                raise AccessError("The reporter adds to a reported hazard; HSE keeps it after.")
            for rec in self:
                if rec.id and rec.state != "reported":
                    _locked_change(
                        rec, vals, {"precautions"}, "%s is confirmed; its precautions are set."
                    )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A site hazard is retired with a reason, never deleted.")
        return super().unlink()

    def action_confirm(self):
        _require_hse(self.env, "confirm a customer site hazard")
        for rec in self:
            if rec.state != "reported":
                raise UserError("Confirm a reported hazard.")
            if not (rec.precautions or "").strip():
                raise UserError("Record the precautions the next technician takes.")
            rec._guarded().write(
                {
                    "state": "confirmed",
                    "confirmed_by_id": self.env.uid,
                    "confirmed_on": fields.Datetime.now(),
                }
            )
        return True

    def action_retire(self, reason=None):
        _require_hse(self.env, "retire a customer site hazard")
        if not (reason or "").strip():
            raise UserError("Say why the hazard no longer applies.")
        for rec in self:
            if rec.state == "retired":
                raise UserError("%s is retired." % rec.name)
            rec._guarded().write(
                {"state": "retired", "retired_by_id": self.env.uid, "retire_reason": reason.strip()}
            )
        return True


class FixFieldOrderSiteHazards(models.Model):
    """AUT-HSE-17: a field order shows the live hazards at its customer's
    premises, so the technician sent there sees them."""

    _inherit = "fix.field.order"

    hse_site_hazard_ids = fields.Many2many(
        "fix.hse.location.hazard",
        compute="_compute_hse_site_hazards",
        string="Customer Site Hazards",
    )
    hse_site_hazard_note = fields.Text(
        compute="_compute_hse_site_hazards", string="Site Hazards to Know"
    )

    def _compute_hse_site_hazards(self):
        Hazard = self.env["fix.hse.location.hazard"].sudo()
        for rec in self:
            customer = rec.sudo().order_id.customer_id.commercial_partner_id
            live = (
                Hazard.search(
                    [
                        ("partner_id", "child_of", customer.id),
                        ("state", "in", ("reported", "confirmed")),
                    ]
                )
                if customer
                else Hazard
            )
            rec.hse_site_hazard_ids = live
            rec.hse_site_hazard_note = (
                "\n".join(
                    "%s: %s%s"
                    % (
                        dict(SITE_HAZARD_TYPES)[h.hazard_type],
                        h.description,
                        (" - " + h.precautions) if h.precautions else "",
                    )
                    for h in live
                )
                or False
            )


# ---------------------------------------------------------------------------
# Page 7 - site emergency plan (FR-HSE-035)
# ---------------------------------------------------------------------------
class FixHseEmergencyPlan(models.Model):
    """A site's emergency arrangements: evacuation, assembly point, wardens,
    first-aiders and fire equipment. Prepared by HSE and put in force by
    another HSE Officer; one plan in force per branch; reviewed on a cycle and
    a change is a new version."""

    _name = "fix.hse.emergency.plan"
    _description = "Site Emergency Plan"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "branch_id, version desc, id desc"

    _CONTENT = (
        "name",
        "branch_id",
        "operating_unit_id",
        "plan_document",
        "plan_document_name",
        "evacuation_procedure",
        "assembly_point",
        "warden_ids",
        "first_aider_ids",
        "fire_extinguishers",
        "extinguisher_service_due",
        "first_aid_boxes",
        "fire_alarm_tested_on",
        "emergency_contacts",
        "company_id",
    )

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    branch_id = fields.Many2one("fix.branch", string="Site / Branch", required=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    plan_document = fields.Binary(string="Emergency Plan Document", attachment=True)
    plan_document_name = fields.Char()
    evacuation_procedure = fields.Text()
    assembly_point = fields.Char()
    warden_ids = fields.Many2many(
        "hr.employee",
        "fix_hse_eplan_warden_rel",
        "plan_id",
        "employee_id",
        string="Fire Wardens",
    )
    first_aider_ids = fields.Many2many(
        "hr.employee",
        "fix_hse_eplan_first_aider_rel",
        "plan_id",
        "employee_id",
        string="First-Aiders",
    )
    fire_extinguishers = fields.Integer(string="Fire Extinguishers")
    extinguisher_service_due = fields.Date(string="Extinguisher Service Due")
    first_aid_boxes = fields.Integer(string="First-Aid Boxes")
    fire_alarm_tested_on = fields.Date(string="Fire Alarm Last Tested")
    emergency_contacts = fields.Text(string="Emergency Contacts (fire service, hospital)")
    version = fields.Integer(default=1, readonly=True, copy=False)
    previous_id = fields.Many2one(
        "fix.hse.emergency.plan", string="Supersedes", readonly=True, copy=False
    )
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", readonly=True, default=lambda self: self.env.user
    )
    approved_by_id = fields.Many2one(
        "res.users", string="Put in Force By", readonly=True, copy=False
    )
    approved_on = fields.Date(readonly=True, copy=False)
    last_reviewed_on = fields.Date(readonly=True, copy=False)
    next_review_date = fields.Date(readonly=True, copy=False)
    review_due = fields.Boolean(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("in_force", "In Force"), ("superseded", "Superseded")],
        required=True,
        default="draft",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "version",
            "previous_id",
            "prepared_by_id",
            "approved_by_id",
            "approved_on",
            "last_reviewed_on",
            "next_review_date",
            "review_due",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" for r in self):
            locked |= set(self._CONTENT)
        return locked

    @api.constrains("fire_extinguishers", "first_aid_boxes")
    def _check_counts(self):
        for rec in self:
            if (rec.fire_extinguishers or 0) < 0 or (rec.first_aid_boxes or 0) < 0:
                raise ValidationError("Equipment counts cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            _require_hse(self.env, "prepare an emergency plan")
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            _require_hse(self.env, "change an emergency plan")
            for rec in self:
                if rec.id and rec.state != "draft":
                    _locked_change(
                        rec, vals, self._CONTENT, "%s is in force or superseded; revise it."
                    )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and self.filtered(lambda r: r.state != "draft"):
            raise UserError("A plan that has been in force is kept, never deleted.")
        return super().unlink()

    def _fix_next_review(self):
        days = _int_param(self.env, "cd_hse.emergency_plan_review_days", 365)
        return fields.Date.context_today(self) + timedelta(days=days) if days else False

    def action_approve(self):
        _require_hse(self.env, "put an emergency plan in force")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Put a draft plan in force.")
            if not self.env.su and self.env.user == rec.prepared_by_id:
                raise UserError("You prepared %s; another HSE Officer puts it in force." % rec.name)
            missing = [
                label
                for label, ok in (
                    ("the evacuation procedure", (rec.evacuation_procedure or "").strip()),
                    ("the assembly point", (rec.assembly_point or "").strip()),
                    ("a fire warden", rec.warden_ids),
                    ("a first-aider", rec.first_aider_ids),
                    ("the fire extinguishers", rec.fire_extinguishers),
                    ("the first-aid boxes", rec.first_aid_boxes),
                )
                if not ok
            ]
            if missing:
                raise UserError("Plan %s needs %s." % (rec.name, ", ".join(missing)))
            live = self.sudo().search(
                [
                    ("branch_id", "=", rec.branch_id.id),
                    ("state", "=", "in_force"),
                    ("id", "!=", rec.id),
                ]
            )
            live._guarded().write({"state": "superseded"})
            rec._guarded().write(
                {
                    "state": "in_force",
                    "approved_by_id": self.env.uid,
                    "approved_on": fields.Date.context_today(rec),
                    "last_reviewed_on": fields.Date.context_today(rec),
                    "next_review_date": rec._fix_next_review(),
                    "review_due": False,
                }
            )
        return True

    def action_review(self):
        _require_hse(self.env, "review an emergency plan")
        for rec in self:
            if rec.state != "in_force":
                raise UserError("Review the plan in force.")
            rec._guarded().write(
                {
                    "last_reviewed_on": fields.Date.context_today(rec),
                    "next_review_date": rec._fix_next_review(),
                    "review_due": False,
                }
            )
        return True

    def action_revise(self):
        _require_hse(self.env, "revise an emergency plan")
        new = self.browse()
        for rec in self:
            if rec.state != "in_force":
                raise UserError("Revise the plan in force.")
            new |= rec._guarded().copy(
                {
                    "version": rec.version + 1,
                    "previous_id": rec.id,
                    "state": "draft",
                    "prepared_by_id": self.env.uid,
                    "warden_ids": [(6, 0, rec.warden_ids.ids)],
                    "first_aider_ids": [(6, 0, rec.first_aider_ids.ids)],
                }
            )
        return {"ids": new.ids}

    @api.model
    def cron_flag_plan_reviews(self):
        """A plan past its review date, or whose extinguishers are past their
        service date, is flagged once to HSE. Idempotent; superuser."""
        today = fields.Date.context_today(self)
        due = self.sudo().search(
            [
                ("state", "=", "in_force"),
                ("review_due", "=", False),
                "|",
                ("next_review_date", "<", today),
                ("extinguisher_service_due", "<", today),
            ]
        )
        for rec in due:
            rec._guarded().write({"review_due": True})
            _todo(
                rec,
                _group_users(self.env, HSE_GROUP, rec.company_id),
                "Emergency plan review due: %s" % rec.name,
                "Review the plan for %s (and the extinguisher service, due %s)."
                % (rec.branch_id.display_name, rec.extinguisher_service_due or "-"),
            )
        return len(due)
