# cd_hr_core — employee master controls (A09 workflow audit M21-1, M21-9,
# M21-10, M21-13, M21-14; P2 "master data"; C3 access revocation).
#
#   * formats: NID 10/13/17 digits, birth registration 17, e-TIN 12, BEFTN
#     routing 9, MFS 01[3-9]XXXXXXXX, bank account 6-20 digits; one NID and one
#     e-TIN per person; an employee code is unique and permanent;
#   * once an employee is under an active contract (on the payroll), the
#     salary channel, identity numbers, pay figures and overtime eligibility
#     are never written directly: a bank or identity change is a routed
#     fix.hr.master.change (maker-checker, FR-HCM-042); pay changes are a
#     movement or a contract version;
#   * dossier flags are computed from documents a second person verified;
#     the PSR is verified by someone other than whoever recorded it;
#   * employee.left is consumed in Odoo: the leaver's Odoo login is archived
#     and its sessions revoked (M29's Keycloak removal is confirmed separately
#     through identity.deprovisioned).
import base64
import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_hr_controls_common import (
    BANK_ACCOUNT_RE,
    MFS_RE,
    NID_RE,
    OFFICER,
    ROUTING_RE,
    TIN_RE,
    digest,
)
from .fix_hr_identity_residency import IDENTITY

_logger = logging.getLogger(__name__)

BANK_FIELDS = (
    "bank_name",
    "bank_branch_name",
    "routing_number",
    "bank_account_number",
    "bank_account_ids",
    "mfs_provider",
    "mfs_account_number",
)
IDENTITY_FIELDS = ("nid_number", "tin_number")
PAY_FIELDS = (
    "wage",
    "basic_wage",
    "house_rent",
    "medical_allowance",
    "conveyance_allowance",
    "technical_allowance",
    "overtime_eligible",
)
SENSITIVE_FIELDS = set(BANK_FIELDS) | set(IDENTITY_FIELDS) | set(PAY_FIELDS)
# FR-HCM-042 applied only to employees with an ACTIVE contract: an officer
# could overwrite the salary account of every employee without one (all 504
# imported ones), and payroll paid it once a contract started (M21 audit F4).
# A first capture is typed on the form; changing a recorded value is a routed
# Employee Master Change, contract or not.
GATED_CHANNELS = tuple(n for n in (*BANK_FIELDS, *IDENTITY_FIELDS) if n != "bank_account_ids")
# NID, birth registration and e-TIN are checked by their inverse, before the
# value is routed to the resident store (fix_hr_identity_residency.py).
FORMATS = (
    ("routing_number", ROUTING_RE, "BEFTN routing number (9 digits)"),
    ("mfs_account_number", MFS_RE, "MFS wallet number (01XXXXXXXXX)"),
    ("bank_account_number", BANK_ACCOUNT_RE, "Bank account number (6-20 digits)"),
)
# fix.hr.document type -> the dossier flag it evidences
DOSSIER = {
    "doc_nid_verified": "nid_smart",
    "doc_tin_verified": "tin_cert",
    "doc_psr_verified": "tax_psr",
    "doc_appointment_signed": "appointment",
    "doc_nda_signed": "nda",
    "customer_nda_signed": "nda",
    "doc_service_book_scanned": "service_book",
    "doc_medical_fit_certified": "medical_fit",
    "doc_police_pcc_cleared": "police_pcc",
}


