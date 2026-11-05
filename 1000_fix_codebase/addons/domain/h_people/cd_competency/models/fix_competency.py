# fix_competency — M22: certification register + FR-LMS-039 (P08-M05).
#
# A09 workflow audit (M22-F2/F3/F4/F5/F8/F9): the Training Manager certified
# himself with no assessment and no expiry; a training pass needed no
# assessment, worked from 'failed', duplicated and issued non-expiring
# certificates; a lapsed certificate was revived by typing a date; no cron
# ever refreshed expiry; "Hard Block Dispatch" blocked nothing; the work-order
# gate failed open for an unconfigured device type; and the waiver was a bare
# Boolean any internal user could tick.
#
# Now:
#   * a certification is draft until a routed GRANT approves it (M63, the
#     Certification Verifier): a passed assessment by someone other than the
#     technician, an expiry date and a certificate scan or evidence reference
#     are required, no duplicate valid certificate may exist, and nobody
#     requests or decides their own;
#   * a granted certificate is frozen; it is renewed (a new draft linked to
#     it), suspended, reinstated or revoked, never re-dated;
#   * a daily cron lapses expired certificates and raises expiry alerts;
#   * only a VALID certification counts for dispatch, and the work-order gate
#     fails closed;
#   * the waiver is a routed, reasoned fix.certification.waiver record.
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Domain

from libs.py.fix_events import publish

EXPIRING_WINDOW_DAYS = 30  # the value the code used; now a setting (below)
LEAD_DAYS_PARAM = "cd_competency.expiry_lead_days"
TIER_RANK = {"l1": 1, "l2": 2, "l3": 3, "l4": 4}

TRAINING = "cd_competency.group_training"
VERIFIER = "cd_competency.group_certification_verifier"
# Who is told when a technician loses a certification a job depends on, and
# who is escalated to when a statutory / safety certification lapses (M59).
DISPATCHER = "cd_field_service.group_fix_field_service_manager"
HSE_OFFICER = "cd_hse.group_hse_officer"
# Work orders that have not started: the gate re-checks them when they start.
WORK_ORDER_OPEN = ("pending", "assigned")

TIERS = [
    ("l1", "L1 - Modular Replacement"),
    ("l2", "L2 - Sub-Assembly Diagnostics"),
    ("l3", "L3 - Component / BGA Micro-Soldering"),
    ("l4", "L4 - Schematic & Firmware Engineering"),
]


def guard_first(records, vals):
    """Refuse a guarded-field change before a model's own write checks."""
    if records and not records._fix_guard_open():
        touched = records._fix_guarded_fields() & set(vals)
        changed = {
            name
            for rec in records
            for name in touched
            if rec._fix_guard_differs(name, vals[name], rec[name])
        }
        if changed:
            records._fix_guard_refuse(changed)


def changed_fields(records, vals, names):
    return {
        name
        for rec in records
        for name in set(names) & set(vals)
        if rec._fix_guard_differs(name, vals[name], rec[name])
    }


def require_group(env, xmlid, what):
    if env.su or env.user.has_group(xmlid):
        return
    group = env.ref(xmlid, raise_if_not_found=False)
    raise AccessError("%s needs the %s role." % (what, group.name if group else xmlid))


def group_users(env, xmlid, company=None):
    """Active internal holders of a group (empty when it is not installed)."""
    group = env.ref(xmlid, raise_if_not_found=False)
    if not group:
        return env["res.users"]
    users = group.sudo().all_user_ids.filtered(lambda u: u.active and not u.share)
    if company:
        users = users.filtered(lambda u: company in u.company_ids)
    return users.sorted("id")


def open_activity_once(record, user, summary, note, deadline=None):
    """A to-do for `user` on `record`, unless the same one is already open."""
    Activity = record.env["mail.activity"].sudo()
    if Activity.search_count(
        [
            ("res_model", "=", record._name),
            ("res_id", "=", record.id),
            ("user_id", "=", user.id),
            ("summary", "=", summary),
        ]
    ):
        return False
    record.sudo().activity_schedule(
        "mail.mail_activity_data_todo",
        date_deadline=deadline or fields.Date.today(),
        summary=summary,
        note=note,
        user_id=user.id,
    )
    return True


def licence_checker(employee):
    """hr.employee._fix_driving_licence when cd_hse provides it, else None."""
    return getattr(employee, "_fix_driving_licence", None)


def expiry_lead_days(env):
    """FR-LMS-011: the configurable alert lead time (default: the 30 days the
    code always used)."""
    raw = env["ir.config_parameter"].sudo().get_param(LEAD_DAYS_PARAM, str(EXPIRING_WINDOW_DAYS))
    try:
        return max(int(raw), 0)
    except (TypeError, ValueError):
        return EXPIRING_WINDOW_DAYS


class FixDeviceCategory(models.Model):
    """Structured Device Taxonomy for M22 Competency & Certification Matrix (RAP-M22-01)."""

    _name = "fix.device.category"
    _description = "Device Category Taxonomy"
    _order = "code, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Category Name (Bengali)")
    parent_id = fields.Many2one(
        "fix.device.category", string="Parent Category", ondelete="restrict"
    )
    repair_tier_floor = fields.Selection(TIERS, string="Minimum Repair Tier", default="l1")
    active = fields.Boolean(default=True)


