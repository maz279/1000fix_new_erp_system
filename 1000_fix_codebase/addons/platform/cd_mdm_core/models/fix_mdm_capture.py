# fix_mdm_capture — the M64 records the workspace pages had no way to capture.
#
# M64 capture audit (2026-11-18). Spec M64 §5/§10 names records that no model
# held, so no sub-module page could capture them:
#   * FR-MDM-021 remediation worklist (P0): the DQ evaluator counted failures
#     and nobody could take one on, assign it or close it;
#   * FR-MDM-033 business parameter registry (P0) with BRU-MDM-16/17: the
#     thresholds M63 executes had no governed home, version or effective date;
#   * FR-MDM-028/029 governed hierarchies (BRU-MDM-18): no structure at all;
#   * FR-MDM-013 bulk change governance (P0, BRU-MDM-08): a mass update could
#     only be raised as N unrelated requests, each applied on its own.
# Each reuses the change-request disciplines already in cd_mdm_core: the
# payload checks of fix.mdm.payload.mixin, the M63 routed approval with the
# proposer excluded (BRU-MDM-06), and fields only a transition may set.
import logging
import re
from collections import Counter

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)

STEWARD_GROUP = "cd_entity_config.group_mdm_domain_steward"
WORKLIST_CAP = 200
_KEY = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$")
_CODE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]*$")


def _is_steward(user):
    return user.has_group(STEWARD_GROUP)


# ---------------------------------------------------------------------------
# FR-MDM-021: the remediation worklist
# ---------------------------------------------------------------------------
class FixMdmDqRuleWorklist(models.Model):
    """The record-level view of a DQ rule: which records fail it."""

    _inherit = "fix.mdm.dq.rule"

    remediation_ids = fields.One2many("fix.mdm.dq.remediation", "rule_id", string="Remediations")
    open_remediation_count = fields.Integer(
        string="Open Remediations", compute="_compute_open_remediation_count"
    )

    def _compute_open_remediation_count(self):
        groups = self.env["fix.mdm.dq.remediation"]._read_group(
            [("rule_id", "in", self.ids), ("state", "in", ("open", "in_progress"))],
            ["rule_id"],
            ["__count"],
        )
        counts = {rule.id: count for rule, count in groups}
        for rec in self:
            rec.open_remediation_count = counts.get(rec.id, 0)

    def _value_fails(self, record):
        """Does this one record fail the rule? None when the rule cannot judge."""
        self.ensure_one()
        if self.field_name not in record._fields:
            return None
        field = record._fields[self.field_name]
        value = record[self.field_name]
        empty = value in (None, False, "")
        if self.rule_type == "completeness":
            return not value
        if self.rule_type == "uniqueness":
            if empty:
                return False
            domain = [(self.field_name, "=", value.id if field.type == "many2one" else value)]
            return bool(record.sudo().search_count([*domain, ("id", "!=", record.id)]))
        if self.rule_type == "format":
            try:
                return not empty and not re.fullmatch(self.expression or "", str(value))
            except re.error:
                return None
        if self.rule_type == "range":
            if field.type not in ("integer", "float", "monetary"):
                return None
            low, _, high = (self.expression or "").partition("..")
            try:
                lo = float(low) if low.strip() else None
                hi = float(high) if high.strip() else None
            except ValueError:
                return None
            return (lo is not None and value < lo) or (hi is not None and value > hi)
        if self.rule_type == "referential":
            return field.type == "many2one" and bool(value) and not value.exists()
        return None

    def _failing_records(self, limit=WORKLIST_CAP):
        """The records failing the rule now, worst first is not knowable: id order."""
        self.ensure_one()
        if self.res_model not in self.env:
            return None
        model = self.env[self.res_model].sudo()
        if self.field_name not in model._fields:
            return None
        if self.rule_type == "uniqueness":
            name = self.field_name
            relational = model._fields[name].type == "many2one"

            def key(record):
                return record[name].id if relational else record[name]

            records = model.search([(name, "!=", False)])
            keys = Counter(key(r) for r in records)
            failing = records.filtered(lambda r: keys[key(r)] > 1)
            return failing[:limit]
        if self.rule_type == "completeness":
            # the database answers it: no need to read the whole master
            return model.search([(self.field_name, "=", False)], order="id", limit=limit)
        failing = model.browse()
        for record in model.search([], order="id"):
            if self._value_fails(record):
                failing |= record
                if len(failing) >= limit:
                    break
        return failing

    def action_raise_worklist(self):
        """FR-MDM-021: every record failing the rule becomes a worklist item a
        steward can take on. One open item per rule and record; capped."""
        if not self.env.su and not _is_steward(self.env.user):
            raise UserError("Raising a remediation worklist needs the 'MDM Domain Steward' group.")
        Remediation = self.env["fix.mdm.dq.remediation"].sudo()
        raised = 0
        for rule in self:
            failing = rule._failing_records()
            if failing is None:
                raise UserError(
                    "DQ rule %s cannot be checked record by record: %s.%s is not there."
                    % (rule.code, rule.res_model, rule.field_name)
                )
            open_ids = set(
                Remediation.search(
                    [("rule_id", "=", rule.id), ("state", "in", ("open", "in_progress"))]
                ).mapped("res_id")
            )
            priority = {"critical": "urgent", "major": "high"}.get(rule.severity, "normal")
            vals = [
                {"rule_id": rule.id, "res_id": record.id, "priority": priority}
                for record in failing
                if record.id not in open_ids
            ]
            if vals:
                Remediation.with_context(fix_mdm_raised_by=self.env.uid).create(vals)
            raised += len(vals)
        return raised