class HrEmployeeMasterControls(models.Model):
    _inherit = "hr.employee"

    psr_submitted_by_id = fields.Many2one(
        "res.users", string="PSR Recorded By", readonly=True, copy=False, groups="hr.group_hr_user"
    )
    psr_verified_by_id = fields.Many2one(
        "res.users", string="PSR Verified By", readonly=True, copy=False, groups="hr.group_hr_user"
    )
    odoo_access_revoked_at = fields.Datetime(
        string="Odoo Access Revoked At",
        readonly=True,
        copy=False,
        help="When the employee.left consumer archived the leaver's Odoo login",
    )

    # ---- computed evidence flags (M21-10) ------------------------------------
    @api.depends("document_ids.doc_type", "document_ids.verified", "document_ids.acknowledged")
    def _compute_dossier_flags(self):
        for rec in self:
            docs = rec.document_ids.filtered("verified")
            for flag, doc_type in DOSSIER.items():
                found = docs.filtered(lambda d, t=doc_type: d.doc_type == t)
                if doc_type == "appointment":
                    found = found.filtered("acknowledged")
                rec[flag] = bool(found)

    @api.depends("education_line_ids.is_verified")
    def _compute_academic_verified(self):
        for rec in self:
            states = set(rec.education_line_ids.mapped("is_verified"))
            for value in ("discrepancy", "verified_physical", "verified_online"):
                if value in states:
                    rec.academic_verified = value
                    break
            else:
                rec.academic_verified = "pending"

    @api.depends("experience_line_ids.reference_status")
    def _compute_prev_reference_status(self):
        for rec in self:
            states = set(rec.experience_line_ids.mapped("reference_status")) - {False}
            for value in ("negative_flag", "verified_neutral", "verified_positive", "unreachable"):
                if value in states:
                    rec.prev_reference_status = value
                    break
            else:
                rec.prev_reference_status = False

    def _compute_employment_status(self):
        super()._compute_employment_status()
        ids = [i for i in self.ids if isinstance(i, int)]
        if not ids:
            return
        serving = (
            self.env["fix.hr.exit"]
            .sudo()
            .search([("employee_id", "in", ids), ("state", "in", ("notice", "cleared"))])
            .mapped("employee_id")
        )
        for rec in self:
            if rec in serving and rec.employment_status == "active":
                rec.employment_status = "notice_period"

    @api.model
    def _fix_recompute_evidence_flags(self):
        """Upgrade step: the dossier and verification flags became computed;
        rows saved before still carry the old typed (defaulted True) values.
        Idempotent; superuser only (run from the module's data file)."""
        if not self.env.su:
            raise AccessError("Run by the module upgrade only.")
        employees = self.with_context(active_test=False).search([])
        names = [*DOSSIER, "academic_verified", "prev_reference_status"]
        for name in names:
            self.env.add_to_compute(self._fields[name], employees)
        self.env.flush_all()
        return len(employees)

    # ---- formats and duplicates (P2 master data) -----------------------------
    @api.constrains(*[f for f, _r, _l in FORMATS])
    def _check_identifier_formats(self):
        for rec in self.sudo():
            for name, pattern, label in FORMATS:
                value = rec[name]
                if value and not pattern.match(value.strip()):
                    raise ValidationError("%s: %r is not valid." % (label, value))

    @api.constrains("employee_code", "company_id")
    def _check_unique_identifiers(self):
        # One NID / e-TIN per person is checked through their keyed hash
        # (fix_hr_identity_residency.py): the values are not in this database.
        Employee = self.sudo().with_context(active_test=False)
        for rec in self.sudo():
            code = (rec.employee_code or "").strip()
            if code and Employee.search_count(
                [
                    ("employee_code", "=", code),
                    ("company_id", "=", rec.company_id.id),
                    ("id", "!=", rec.id),
                ]
            ):
                raise ValidationError("Employee code %s is already in use." % code)

    # ---- the master write gate (M21-1) -----------------------------------------
    def _fix_under_contract(self):
        """Employees of this set on the payroll (an active contract)."""
        if not self.ids:
            return self.browse()
        contracts = (
            self.env["fix.employment.contract"]
            .sudo()
            .search([("employee_id", "in", self.ids), ("state", "=", "active")])
        )
        return contracts.mapped("employee_id")

    def _fix_recorded_channel(self, name):
        """Is a bank/MFS/identity value already on record (no value read for
        an identifier: its hash says whether one is held)?"""
        self.ensure_one()
        srec = self.sudo()
        if name in IDENTITY:
            hash_field = self._fix_identity_fields[name][2]
            return bool(srec[hash_field] or self._fix_identity_legacy_value(name))
        return bool(srec[name])

    def _fix_form_locked_fields(self) -> set:
        """The form offers an input only where the server accepts a change."""
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and isinstance(self.id, int):
            locked |= {n for n in GATED_CHANNELS if self._fix_recorded_channel(n)}
            if self._fix_under_contract():
                locked |= SENSITIVE_FIELDS
            if self.sudo().employee_code:
                locked.add("employee_code")
        return locked

    def write(self, vals):
        if self.ids and not self._fix_guard_open():
            real = self.filtered("id")
            if "employee_code" in vals:
                for rec in real.sudo():
                    old = (rec.employee_code or "").strip()
                    if old and (vals["employee_code"] or "").strip() != old:
                        raise UserError(
                            "Employee code %s is permanent (FR-HCM-003); it is never "
                            "rewritten." % old
                        )
            gated = set(GATED_CHANNELS) & set(vals)
            if gated:
                for rec in real - real._fix_under_contract():
                    changed = [
                        n
                        for n in gated
                        if rec._fix_recorded_channel(n)
                        and (
                            not rec._fix_identity_unchanged(n, vals[n])
                            if n in IDENTITY
                            else rec.sudo()._fix_guard_differs(n, vals[n], rec.sudo()[n])
                        )
                    ]
                    if changed:
                        labels = ", ".join(sorted(self._fields[n].string for n in changed))
                        raise UserError(
                            "%s: %s is already recorded and changes only through an approved "
                            "Employee Master Change (maker-checker, FR-HCM-042)."
                            % (rec.name, labels)
                        )
            touched = SENSITIVE_FIELDS & set(vals)
            if touched:
                for rec in real._fix_under_contract():
                    changed = [
                        n
                        for n in touched
                        if (
                            not rec._fix_identity_unchanged(n, vals[n])
                            if n in IDENTITY
                            else rec.sudo()._fix_guard_differs(n, vals[n], rec.sudo()[n])
                        )
                    ]
                    if not changed:
                        continue
                    labels = ", ".join(sorted(self._fields[n].string for n in changed))
                    if set(changed) & set(PAY_FIELDS):
                        raise UserError(
                            "%s is on the payroll: %s change only through an approved "
                            "Transfer / Promotion or a new contract version." % (rec.name, labels)
                        )
                    raise UserError(
                        "%s is on the payroll: %s change only through an approved Employee "
                        "Master Change (maker-checker)." % (rec.name, labels)
                    )
        return super().write(vals)

    # ---- PSR (ITA 2023 s.264) ----------------------------------------------------
    def _fix_hr_actor(self, what):
        if not (self.env.su or self.env.user.has_group(OFFICER)):
            raise AccessError("%s needs the HR Officer role." % what)
        for rec in self:
            if not self.env.su and rec.user_id == self.env.user:
                raise UserError("You cannot %s on your own record." % what.lower())

    def action_record_psr_submission(self):
        self._fix_hr_actor("Recording a PSR")
        for rec in self.sudo():
            if not (rec.psr_ack_number and rec.psr_tax_year):
                raise UserError("Enter the PSR acknowledgement number and assessment year.")
            rec._guarded().write(
                {
                    "psr_status": "submitted",
                    "psr_submitted_by_id": self.env.uid,
                    "psr_verified_on": False,
                    "psr_verified_by_id": False,
                }
            )
        return True

    def action_verify_psr(self):
        """A second HR person verifies the PSR against its evidence."""
        self._fix_hr_actor("Verifying a PSR")
        for rec in self.sudo():
            if rec.psr_status != "submitted":
                raise UserError("Record the PSR submission first.")
            if not self.env.su and rec.psr_submitted_by_id == self.env.user:
                raise UserError("The person who recorded the PSR cannot verify it.")
            evidence = rec.doc_psr_file or rec.document_ids.filtered(
                lambda d: d.doc_type == "tax_psr" and d.file_data
            )
            if not evidence:
                raise UserError("Attach the PSR acknowledgement before verifying it.")
            rec._guarded().write(
                {
                    "psr_status": "verified",
                    "psr_verified_on": fields.Date.context_today(self),
                    "psr_verified_by_id": self.env.uid,
                }
            )
        return True

    def action_mark_psr_exempt(self):
        self._fix_hr_actor("Marking a PSR exemption")
        self.sudo()._guarded().write({"psr_status": "exempt", "psr_verified_by_id": self.env.uid})
        return True

    # ---- ID card (FR-HCM-014) ----------------------------------------------------
    def action_generate_id_card(self):
        """An employee ID card entry (unverified until its signed copy is verified)."""
        self._fix_hr_actor("Issuing an ID card")
        docs = self.env["fix.hr.document"]
        today = fields.Date.context_today(self)
        for rec in self.sudo():
            text = (
                "1000FiX SERVICES LTD - EMPLOYEE ID CARD\n"
                f"Name: {rec.name}\nName (Bengali): {rec.name_bn or ''}\n"
                f"Employee Code: {rec.employee_code or ''}\n"
                f"Designation: {rec.job_title or (rec.position_id.name or '')}\n"
                f"Blood Group: {rec.blood_group or ''}\nIssued: {today}\n"
            ).encode()
            docs |= (
                self.env["fix.hr.document"]
                ._guarded()
                .create(
                    {
                        "employee_id": rec.id,
                        "company_id": rec.company_id.id,
                        "doc_type": "id_card",
                        "reference": "ID/%s" % (rec.employee_code or rec.id),
                        "issued_on": today,
                        "generated": True,
                        "file_name": "IDCard_%s.txt" % (rec.employee_code or rec.id),
                        "file_data": base64.b64encode(text),
                    }
                )
            )
        return {"documents": docs.ids}

    # ---- employee.left -> Odoo access revocation (C3) -------------------------
    @api.model
    def consume_employee_left(self, event):
        """Relay consumer of employee.left: archive the leaver's Odoo login and
        revoke its sessions. Idempotent; superuser only (the relay cron)."""
        if not self.env.su:
            raise AccessError("The leaver consumer runs from the event relay only.")
        payload = event.get("payload") or {}
        emp = (
            self.with_context(active_test=False)
            .browse(int(payload.get("employee_id") or event.get("aggregate_id") or 0))
            .exists()
        )
        if not emp or not emp.left_date or emp.odoo_access_revoked_at:
            return False
        user = emp.user_id
        protected = (self.env.ref("base.user_root"), self.env.ref("base.user_admin"))
        still_employed = (
            self.search_count(
                [("user_id", "=", user.id), ("id", "!=", emp.id), ("left_date", "=", False)]
            )
            if user
            else 0
        )
        revoked = False
        if user and user.active and user not in protected and not still_employed:
            try:
                with self.env.cr.savepoint():
                    user.device_ids._revoke()
            except Exception as exc:  # no session store in a cron: archiving still stops logins
                _logger.info("leaver %s: session revoke skipped (%s)", emp.id, exc)
            user.write({"active": False})
            revoked = True
        emp._guarded().write({"odoo_access_revoked_at": fields.Datetime.now()})
        emp.message_post(
            body="Leaver processed: Odoo login %s. Keycloak removal is confirmed by M29 "
            "(identity.deprovisioned) or by an HR manager."
            % (
                "archived and sessions revoked"
                if revoked
                else "not archived (none, shared or protected)"
            )
        )
        publish(
            self.env,
            "employee.access_revoked",
            "hr.employee",
            emp.id,
            {"employee_id": emp.id, "user_id": user.id or None, "odoo_login_archived": revoked},
        )
        return True

    # ---- employee.moved -> mover access review (C3) ---------------------------
    MOVER_REVIEW = "Mover access review"

    @api.model
    def consume_employee_moved(self, event):
        """Relay consumer of employee.moved (JML mover, A09 C3): a move of
        branch, position or band leaves the old access in place, so the move
        opens one access review for the IT clearance owner (or HR) to
        re-certify the login's groups and operating units. Nothing is changed
        automatically: which access the new role needs is a person's call.
        Idempotent: one open review per employee; superuser only."""
        if not self.env.su:
            raise AccessError("The mover consumer runs from the event relay only.")
        payload = event.get("payload") or {}
        emp_id = payload.get("employee_id")
        if not emp_id and event.get("aggregate") == "hr.employee":
            emp_id = event.get("aggregate_id")
        emp = self.with_context(active_test=False).browse(int(emp_id or 0)).exists()
        if not emp or emp.left_date or not emp.user_id or not emp.user_id.active:
            return False
        if emp.activity_ids.filtered(lambda a: a.summary == self.MOVER_REVIEW):
            return False
        moved = ", ".join(
            "%s %s -> %s" % (label, payload[f"from_{key}"], payload[f"to_{key}"])
            for key, label in (("branch", "branch"), ("position", "position"), ("tier", "tier"))
            if payload.get(f"from_{key}") != payload.get(f"to_{key}")
        )
        reviewers = (
            self.env.ref("cd_hr_core.group_clearance_it").all_user_ids
            or self.env.ref(OFFICER).all_user_ids
        ).filtered(lambda u: u.active and not u.share and u != emp.user_id)
        emp.activity_schedule(
            "mail.mail_activity_data_todo",
            summary=self.MOVER_REVIEW,
            note="%s moved (%s). Re-certify the login %s: its groups and operating "
            "units must fit the new role." % (emp.name, moved or "department", emp.user_id.login),
            user_id=(reviewers[:1] or self.env.ref("base.user_admin")).id,
        )
        return True

    # ---- employee.role_changed -> role access review (C3) ---------------------
    ROLE_REVIEW = "Role change access review"

    @api.model
    def consume_employee_role_changed(self, event):
        """Relay consumer of employee.role_changed (cd_employee_core publishes it
        when primary_role_id or additional_role_ids change).

        A role-to-group mapping exists as a field (fix.role.group_id) but is not
        ruled: no role of the reconciled register carries a group, and the link
        "is authored once the reconciled 05-04 register loads, never guessed"
        (cd_rbac_ext). So nothing is granted or removed automatically. One access
        review opens for the IT clearance owner (or HR), naming the roles, any
        group they map to and every SoD control the role set breaches. Idempotent:
        one open review per employee; superuser only (the relay cron)."""
        if not self.env.su:
            raise AccessError("The role-change consumer runs from the event relay only.")
        payload = event.get("payload") or {}
        emp_id = payload.get("employee_id")
        if not emp_id and event.get("aggregate") == "hr.employee":
            emp_id = event.get("aggregate_id")
        emp = self.with_context(active_test=False).browse(int(emp_id or 0)).exists()
        if not emp or emp.left_date or not emp.user_id or not emp.user_id.active:
            return False
        if emp.activity_ids.filtered(lambda a: a.summary == self.ROLE_REVIEW):
            return False
        roles = emp.primary_role_id | emp.additional_role_ids
        mapped = roles.filtered("group_id")
        conflicts = (
            self.env["fix.sod.control"]
            .sudo()
            .search(
                [
                    ("role_a_id", "in", roles.ids),
                    ("role_b_id", "in", roles.ids),
                    ("active", "=", True),
                ]
            )
            if roles and "fix.sod.control" in self.env
            else []
        )
        lines = [
            "%s's business roles changed: %s."
            % (emp.name, ", ".join("%s %s" % (r.code, r.name) for r in roles) or "none"),
            "Odoo groups these roles map to: %s."
            % (
                ", ".join("%s -> %s" % (r.code, r.group_id.display_name) for r in mapped)
                or "none (no role-to-group mapping is ruled)"
            ),
        ]
        if conflicts:
            lines.append(
                "SoD conflicts in this role set: %s."
                % "; ".join("%s %s (%s)" % (c.code, c.name, c.conflict_action) for c in conflicts)
            )
        lines.append(
            "Re-certify the login %s: its groups must fit the new roles and break no SoD "
            "control. Nothing was changed automatically." % emp.user_id.login
        )
        reviewers = (
            self.env.ref("cd_hr_core.group_clearance_it").all_user_ids
            or self.env.ref(OFFICER).all_user_ids
        ).filtered(lambda u: u.active and not u.share and u != emp.user_id)
        emp.activity_schedule(
            "mail.mail_activity_data_todo",
            summary=self.ROLE_REVIEW,
            note="\n".join(lines),
            user_id=(reviewers[:1] or self.env.ref("base.user_admin")).id,
        )
        return True


