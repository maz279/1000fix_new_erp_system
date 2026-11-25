# M08 contract gaps closed on 13 Nov 2026 (capture-button audit follow-up):
#
# - SCOPE AMENDMENTS that change the cover. `_amendment_apply` handled only
#   pricing and term: a scope amendment versioned the contract and changed
#   nothing, while the entitlement guard told users to change a live
#   contract's cover "through an approved scope amendment" (FR-CTR-015/036,
#   BRU-CTR-10/18). A scope amendment now carries lines - attach / detach a
#   covered asset, add / adjust an entitlement, add / remove an SLA or an
#   exclusion - that are applied when it is approved and effective.
# - PARTIES and signatories (FR-CTR-004).
# - COVERAGE EXCLUSIONS that override inclusion (FR-CTR-016).
# - the OBLIGATION REGISTER with owner, due date, evidence and an overdue
#   escalation (FR-CTR-032/033, AUT-CTR-16, BRU-CTR-14).
#
# Child records of a contract: like entitlements and PM visits they carry no
# company or operating unit of their own; access is the contract roles' ACL.
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_contract import IN_FORCE, MANAGER, OFFICER, require_role

SIGNED_STATES = (*IN_FORCE, "suspended", "expired", "terminated")
CLOSED_STATES = ("expired", "terminated")

SCOPE_ACTIONS = [
    ("attach_asset", "Attach covered asset"),
    ("detach_asset", "Detach covered asset"),
    ("add_entitlement", "Add entitlement"),
    ("adjust_entitlement", "Change entitlement quantity"),
    ("add_sla", "Add contract SLA"),
    ("remove_sla", "Remove contract SLA"),
    ("add_exclusion", "Add exclusion"),
    ("remove_exclusion", "Remove exclusion"),
]

ENTITLEMENT_TYPES = [
    ("visits", "Preventive Visits"),
    ("incidents", "Repair Incidents"),
    ("hours", "Labour Hours"),
    ("loaners", "Loaner Devices"),
]

EXCLUSION_TYPES = [
    ("fault_type", "Fault type"),
    ("cause", "Cause (e.g. power surge, liquid)"),
    ("consumable", "Consumables"),
    ("accidental_damage", "Accidental / physical damage"),
    ("unauthorised_repair", "Unauthorised repair or tampering"),
    ("other", "Other"),
]