class FixMdmDqRemediation(models.Model):
    """A failing record a steward must fix (FR-MDM-005 console, FR-MDM-021)."""

    _name = "fix.mdm.dq.remediation"
    _description = "Data Quality Remediation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state_rank, priority_rank desc, due_by, id"

    name = fields.Char(string="Reference", compute="_compute_name", store=True)
    rule_id = fields.Many2one(
        "fix.mdm.dq.rule", string="DQ Rule", required=True, index=True, ondelete="restrict"
    )
    company_id = fields.Many2one(related="rule_id.company_id", store=True, index=True)
    res_model = fields.Char(related="rule_id.res_model", store=True, string="Master Model")
    res_id = fields.Integer(string="Record ID", required=True, index=True)
    record_name = fields.Char(string="Record", readonly=True)
    severity = fields.Selection(related="rule_id.severity", store=True)
    priority = fields.Selection(
        [("low", "Low"), ("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")],
        default="normal",
        required=True,
        tracking=True,
    )
    priority_rank = fields.Integer(compute="_compute_ranks", store=True)
    business_impact = fields.Text(
        string="Business Impact", help="What breaks while the record stays wrong."
    )
    assigned_to_id = fields.Many2one(
        "res.users", string="Assigned Steward", tracking=True, index=True
    )
    due_by = fields.Date(string="Due By", tracking=True)
    state = fields.Selection(
        [
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
            ("waived", "Waived"),
        ],
        default="open",
        required=True,
        tracking=True,
        index=True,
    )
    state_rank = fields.Integer(compute="_compute_ranks", store=True)
    resolution = fields.Text(string="Resolution", readonly=True, tracking=True)
    raised_by_id = fields.Many2one("res.users", string="Raised By", readonly=True)
    resolved_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)
    resolved_at = fields.Datetime(string="Closed At", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "resolution",
            "record_name",
            "raised_by_id",
            "resolved_by_id",
            "resolved_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state in ("resolved", "waived"):
            locked |= {
                "rule_id",
                "res_id",
                "priority",
                "business_impact",
                "assigned_to_id",
                "due_by",
            }
        elif self:
            locked |= {"rule_id", "res_id"}
        return locked

    @api.depends("rule_id.code", "res_id")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s / %s" % (rec.rule_id.code or "?", rec.res_id or "?")

    @api.depends("priority", "state")
    def _compute_ranks(self):
        order = {"low": 0, "normal": 1, "high": 2, "urgent": 3}
        states = {"open": 0, "in_progress": 0, "resolved": 1, "waived": 1}
        for rec in self:
            rec.priority_rank = order.get(rec.priority, 1)
            rec.state_rank = states.get(rec.state, 0)

    def _target(self):
        self.ensure_one()
        if self.res_model not in self.env:
            return None
        return self.env[self.res_model].sudo().browse(self.res_id).exists()

    @api.constrains("rule_id", "res_id")
    def _check_target(self):
        for rec in self:
            target = rec._target()
            if not target:
                raise ValidationError(
                    "No %s with id %s exists: there is nothing to remediate."
                    % (rec.res_model, rec.res_id)
                )
            twin = self.search_count(
                [
                    ("id", "!=", rec.id),
                    ("rule_id", "=", rec.rule_id.id),
                    ("res_id", "=", rec.res_id),
                    ("state", "in", ("open", "in_progress")),
                ]
            )
            if twin and rec.state in ("open", "in_progress"):
                raise ValidationError(
                    "%s already has an open remediation for rule %s."
                    % (target.display_name, rec.rule_id.code)
                )

    @api.constrains("assigned_to_id")
    def _check_assignee(self):
        for rec in self:
            if rec.assigned_to_id and not _is_steward(rec.assigned_to_id):
                raise ValidationError(
                    "%s cannot take remediation work: assign it to a holder of the "
                    "'MDM Domain Steward' group." % rec.assigned_to_id.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        raiser = self.env.context.get("fix_mdm_raised_by") or self.env.uid
        for rec in records:
            target = rec._target()
            rec._guarded().write(
                {"record_name": target.display_name if target else False, "raised_by_id": raiser}
            )
        return records

    def _assert_worker(self, what):
        user = self.env.user
        if self.env.su:
            return
        for rec in self:
            if not (_is_steward(user) or user == rec.assigned_to_id):
                raise UserError(
                    "%s a remediation is the assigned steward's work, or a domain steward's." % what
                )

    def action_start(self):
        self._assert_worker("Starting")
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open remediation can be started (%s)." % rec.name)
            vals = {"state": "in_progress"}
            rec._guarded().write(vals)
            if not rec.assigned_to_id and _is_steward(self.env.user):
                rec.write({"assigned_to_id": self.env.uid})
        return True

    def action_resolve(self, note=None):
        """Closed only when the record now passes its rule: a 'fixed' item on a
        record that still fails is the dashboard-that-declines-gracefully failure."""
        self._assert_worker("Resolving")
        for rec in self:
            if rec.state not in ("open", "in_progress"):
                raise UserError("%s is already closed." % rec.name)
            target = rec._target()
            if target:
                fails = rec.rule_id.sudo()._value_fails(target)
                if fails:
                    raise UserError(
                        "%s still fails rule %s (%s): fix the record first, then resolve."
                        % (target.display_name, rec.rule_id.code, rec.rule_id.name)
                    )
            rec._guarded().write(
                {
                    "state": "resolved",
                    "resolution": (note or "").strip() or "Record now passes the rule.",
                    "resolved_by_id": self.env.uid,
                    "resolved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_waive(self, note=None):
        """An exception to the rule: a steward who neither defined the rule nor
        raised the item, with a stated reason (M64 §13 segregation of duties)."""
        if not (note or "").strip():
            raise UserError("State why this record is exempt from the rule.")
        for rec in self:
            if rec.state not in ("open", "in_progress"):
                raise UserError("%s is already closed." % rec.name)
            if not self.env.su:
                user = self.env.user
                if not _is_steward(user):
                    raise UserError("Waiving a data-quality failure needs a domain steward.")
                if user in (rec.rule_id.create_uid | rec.raised_by_id):
                    raise UserError(
                        "Segregation of duties: you defined rule %s or raised this item, so "
                        "another steward decides the exception." % rec.rule_id.code
                    )
            rec._guarded().write(
                {
                    "state": "waived",
                    "resolution": note.strip(),
                    "resolved_by_id": self.env.uid,
                    "resolved_at": fields.Datetime.now(),
                }
            )
        return True


# ---------------------------------------------------------------------------
# FR-MDM-033: the business parameter registry (M64 stores, M63 executes)
# ---------------------------------------------------------------------------
PARAMETER_TYPES = [
    ("integer", "Whole Number"),
    ("float", "Decimal"),
    ("amount", "Amount (BDT)"),
    ("percent", "Percentage"),
    ("days", "Days"),
    ("boolean", "Yes / No"),
    ("text", "Text"),
]


class FixMdmBusinessParameter(models.Model):
    """A threshold, ceiling, period or rate the business runs on (FR-MDM-033).

    The value is typed while the parameter is a draft. Once active it changes
    only through a Parameter Change, approved by the parameter's owner (or a
    steward when the owner proposed it) and effective from a stated date;
    `value_at` answers what was in force on any date (BRU-MDM-17)."""

    _name = "fix.mdm.business.parameter"
    _description = "Business Parameter"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "domain, key"
    _rec_name = "key"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    key = fields.Char(
        required=True, index=True, tracking=True, help="e.g. pricing.discount_ceiling"
    )
    name = fields.Char(string="Parameter", required=True, tracking=True)
    name_bn = fields.Char(string="Parameter (Bengali)")
    domain = fields.Selection(
        [
            ("pricing", "Pricing & Discounts"),
            ("credit", "Credit & Collections"),
            ("sla", "Service Levels"),
            ("warranty", "Warranty"),
            ("inventory", "Inventory"),
            ("procurement", "Procurement"),
            ("finance", "Finance & Approval Bands"),
            ("people", "People"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
        tracking=True,
    )
    value_type = fields.Selection(PARAMETER_TYPES, required=True, default="float")
    unit = fields.Char(help="BDT, %, days, hours…")
    min_value = fields.Float(string="Lowest Allowed")
    max_value = fields.Float(string="Highest Allowed")
    scope_level = fields.Selection(
        [("global", "Whole Estate"), ("company", "This Company")],
        required=True,
        default="company",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Business Owner",
        required=True,
        tracking=True,
        help="Decides changes to the value (BRU-MDM-16).",
    )
    consumer_note = fields.Text(
        string="Read By", help="The M63 rules and modules that execute this parameter."
    )
    description = fields.Text()
    initial_value = fields.Char(
        string="Value", tracking=True, help="Typed while a draft; frozen when activated."
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    activated_on = fields.Date(string="Active Since", readonly=True)
    activated_by_id = fields.Many2one("res.users", string="Activated By", readonly=True)
    version = fields.Integer(readonly=True, default=1)
    current_value = fields.Char(string="Value in Force", compute="_compute_current_value")
    change_ids = fields.One2many("fix.mdm.parameter.change", "parameter_id", string="Changes")

    _key_company_unique = models.Constraint(
        "UNIQUE (key, company_id)", "A business parameter key is unique per company."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "activated_on",
            "activated_by_id",
            "version",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {
                "key",
                "value_type",
                "initial_value",
                "min_value",
                "max_value",
                "scope_level",
            }
        return locked

    @api.constrains("key")
    def _check_key(self):
        for rec in self:
            if not _KEY.match(rec.key or ""):
                raise ValidationError(
                    "Parameter key %r must be lower-case and dotted, like "
                    "pricing.discount_ceiling." % rec.key
                )

    @api.constrains("min_value", "max_value")
    def _check_bounds(self):
        for rec in self:
            if rec.min_value and rec.max_value and rec.min_value > rec.max_value:
                raise ValidationError(
                    "%s: the lowest allowed value is above the highest." % rec.key
                )

    @api.constrains("initial_value", "value_type", "min_value", "max_value")
    def _check_initial_value(self):
        for rec in self:
            if rec.initial_value not in (False, ""):
                rec._normalise(rec.initial_value)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {"key", "value_type", "initial_value", "min_value", "max_value", "scope_level"}
            moved = self.filtered(lambda r: r.state != "draft")
            changed = [
                name
                for rec in moved
                for name in frozen & set(vals)
                if rec._fix_guard_differs(name, vals[name], rec[name])
            ]
            if changed:
                raise UserError(
                    "%s is in force: its key, type, bounds and value change only through a "
                    "Parameter Change approved by its owner." % moved[:1].key
                )
        return super().write(vals)

    def _normalise(self, raw):
        """The value as stored text, or a refusal naming what is wrong."""
        self.ensure_one()
        text = ("%s" % (raw if raw is not None else "")).strip()
        if not text:
            raise ValidationError("%s needs a value." % self.key)
        if self.value_type == "text":
            return text
        if self.value_type == "boolean":
            lowered = text.lower()
            if lowered not in ("yes", "no", "true", "false", "1", "0"):
                raise ValidationError("%s takes Yes or No, not %r." % (self.key, text))
            return "yes" if lowered in ("yes", "true", "1") else "no"
        try:
            number = float(text.replace(",", ""))
        except ValueError as exc:
            raise ValidationError("%s takes a number, not %r." % (self.key, text)) from exc
        if self.value_type in ("integer", "days") and number != int(number):
            raise ValidationError("%s takes a whole number, not %r." % (self.key, text))
        if self.value_type == "percent" and not 0 <= number <= 100:
            raise ValidationError("%s is a percentage: %r is outside 0-100." % (self.key, text))
        bounded = self.min_value or self.max_value
        if bounded and (
            (self.min_value and number < self.min_value)
            or (self.max_value and number > self.max_value)
        ):
            raise ValidationError(
                "%s must lie between %s and %s; %r does not."
                % (self.key, self.min_value or "-", self.max_value or "-", text)
            )
        if self.value_type in ("integer", "days"):
            return str(int(number))
        return ("%.6f" % number).rstrip("0").rstrip(".")

    def _compute_current_value(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.current_value = rec._value_on(today) or False

    def _value_on(self, on_date):
        """BRU-MDM-17: the value in force on `on_date` (None before activation)."""
        self.ensure_one()
        if self.state == "draft" or not self.activated_on or on_date < self.activated_on:
            return None
        published = self.change_ids.sudo().filtered(
            lambda c: c.state == "published" and c.effective_from <= on_date
        )
        if published:
            latest = published.sorted(lambda c: (c.effective_from, c.published_at, c.id))[-1]
            return latest.proposed_value
        return self.initial_value

    @api.model
    def value_at(self, key, on_date=None, company=None):
        """What M63 and the modules call: the value of `key` in force on a date."""
        company = company or self.env.company
        param = self.sudo().search([("key", "=", key), ("company_id", "=", company.id)], limit=1)
        if not param:
            param = self.sudo().search([("key", "=", key), ("scope_level", "=", "global")], limit=1)
        if not param:
            return None
        return param._value_on(on_date or fields.Date.context_today(self))

    def action_activate(self):
        """A second person puts a parameter in force: its owner or a steward,
        never the one who drafted it."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft parameter can be activated (%s)." % rec.key)
            if rec.initial_value in (False, ""):
                raise UserError("Give %s a value before activating it." % rec.key)
            if not self.env.su:
                user = self.env.user
                if user != rec.owner_id and not _is_steward(user):
                    raise UserError(
                        "%s is activated by its business owner or a domain steward." % rec.key
                    )
                if user == rec.create_uid:
                    raise UserError(
                        "Segregation of duties: you drafted %s, so its owner or another "
                        "steward activates it." % rec.key
                    )
            rec.sudo()._guarded().write(  # the owner decides; need not be a steward
                {
                    "state": "active",
                    "initial_value": rec._normalise(rec.initial_value),
                    "activated_on": fields.Date.context_today(rec),
                    "activated_by_id": self.env.uid,
                }
            )
            rec.sudo().message_post(
                body="Activated by %s at %s." % (self.env.user.name, rec.initial_value)
            )
        return True

    def action_retire(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active parameter can be retired (%s)." % rec.key)
            if not self.env.su and self.env.user != rec.owner_id and not _is_steward(self.env.user):
                raise UserError("%s is retired by its business owner or a steward." % rec.key)
            if rec.change_ids.filtered(lambda c: c.state == "submitted"):
                raise UserError("%s has a change awaiting its owner: decide it first." % rec.key)
            rec.sudo()._guarded().write({"state": "retired"})
            rec.sudo().message_post(body="Retired by %s." % self.env.user.name)
        return True


class FixMdmParameterChange(models.Model):
    """A proposed new value for an active business parameter (BRU-MDM-16)."""

    _name = "fix.mdm.parameter.change"
    _description = "Business Parameter Change"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "id desc"

    _approval_domain = "other"
    _approval_apply_method = "action_approve"
    _approval_group = STEWARD_GROUP
    _approval_routed = True

    name = fields.Char(string="Reference", compute="_compute_name", store=True)
    parameter_id = fields.Many2one(
        "fix.mdm.business.parameter",
        string="Parameter",
        required=True,
        index=True,
        ondelete="restrict",
        domain="[('state', '=', 'active')]",
    )
    company_id = fields.Many2one(related="parameter_id.company_id", store=True, index=True)
    owner_id = fields.Many2one(related="parameter_id.owner_id", string="Business Owner")
    proposed_value = fields.Char(string="New Value", required=True)
    previous_value = fields.Char(string="Value Before", readonly=True)
    effective_from = fields.Date(
        string="Effective From", required=True, default=fields.Date.context_today
    )
    reason = fields.Text(required=True, help="Why the value changes (BRU-MDM-22).")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Owner"),
            ("published", "Published"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    submitted_by_id = fields.Many2one("res.users", string="Proposed By", readonly=True)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    published_at = fields.Datetime(string="Published At", readonly=True)
    decision_note = fields.Text(string="Decision Note", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "previous_value",
            "submitted_by_id",
            "decided_by_id",
            "published_at",
            "decision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {"parameter_id", "proposed_value", "effective_from", "reason"}
        return locked

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {
            "parameter_id",
            "proposed_value",
            "effective_from",
        }

    def _approval_needed(self) -> bool:
        return self.state == "submitted"

    def _approval_excluded(self):
        return super()._approval_excluded() | self.submitted_by_id

    def _approval_resolve(self, rule, tier):
        """The parameter's owner decides; a steward when the owner proposed it."""
        owner = self.parameter_id.owner_id
        if owner and owner.active and owner not in self._approval_excluded():
            return self._approval_substitutes(owner)
        return super()._approval_resolve(rule, tier)

    @api.depends("parameter_id.key", "effective_from")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s from %s" % (rec.parameter_id.key or "?", rec.effective_from or "?")

    @api.constrains("parameter_id", "proposed_value")
    def _check_value(self):
        for rec in self:
            rec.parameter_id._normalise(rec.proposed_value)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {"parameter_id", "proposed_value", "effective_from", "reason"}
            moved = self.filtered(lambda r: r.state != "draft")
            if any(
                rec._fix_guard_differs(name, vals[name], rec[name])
                for rec in moved
                for name in frozen & set(vals)
            ):
                raise UserError(
                    "%s was submitted: cancel it and propose again to change it." % moved[:1].name
                )
        return super().write(vals)

    def action_submit(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft change can be submitted (%s)." % rec.name)
            param = rec.parameter_id
            if param.state != "active":
                raise UserError("%s is not in force: only an active parameter changes." % param.key)
            if rec.effective_from < today:
                raise UserError("A parameter change cannot take effect in the past.")
            normalised = param._normalise(rec.proposed_value)
            before = param._value_on(rec.effective_from)
            if normalised == before:
                raise UserError("%s is already %s on that date." % (param.key, before))
            open_twin = param.change_ids.filtered(lambda c: c.state == "submitted") - rec
            if open_twin:
                raise UserError(
                    "%s already has a change awaiting its owner (%s)."
                    % (param.key, open_twin[0].name)
                )
            rec._guarded().write(
                {
                    "state": "submitted",
                    "proposed_value": normalised,
                    "previous_value": before or False,
                    "submitted_by_id": self.env.uid,
                }
            )
        return True

    def action_request_approval(self, justification=None):
        if not self.env.su:
            for rec in self:
                if rec.state != "submitted":
                    raise UserError("Submit %s before routing it." % rec.name)
        return super().action_request_approval(justification=justification or self[:1].reason)

    def action_approve(self):
        """The routed decision publishes the value with its effective date."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted change can be approved (%s)." % rec.name)
            acting = rec._approval_acting_users()
            if not self.env.su:
                authority = rec._approval_authority_user()
                if authority != rec.parameter_id.owner_id and not _is_steward(authority):
                    raise UserError(
                        "%s is decided by its business owner or a domain steward."
                        % rec.parameter_id.key
                    )
                if (rec.submitted_by_id | rec.create_uid) & acting:
                    raise UserError(
                        "Segregation of duties: you proposed %s, so someone else decides it."
                        % rec.name
                    )
            rec.sudo()._guarded().write(
                {
                    "state": "published",
                    "decided_by_id": self.env.uid,
                    "published_at": fields.Datetime.now(),
                }
            )
            rec.parameter_id.sudo()._guarded().write({"version": rec.parameter_id.version + 1})
            rec.parameter_id.sudo().message_post(
                body="%s -> %s from %s (%s), approved by %s."
                % (
                    rec.previous_value or "-",
                    rec.proposed_value,
                    rec.effective_from,
                    rec.reason,
                    self.env.user.name,
                )
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            if rec.state == "submitted":
                rec.sudo()._guarded().write(
                    {
                        "state": "rejected",
                        "decided_by_id": self.env.uid,
                        "decision_note": comment or False,
                    }
                )

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "submitted"):
                raise UserError("Only an open change can be cancelled (%s)." % rec.name)
            if rec.approval_state == "pending":
                raise UserError("Recall the approval request before cancelling.")
            rec._guarded().write({"state": "cancelled"})
        return True


# ---------------------------------------------------------------------------
# FR-MDM-028/029: governed hierarchies (BRU-MDM-18)
# ---------------------------------------------------------------------------
class FixMdmHierarchy(models.Model):
    """A governed classification, roll-up or segmentation tree."""

    _name = "fix.mdm.hierarchy"
    _description = "Governed Hierarchy"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "code, version desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(required=True, index=True, tracking=True)
    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)")
    hierarchy_type = fields.Selection(
        [
            ("classification", "Product / Service Classification"),
            ("spend", "Spend Category"),
            ("rollup", "Cost Centre Roll-up"),
            ("segmentation", "Customer Segmentation"),
            ("other", "Other"),
        ],
        string="Type",
        required=True,
        default="classification",
    )
    max_depth = fields.Integer(string="Deepest Level", required=True, default=4)
    owner_id = fields.Many2one("res.users", string="Business Owner", tracking=True)
    version = fields.Integer(readonly=True, default=1)
    effective_from = fields.Date(string="Effective From")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    node_ids = fields.One2many("fix.mdm.hierarchy.node", "hierarchy_id", string="Nodes", copy=True)
    node_count = fields.Integer(compute="_compute_node_count")
    published_by_id = fields.Many2one("res.users", string="Published By", readonly=True, copy=False)
    published_at = fields.Datetime(string="Published At", readonly=True, copy=False)
    superseded_by_id = fields.Many2one(
        "fix.mdm.hierarchy", string="Superseded By", readonly=True, copy=False
    )

    _code_version_unique = models.Constraint(
        "UNIQUE (code, version, company_id)", "A hierarchy version is unique per code."
    )
    _depth_range = models.Constraint(
        "CHECK (max_depth BETWEEN 1 AND 10)", "A hierarchy is 1 to 10 levels deep."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "version",
            "published_by_id",
            "published_at",
            "superseded_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {
                "code",
                "name",
                "name_bn",
                "hierarchy_type",
                "max_depth",
                "effective_from",
                "node_ids",
            }
        return locked

    def _compute_node_count(self):
        for rec in self:
            rec.node_count = len(rec.node_ids)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {"code", "name", "hierarchy_type", "max_depth", "effective_from", "node_ids"}
            moved = self.filtered(lambda r: r.state != "draft")
            if moved and frozen & set(vals):
                raise UserError(
                    "Hierarchy %s v%s is %s: cut a new version to change it."
                    % (moved[:1].code, moved[:1].version, moved[:1].state)
                )
        return super().write(vals)

    @api.constrains("node_ids", "max_depth")
    def _check_tree(self):
        """BRU-MDM-18: no orphan, no cycle, no level beyond the depth."""
        for rec in self:
            nodes = rec.node_ids
            by_code = {}
            for node in nodes:
                if node.code in by_code:
                    raise ValidationError("%s: node code %s is used twice." % (rec.code, node.code))
                by_code[node.code] = node
            for node in nodes:
                seen = {node.code}
                parent_code = node.parent_code
                depth = 1
                while parent_code:
                    if parent_code not in by_code:
                        raise ValidationError(
                            "%s: node %s hangs under %s, which is not in the hierarchy (an "
                            "orphan)." % (rec.code, node.code, parent_code)
                        )
                    if parent_code in seen:
                        raise ValidationError(
                            "%s: node %s is its own ancestor through %s (a cycle)."
                            % (rec.code, node.code, parent_code)
                        )
                    seen.add(parent_code)
                    depth += 1
                    parent_code = by_code[parent_code].parent_code
                if depth > rec.max_depth:
                    raise ValidationError(
                        "%s: node %s sits at level %d, below the deepest level %d."
                        % (rec.code, node.code, depth, rec.max_depth)
                    )

    def action_publish(self):
        """A second steward publishes; the version it succeeds retires."""
        if not self.env.su and not _is_steward(self.env.user):
            raise UserError("Publishing a hierarchy needs the 'MDM Domain Steward' group.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft hierarchy can be published (%s)." % rec.code)
            if not rec.node_ids:
                raise UserError("Publish %s with at least one node." % rec.code)
            if not self.env.su and self.env.user == rec.create_uid:
                raise UserError(
                    "Segregation of duties: you built hierarchy %s, so a different steward "
                    "publishes it." % rec.code
                )
            rec._check_tree()
            today = fields.Date.context_today(rec)
            older = self.search(
                [
                    ("code", "=", rec.code),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "published"),
                    ("id", "!=", rec.id),
                ]
            )
            older._guarded().write({"state": "retired", "superseded_by_id": rec.id})
            rec._guarded().write(
                {
                    "state": "published",
                    "published_by_id": self.env.uid,
                    "published_at": fields.Datetime.now(),
                }
            )
            if not rec.effective_from:
                rec.sudo().write({"effective_from": today})
            rec.message_post(
                body="Published by %s (%d nodes)." % (self.env.user.name, len(rec.node_ids))
            )
        return True

    def action_new_version(self):
        """A published tree changes as a new draft version (FR-MDM-028)."""
        for rec in self:
            if rec.state != "published":
                raise UserError("A new version is cut from the published hierarchy.")
            if self.search_count(
                [
                    ("code", "=", rec.code),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "draft"),
                ]
            ):
                raise UserError("%s already has a draft version in progress." % rec.code)
            top = max(
                self.search(
                    [("code", "=", rec.code), ("company_id", "=", rec.company_id.id)]
                ).mapped("version")
            )
            # sudo: the copy carries guarded values (version); create_uid stays the user
            rec.sudo().copy({"effective_from": False, "version": top + 1, "state": "draft"})
        return True


class FixMdmHierarchyNode(models.Model):
    """One node; its parent is named by code so a whole tree is keyed in one form."""

    _name = "fix.mdm.hierarchy.node"
    _description = "Governed Hierarchy Node"
    _order = "hierarchy_id, level, sequence, code"

    hierarchy_id = fields.Many2one(
        "fix.mdm.hierarchy", required=True, index=True, ondelete="cascade"
    )
    code = fields.Char(required=True)
    label = fields.Char(required=True)
    label_bn = fields.Char(string="Label (Bengali)")
    parent_code = fields.Char(string="Parent Code", help="Blank for a top-level node.")
    sequence = fields.Integer(default=10)
    parent_id = fields.Many2one(
        "fix.mdm.hierarchy.node", compute="_compute_tree", store=True, string="Parent"
    )
    level = fields.Integer(compute="_compute_tree", store=True)

    @api.constrains("code", "parent_code")
    def _check_codes(self):
        for rec in self:
            if not _CODE.match(rec.code or ""):
                raise ValidationError(
                    "Node code %r may use letters, digits, '.', '-' and '_'." % rec.code
                )
            if rec.parent_code and rec.parent_code == rec.code:
                raise ValidationError("Node %s cannot be its own parent." % rec.code)
        self.mapped("hierarchy_id")._check_tree()

    @api.depends("parent_code", "hierarchy_id.node_ids.code", "hierarchy_id.node_ids.parent_code")
    def _compute_tree(self):
        for rec in self:
            by_code = {n.code: n for n in rec.hierarchy_id.node_ids if n.code}
            parent = by_code.get(rec.parent_code) if rec.parent_code else False
            rec.parent_id = parent.id if parent and parent.id else False
            level, code, seen = 1, rec.parent_code, {rec.code}
            while code and code in by_code and code not in seen:
                seen.add(code)
                level += 1
                code = by_code[code].parent_code
            rec.level = level

    def _frozen(self):
        return self.mapped("hierarchy_id").filtered(lambda h: h.state != "draft")

    @api.model_create_multi
    def create(self, vals_list):
        hierarchies = self.env["fix.mdm.hierarchy"].browse(
            [v.get("hierarchy_id") for v in vals_list if v.get("hierarchy_id")]
        )
        if not self.env.su and hierarchies.filtered(lambda h: h.state != "draft"):
            raise UserError("A published hierarchy is frozen: cut a new version to add nodes.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su and self._frozen():
            raise UserError("A published hierarchy is frozen: cut a new version to change nodes.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and self._frozen():
            raise UserError("A published hierarchy is frozen: cut a new version to remove nodes.")
        return super().unlink()


# ---------------------------------------------------------------------------
# FR-MDM-013: bulk change governance (BRU-MDM-08)
# ---------------------------------------------------------------------------
BULK_STATES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("approved", "Approved"),
    ("applied", "Applied"),
    ("rejected", "Rejected"),
    ("cancelled", "Cancelled"),
]
BULK_TERMINAL = ("applied", "rejected", "cancelled")


class FixMdmChangeBatch(models.Model):
    """A mass update reviewed and approved as one set, applied all-or-nothing."""

    _name = "fix.mdm.change.batch"
    _description = "Bulk Master-Data Change Set"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "fix.approvable.mixin",
        "fix.mdm.payload.mixin",
    ]
    _order = "id desc"

    _approval_domain = "other"
    _approval_apply_method = "action_approve"
    _approval_group = STEWARD_GROUP
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(string="Reference", readonly=True, copy=False)
    title = fields.Char(required=True, tracking=True)
    justification = fields.Text(required=True, help="Why every record in the set changes.")
    model_name = fields.Char(string="Target Model", required=True)
    line_ids = fields.One2many("fix.mdm.change.batch.line", "batch_id", string="Records")
    line_count = fields.Integer(string="Record Count", compute="_compute_line_count")
    state = fields.Selection(BULK_STATES, default="draft", required=True, tracking=True, index=True)
    preview = fields.Text(string="Preview (measured at submit)", readonly=True)
    submitted_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True)
    reviewed_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    applied_by_id = fields.Many2one("res.users", string="Applied By", readonly=True)
    applied_at = fields.Datetime(string="Applied At", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "name",
            "preview",
            "submitted_by_id",
            "reviewed_by_id",
            "applied_by_id",
            "applied_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {"title", "justification", "model_name", "line_ids"}
        return locked

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"model_name"}

    def _approval_needed(self) -> bool:
        return self.state == "submitted"

    def _approval_excluded(self):
        return super()._approval_excluded() | self.submitted_by_id

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"name": "BULK/%05d" % rec.id})
        return records

    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    def write(self, vals):
        if self and not self._fix_guard_open():
            moved = self.filtered(lambda r: r.state != "draft")
            frozen = {"title", "justification", "model_name", "line_ids"}
            if (moved and frozen & set(vals)) and (
                "line_ids" in vals
                or any(
                    rec._fix_guard_differs(name, vals[name], rec[name])
                    for rec in moved
                    for name in frozen & set(vals) - {"line_ids"}
                )
            ):
                raise UserError(
                    "%s is %s: the set reviewed is the set applied. Cancel it and raise a "
                    "new one." % (moved[:1].name, moved[:1].state)
                )
        return super().write(vals)

    def _checked_lines(self):
        """[(line, target, changes)] for every line, each meeting every check."""
        self.ensure_one()
        out, seen = [], set()
        self._mdm_assert_governed(self.model_name, (), self.name)
        for line in self.line_ids:
            label = "%s line %s" % (self.name, line.record_id)
            if line.record_id in seen:
                raise ValidationError("%s names record %s twice." % (self.name, line.record_id))
            seen.add(line.record_id)
            target = self.env[self.model_name].browse(line.record_id).exists()
            if not target:
                raise ValidationError(
                    "%s: no %s with id %s exists." % (self.name, self.model_name, line.record_id)
                )
            changes = self._mdm_parse_payload(line.proposed_changes, self.model_name, label)
            self._mdm_check_payload(target, changes, self.company_id, label)
            out.append((line, target, changes))
        return out

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft set can be submitted (%s)." % rec.name)
            if not rec.line_ids:
                raise UserError("%s holds no records." % rec.name)
            checked = rec._checked_lines()
            fields_touched = set()
            preview = []
            for line, target, changes in checked:
                # a value that cannot be written never reaches a steward
                rec._mdm_dry_run(target, changes, rec.name)
                line.sudo().write({"current_values": rec._mdm_snapshot(target, changes)})
                fields_touched |= set(changes)
                preview.append(
                    "%s: %s"
                    % (
                        target.display_name,
                        ", ".join("%s -> %s" % (k, v) for k, v in sorted(changes.items())),
                    )
                )
            head = "%d record(s) of %s; fields: %s." % (
                len(checked),
                rec.model_name,
                ", ".join(sorted(fields_touched)),
            )
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by_id": self.env.uid,
                    "preview": "\n".join([head] + preview[:200]),
                }
            )
            rec.message_post(body="Submitted by %s. %s" % (self.env.user.name, head))
        return True

    def action_request_approval(self, justification=None):
        return super().action_request_approval(
            justification=justification or self[:1].justification
        )

    def _decision_checks(self):
        authority = self._approval_authority_user()
        if not (self.env.su and not self._approval_task()) and not _is_steward(authority):
            raise UserError(
                "Deciding a bulk change needs the 'MDM Domain Steward' group, which %s does "
                "not hold." % authority.name
            )
        acting = self._approval_acting_users()
        if (self.submitted_by_id | self.create_uid) & acting:
            raise UserError(
                "Segregation of duties: you raised %s, so a different steward decides it."
                % self.name
            )

    def action_approve(self):
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted set can be approved (%s)." % rec.name)
            rec._decision_checks()
            rec.sudo()._guarded().write({"state": "approved", "reviewed_by_id": self.env.uid})
            rec.sudo().message_post(body="Approved as a set by %s." % self.env.user.name)
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            if rec.state == "submitted":
                rec.sudo()._guarded().write({"state": "rejected", "reviewed_by_id": self.env.uid})
                rec.sudo().message_post(body="Rejected: %s" % (comment or "no reason given"))

    def action_apply(self):
        """BRU-MDM-08: every record or none. One savepoint around the set."""
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved set can be applied (%s)." % rec.name)
            if not (self.env.su and not self._approval_task()) and not _is_steward(self.env.user):
                raise UserError("Applying a bulk change needs the 'MDM Domain Steward' group.")
            with self.env.cr.savepoint():
                for line, target, changes in rec._checked_lines():
                    rec._mdm_assert_fresh(target, changes, line.current_values, rec.name)
                    rec._mdm_write(target, changes, "%s line %s" % (rec.name, line.record_id))
            rec._guarded().write(
                {
                    "state": "applied",
                    "applied_by_id": self.env.uid,
                    "applied_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Applied by %s: %d record(s) written as one set."
                % (self.env.user.name, len(rec.line_ids))
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state in BULK_TERMINAL:
                raise UserError("%s is closed." % rec.name)
            if rec.approval_state == "pending":
                raise UserError("Recall the approval request before cancelling.")
            if rec.state == "approved":
                rec._approval_void("the approved set was cancelled before it was applied")
            rec._guarded().write({"state": "cancelled"})
        return True


class FixMdmChangeBatchLine(models.Model):
    _name = "fix.mdm.change.batch.line"
    _description = "Bulk Change Record"
    _order = "batch_id, id"

    batch_id = fields.Many2one(
        "fix.mdm.change.batch", required=True, index=True, ondelete="cascade"
    )
    record_id = fields.Integer(string="Record ID", required=True)
    proposed_changes = fields.Text(
        string="Proposed Changes", required=True, help="field=value per line, or a JSON object"
    )
    target_name = fields.Char(string="Record", compute="_compute_target_name")
    current_values = fields.Text(string="Values at Submit", readonly=True)

    def _compute_target_name(self):
        for rec in self:
            model = rec.batch_id.model_name
            target = (
                self.env[model].sudo().browse(rec.record_id).exists()
                if model in self.env and rec.record_id
                else None
            )
            rec.target_name = target.display_name if target else False

    def _assert_draft(self, batches):
        if not self.env.su and batches.filtered(lambda b: b.state != "draft"):
            raise UserError("The records of a submitted set cannot change: cancel and raise again.")

    @api.model_create_multi
    def create(self, vals_list):
        self._assert_draft(
            self.env["fix.mdm.change.batch"].browse(
                [v.get("batch_id") for v in vals_list if v.get("batch_id")]
            )
        )
        for vals in vals_list:
            if "current_values" in vals and not self.env.su:
                vals.pop("current_values")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            if "current_values" in vals:
                raise UserError("The submitted values are measured, never typed.")
            self._assert_draft(self.mapped("batch_id"))
        return super().write(vals)

    def unlink(self):
        self._assert_draft(self.mapped("batch_id"))
        return super().unlink()