class ResPartnerBankEmployeeGuard(models.Model):
    """The salary account itself cannot be rewritten behind the master gate."""

    _inherit = "res.partner.bank"

    def write(self, vals):
        # the routing number decides where a BEFTN credit lands: it is part of
        # the salary account (E2E3 flow 9)
        guarded = {"acc_number", "bank_id", "partner_id", "fix_routing_number"}
        if not self.env.su and guarded & set(vals):
            employees = (
                self.env["hr.employee"]
                .sudo()
                .with_context(active_test=False)
                .search([("bank_account_ids", "in", self.ids)])
            )
            if employees._fix_under_contract():
                raise UserError(
                    "This is the salary account of an employee on the payroll: change it "
                    "through an approved Employee Master Change."
                )
        return super().write(vals)


class FixHrMasterChange(models.Model):
    """A sensitive master change: bank, MFS, NID, e-TIN, overtime eligibility.

    The maker (HR, or the employee for their own record) proposes; another HR
    officer decides from the approval inbox; the apply writes the master
    through the guard and logs which fields changed (never their values)."""

    _name = "fix.hr.master.change"
    _description = "Employee Master Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.people.approval.mixin"]
    _order = "id desc"

    _approval_domain = "hr_master_change"
    _approval_apply_method = "action_apply_change"
    _approval_group = OFFICER

    name = fields.Char(default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True, ondelete="cascade")
    reason = fields.Text(required=True)
    proposed_bank_name = fields.Char()
    proposed_bank_branch_name = fields.Char()
    proposed_routing_number = fields.Char(string="Proposed BEFTN Routing")
    proposed_bank_account_number = fields.Char()
    proposed_mfs_provider = fields.Selection(
        lambda self: self.env["hr.employee"]._fields["mfs_provider"].selection
    )
    proposed_mfs_account_number = fields.Char()
    proposed_nid_number = fields.Char(string="Proposed NID")
    proposed_tin_number = fields.Char(string="Proposed e-TIN")
    proposed_overtime_eligible = fields.Selection(
        [("yes", "Eligible"), ("no", "Not Eligible")], string="Proposed Overtime Eligibility"
    )
    evidence_file = fields.Binary(attachment=True, string="Evidence (cheque leaf, NID, TIN)")
    evidence_filename = fields.Char()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    snapshot_digest = fields.Char(readonly=True, copy=False)
    applied_on = fields.Datetime(readonly=True, copy=False)
    applied_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    PROPOSALS = {
        "proposed_bank_name": "bank_name",
        "proposed_bank_branch_name": "bank_branch_name",
        "proposed_routing_number": "routing_number",
        "proposed_bank_account_number": "bank_account_number",
        "proposed_mfs_provider": "mfs_provider",
        "proposed_mfs_account_number": "mfs_account_number",
        "proposed_nid_number": "nid_number",
        "proposed_tin_number": "tin_number",
        "proposed_overtime_eligible": "overtime_eligible",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "snapshot_digest",
            "applied_on",
            "applied_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self.PROPOSALS) | {"employee_id", "reason", "evidence_file"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        officer = self.env.su or self.env.user.has_group(OFFICER)
        for vals in vals_list:
            if not officer:
                emp = self.env["hr.employee"].sudo().browse(vals.get("employee_id") or 0)
                if emp.user_id != self.env.user:
                    raise AccessError("Raise a master change for your own record, or as HR.")
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.hr.master.change") or "HMC/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = (set(self.PROPOSALS) | {"employee_id", "reason", "evidence_file"}) & set(vals)
            if frozen and any(r.state != "draft" for r in self.filtered("id")):
                raise UserError(
                    "A submitted master change is never edited; cancel it and raise a new one."
                )
        return super().write(vals)

    def _fix_values(self):
        """{employee field: new value} for what this request changes."""
        self.ensure_one()
        out = {}
        for prop, target in self.PROPOSALS.items():
            value = self[prop]
            if not value:
                continue
            out[target] = (value == "yes") if target == "overtime_eligible" else value
        return out

    def _fix_snapshot(self):
        self.ensure_one()
        emp = self.employee_id.sudo()
        # an identity number is compared by its keyed hash: it is never read here
        current = {t: emp[IDENTITY[t][2]] if t in IDENTITY else emp[t] for t in self._fix_values()}
        current["bank_account_ids"] = emp.bank_account_ids.ids
        return digest(current)

    @api.constrains(*PROPOSALS)
    def _check_formats(self):
        checks = {
            "proposed_nid_number": (NID_RE, "NID"),
            "proposed_tin_number": (TIN_RE, "e-TIN"),
            "proposed_routing_number": (ROUTING_RE, "BEFTN routing"),
            "proposed_mfs_account_number": (MFS_RE, "MFS wallet"),
            "proposed_bank_account_number": (BANK_ACCOUNT_RE, "Bank account"),
        }
        for rec in self:
            for name, (pattern, label) in checks.items():
                if rec[name] and not pattern.match(rec[name].strip()):
                    raise ValidationError("%s %r is not valid." % (label, rec[name]))

    def _approval_preparers(self):
        return self.mapped("create_uid")

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft request is submitted.")
            if not rec._fix_values():
                raise UserError("Propose at least one change.")
            mine = rec.employee_id.sudo().user_id == self.env.user
            if not (self.env.su or mine or self.env.user.has_group(OFFICER)):
                raise AccessError("Raise a master change for your own record, or as HR.")
            rec._guarded().write({"state": "submitted", "snapshot_digest": rec._fix_snapshot()})
            rec.action_request_approval()
        return True

    def action_apply_change(self):
        """The checker's decision (approval inbox only): write the master."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted request is applied.")
            if rec.snapshot_digest != rec._fix_snapshot():
                raise UserError(
                    "%s changed since this request was raised; raise it again."
                    % rec.employee_id.name
                )
            emp = rec.employee_id.sudo()
            vals = rec._fix_values()
            Bank = self.env["res.partner.bank"].sudo()
            bank = Bank
            if "bank_account_number" in vals:
                partner = emp.work_contact_id
                bank = Bank.search(
                    [
                        ("acc_number", "=", vals["bank_account_number"]),
                        ("partner_id", "=", partner.id),
                    ],
                    limit=1,
                ) or Bank.create(
                    {"acc_number": vals["bank_account_number"], "partner_id": partner.id}
                )
                vals["bank_account_ids"] = [(6, 0, [bank.id])]
            elif "routing_number" in vals:
                bank = emp.bank_account_ids[:1]
            # E2E3 flow 9: the payee account treasury pays to carries the
            # approved BEFTN routing number too; without it every BEFTN / RTGS
            # disbursement to the employee was refused at release.
            routing = vals.get("routing_number") or emp.routing_number
            if (
                bank
                and routing
                and "fix_routing_number" in Bank._fields
                and bank.fix_routing_number != routing
            ):
                bank.write({"fix_routing_number": routing})
            emp._guarded().write(vals)
            labels = sorted(emp._fields[n].string for n in vals if n != "bank_account_ids")
            emp.message_post(
                body="Master change %s applied (approved by %s): %s."
                % (rec.name, rec._people_decider().name, ", ".join(labels))
            )
            rec._guarded().write(
                {
                    "state": "applied",
                    "applied_on": fields.Datetime.now(),
                    "applied_by_id": self.env.uid,
                    **rec._fix_identity_scrub_vals(),
                }
            )
            publish(
                self.env,
                "employee.master.changed",
                "hr.employee",
                emp.id,
                {"employee_id": emp.id, "request": rec.name, "fields": sorted(vals)},
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec._guarded().write({"state": "rejected", **rec._fix_identity_scrub_vals()})

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "submitted"):
                raise UserError("Only an open request is cancelled.")
            if not (
                self.env.su or self.env.user.has_group(OFFICER) or rec.create_uid == self.env.user
            ):
                raise AccessError("Only HR or the requester cancels a master change.")
            req = rec.approval_request_id.sudo()
            if rec.approval_state == "pending" and req.state == "pending":
                req._finish("recalled", "recalled", self.env.user, record_state="none")
            rec._guarded().write({"state": "cancelled", **rec._fix_identity_scrub_vals()})
        return True

    # ---- identity proposals are not kept once decided (BRU-HCM-06) -------------
    IDENTITY_PROPOSALS = ("proposed_nid_number", "proposed_tin_number")

    def _fix_identity_scrub_vals(self):
        """A decided request keeps which identity fields it proposed (on its
        chatter), never the numbers: those live in the resident store."""
        self.ensure_one()
        proposed = [p for p in self.IDENTITY_PROPOSALS if self[p]]
        if proposed:
            self.message_post(
                body="Proposed %s removed from this request on closing (held in the "
                "Bangladesh-resident store once applied)."
                % ", ".join(self._fields[p].string for p in proposed),
                subtype_xmlid="mail.mt_note",
            )
        return dict.fromkeys(proposed, False)

    @api.model
    def _fix_scrub_closed_identity_proposals(self):
        """Upgrade step: requests decided before this build kept the numbers."""
        if not self.env.su:
            raise AccessError("Run by the module upgrade only.")
        self.flush_model()
        self.env.cr.execute(
            "UPDATE fix_hr_master_change SET proposed_nid_number = NULL, "
            "proposed_tin_number = NULL WHERE state IN ('applied', 'rejected', 'cancelled') "
            "AND (proposed_nid_number IS NOT NULL OR proposed_tin_number IS NOT NULL)"
        )
        scrubbed = self.env.cr.rowcount
        self.invalidate_model(list(self.IDENTITY_PROPOSALS))
        return scrubbed
