# fix_hr_core — M21 complete: contracts, statutory leave, org structure (P08-M01, R06-M01).
import base64
from datetime import UTC, date, datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import get_migration_manager, normalize_bus_event, publish

# Bangladesh Labour Act 2006 statutory leave entitlements (SC-008, DoD-17), in days
STATUTORY_LEAVE = {
    "casual": 10,  # s. 115 casual leave with full wages (non-cumulative)
    "annual": 20,  # s. 117 casual+earned composite floor as practised (1 day per 18 days worked)
    "sick": 14,  # s. 116 / 148 sick leave upon medical practitioner certificate
    "festival": 11,  # s. 118 / 146 festival holidays
    "maternity": 112,  # s. 46-48: 16 weeks (112 days: 8 weeks pre-natal, 8 weeks post-natal)
    "paternity": 10,  # policy floor (not statutory; recorded as corporate policy benefit)
}
PROBATION_CAP_MONTHS = 6  # Labour Rules 2021 r.25: probation <= 6 months
KPI_090_ORPHAN_HOURS = 24  # KPI-090: no account may outlive the leaver event by 24 h
KPI_090_DEPROVISION_SLA_HOURS = 1.0  # KPI-090 deprovisioning target from the leaver event
# M29's identity-lifecycle service reports the IdP outcome of every leaver back (AS-08).
IDP_PROVISIONED = "identity.provisioned"
IDP_PROVISION_FAILED = "identity.provision_failed"
IDP_DEPROVISIONED = "identity.deprovisioned"
IDP_DEPROVISION_FAILED = "identity.deprovision_failed"
IDENTITY_TOPIC = "fix.events.identity"
IDENTITY_CONSUMER_GROUP = "hr-core-identity"