# =============================================================================
# Scope amendment lines
# =============================================================================
class FixContractAmendmentLine(models.Model):
    _name = "fix.contract.amendment.line"
    _description = "Contract Scope Amendment Line"
    _order = "amendment_id, sequence, id"

    sequence = fields.Integer(default=10)
    amendment_id = fields.Many2one(
        "fix.contract.amendment", required=True, ondelete="cascade", index=True
    )
    contract_id = fields.Many2one(related="amendment_id.contract_id", store=True)
    action = fields.Selection(SCOPE_ACTIONS, required=True, default="attach_asset")
    device_id = fields.Many2one("fix.device", string="Device", ondelete="restrict")
    entitlement_type = fields.Selection(ENTITLEMENT_TYPES)
    entitlement_id = fields.Many2one(
        "fix.contract.entitlement", string="Entitlement", ondelete="set null"
    )
    quantity = fields.Float(help="Add: the quantity included. Change: the new included quantity.")
    sla_policy_id = fields.Many2one("fix.sla.policy", string="SLA", ondelete="restrict")
    exclusion_type = fields.Selection(EXCLUSION_TYPES)
    exclusion_text = fields.Char(string="Exclusion")
    exclusion_id = fields.Many2one(
        "fix.contract.exclusion", string="Exclusion to remove", ondelete="set null"
    )

    def _line_assert_editable(self, amendments):
        if self.env.su or self.env.context.get("fix_scope_apply"):
            return
        fixed = amendments.filtered(lambda a: a.state != "draft")
        if fixed:
            raise UserError(
                "Amendment %s is %s: its lines are fixed. Cancel it and raise a new one."
                % (fixed[0].name, dict(fixed[0]._fields["state"].selection)[fixed[0].state])
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = {v.get("amendment_id") for v in vals_list if v.get("amendment_id")}
        self._line_assert_editable(self.env["fix.contract.amendment"].browse(list(ids)))
        return super().create(vals_list)

    def write(self, vals):
        self._line_assert_editable(self.mapped("amendment_id"))
        return super().write(vals)

    def unlink(self):
        self._line_assert_editable(self.mapped("amendment_id"))
        return super().unlink()

    def _line_label(self):
        return "%s (line %s)" % (dict(SCOPE_ACTIONS)[self.action], self.sequence)

    def _line_validate(self):
        """What the contract must read for this line to apply."""
        self.ensure_one()
        contract = self.contract_id
        label = self._line_label()
        if self.action in ("attach_asset", "detach_asset"):
            if not self.device_id:
                raise UserError("%s: choose the device." % label)
            covered = self.device_id in contract.covered_device_ids
            if self.action == "attach_asset":
                if covered:
                    raise UserError(
                        "%s: %s is already covered by %s."
                        % (label, self.device_id.display_name, contract.code)
                    )
                owner = self.device_id.owner_id.commercial_partner_id
                customer = contract.customer_id.commercial_partner_id
                if owner and owner != customer:
                    raise UserError(
                        "%s: %s belongs to %s, not to the contract's customer %s."
                        % (label, self.device_id.display_name, owner.name, customer.name)
                    )
            elif not covered:
                raise UserError(
                    "%s: %s is not covered by %s."
                    % (label, self.device_id.display_name, contract.code)
                )
        elif self.action == "add_entitlement":
            if not self.entitlement_type:
                raise UserError("%s: choose the entitlement type." % label)
            if (self.quantity or 0.0) < 0:
                raise UserError("%s: the quantity cannot be negative." % label)
            if self.device_id and self.device_id not in contract.covered_device_ids:
                attaching = self.amendment_id.line_ids.filtered(
                    lambda line: line.action == "attach_asset" and line.device_id == self.device_id
                )
                if not attaching:
                    raise UserError(
                        "%s: %s is not covered by %s (attach it on this amendment)."
                        % (label, self.device_id.display_name, contract.code)
                    )
        elif self.action == "adjust_entitlement":
            ent = self.entitlement_id
            if not ent or ent.contract_id != contract:
                raise UserError("%s: choose an entitlement of %s." % (label, contract.code))
            if (self.quantity or 0.0) < 0:
                raise UserError("%s: the quantity cannot be negative." % label)
            if self.quantity and self.quantity < ent.quantity_consumed:
                raise UserError(
                    "%s: %s has already consumed %s; the included quantity cannot go below it."
                    % (label, dict(ENTITLEMENT_TYPES)[ent.entitlement_type], ent.quantity_consumed)
                )
        elif self.action in ("add_sla", "remove_sla"):
            if not self.sla_policy_id:
                raise UserError("%s: choose the SLA." % label)
            present = self.sla_policy_id in contract.sla_policy_ids
            if self.action == "add_sla" and present:
                raise UserError("%s: the contract already has this SLA." % label)
            if self.action == "remove_sla" and not present:
                raise UserError("%s: the contract does not have this SLA." % label)
        elif self.action == "add_exclusion":
            if not self.exclusion_type or not (self.exclusion_text or "").strip():
                raise UserError("%s: state the exclusion type and wording." % label)
        elif self.action == "remove_exclusion":
            if not self.exclusion_id or self.exclusion_id.contract_id != contract:
                raise UserError("%s: choose an exclusion of %s." % (label, contract.code))

    def _line_apply(self, effective):
        """Write this line onto the contract. Service code, run by the
        approval or the daily cron through _amendment_apply."""
        self.ensure_one()
        contract = self.contract_id.sudo()
        Entitlement = self.env["fix.contract.entitlement"].sudo()._guarded()
        payload = {"code": contract.code, "amendment_id": self.amendment_id.id}
        if self.action == "attach_asset":
            contract._guarded().write({"covered_device_ids": [(4, self.device_id.id)]})
            contract._generate_pm_schedule_for(self.device_id, effective)
            publish(
                self.env,
                "contract.asset_attached",
                "fix.contract",
                contract.id,
                dict(payload, device_id=self.device_id.id, effective_date=str(effective)),
            )
        elif self.action == "detach_asset":
            contract._guarded().write({"covered_device_ids": [(3, self.device_id.id)]})
            visits = (
                self.env["fix.contract.pm.visit"]
                .sudo()
                .search(
                    [
                        ("contract_id", "=", contract.id),
                        ("device_id", "=", self.device_id.id),
                        ("state", "=", "scheduled"),
                        ("scheduled_date", ">=", effective),
                    ]
                )
            )
            visits._guarded().write(
                {"state": "skipped", "skip_reason": "Asset detached by %s" % self.amendment_id.name}
            )
            publish(
                self.env,
                "contract.asset_detached",
                "fix.contract",
                contract.id,
                dict(payload, device_id=self.device_id.id, effective_date=str(effective)),
            )
        elif self.action == "add_entitlement":
            Entitlement.create(
                {
                    "contract_id": contract.id,
                    "entitlement_type": self.entitlement_type,
                    "quantity_included": self.quantity or 0.0,
                    "device_id": self.device_id.id or False,
                }
            )
        elif self.action == "adjust_entitlement":
            self.entitlement_id.sudo()._guarded().write({"quantity_included": self.quantity or 0.0})
        elif self.action == "add_sla":
            contract._guarded().write({"sla_policy_ids": [(4, self.sla_policy_id.id)]})
        elif self.action == "remove_sla":
            contract._guarded().write({"sla_policy_ids": [(3, self.sla_policy_id.id)]})
        elif self.action == "add_exclusion":
            self.env["fix.contract.exclusion"].sudo().with_context(fix_scope_apply=True).create(
                {
                    "contract_id": contract.id,
                    "exclusion_type": self.exclusion_type,
                    "name": self.exclusion_text,
                }
            )
        elif self.action == "remove_exclusion":
            self.exclusion_id.sudo().with_context(fix_scope_apply=True).unlink()
        return "%s: %s" % (
            dict(SCOPE_ACTIONS)[self.action],
            (
                self.device_id.display_name
                or self.sla_policy_id.display_name
                or self.exclusion_text
                or dict(ENTITLEMENT_TYPES).get(
                    self.entitlement_type or self.entitlement_id.entitlement_type
                )
                or ""
            ),
        )


class FixContractAmendmentScope(models.Model):
    _inherit = "fix.contract.amendment"

    line_ids = fields.One2many(
        "fix.contract.amendment.line", "amendment_id", string="Scope Changes", copy=True
    )

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked.add("line_ids")
        return locked

    def _amendment_validate(self):
        super()._amendment_validate()
        for rec in self:
            if rec.kind == "scope":
                if not rec.line_ids:
                    raise UserError(
                        "Scope amendment %s changes nothing: add the assets, entitlements, "
                        "SLAs or exclusions it attaches or removes." % rec.name
                    )
                if not self.env.context.get("fix_scope_lines_applied"):
                    for line in rec.line_ids:
                        line._line_validate()
            elif rec.line_ids:
                raise UserError(
                    "Amendment %s is a %s change: scope lines belong on a scope amendment."
                    % (rec.name, rec.kind)
                )

    def _amendment_apply(self):
        """A scope amendment writes its lines onto the contract, then the
        common path versions it and marks it applied."""
        for rec in self.filtered(lambda r: r.kind == "scope" and r.state != "applied"):
            if not self.env.su:
                rec._amendment_require_state(("approved",), "be applied")
                rec._amendment_assert_approved()
            rec._amendment_validate()
            effective = max(rec.effective_from, fields.Date.context_today(rec))
            done = [line._line_apply(effective) for line in rec.line_ids.sorted("sequence")]
            rec.contract_id.sudo().message_post(
                body="Scope amendment %s: %s." % (rec.name, "; ".join(done))
            )
        # the lines now read as applied ("already covered"): the common path
        # versions the contract without checking them again
        return super(
            FixContractAmendmentScope, self.with_context(fix_scope_lines_applied=True)
        )._amendment_apply()


# =============================================================================
# Parties and signatories (FR-CTR-004)
# =============================================================================
PARTY_ROLES = [
    ("customer_signatory", "Customer signatory"),
    ("our_signatory", "1000FiX signatory"),
    ("authorised_requester", "Authorised requester"),
    ("approver", "Customer approver"),
    ("notice", "Notice address"),
    ("billing", "Billing contact"),
]
SIGNATORY_ROLES = ("customer_signatory", "our_signatory")


class FixContractParty(models.Model):
    _name = "fix.contract.party"
    _description = "Contract Party / Signatory"
    _order = "contract_id, role, id"
    _rec_name = "partner_id"

    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    contract_state = fields.Selection(related="contract_id.state", string="Contract Status")
    partner_id = fields.Many2one("res.partner", string="Person / Entity", required=True)
    role = fields.Selection(PARTY_ROLES, required=True, default="authorised_requester")
    designation = fields.Char(help="Title of the person, e.g. Head of IT")
    email = fields.Char()
    phone = fields.Char()
    notice_address = fields.Text(help="Where formal notices are served (role: notice address)")
    portal_access = fields.Boolean(
        help="May see this contract in the corporate portal (P04), scoped to the role"
    )
    is_primary = fields.Boolean(string="Primary for this role")

    def _party_assert_editable(self, contracts, roles):
        if self.env.su:
            return
        require_role(self.env, OFFICER, "Changing contract parties")
        for contract in contracts:
            if contract.state in CLOSED_STATES:
                raise UserError("Contract %s is closed: its parties are fixed." % contract.code)
            if contract.state in SIGNED_STATES and set(roles) & set(SIGNATORY_ROLES):
                raise UserError(
                    "Contract %s is signed: its signatories are part of the executed "
                    "agreement and do not change." % contract.code
                )

    @api.model_create_multi
    def create(self, vals_list):
        contracts = self.env["fix.contract"].browse(
            list({v["contract_id"] for v in vals_list if v.get("contract_id")})
        )
        self._party_assert_editable(contracts, {v.get("role") for v in vals_list})
        return super().create(vals_list)

    def write(self, vals):
        roles = set(self.mapped("role")) | ({vals["role"]} if vals.get("role") else set())
        self._party_assert_editable(self.mapped("contract_id"), roles)
        return super().write(vals)

    def unlink(self):
        self._party_assert_editable(self.mapped("contract_id"), set(self.mapped("role")))
        return super().unlink()

    @api.constrains("role", "notice_address", "email")
    def _check_notice(self):
        for rec in self:
            if rec.role == "notice" and not (rec.notice_address or rec.email):
                raise ValidationError("A notice party needs a postal address or an e-mail.")


# =============================================================================
# Coverage exclusions (FR-CTR-016)
# =============================================================================
class FixContractExclusion(models.Model):
    _name = "fix.contract.exclusion"
    _description = "Contract Coverage Exclusion"
    _order = "contract_id, exclusion_type, id"

    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    contract_state = fields.Selection(related="contract_id.state", string="Contract Status")
    exclusion_type = fields.Selection(EXCLUSION_TYPES, required=True, default="other")
    name = fields.Char(string="Exclusion", required=True)
    name_bn = fields.Char(string="Exclusion (Bangla)")

    def _exclusion_assert_editable(self, contracts):
        if self.env.su or self.env.context.get("fix_scope_apply"):
            return
        require_role(self.env, OFFICER, "Changing contract exclusions")
        live = contracts.filtered(lambda c: c.state != "draft")
        if live:
            raise UserError(
                "Contract %s is no longer a draft: its exclusions change through an "
                "approved scope amendment." % ", ".join(live.mapped("code"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        self._exclusion_assert_editable(
            self.env["fix.contract"].browse(
                list({v["contract_id"] for v in vals_list if v.get("contract_id")})
            )
        )
        return super().create(vals_list)

    def write(self, vals):
        contracts = self.mapped("contract_id")
        if vals.get("contract_id"):
            contracts |= self.env["fix.contract"].browse(vals["contract_id"])
        self._exclusion_assert_editable(contracts)
        return super().write(vals)

    def unlink(self):
        self._exclusion_assert_editable(self.mapped("contract_id"))
        return super().unlink()


# =============================================================================
# Obligation register (FR-CTR-032/033, AUT-CTR-16, BRU-CTR-14)
# =============================================================================
OBLIGATION_TYPES = [
    ("calibration", "Calibration"),
    ("certificate", "Certificate / statutory inspection"),
    ("insurance", "Insurance"),
    ("report", "Report to the customer"),
    ("service_review", "Service review"),
    ("audit", "Audit"),
    ("notice", "Notice deadline"),
    ("other", "Other"),
]
RECURRENCE = {
    "none": None,
    "monthly": relativedelta(months=1),
    "quarterly": relativedelta(months=3),
    "half_yearly": relativedelta(months=6),
    "yearly": relativedelta(years=1),
}


class FixContractObligation(models.Model):
    _name = "fix.contract.obligation"
    _description = "Contract Obligation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "due_date, id"

    name = fields.Char(string="Obligation", required=True, tracking=True)
    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    obligation_type = fields.Selection(OBLIGATION_TYPES, required=True, default="other")
    owed_by = fields.Selection(
        [("us", "1000FiX"), ("customer", "Customer")], required=True, default="us"
    )
    mandatory = fields.Boolean(
        help="A lapsed mandatory obligation blocks contract compliance sign-off (BRU-CTR-14)"
    )
    due_date = fields.Date(required=True, tracking=True)
    recurrence = fields.Selection(
        [
            ("none", "One-off"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("half_yearly", "Half-yearly"),
            ("yearly", "Yearly"),
        ],
        required=True,
        default="none",
    )
    owner_id = fields.Many2one(
        "res.users", string="Owner", required=True, default=lambda self: self.env.user
    )
    description = fields.Text()
    state = fields.Selection(
        [("open", "Open"), ("overdue", "Overdue"), ("done", "Discharged"), ("waived", "Waived")],
        required=True,
        default="open",
        readonly=True,
        tracking=True,
    )
    evidence_note = fields.Text(string="Completion Evidence", readonly=True, copy=False)
    evidence_document_id = fields.Many2one(
        "fix.document", string="Evidence Document (M24)", copy=False
    )
    completed_by = fields.Many2one("res.users", readonly=True, copy=False)
    completed_on = fields.Datetime(readonly=True, copy=False)
    waive_reason = fields.Text(readonly=True, copy=False)
    next_obligation_id = fields.Many2one(
        "fix.contract.obligation", string="Next Occurrence", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "evidence_note",
            "completed_by",
            "completed_on",
            "waive_reason",
            "next_obligation_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state in ("done", "waived"):
            locked |= {
                "name",
                "contract_id",
                "obligation_type",
                "owed_by",
                "mandatory",
                "due_date",
                "recurrence",
                "owner_id",
                "description",
            }
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            closed = self.filtered(lambda r: r.state in ("done", "waived"))
            touched = set(vals) - {"evidence_document_id", "message_main_attachment_id"}
            if closed and touched:
                raise UserError(
                    "Obligation %s is %s: it is closed." % (closed[0].name, closed[0].state)
                )
        return super().write(vals)

    def action_complete(self, evidence=None):
        """Discharge the obligation with its evidence; a recurring one opens
        its next occurrence."""
        require_role(self.env, OFFICER, "Discharging a contract obligation")
        evidence = (evidence or "").strip()
        for rec in self:
            if rec.state not in ("open", "overdue"):
                raise UserError("Obligation %s is already %s." % (rec.name, rec.state))
            if not evidence and not rec.evidence_document_id:
                raise UserError(
                    "Obligation %s: state the evidence (certificate number, report "
                    "reference) or attach the evidence document." % rec.name
                )
            vals = {
                "state": "done",
                "evidence_note": evidence or False,
                "completed_by": self.env.user.id,
                "completed_on": fields.Datetime.now(),
            }
            step = RECURRENCE.get(rec.recurrence)
            if step:
                nxt = rec.sudo().copy(
                    {
                        "due_date": rec.due_date + step,
                        "state": "open",
                        "evidence_document_id": False,
                    }
                )
                vals["next_obligation_id"] = nxt.id
            rec.sudo()._guarded().write(vals)
            rec.activity_ids.sudo().action_feedback(
                feedback="Discharged: %s" % (evidence or "evidence on file")
            )
        return True

    def action_waive(self, reason=None):
        """A Contract Manager may waive an obligation, with the reason; a
        mandatory one cannot be waived."""
        require_role(self.env, MANAGER, "Waiving a contract obligation")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("State why the obligation is waived.")
        for rec in self:
            if rec.mandatory:
                raise UserError(
                    "Obligation %s is mandatory (BRU-CTR-14): it is discharged, not waived."
                    % rec.name
                )
            if rec.state not in ("open", "overdue"):
                raise UserError("Obligation %s is already %s." % (rec.name, rec.state))
            rec.sudo()._guarded().write({"state": "waived", "waive_reason": reason})
        return True

    @api.model
    def cron_obligations_due(self, lead_days=7):
        """AUT-CTR-16, daily and idempotent: an obligation due within the lead
        time gets one to-do for its owner; one past its date turns overdue and
        is announced once (contract.obligation_overdue). Returns the overdue
        count."""
        today = fields.Date.context_today(self)
        Obligation = self.sudo()
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        soon = Obligation.search(
            [("state", "=", "open"), ("due_date", "<=", today + timedelta(days=lead_days))]
        )
        for rec in soon.filtered(lambda r: not r.activity_ids):
            rec.activity_schedule(
                activity_type_id=todo.id if todo else False,
                date_deadline=rec.due_date,
                summary="Contract obligation due: %s" % rec.name,
                user_id=rec.owner_id.id,
            )
        overdue = Obligation.search([("state", "=", "open"), ("due_date", "<", today)])
        for rec in overdue:
            rec._guarded().write({"state": "overdue"})
            publish(
                self.env,
                "contract.obligation_overdue",
                "fix.contract",
                rec.contract_id.id,
                {
                    "code": rec.contract_id.code,
                    "obligation_id": rec.id,
                    "obligation": rec.name,
                    "owner_id": rec.owner_id.id,
                    "mandatory": rec.mandatory,
                    "days_overdue": (today - rec.due_date).days,
                },
            )
        return len(overdue)


# =============================================================================
# The contract side
# =============================================================================
class FixContractGaps(models.Model):
    _inherit = "fix.contract"

    party_ids = fields.One2many("fix.contract.party", "contract_id", string="Parties", copy=True)
    exclusion_ids = fields.One2many(
        "fix.contract.exclusion", "contract_id", string="Exclusions", copy=True
    )
    obligation_ids = fields.One2many("fix.contract.obligation", "contract_id", string="Obligations")
    obligations_overdue = fields.Integer(compute="_compute_obligations_overdue")

    @api.depends("obligation_ids.state")
    def _compute_obligations_overdue(self):
        for rec in self:
            rec.obligations_overdue = len(
                rec.obligation_ids.filtered(lambda o: o.state == "overdue")
            )

    def _generate_pm_schedule_for(self, devices, start):
        """The preventive visits of devices attached mid-term, from `start`
        to the end of the term, on the family's interval."""
        self.ensure_one()
        interval = self.PM_INTERVALS.get(self.family, 0)
        if not interval or not devices:
            return self.env["fix.contract.pm.visit"]
        Visit = self.env["fix.contract.pm.visit"].sudo()._guarded()
        made = Visit.browse()
        day = start
        while day + timedelta(days=interval) <= self.date_end:
            day = day + timedelta(days=interval)
            for device in devices:
                made |= Visit.create(
                    {
                        "contract_id": self.id,
                        "device_id": device.id,
                        "scheduled_date": day,
                        "state": "scheduled",
                    }
                )
        return made