class FixCompetency(models.Model):
    _name = "fix.competency"
    _description = "Competency"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Competency (Bengali)", help="DE-17")
    device_type = fields.Char(
        string="Device Type Scope",
        help="Comma-separated fix.device device types (e.g. smartphone, laptop, "
        "appliance_ac) — the dispatch eligibility match key (FR-LMS-039)",
    )
    device_category_id = fields.Many2one(
        "fix.device.category", string="Device Category", ondelete="set null"
    )
    brand_id = fields.Many2one("fix.brand", string="OEM Brand Scope", ondelete="set null")
    repair_tier = fields.Selection(TIERS, string="Minimum Repair Tier")
    required_for_dispatch = fields.Boolean(
        default=True, help="Unchecked for developmental competencies that do not gate assignment"
    )
    # FR-LMS-026: pass criteria and attempt limit are policy (BRU-LMS-09, the
    # HR Director's); the code holds no figure. No pass mark = no assessment
    # of this competency can pass, so nothing is certified by default.
    pass_mark = fields.Float(
        string="Pass Mark %", help="An assessment passes at or above this score (0 = not set)."
    )
    attempt_limit = fields.Integer(
        string="Attempt Limit",
        help="Failed assessments allowed before HR escalation (0 = no limit).",
    )
    validity_months = fields.Integer(
        string="Validity (months)",
        help="Expiry of a certificate issued after a training pass (0 = the verifier "
        "types the expiry date).",
    )
    # BRU-LMS-07 / FR-LMS-015: electrical, refrigerant and gas-handling work
    # needs a statutory or safety certification; its lapse is escalated to
    # Health & Safety (M59), not only blocked.
    certification_class = fields.Selection(
        [("standard", "Operational"), ("safety", "Statutory / Safety")],
        string="Certification Class",
        required=True,
        default="standard",
        help="Statutory / Safety: a lapse is escalated to the HSE Officers (M59).",
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _pass_mark_range = models.Constraint(
        "CHECK (pass_mark IS NULL OR (pass_mark >= 0 AND pass_mark <= 100))",
        "A pass mark is a 0-100 percentage.",
    )

    @api.constrains("device_type")
    def _check_device_type(self):
        """M22-F2: a device type no device has (fix_dev's 'home_appliance')
        made the gate fail open. A scope names real fix.device types."""
        if "fix.device" not in self.env:
            return
        field = self.env["fix.device"]._fields.get("device_type")
        try:
            valid = {k for k, _l in (field._description_selection(self.env) or [])}
        except Exception:
            return
        if not valid:
            return
        for rec in self:
            tokens = [t.strip() for t in (rec.device_type or "").split(",") if t.strip()]
            unknown = [t for t in tokens if t not in valid]
            if unknown:
                raise ValidationError(
                    "Device type scope %s names no device type (%s). Use: %s"
                    % (rec.code, ", ".join(unknown), ", ".join(sorted(valid)))
                )


class FixCertification(models.Model):
    """The certification register with expiry tracking (P08-M05-T02)."""

    _name = "fix.certification"
    _description = "Certification"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.people.approval.mixin"]
    _order = "employee_id, expires_on"

    _approval_domain = "hr_certification"
    _approval_apply_method = "action_approve_grant"
    _approval_group = VERIFIER

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    competency_id = fields.Many2one("fix.competency", required=True, ondelete="restrict")
    brand_id = fields.Many2one("fix.brand", string="Certified OEM Brand", ondelete="set null")
    device_category_id = fields.Many2one(
        "fix.device.category", string="Device Category", ondelete="set null"
    )
    repair_tier = fields.Selection(TIERS, string="Certified Repair Tier")
    certificate_file = fields.Binary(string="Certificate Scan", attachment=True)
    certificate_filename = fields.Char(string="Certificate Filename")
    issued_on = fields.Date(required=True, default=fields.Date.today)
    expires_on = fields.Date(help="Required for a grant (BRU-LMS-04/05)")
    evidence_ref = fields.Char(
        string="Evidence Reference", help="Pointer into M24 documents — the certificate artefact"
    )
    assessment_id = fields.Many2one(
        "fix.competency.assessment",
        string="Qualifying Assessment",
        ondelete="restrict",
        help="The passed assessment the grant rests on (BRU-LMS-06).",
    )
    # Superuser code (seeds, migrations, data loading) is trusted, as for the
    # guard: its records are valid. Everyone else starts at draft and is granted.
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("valid", "Valid"),
            ("suspended", "Suspended"),
            ("lapsed", "Lapsed"),
            ("revoked", "Revoked"),
            ("superseded", "Renewed"),
        ],
        default=lambda self: "valid" if self.env.su else "draft",
        required=True,
        tracking=True,
        index=True,
    )
    status = fields.Selection(
        [("active", "Active"), ("expiring", "Expiring Soon"), ("expired", "Expired")],
        compute="_compute_status",
        search="_search_status",
        help="Judged against today's date every time it is read.",
    )
    verified_by_id = fields.Many2one("res.users", string="Granted By", readonly=True)
    verified_at = fields.Datetime(string="Granted At", readonly=True)
    suspended_by_id = fields.Many2one("res.users", string="Suspended By", readonly=True)
    suspended_at = fields.Datetime(string="Suspended At", readonly=True)
    suspension_reason = fields.Char(string="Suspension / Revocation Reason", readonly=True)
    renewal_of_id = fields.Many2one(
        "fix.certification", string="Renews", readonly=True, ondelete="set null"
    )
    expiry_alerted_on = fields.Date(string="Expiry Alert Sent", readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _FROZEN_AFTER_DRAFT = frozenset(
        {
            "employee_id",
            "competency_id",
            "brand_id",
            "device_category_id",
            "repair_tier",
            "certificate_file",
            "certificate_filename",
            "issued_on",
            "expires_on",
            "evidence_ref",
            "assessment_id",
            "company_id",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "verified_by_id",
            "verified_at",
            "suspended_by_id",
            "suspended_at",
            "suspension_reason",
            "renewal_of_id",
            "expiry_alerted_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" or rec.approval_state == "pending" for rec in self):
            locked = locked | self._FROZEN_AFTER_DRAFT
        return locked

    # ---- status ---------------------------------------------------------------
    @api.depends("expires_on")
    def _compute_status(self):
        today = fields.Date.today()
        lead = expiry_lead_days(self.env)
        for rec in self:
            if not rec.expires_on:
                rec.status = "active"
            elif rec.expires_on < today:
                rec.status = "expired"
            elif (rec.expires_on - today).days <= lead:
                rec.status = "expiring"
            else:
                rec.status = "active"

    def _search_status(self, operator, value):
        today = fields.Date.today()
        soon = today + timedelta(days=expiry_lead_days(self.env))
        domains = {
            "expired": [("expires_on", "!=", False), ("expires_on", "<", today)],
            "expiring": [("expires_on", ">=", today), ("expires_on", "<=", soon)],
            "active": ["|", ("expires_on", "=", False), ("expires_on", ">", soon)],
        }
        # The ORM may pass any iterable for 'in' (a frozenset, an OrderedSet).
        values = (
            [value] if isinstance(value, str) or not hasattr(value, "__iter__") else list(value)
        )
        if operator in ("=", "in"):
            parts = [domains[v] for v in values if v in domains]
        elif operator in ("!=", "not in"):
            parts = [domains[k] for k in domains if k not in values]
        else:
            raise UserError("Unsupported search on certification status: %s" % operator)
        if not parts:
            return [("id", "=", 0)]
        return Domain.OR(parts)

    # ---- approval declarations ---------------------------------------------
    def _approval_preparers(self):
        assessors = self.mapped("assessment_id.assessor_id.user_id")
        return assessors | self.mapped("create_uid")

    # ---- writes ---------------------------------------------------------------
    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(
                self.filtered(lambda r: r.state != "draft" or r.approval_state == "pending"),
                vals,
                self._FROZEN_AFTER_DRAFT,
            )
            if frozen:
                raise UserError(
                    "A granted or pending certification is not edited (%s): renew it, or "
                    "suspend or revoke it. A lapsed certificate is never revived by typing "
                    "a new date." % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    # ---- the grant --------------------------------------------------------------
    def _fix_grant_gate(self):
        """Everything a grant rests on (BRU-LMS-04/06, FR-LMS-026)."""
        today = fields.Date.today()
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft certification." % rec.display_name)
            if not rec.expires_on:
                raise UserError("A certification is granted with an expiry date (BRU-LMS-05).")
            if rec.expires_on <= max(rec.issued_on, today):
                raise UserError("The expiry date of %s has already passed." % rec.display_name)
            if not (rec.certificate_file or (rec.evidence_ref or "").strip()):
                raise UserError(
                    "BRU-LMS-04: attach the certificate scan or give the evidence reference."
                )
            asmt = rec.assessment_id.sudo()
            if not asmt:
                raise UserError(
                    "BRU-LMS-06: a certification rests on a passed assessment by an "
                    "authorised assessor; link it."
                )
            if not asmt.passed:
                raise UserError("Assessment %s did not pass." % asmt.name)
            if asmt.employee_id != rec.employee_id or asmt.competency_id != rec.competency_id:
                raise UserError(
                    "Assessment %s is for another technician or competency." % asmt.name
                )
            if not asmt.assessor_id or asmt.assessor_id == rec.employee_id:
                raise UserError(
                    "Assessment %s was not made by an independent assessor." % asmt.name
                )
            twin = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("id", "!=", rec.renewal_of_id.id or 0),
                    ("employee_id", "=", rec.employee_id.id),
                    ("competency_id", "=", rec.competency_id.id),
                    ("brand_id", "=", rec.brand_id.id or False),
                    ("repair_tier", "=", rec.repair_tier or False),
                    ("state", "in", ("valid", "suspended")),
                ],
                limit=1,
            )
            if twin:
                raise UserError(
                    "%s already holds this certification (%s); renew it instead."
                    % (rec.employee_id.name, twin.display_name)
                )

    def _fix_assert_not_own(self):
        for rec in self:
            if not self.env.su and rec.employee_id.sudo().user_id == self.env.user:
                raise UserError("BRU-LMS-06: nobody certifies themself.")

    def action_request_grant(self, justification=None):
        """Route a draft certification to the Certification Verifier."""
        require_group(self.env, TRAINING, "Requesting a certification grant")
        self._fix_assert_not_own()
        self._fix_grant_gate()
        return self.action_request_approval(justification=justification)

    def action_grant(self):
        """The register's "Grant Certification" button: a routed request, never
        a grant by the person who presses it."""
        return self.action_request_grant()

    def action_approve_grant(self):
        """Run by the approval engine from the verifier's inbox task."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        self._fix_grant_gate()
        for rec in self:
            rec._guarded().write(
                {
                    "state": "valid",
                    "verified_by_id": rec._people_decider().id,
                    "verified_at": fields.Datetime.now(),
                }
            )
            if rec.renewal_of_id and rec.renewal_of_id.state in ("valid", "lapsed", "suspended"):
                rec.renewal_of_id.sudo()._guarded().write({"state": "superseded"})
            publish(
                self.env,
                "certification.granted",
                "fix.certification",
                rec.id,
                {"employee": rec.employee_id.name, "competency": rec.competency_id.code},
            )
        return True

    # ---- after the grant -----------------------------------------------------
    def action_renew(self):
        """FR-LMS-012: a renewal is a new draft certification that goes through
        its own grant (assessment, evidence, expiry); the old one stays until then."""
        require_group(self.env, TRAINING, "Renewing a certification")
        out = self.browse()
        for rec in self:
            if rec.state not in ("valid", "lapsed"):
                raise UserError("Only a valid or lapsed certification is renewed.")
            out |= (
                self.sudo()
                ._guarded()
                .create(
                    {
                        "employee_id": rec.employee_id.id,
                        "competency_id": rec.competency_id.id,
                        "brand_id": rec.brand_id.id,
                        "device_category_id": rec.device_category_id.id,
                        "repair_tier": rec.repair_tier,
                        "company_id": rec.company_id.id,
                        "operating_unit_id": rec.operating_unit_id.id,
                        "issued_on": fields.Date.today(),
                        "state": "draft",
                        "renewal_of_id": rec.id,
                    }
                )
            )
        return {"renewal_ids": out.ids}

    def _fix_reason(self, reason):
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Give the reason.")
        return reason

    def action_suspend(self, reason=None):
        """M22-F8: blocks dispatch at once (a quality incident, an investigation)."""
        require_group(self.env, TRAINING, "Suspending a certification")
        reason = self._fix_reason(reason)
        for rec in self:
            if rec.state != "valid":
                raise UserError("Only a valid certification is suspended.")
            rec._guarded().write(
                {
                    "state": "suspended",
                    "suspended_by_id": self.env.user.id,
                    "suspended_at": fields.Datetime.now(),
                    "suspension_reason": reason,
                }
            )
            publish(
                self.env,
                "certification.suspended",
                "fix.certification",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "competency": rec.competency_id.code,
                    "reason": reason,
                },
            )
        return True

    def action_reinstate(self, reason=None):
        """A verifier other than the one who suspended lifts a suspension."""
        require_group(self.env, VERIFIER, "Reinstating a certification")
        reason = self._fix_reason(reason)
        today = fields.Date.today()
        for rec in self:
            if rec.state != "suspended":
                raise UserError("Only a suspended certification is reinstated.")
            if not self.env.su and self.env.user in (
                rec.suspended_by_id | rec.employee_id.sudo().user_id
            ):
                raise UserError(
                    "The person who suspended a certification, or its holder, does not lift it."
                )
            if rec.expires_on and rec.expires_on < today:
                raise UserError("%s has expired meanwhile; renew it." % rec.display_name)
            rec._guarded().write({"state": "valid", "suspension_reason": reason})
            rec.message_post(body="Reinstated by %s: %s" % (self.env.user.name, reason))
        return True

    def action_revoke(self, reason=None):
        require_group(self.env, TRAINING, "Revoking a certification")
        reason = self._fix_reason(reason)
        for rec in self:
            if rec.state not in ("valid", "suspended", "lapsed"):
                raise UserError("Only a granted certification is revoked.")
            rec._guarded().write(
                {
                    "state": "revoked",
                    "suspended_by_id": self.env.user.id,
                    "suspended_at": fields.Datetime.now(),
                    "suspension_reason": reason,
                }
            )
            publish(
                self.env,
                "certification.revoked",
                "fix.certification",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "competency": rec.competency_id.code,
                    "reason": reason,
                },
            )
        return True

    # ---- expiry ---------------------------------------------------------------
    def _fix_lapse_expired(self):
        """Valid certificates past their expiry become lapsed (AUT-LMS-02)."""
        today = fields.Date.today()
        lapsed = self.filtered(
            lambda r: r.state == "valid" and r.expires_on and r.expires_on < today
        )
        for rec in lapsed:
            rec.sudo()._guarded().write({"state": "lapsed"})
            publish(
                self.env,
                "certification.expired",
                "fix.certification",
                rec.id,
                {
                    "employee": rec.employee_id.name,
                    "employee_id": rec.employee_id.id,
                    "competency": rec.competency_id.code,
                },
            )
        lapsed.filtered(
            lambda r: r.competency_id.certification_class == "safety"
        )._fix_escalate_safety_lapse()
        return lapsed

    def _fix_escalate_safety_lapse(self):
        """BRU-LMS-07: a lapsed statutory / safety certification is escalated
        to Health & Safety: a to-do for each HSE Officer (the Training
        Managers when M59 is not installed or has no officer) and an event
        M59 can consume."""
        for rec in self.sudo():
            emp = rec.employee_id
            users = group_users(self.env, HSE_OFFICER, rec.company_id) or group_users(
                self.env, TRAINING, rec.company_id
            )
            summary = "Safety certification lapsed: %s / %s" % (emp.name, rec.competency_id.code)
            for user in users - emp.user_id:
                open_activity_once(
                    rec,
                    user,
                    summary,
                    "The statutory / safety certification %s of %s lapsed on %s. The "
                    "technician is blocked from work that needs it; record the HSE "
                    "follow-up (M59)." % (rec.competency_id.name, emp.name, rec.expires_on),
                )
            publish(
                self.env,
                "certification.safety_lapsed",
                "fix.certification",
                rec.id,
                {
                    "employee_id": emp.id,
                    "certification_id": rec.id,
                    "competency": rec.competency_id.code,
                    "expired_on": str(rec.expires_on or ""),
                },
            )
        return True

    def action_mark_expired(self):
        """Manual sweep of the selected certifications (the cron does it daily)."""
        require_group(self.env, TRAINING, "Lapsing certifications")
        self._fix_lapse_expired()
        return True

    @api.model
    def _cron_certification_expiry(self):
        """Daily (ir.cron): lapse expired certificates, alert those expiring
        inside the lead time once each (FR-LMS-011/013, AUT-LMS-01/02).
        Idempotent: a lapsed certificate is not lapsed again, an alerted one
        is not alerted again."""
        Cert = self.sudo()
        today = fields.Date.today()
        Cert.search([("state", "=", "valid"), ("expires_on", "<", today)])._fix_lapse_expired()
        soon = today + timedelta(days=expiry_lead_days(self.env))
        due = Cert.search(
            [
                ("state", "=", "valid"),
                ("expires_on", ">=", today),
                ("expires_on", "<=", soon),
                ("expiry_alerted_on", "=", False),
            ]
        )
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        for rec in due:
            emp = rec.employee_id
            notify = emp.parent_id.user_id or emp.user_id
            if todo and notify:
                rec.activity_schedule(
                    activity_type_id=todo.id,
                    user_id=notify.id,
                    date_deadline=rec.expires_on,
                    summary="Renew %s for %s before %s"
                    % (rec.competency_id.name, emp.name, rec.expires_on),
                )
            rec._guarded().write({"expiry_alerted_on": today})
            publish(
                self.env,
                "certification.expiring",
                "fix.certification",
                rec.id,
                {
                    "employee_id": emp.id,
                    "competency": rec.competency_id.code,
                    "expires_on": str(rec.expires_on),
                    "days_remaining": (rec.expires_on - today).days,
                },
            )
        return True

    # ---- FR-LMS-039 -----------------------------------------------------------
    @api.model
    def _fix_driving_licence_problem(self, employee, day):
        """FR-HSE-019 / BRU-HSE-07: vehicle-based work needs a driving licence
        valid on `day`. The licence lives in M59/M46 (cd_hse provides
        hr.employee._fix_driving_licence); cd_competency does not depend on
        it, so a check that cannot run FAILS CLOSED. None when the licence
        is valid."""
        emp = employee.sudo()
        check = licence_checker(emp)
        if check is None:
            return (
                "FR-HSE-019: the job needs a vehicle and no driving-licence check is "
                "installed (fail-closed)"
            )
        try:
            licence, reason = check(day)
        except Exception as exc:  # the licence register itself is unavailable
            return (
                "FR-HSE-019: the driving licence of %s could not be checked (%s; "
                "fail-closed)" % (emp.name, exc)
            )
        if not licence:
            return "FR-HSE-019: vehicle-based work refused: %s" % (
                reason or "no valid driving licence"
            )
        return None

    @api.model
    def dispatch_eligibility(
        self,
        employee,
        device_type=None,
        brand_id=None,
        repair_tier=None,
        fail_closed=False,
        requires_vehicle=False,
    ):
        """FR-LMS-039 — the dispatch eligibility check (brand + device + tier aware).

        Returns (eligible: bool, reason: str). A technician is eligible for
        a device type, OEM brand, and repair tier when they hold a VALID
        (granted, not suspended, revoked or lapsed) certification, inside its
        dates, in a dispatch-gating competency whose scope matches.
        """
        if not employee:
            return False, "no technician assigned"
        today = fields.Date.today()
        if requires_vehicle:
            problem = self._fix_driving_licence_problem(employee, today)
            if problem:
                return False, problem
        certs = self.search(
            [
                ("employee_id", "=", employee.id),
                ("state", "=", "valid"),
                ("issued_on", "<=", today),
                "|",
                ("expires_on", "=", False),
                ("expires_on", ">=", today),
            ]
        )
        brand_id_int = (
            brand_id.id if hasattr(brand_id, "id") else (int(brand_id) if brand_id else None)
        )
        req_rank = TIER_RANK.get(repair_tier, 0) if repair_tier else 0

        valid_certs = self.browse()
        # Track WHY a certificate was filtered out. Reporting a tier shortfall
        # as a missing brand certification sends the operator after the wrong
        # certificate, which is worse than no reason at all.
        tier_blocked = self.browse()
        for cert in certs:
            c_brand = cert.brand_id.id or cert.competency_id.brand_id.id or None
            if brand_id_int and c_brand and c_brand != brand_id_int:
                continue
            c_tier = cert.repair_tier or cert.competency_id.repair_tier or None
            if req_rank and c_tier and TIER_RANK.get(c_tier, 0) < req_rank:
                tier_blocked |= cert
                continue
            valid_certs |= cert

        gating = self.env["fix.competency"].search([("required_for_dispatch", "=", True)])
        gating_by_id = {c.id: c for c in gating}
        held = set(valid_certs.competency_id.ids)

        if brand_id_int:
            brand_gating = [c for c in gating if c.brand_id.id == brand_id_int]
            if brand_gating and not any(
                (cert.brand_id.id == brand_id_int or cert.competency_id.brand_id.id == brand_id_int)
                for cert in valid_certs
            ):
                brand_rec = self.env["fix.brand"].browse(brand_id_int)
                tier_hit = tier_blocked.filtered(
                    lambda c: (c.brand_id.id or c.competency_id.brand_id.id) == brand_id_int
                )
                if tier_hit:
                    held_tier = tier_hit[0].repair_tier or tier_hit[0].competency_id.repair_tier
                    return False, (
                        "FR-LMS-039: %s is certified for %s at tier %s, below the %s "
                        "required by this job"
                        % (
                            employee.name,
                            brand_rec.name or brand_id_int,
                            (held_tier or "?").upper(),
                            (repair_tier or "?").upper(),
                        )
                    )
                return False, (
                    "FR-LMS-039: %s holds no ACTIVE brand certification for %s"
                    % (employee.name, brand_rec.name or brand_id_int)
                )

        if device_type:
            scoped = [
                c
                for c in gating
                if (c.device_type and device_type in [t.strip() for t in c.device_type.split(",")])
                or (c.device_category_id and c.device_category_id.code == device_type)
            ]
            if scoped:
                for comp in scoped:
                    if comp.id in held:
                        return True, "certified for %s" % device_type
                short = tier_blocked.filtered(lambda c: c.competency_id in scoped)
                if short:
                    held_tier = short[0].repair_tier or short[0].competency_id.repair_tier
                    return False, (
                        "FR-LMS-039: %s is certified for %s at tier %s, below the %s "
                        "required by this job"
                        % (
                            employee.name,
                            device_type,
                            (held_tier or "?").upper(),
                            (repair_tier or "?").upper(),
                        )
                    )
                return False, (
                    "FR-LMS-039: %s holds no ACTIVE certification for %s"
                    % (employee.name, device_type)
                )
            if fail_closed:
                return False, (
                    "FR-LMS-039: no dispatch-gating competency configured for %s (fail-closed)"
                    % device_type
                )
        # No device scope demanded: at least one gating competency held
        if held & set(gating_by_id):
            return True, "holds dispatch-gating certification"
        if brand_id_int and certs and not valid_certs:
            brand_rec = self.env["fix.brand"].browse(brand_id_int)
            return False, (
                "FR-LMS-039: %s holds no ACTIVE certification for brand %s"
                % (employee.name, brand_rec.name or brand_id_int)
            )
        return False, ("FR-LMS-039: %s holds no dispatch-gating certification" % employee.name)


class FixTrainingCourse(models.Model):
    _name = "fix.training.course"
    _description = "Training Course"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Course (Bengali)", help="DE-17")
    content_ref = fields.Char(
        string="Content Pack",
        help="project_content 08 pack (the 24 TR-* files) — loaded content "
        "pointer; authoring degrades without M61 (accepted)",
    )
    competency_id = fields.Many2one("fix.competency", string="Certifies Towards")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # BRU-LMS-10: what one seat costs against the year's training budget.
    cost_per_seat = fields.Monetary(
        string="Cost per Seat", currency_field="currency_id", default=0.0
    )
    enrollment_ids = fields.One2many("fix.training.enrollment", "course_id", string="Enrollments")
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    def _fix_employees_from(self, employees):
        """A recordset, a list of ids, or the workspace prompt's text "12, 13"."""
        Employee = self.env["hr.employee"]
        if isinstance(employees, models.BaseModel):
            return employees
        if isinstance(employees, str):
            employees = [t for t in employees.replace(";", ",").replace(" ", ",").split(",") if t]
        ids = []
        for value in employees or []:
            try:
                ids.append(int(value))
            except (TypeError, ValueError):
                raise UserError("Name the technicians by their employee ids.") from None
        found = Employee.browse(ids).exists()
        missing = set(ids) - set(found.ids)
        if missing:
            raise UserError("No employee with id %s." % ", ".join(str(i) for i in sorted(missing)))
        return found

    def action_enroll(self, employees=None, employee_ids=None):
        """M22-F9: the workspace sends ids (or the prompt's text), not a recordset."""
        require_group(self.env, TRAINING, "Enrolling technicians")
        emps = self._fix_employees_from(employees if employees is not None else employee_ids)
        if not emps:
            raise UserError("Name at least one technician to enroll.")
        Enrollment = self.env["fix.training.enrollment"]
        created = Enrollment.browse()
        for rec in self:
            for emp in emps:
                if Enrollment.search_count(
                    [
                        ("course_id", "=", rec.id),
                        ("employee_id", "=", emp.id),
                        ("state", "=", "enrolled"),
                    ]
                ):
                    continue
                created |= Enrollment.create({"course_id": rec.id, "employee_id": emp.id})
        return {"enrolled": len(created), "enrollment_ids": created.ids}


class FixTrainingEnrollment(models.Model):
    _name = "fix.training.enrollment"
    _description = "Training Enrollment"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    course_id = fields.Many2one("fix.training.course", required=True, ondelete="cascade")
    employee_id = fields.Many2one("hr.employee", required=True)
    state = fields.Selection(
        [("enrolled", "Enrolled"), ("passed", "Passed"), ("failed", "Failed")],
        default="enrolled",
        required=True,
    )
    completed_on = fields.Date(readonly=True)
    assessment_id = fields.Many2one(
        "fix.competency.assessment", string="Qualifying Assessment", readonly=True
    )
    certification_id = fields.Many2one(
        "fix.certification", string="Draft Certification", readonly=True
    )
    decided_by_id = fields.Many2one("res.users", string="Result Recorded By", readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "completed_on",
            "assessment_id",
            "certification_id",
            "decided_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "enrolled" for rec in self):
            locked = locked | {"course_id", "employee_id", "company_id"}
        return locked

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(
                self.filtered(lambda r: r.state != "enrolled"),
                vals,
                {"course_id", "employee_id", "company_id"},
            )
            if frozen:
                raise UserError("A decided enrolment is final (%s)." % ", ".join(sorted(frozen)))
        return super().write(vals)

    def _fix_assert_decider(self):
        require_group(self.env, TRAINING, "Recording a training result")
        for rec in self:
            if rec.state != "enrolled":
                raise UserError(
                    "%s is already %s; a retake is a new enrolment (BRU-LMS-09)."
                    % (rec.display_name, rec.state)
                )
            if not self.env.su and rec.employee_id.sudo().user_id == self.env.user:
                raise UserError("You cannot record the result of your own training.")

    def _fix_qualifying_assessment(self):
        self.ensure_one()
        comp = self.course_id.competency_id
        if not comp:
            return self.env["fix.competency.assessment"]
        since = fields.Date.to_date(self.create_date) if self.create_date else False
        domain = [
            ("employee_id", "=", self.employee_id.id),
            ("competency_id", "=", comp.id),
            ("passed", "=", True),
            ("assessor_id", "!=", False),
            ("assessor_id", "!=", self.employee_id.id),
        ]
        if since:
            domain.append(("assessed_on", ">=", since))
        return (
            self.env["fix.competency.assessment"]
            .sudo()
            .search(domain, order="assessed_on desc, id desc", limit=1)
        )

    def action_pass(self):
        """FR-LMS-026, §8.1 ASSESSED -> VALID: a pass needs a passed assessment
        by an independent assessor. It drafts the certificate; the certificate
        is valid only once its grant is approved."""
        self._fix_assert_decider()
        Cert = self.env["fix.certification"].sudo()._guarded()
        today = fields.Date.today()
        for rec in self:
            comp = rec.course_id.competency_id
            asmt = rec._fix_qualifying_assessment()
            if comp and not asmt:
                raise UserError(
                    "No passed assessment of %s in %s since the enrolment: assess before "
                    "passing." % (rec.employee_id.name, comp.name)
                )
            cert = rec.env["fix.certification"]
            if comp:
                cert = Cert.search(
                    [
                        ("employee_id", "=", rec.employee_id.id),
                        ("competency_id", "=", comp.id),
                        ("state", "=", "draft"),
                    ],
                    limit=1,
                ) or Cert.create(
                    {
                        "employee_id": rec.employee_id.id,
                        "competency_id": comp.id,
                        "company_id": rec.company_id.id,
                        "issued_on": today,
                        "expires_on": today + relativedelta(months=comp.validity_months)
                        if comp.validity_months
                        else False,
                        "assessment_id": asmt.id,
                        "state": "draft",
                    }
                )
            rec._guarded().write(
                {
                    "state": "passed",
                    "completed_on": today,
                    "assessment_id": asmt.id or False,
                    "certification_id": cert.id or False,
                    "decided_by_id": self.env.user.id,
                }
            )
            publish(
                self.env,
                "training.passed",
                "fix.training.enrollment",
                rec.id,
                {"employee": rec.employee_id.name, "course": rec.course_id.code},
            )
        return True

    def action_fail(self):
        self._fix_assert_decider()
        for rec in self:
            rec._guarded().write(
                {
                    "state": "failed",
                    "completed_on": fields.Date.context_today(self),
                    "decided_by_id": self.env.user.id,
                }
            )
        return True


class FixWorkOrderEligibilityExt(models.Model):
    """P08-M05-T04/T05: the M02 -> M22 AND M31 -> M22 stubs CLOSED —
    certification eligibility is now a BLOCKING check on the live
    assignment path (both field service and workshop share
    fix.work.order). It fails closed for a device type with no gating
    competency; the waiver is set only by an approved waiver record."""

    _name = "fix.work.order"
    _inherit = ["fix.work.order", "fix.guarded.mixin"]

    certification_waiver = fields.Boolean(
        string="Certification Waiver",
        readonly=True,
        help="Set only by an approved certification waiver for this job and technician",
    )
    certification_waiver_reason = fields.Char(string="Waiver Justification", readonly=True)
    certification_waiver_id = fields.Many2one(
        "fix.certification.waiver", string="Approved Waiver", readonly=True, ondelete="set null"
    )
    # A09 round 2: the tier the job needs (L1 modular ... L4 firmware); the
    # eligibility check then demands a certification at that tier or above.
    repair_tier = fields.Selection(TIERS, string="Required Repair Tier")
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    def _fix_guarded_fields(self) -> set:
        # M22-F3: the waiver was a Boolean any internal user could tick.
        return super()._fix_guarded_fields() | {
            "certification_waiver",
            "certification_waiver_reason",
            "certification_waiver_id",
        }

    def _fix_waiver_covers(self):
        self.ensure_one()
        if not self.certification_waiver:
            return False
        waiver = self.certification_waiver_id.sudo()
        if not waiver:
            # Set by trusted (superuser) code with no waiver record.
            return True
        return waiver._fix_covers_target("fix.work.order", self.id, self.technician_id)

    def _fix_certification_problem(self, technician=None):
        """Why the technician may not take this job (None when they may)."""
        self.ensure_one()
        tech = technician or self.technician_id
        if not tech or (not technician and self._fix_waiver_covers()):
            return None
        # order_id is required on fix.work.order, so the device is reachable
        device = self.sudo().order_id.device_id
        device_type = device.device_type or None
        brand = device.device_model_id.brand_id if device and device.device_model_id else None
        eligible, reason = self.env["fix.certification"].dispatch_eligibility(
            tech,
            device_type=device_type,
            brand_id=brand,
            repair_tier=self.repair_tier or None,
            fail_closed=True,
        )
        return None if eligible else reason

    def action_check_certification(self):
        # Every record is checked (the loop used to return after the first
        # one, waving the rest of a multi-record call through).
        for rec in self:
            reason = rec._fix_certification_problem()
            if reason:
                raise UserError("M22 eligibility: assignment blocked — %s" % reason)
        return True

    def _fix_assert_may_start(self):
        """A job starts only while its technician is still eligible: a
        certification that lapsed, was suspended or revoked after the
        assignment stops the work from starting (FR-LMS-013)."""
        for rec in self:
            reason = rec._fix_certification_problem()
            if reason:
                raise UserError(
                    "M22 eligibility: work on %s cannot start — %s" % (rec.display_name, reason)
                )
        return True

    def _fix_flag_certification_lost(self, certification, event_type):
        """Consumer side: tell a dispatcher that a not-started job's
        technician lost the certification it needs. The job is not changed;
        starting it is refused until it is reassigned or waived."""
        flagged = self.browse()
        for rec in self.sudo():
            if rec.state not in WORK_ORDER_OPEN or not rec.technician_id:
                continue
            reason = rec._fix_certification_problem()
            if not reason:
                continue
            users = group_users(self.env, DISPATCHER, rec.company_id) or rec.create_uid
            summary = "Reassign %s: certification %s" % (
                rec.display_name,
                event_type.split(".")[-1],
            )
            for user in users[:1]:
                if open_activity_once(
                    rec,
                    user,
                    summary,
                    "%s (%s) no longer qualifies for this job: %s. Reassign it or request "
                    "a certification waiver before work starts."
                    % (rec.technician_id.name, certification.display_name, reason),
                ):
                    flagged |= rec
        return flagged

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.technician_id:
                rec.action_check_certification()
        return records

    def action_request_certification_waiver(self, technician_id=None, reason=None, waiver=None):
        """Ask the Certification Override Approver to let one uncertified
        technician take this job (BRU-LMS-02). ``waiver`` is the workspace
        prompt's one string: "<employee id> <reason>"."""
        self.ensure_one()
        if waiver not in (None, "", False):
            head, _sep, tail = str(waiver).strip().partition(" ")
            technician_id, reason = head, tail
        technician = self.technician_id
        if technician_id:
            try:
                technician = self.env["hr.employee"].sudo().browse(int(technician_id)).exists()
            except (TypeError, ValueError):
                raise UserError("Name the technician by their employee id.") from None
        self.check_access("write")
        req = self.env["fix.certification.waiver"]._fix_request_for(
            "fix.work.order", self.id, technician, reason
        )
        return {"waiver_id": req.id}

    def write(self, vals):
        result = super().write(vals)
        if vals.get("technician_id"):
            if "certification_waiver" not in vals:
                # A waiver covers one technician on one job: a new technician
                # loses it unless the approved waiver names them.
                stale = self.filtered(
                    lambda r: (
                        r.certification_waiver
                        and r.certification_waiver_id.sudo().employee_id != r.technician_id
                    )
                )
                if stale:
                    stale._guarded().write(
                        {
                            "certification_waiver": False,
                            "certification_waiver_reason": False,
                            "certification_waiver_id": False,
                        }
                    )
            for rec in self:
                rec.action_check_certification()
        elif "repair_tier" in vals:
            self.filtered("technician_id").action_check_certification()
        if vals.get("state") == "in_progress":
            self._fix_assert_may_start()
        return result