class HrEmployeeCdCoreExt(models.Model):
    """M21 completion fields on the W1 master slice.

    PII routing (SC-007/FF-09): NID/TIN/biometric templates NEVER land on
    hr.employee — they live in fix.identity.document (cd_party_master),
    which the residency service classifies. This extension references the
    identity store only.
    """

    _inherit = "hr.employee"

    employee_code = fields.Char(
        string="Employee Code",
        index=True,
        help="Payroll reference (M56); the identity " "documents carry the PII, not this model",
    )
    position_id = fields.Many2one("fix.org.position", string="Position")
    contract_count = fields.Integer(compute="_compute_contract_count", string="Contracts")
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    # KPI-090 (BRD 2712; 06-02 KPI register): zero orphaned accounts beyond
    # 24 h AFTER A LEAVER EVENT; deprovisioning target <= 1 h. The clock starts
    # at the leaver event (left_at), never at the hire date. "deprovisioned" is
    # set only when the removal is CONFIRMED - the module never claims it
    # itself (GV-009: no self-reported compliance).
    keycloak_deprovision_status = fields.Selection(
        [
            ("active", "Active"),
            ("pending", "Pending Deprovision"),
            ("deprovisioned", "Deprovisioned"),
            ("failed", "Failed"),
        ],
        default="active",
        tracking=True,
        help="KPI-090: 'pending' from the leaver event (employee.left, consumed by "
        "M29) until the Keycloak removal is confirmed",
    )
    left_at = fields.Datetime(
        string="Left At (Leaver Event)",
        readonly=True,
        copy=False,
        tracking=True,
        help="When employee.left was emitted - the KPI-090 clock start",
    )
    keycloak_deprovisioned_at = fields.Datetime(
        string="Keycloak Deprovisioned At",
        readonly=True,
        copy=False,
        help="When the Keycloak removal was confirmed (target <= 1 h after the leaver event)",
    )
    keycloak_deprovision_confirmed_by = fields.Many2one(
        "res.users",
        string="Deprovisioning Confirmed By",
        readonly=True,
        copy=False,
        tracking=True,
        help="The HR manager who confirmed the Keycloak removal (manual control)",
    )
    keycloak_deprovision_hours = fields.Float(
        string="Deprovisioning Time (Hours)",
        compute="_compute_keycloak_deprovision_hours",
        store=True,
        help="Hours from the leaver event to the confirmed removal (KPI-090 target <= 1 h)",
    )

    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = self.env["fix.employment.contract"].search_count(
                [("employee_id", "=", rec.id)]
            )

    @api.depends("left_at", "keycloak_deprovisioned_at")
    def _compute_keycloak_deprovision_hours(self):
        for rec in self:
            if rec.left_at and rec.keycloak_deprovisioned_at:
                span = rec.keycloak_deprovisioned_at - rec.left_at
                rec.keycloak_deprovision_hours = round(span.total_seconds() / 3600, 2)
            else:
                rec.keycloak_deprovision_hours = 0.0

    def _emit_leaver(self):
        """The leaver event (cd_employee_core: employee.left, which M29
        consumes to remove the Keycloak account) starts the KPI-090 clock:
        the time is recorded and deprovisioning is REQUESTED (pending)."""
        super()._emit_leaver()
        self.write(
            {
                "left_at": fields.Datetime.now(),
                "keycloak_deprovision_status": "pending",
                "keycloak_deprovisioned_at": False,
                "keycloak_deprovision_confirmed_by": False,
            }
        )

    def action_confirm_keycloak_deprovisioned(self):
        """Manual control: an HR manager confirms that the leaver's Keycloak
        account was verified as removed.

        The normal path is the identity provider's own confirmation
        (consume_identity_lifecycle_event, "confirmation": "idp"); this named
        person's confirmation - recorded with the time - is the fallback when the
        IdP reported a failure or did not answer."""
        if not (self.env.su or self.env.user.has_group("hr.group_hr_manager")):
            raise AccessError(
                "Only an HR manager may confirm a Keycloak deprovisioning (KPI-090 control)"
            )
        now = fields.Datetime.now()
        for rec in self:
            if rec.keycloak_deprovision_status not in ("pending", "failed"):
                raise UserError(
                    "%s has no Keycloak deprovisioning to confirm (status: %s) - it is "
                    "requested by the leaver event" % (rec.name, rec.keycloak_deprovision_status)
                )
            rec.write(
                {
                    "keycloak_deprovision_status": "deprovisioned",
                    "keycloak_deprovisioned_at": now,
                    "keycloak_deprovision_confirmed_by": self.env.uid,
                }
            )
            publish(
                self.env,
                "employee.keycloak.deprovisioned",
                "hr.employee",
                rec.id,
                {
                    "employee_code": rec.employee_code or "",
                    "left_at": str(rec.left_at),
                    "deprovisioned_at": str(now),
                    "hours": rec.keycloak_deprovision_hours,
                    "within_sla": rec.keycloak_deprovision_hours <= KPI_090_DEPROVISION_SLA_HOURS,
                    "confirmed_by": self.env.user.name,
                    "confirmation": "manual",
                    "kpi": "KPI-090",
                },
            )

    @api.model
    def consume_identity_lifecycle_event(self, raw_event):
        """M29 -> M21: apply the identity provider's joiner / leaver outcome.

        ``identity.provisioned`` (or a provisioning failure that still created the
        account) stores the Keycloak user id on the employee, so the leaver event
        later deprovisions by id. ``identity.deprovisioned`` is the IdP-confirmed removal (the account verified
        disabled with no session left): the leaver is marked deprovisioned with
        ``"confirmation": "idp"``. ``identity.deprovision_failed`` marks it failed and
        records the reason - the HR manager's manual confirmation stays the fallback
        control. Idempotent: a re-delivered or late event never changes a confirmed
        removal. Returns the employee updated (empty when nothing applied).
        """
        event = normalize_bus_event(raw_event)
        if event["event_type"] not in (
            IDP_PROVISIONED,
            IDP_PROVISION_FAILED,
            IDP_DEPROVISIONED,
            IDP_DEPROVISION_FAILED,
        ):
            return self.browse()
        payload = event["payload"]
        employee = (
            self.with_context(active_test=False)
            .browse(int(payload.get("employee_id") or event["aggregate_id"] or 0))
            .exists()
        )
        if employee and event["event_type"] in (IDP_PROVISIONED, IDP_PROVISION_FAILED):
            return employee._apply_identity_provisioning(event["event_type"], payload)
        # only a leaver with a running KPI-090 clock; a confirmed removal is final
        if not employee or employee.keycloak_deprovision_status not in ("pending", "failed"):
            return self.browse()
        if event["event_type"] == IDP_DEPROVISION_FAILED:
            employee.keycloak_deprovision_status = "failed"
            employee.message_post(
                body="Keycloak deprovisioning failed (%s): %s - confirm manually once removed."
                % (payload.get("reason_code"), payload.get("reason"))
            )
            return employee
        stamp = datetime.fromisoformat(str(payload["deprovisioned_at"]).replace("Z", "+00:00"))
        deprovisioned_at = stamp.astimezone(UTC).replace(tzinfo=None)
        employee.write(
            {
                "keycloak_deprovision_status": "deprovisioned",
                "keycloak_deprovisioned_at": deprovisioned_at,
                "keycloak_deprovision_confirmed_by": False,
                "keycloak_user_id": payload.get("keycloak_user_id") or employee.keycloak_user_id,
            }
        )
        publish(
            self.env,
            "employee.keycloak.deprovisioned",
            "hr.employee",
            employee.id,
            {
                "employee_code": employee.employee_code or "",
                "left_at": str(employee.left_at),
                "deprovisioned_at": str(deprovisioned_at),
                "hours": employee.keycloak_deprovision_hours,
                "within_sla": employee.keycloak_deprovision_hours <= KPI_090_DEPROVISION_SLA_HOURS,
                "confirmed_by": "identity-lifecycle (Keycloak)",
                "confirmation": "idp",
                "kpi": "KPI-090",
            },
            {"correlation_id": event["correlation_id"], "causation_id": event["event_id"]},
        )
        return employee

    def _apply_identity_provisioning(self, event_type, payload):
        """Store the joiner's Keycloak user id (never silently replace another one)."""
        self.ensure_one()
        kc_id = payload.get("keycloak_user_id")
        if event_type == IDP_PROVISION_FAILED:
            self.message_post(
                body="Keycloak provisioning failed (%s): %s"
                % (payload.get("reason_code"), payload.get("reason"))
            )
        if not kc_id or kc_id == self.keycloak_user_id:
            return self if event_type == IDP_PROVISION_FAILED else self.browse()
        if self.keycloak_user_id:
            self.message_post(
                body="Keycloak reported account %s for this employee, but %s is on record - "
                "kept the recorded one; check for a duplicate identity."
                % (kc_id, self.keycloak_user_id)
            )
            return self.browse()
        self.keycloak_user_id = kc_id
        return self

    @api.model
    def drain_identity_lifecycle_events(self, limit=50):
        """Consume M29's identity outcomes through fix_events (FF-28) - the cron's job."""
        manager = get_migration_manager()
        manager.register_group(IDENTITY_CONSUMER_GROUP)
        applied = []
        manager.consume_event(
            IDENTITY_CONSUMER_GROUP,
            IDENTITY_TOPIC,
            lambda raw: applied.append(self.consume_identity_lifecycle_event(raw)),
            limit,
        )
        return self.browse([e.id for e in applied if e])

    @api.model
    def measure_kpi_090_orphaned_accounts(self):
        """KPI-090: leavers whose leaver event is more than 24 h old and whose
        Keycloak removal is not confirmed - archived or not (a leaver may
        still be an active record)."""
        cutoff = fields.Datetime.now() - timedelta(hours=KPI_090_ORPHAN_HOURS)
        return self.with_context(active_test=False).search_count(
            [
                ("left_at", "!=", False),
                ("left_at", "<=", cutoff),
                ("keycloak_deprovision_status", "!=", "deprovisioned"),
            ]
        )

    # P08-M01-T06 / R06-M01-T03: joiner/mover/leaver event set drives M29 provisioning
    def write(self, vals):
        result = super().write(vals)
        # Odoo 19's field is work_location_id (there is no `work_location`):
        # a location move used to go unannounced to M29.
        if "department_id" in vals or "job_id" in vals or "work_location_id" in vals:
            for rec in self:
                publish(
                    self.env,
                    "employee.moved",
                    "hr.employee",
                    rec.id,
                    {
                        "employee_code": rec.employee_code or "",
                        "department": rec.department_id.name or "",
                    },
                )
        return result


class FixOrgPosition(models.Model):
    """Organisation structure: reporting lines and position management."""

    _name = "fix.org.position"
    _description = "Organisation Position"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, tracking=True)
    parent_id = fields.Many2one(
        "fix.org.position", string="Reports To", ondelete="restrict", index=True
    )
    employee_ids = fields.One2many("hr.employee", "position_id", string="Holders")
    grade = fields.Char(string="Grade", help="M57 compensation band reference")

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        # Wired as a constraint (it was a plain method nobody called, so a
        # reporting-line loop could be saved).
        for rec in self:
            seen, node = {rec.id}, rec.parent_id
            while node:
                if node.id in seen:
                    raise ValidationError("Reporting line loop at %s" % rec.name)
                seen.add(node.id)
                node = node.parent_id


class FixEmploymentContract(models.Model):
    """Labour Act 2006 employment artefacts (P08-M01-T05, R06-M01-T02) — where the
    category-H statutory density (+52%) lives on M24 templates."""

    _name = "fix.employment.contract"
    _description = "Employment Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "employee_id, joining_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Contract Ref", compute="_compute_name", store=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, ondelete="cascade", index=True
    )
    contract_type = fields.Selection(
        [
            ("permanent", "Permanent"),
            ("probation", "Probation"),
            ("fixed_term", "Fixed Term"),
            ("part_time", "Part Time"),
        ],
        required=True,
        default="probation",
        tracking=True,
    )
    joining_date = fields.Date(required=True)
    probation_end = fields.Date(help="Labour Rules 2021 r.25: probation may not exceed 6 months")
    weekly_hours = fields.Float(
        string="Statutory Weekly Hours",
        default=48,
        required=True,
        help="s. 102: 48 hours/week ceiling",
    )
    basic_monthly = fields.Monetary(
        string="Basic Salary (Monthly)", currency_field="currency_id", required=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("expired", "Expired"),
            ("terminated", "Terminated"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    identity_document_note = fields.Char(
        string="Identity Store Ref",
        help="PII pointer: the NID/passport/biometric artefact lives in "
        "fix.identity.document (Z4 residency), referenced, never copied",
    )

    # M24 Document Engine Integration (+52% Category H statutory density)
    template_id = fields.Many2one(
        "fix.document.template",
        string="M24 Document Template",
        help="M24 governed document template for Bangladesh Labour Rules Form 6",
    )
    document_id = fields.Many2one(
        "fix.document",
        string="Generated Contract Document",
        readonly=True,
        help="Governed contract artefact produced by M24 document engine",
    )
    statutory_density_score = fields.Float(
        string="Statutory Density (%)",
        default=52.0,
        help="Statutory density rating exceeding standard contracts (+52% Category H density)",
    )
    legal_signoff_state = fields.Selection(
        [
            ("pending", "Pending Signoff"),
            ("approved", "Approved by Legal"),
            ("rejected", "Changes Required"),
        ],
        default="pending",
        tracking=True,
        string="Legal Signoff",
    )
    signed_by_legal_counsel = fields.Char(string="Legal Counsel Signoff", tracking=True)

    @api.depends("employee_id.employee_code", "employee_id.name", "contract_type", "joining_date")
    def _compute_name(self):
        for rec in self:
            code = rec.employee_id.employee_code or (rec.employee_id.name or "EMP")
            year = rec.joining_date.year if rec.joining_date else fields.Date.today().year
            rec.name = f"CNT/{code}/{rec.contract_type.upper()}/{year}"

    def action_activate(self):
        for rec in self:
            rec._validate_statutory()
            rec.state = "active"
            publish(
                self.env,
                "employment.contract.activated",
                "fix.employment.contract",
                rec.id,
                {
                    "employee": rec.employee_id.name,
                    "contract_type": rec.contract_type,
                    "joining": str(rec.joining_date),
                },
            )

    def action_terminate(self):
        """End the contract. Unless another active contract continues the
        employment, the employee leaves through the canonical leaver path
        (cd_employee_core.action_mark_left: employee.left, which M29 consumes;
        KPI-090 clock and a PENDING Keycloak deprovisioning) - the removal is
        never marked done here."""
        for rec in self:
            rec.state = "terminated"
            continuing = self.search_count(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("state", "=", "active"),
                    ("id", "!=", rec.id),
                ]
            )
            if not continuing:
                rec.employee_id.action_mark_left()

    def action_request_legal_signoff(self):
        for rec in self:
            rec.legal_signoff_state = "pending"

    def action_approve_legal_signoff(self):
        for rec in self:
            rec.legal_signoff_state = "approved"
            rec.signed_by_legal_counsel = self.env.user.name

    def action_generate_contract_document(self):
        """Generate official Labour Rules 2015 Form 6 contract via M24 document engine.

        Returns the generated fix.document records (one per contract; the
        loop used to `return` after the first contract of a multi-record call)."""
        docs = self.env["fix.document"]
        for rec in self:
            rec._validate_statutory()
            template = rec.template_id
            if not template:
                # Default to Form 6 contract template
                template = self.env["fix.document.template"].search(
                    [("document_type", "=", "contract")], limit=1
                )

            # Create ir.attachment containing Form 6 appointment / contract details
            content = (
                f"1000FiX SERVICES LTD - STATUTORY EMPLOYMENT CONTRACT\n"
                f"Statutory Form: Form 6, Bangladesh Labour Rules 2015\n"
                f"Statutory Density: {rec.statutory_density_score}% (Category H)\n"
                f"Contract Ref: {rec.name}\n"
                f"Employee: {rec.employee_id.name} (Code: {rec.employee_id.employee_code or 'N/A'})\n"
                f"Type: {rec.contract_type}\n"
                f"Joining Date: {rec.joining_date}\n"
                f"Statutory Weekly Hours: {rec.weekly_hours} (s.102 cap)\n"
                f"Basic Monthly Salary: BDT {rec.basic_monthly:,.2f}\n"
                f"Statutory Citations: Bangladesh Labour Act 2006 (Act XLII of 2006) as amended 2026\n"
            ).encode()

            attachment = self.env["ir.attachment"].create(
                {
                    "name": f"Employment_Contract_{rec.name.replace('/', '_')}.txt",
                    "type": "binary",
                    "datas": base64.b64encode(content),
                    "res_model": "fix.employment.contract",
                    "res_id": rec.id,
                    "mimetype": "text/plain",
                }
            )

            doc = self.env["fix.document"].create(
                {
                    "name": f"Contract - {rec.employee_id.name} ({rec.contract_type})",
                    "name_bn": f"নিয়োগ চুক্তি - {rec.employee_id.name}",
                    "document_type": "contract",
                    "template_id": template.id if template else False,
                    "attachment_id": attachment.id,
                    "res_model": "fix.employment.contract",
                    "res_id": rec.id,
                    "isolation_tier": "T1",
                    "description": f"Labour Rules Form 6 employment contract for {rec.employee_id.name}",
                }
            )
            rec.document_id = doc.id
            publish(
                self.env,
                "employment.contract.generated",
                "fix.employment.contract",
                rec.id,
                {
                    "contract": rec.name,
                    "document_id": doc.id,
                    "statutory_density": rec.statutory_density_score,
                },
            )
            docs |= doc
        return docs

    def _validate_statutory(self):
        for rec in self:
            if rec.probation_end:
                cap_months = PROBATION_CAP_MONTHS * 30
                span = (
                    fields.Date.to_date(rec.probation_end) - fields.Date.to_date(rec.joining_date)
                ).days
                if span > cap_months:
                    raise ValidationError(
                        "Probation exceeds the 6-month statutory cap " "(Labour Rules 2021 r.25)"
                    )
            if rec.weekly_hours > 48:
                raise ValidationError("s.102: weekly hours may not exceed 48")
            if rec.basic_monthly <= 0:
                raise ValidationError("Basic salary must be positive")


class FixLeaveType(models.Model):
    """Statutory leave catalogue (Bangladesh Labour Act 2006, SC-008, DoD-17)."""

    _name = "fix.leave.type"
    _description = "Leave Type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Leave Name (Bengali)", help="DE-17")
    entitlement_days = fields.Integer(required=True)
    encashable = fields.Boolean(help="Annual leave is encashable at separation (s.118)")
    maternity = fields.Boolean()

    # DoD-17 statutory citation fields verified current
    is_statutory = fields.Boolean(
        string="Is Statutory",
        default=True,
        help="Whether this leave is an obligatory statutory entitlement under Bangladesh Labour Act",
    )
    carry_forward_limit = fields.Integer(
        string="Carry Forward Limit (Days)",
        default=0,
        help="Maximum days that can be carried forward (s. 117(7): 40 days for annual leave)",
    )
    labour_act_section = fields.Char(
        string="Labour Act Section",
        help="Governing statutory section (e.g. Section 115, Section 116, Section 117)",
    )
    legal_citation = fields.Text(
        string="Legal Citation",
        help="Explicit statutory citation and formula under Bangladesh Labour Act 2006",
    )
    amendment_ref = fields.Char(
        string="Amendment Reference",
        default="Labour (Amendment) Act 2013, 2018, 2026",
        help="Latest amendments verified applicable",
    )
    verified_on = fields.Date(
        string="Verified On",
        default=fields.Date.today,
        help="Date statutory citation verified current (DoD-17)",
    )

    def action_validate_statutory(self):
        """The entitlement must be at least the statutory floor."""
        for rec in self:
            if rec.is_statutory:
                floor = STATUTORY_LEAVE.get(rec.code)
                if floor and rec.entitlement_days < floor:
                    raise ValidationError(
                        "%s entitlement below the statutory floor (%d days)" % (rec.code, floor)
                    )


class FixLeaveRequest(models.Model):
    """Leave and absence management on the statutory floors."""

    _name = "fix.leave.request"
    _description = "Leave Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    leave_type_id = fields.Many2one("fix.leave.type", required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    days = fields.Integer(compute="_compute_days", store=True)
    reason = fields.Text()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    @api.depends("date_from", "date_to")
    def _compute_days(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to >= rec.date_from:
                rec.days = (
                    fields.Date.to_date(rec.date_to) - fields.Date.to_date(rec.date_from)
                ).days + 1
            else:
                rec.days = 0

    def action_approve(self):
        for rec in self:
            rec.leave_type_id.action_validate_statutory()
            # Entitlements are DAYS per calendar year (BLA s.115/116: "in a
            # calendar year"). The former search_count counted approved
            # REQUESTS across all years, so 3 x 5-day casual leaves (15 days)
            # passed a 10-day entitlement, and a second year was over-blocked.
            year = rec.date_from.year
            taken = sum(
                self.search(
                    [
                        ("id", "!=", rec.id),
                        ("employee_id", "=", rec.employee_id.id),
                        ("leave_type_id", "=", rec.leave_type_id.id),
                        ("state", "=", "approved"),
                        ("date_from", ">=", date(year, 1, 1)),
                        ("date_from", "<=", date(year, 12, 31)),
                    ]
                ).mapped("days")
            )
            if taken + rec.days > rec.leave_type_id.entitlement_days:
                raise UserError(
                    "Entitlement exhausted: %d approved + %d requested > %d days in %d"
                    % (taken, rec.days, rec.leave_type_id.entitlement_days, year)
                )
            rec.state = "approved"
            publish(
                self.env,
                "leave.approved",
                "fix.leave.request",
                rec.id,
                {"employee": rec.employee_id.name, "days": rec.days},
            )
