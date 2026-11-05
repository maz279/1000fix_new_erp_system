# fix_platform_ops — M30 (announcements), M64 (MDM: steward/DQ/code lists),
# M65 (locale packs, jurisdiction rules). Branch/entity/config/feature-flag/
# country-pack models live in the sibling files of this module.
#
# A12 audit (2026-11-04), M64/M65 P1-2/P1-4/R4:
#   * fix.mdm.steward approved itself, kept no proposed values, and never
#     touched the record it governed. It now carries the proposed payload,
#     requires the MDM Domain Steward group IN CODE (an ACL cannot express
#     "a different steward than the proposer"), refuses the proposer's own
#     decision, and applies approved values through a separate sudo() step.
#     (The M63 routing lives in cd_mdm_core, which may depend on the
#     workflow engine - this module cannot.)
#   * fix.mdm.dq.rule had no evaluator: the DQ dashboard showed assertions.
#     cron_evaluate_dq_rules() (pinned by the lead's ir.cron) now measures
#     completeness/uniqueness/format/range/referential and records the
#     results on the rule; a rule for a missing model/field is SKIPPED with
#     a note, never a crash (DQ-PARTY-002).
#   * fix.mdm.code.list entries were editable after publication: a published
#     governed list is now FROZEN - changes go through a new version.
#   * fix.locale.pack activated from any state; activation is now a guarded
#     draft->active transition with a minimum translation coverage gate.
import json
import logging
import re
from collections import Counter

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)

STEWARD_GROUP = "cd_entity_config.group_mdm_domain_steward"


def _require_steward_group(env, what):
    """Code check for the coded steward group - the ACL grants access, this
    guards the decision (P1-2: ACL alone is not enough). Superuser code
    (crons, migrations) is trusted."""
    if env.su:
        return
    if not env.user.has_group(STEWARD_GROUP):
        raise UserError(
            "%s requires the 'MDM Domain Steward' role, which %s does not hold."
            % (what, env.user.name)
        )


class FixPlatformAnnouncement(models.Model):
    _name = "fix.platform.announcement"
    _description = "Platform Announcement"
    _inherit = ["fix.guarded.mixin"]
    _order = "publish_on desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    severity = fields.Selection(
        [("info", "Information"), ("warning", "Warning"), ("critical", "Critical")],
        required=True,
        default="info",
    )
    body = fields.Text()
    publish_on = fields.Date(required=True, default=fields.Date.context_today)
    expires_on = fields.Date()
    audience = fields.Selection(
        [("all", "All users"), ("internal", "Internal only"), ("technicians", "Field technicians")],
        required=True,
        default="all",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    def action_publish(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Publish a draft announcement")
            rec._guarded().write({"state": "published"})

    def action_retire(self):
        for rec in self:
            if rec.state == "retired":
                raise UserError("The announcement is already retired")
            rec._guarded().write({"state": "retired"})


class FixMdmSteward(models.Model):
    """A data-steward request over a master record.

    The request holds the PROPOSED values (proposed_changes JSON); it never
    writes the live record directly. A different steward than the proposer
    decides it, and only then does action_apply write the target under sudo,
    inside a savepoint, after re-validating the payload.
    """

    _name = "fix.mdm.steward"
    _description = "Data Steward Request"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "created_at desc, id desc"

    name = fields.Char(required=True, default="New", tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    request_type = fields.Selection(
        [
            ("create", "Create Record"),
            ("update", "Update Record"),
            ("merge", "Merge Duplicates"),
            ("deactivate", "Deactivate"),
        ],
        required=True,
        default="update",
        tracking=True,
    )
    res_model = fields.Char(string="Master Model", required=True, index=True)
    record_ref = fields.Char(
        string="Record Reference", help="The target's database id or reference"
    )
    reason = fields.Text(required=True)
    proposed_changes = fields.Text(
        string="Proposed Changes (JSON)",
        help="JSON object of {field: new_value} the steward is asked to approve",
    )
    requested_by_id = fields.Many2one(
        "hr.employee",
        string="Requested By",
        default=lambda self: self.env.user.employee_id,
        index=True,
    )
    steward_id = fields.Many2one("hr.employee", string="Assigned Steward", index=True)
    created_at = fields.Datetime(required=True, default=fields.Datetime.now)
    decided_at = fields.Datetime()
    decision_note = fields.Char()
    applied_by = fields.Many2one("res.users", string="Applied By", readonly=True, copy=False)
    applied_at = fields.Datetime(string="Applied At", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("submitted", "Submitted"),
            ("in_review", "In Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("applied", "Applied"),
        ],
        required=True,
        default="submitted",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "decided_at",
            "decision_note",
            "applied_by",
            "applied_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "submitted":
            locked |= {"res_model", "record_ref", "proposed_changes", "request_type"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.mdm.steward") or "STE/New"
        return super().create(vals_list)

    # ---- target / payload validation --------------------------------------
    def _target_record(self):
        self.ensure_one()
        if self.res_model not in self.env:
            raise ValidationError(
                "Master model %r does not exist, so steward request %s cannot govern it."
                % (self.res_model, self.name)
            )
        ref = (self.record_ref or "").strip()
        if not ref.isdigit():
            raise ValidationError(
                "Steward request %s needs a record reference that is the target's database id."
                % self.name
            )
        record = self.env[self.res_model].browse(int(ref)).exists()
        if not record:
            raise ValidationError(
                "No %s with id %s exists (steward request %s)." % (self.res_model, ref, self.name)
            )
        return record

    def _proposed_values(self) -> dict:
        self.ensure_one()
        if not self.proposed_changes:
            raise ValidationError(
                "Steward request %s carries no proposed values: nothing to approve." % self.name
            )
        try:
            changes = json.loads(self.proposed_changes)
        except ValueError as exc:
            raise ValidationError(
                "Proposed changes of %s are not valid JSON: %s" % (self.name, exc)
            ) from exc
        if not isinstance(changes, dict) or not changes:
            raise ValidationError(
                "Steward request %s must propose a JSON object of {field: value}." % self.name
            )
        return changes

    @api.constrains("res_model", "record_ref", "proposed_changes")
    def _check_target_and_payload(self):
        for rec in self:
            if not rec.proposed_changes:
                continue  # a request may be raised before the payload is attached
            changes = rec._proposed_values()
            target_model = self.env.get(rec.res_model)
            if target_model is None:
                raise ValidationError(
                    "Master model %r does not exist (steward request %s)."
                    % (rec.res_model, rec.name)
                )
            unknown = sorted(set(changes) - set(target_model._fields))
            if unknown:
                raise ValidationError(
                    "%s has no field(s) %s (steward request %s)."
                    % (rec.res_model, ", ".join(unknown), rec.name)
                )

    # ---- lifecycle ---------------------------------------------------------
    def action_review(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Review a submitted request")
            rec._guarded().write({"state": "in_review"})

    def _decision_checks(self, rec):
        """P1-2: a coded-group steward who is NOT the proposer decides."""
        _require_steward_group(self.env, "Deciding a data steward request")
        acting = self.env.user
        proposer_users = rec.requested_by_id.user_id | rec.create_uid
        if not self.env.su and acting in proposer_users:
            raise UserError(
                "Segregation of duties: you raised steward request %s, so a "
                "different MDM domain steward must decide it." % rec.name
            )

    def action_approve(self):
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Approve a request in review")
            rec._decision_checks(rec)
            # an approval with nothing to apply is a note, not a decision
            if rec.request_type == "update":
                rec._proposed_values()
            rec._guarded().write({"state": "approved", "decided_at": fields.Datetime.now()})
            rec.message_post(body="Approved by %s." % self.env.user.name)

    def action_reject(self):
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Reject a request in review")
            rec._decision_checks(rec)
            if not (rec.decision_note or "").strip():
                raise UserError("Give a decision note when rejecting a steward request.")
            rec._guarded().write({"state": "rejected", "decided_at": fields.Datetime.now()})

    def action_apply(self):
        """The separate sudo() apply step AFTER the checks (P1-2).

        Re-validates the payload, writes the target inside a savepoint, and
        stamps who applied what and when."""
        for rec in self:
            if rec.state != "approved":
                raise UserError(
                    "Only an approved steward request can be applied (state=%s)." % rec.state
                )
            _require_steward_group(self.env, "Applying a data steward request")
            if rec.request_type == "update":
                changes = rec._proposed_values()
                target = rec._target_record()
                unknown = sorted(set(changes) - set(target._fields))
                if unknown:
                    raise ValidationError(
                        "%s no longer carries field(s) %s; re-raise the request."
                        % (rec.res_model, ", ".join(unknown))
                    )
                with rec.env.cr.savepoint():
                    # sudo: the steward holds the decision, not write access to
                    # the governed master.
                    target.sudo().write(changes)
            rec._guarded().write(
                {
                    "state": "applied",
                    "applied_by": rec.env.uid,
                    "applied_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Applied by %s (state=%s)." % (rec.env.user.name, rec.state))


class FixMdmDqRule(models.Model):
    _name = "fix.mdm.dq.rule"
    _description = "Data Quality Rule"
    _inherit = ["fix.guarded.mixin"]
    _order = "code"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    res_model = fields.Char(string="Master Model", required=True)
    field_name = fields.Char(required=True)
    rule_type = fields.Selection(
        [
            ("completeness", "Completeness"),
            ("uniqueness", "Uniqueness"),
            ("format", "Format"),
            ("range", "Range"),
            ("referential", "Referential"),
        ],
        required=True,
        default="completeness",
    )
    expression = fields.Char(required=True, help="The checked condition, e.g. 'not null'")
    severity = fields.Selection(
        [("critical", "Critical"), ("major", "Major"), ("minor", "Minor")],
        required=True,
        default="major",
    )
    active = fields.Boolean(default=True)

    # ---- evaluator results (M64 dq_03): MEASURED, never assumed ------------
    last_run_at = fields.Datetime(string="Last Evaluation", readonly=True, copy=False)
    last_status = fields.Selection(
        [("ok", "Evaluated"), ("skipped", "Skipped"), ("error", "Error")],
        string="Last Status",
        readonly=True,
        copy=False,
    )
    last_violation_count = fields.Integer(string="Last Violations", readonly=True, copy=False)
    last_records_checked = fields.Integer(string="Records Checked", readonly=True, copy=False)
    last_note = fields.Char(string="Last Note", readonly=True, copy=False)

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A DQ rule code is unique per company"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "last_run_at",
            "last_status",
            "last_violation_count",
            "last_records_checked",
            "last_note",
        }

    @api.constrains("res_model", "field_name")
    def _check_target_exists(self):
        # dq_01: a rule against a model/field that is not there can never
        # fire, yet used to count as a passing check. Refused at entry now;
        # rows that predate this (e.g. DQ-PARTY-002 against the nonexistent
        # res.partner.mobile) are skipped WITH A NOTE by the evaluator.
        for rec in self:
            if rec.res_model not in self.env:
                raise ValidationError(
                    "DQ rule %s targets model %r, which does not exist." % (rec.code, rec.res_model)
                )
            if rec.field_name not in self.env[rec.res_model]._fields:
                raise ValidationError(
                    "%s has no field %r: DQ rule %s cannot check it."
                    % (rec.res_model, rec.field_name, rec.code)
                )

    # ---- the evaluator ------------------------------------------------------
    def _skip(self, note):
        self._guarded().write(
            {
                "last_run_at": fields.Datetime.now(),
                "last_status": "skipped",
                "last_violation_count": 0,
                "last_records_checked": 0,
                "last_note": note[:380],
            }
        )
        logger.info("DQ rule %s skipped: %s", self.code, note)

    def _record(self, violations, checked, note=""):
        self._guarded().write(
            {
                "last_run_at": fields.Datetime.now(),
                "last_status": "ok",
                "last_violation_count": violations,
                "last_records_checked": checked,
                "last_note": note[:380] or False,
            }
        )

    def _error(self, exc):
        self._guarded().write(
            {
                "last_run_at": fields.Datetime.now(),
                "last_status": "error",
                "last_violation_count": 0,
                "last_records_checked": 0,
                "last_note": ("evaluation error: %s" % exc)[:380],
            }
        )
        logger.exception("DQ rule %s failed", self.code)

    def _evaluate_one(self):
        self.ensure_one()
        if self.res_model not in self.env:
            return self._skip("model %r is not installed" % self.res_model)
        model = self.env[self.res_model]
        if self.field_name not in model._fields:
            return self._skip("%s has no field %r" % (self.res_model, self.field_name))
        field = model._fields[self.field_name]
        # the evaluator reads the whole governed master, not the caller's slice
        records = model.sudo().search([])
        total = len(records)

        if self.rule_type == "completeness":
            violations = sum(1 for rec in records if not rec[self.field_name])
            return self._record(violations, total)

        if self.rule_type == "uniqueness":
            values = [rec[self.field_name] for rec in records]
            keyed = [v for v in values if v not in (None, False, "")]
            counts = Counter(keyed)
            # every extra occurrence of a shared key is one violation
            violations = sum(c - 1 for c in counts.values() if c > 1)
            return self._record(violations, total)

        if self.rule_type == "format":
            pattern = self.expression or ""
            try:
                re.compile(pattern)
            except re.error as exc:
                return self._skip("invalid format expression %r (%s)" % (pattern, exc))
            # empty values are the completeness rule's business; here they are
            # not format violations
            violations = sum(
                1
                for rec in records
                if rec[self.field_name] not in (None, False, "")
                and not re.fullmatch(pattern, str(rec[self.field_name]))
            )
            return self._record(violations, total)

        if self.rule_type == "range":
            if field.type not in ("integer", "float", "monetary"):
                return self._skip(
                    "range rule on non-numeric field %s.%s (%s)"
                    % (self.res_model, self.field_name, field.type)
                )
            low, _, high = (self.expression or "").partition("..")
            try:
                lo = float(low) if low.strip() else None
                hi = float(high) if high.strip() else None
            except ValueError:
                return self._skip("range expression must look like 'min..max'")
            violations = sum(
                1
                for rec in records
                if (lo is not None and rec[self.field_name] < lo)
                or (hi is not None and rec[self.field_name] > hi)
            )
            return self._record(violations, total)

        if self.rule_type == "referential":
            if field.type != "many2one":
                return self._skip(
                    "referential rule on non-relational field %s.%s (%s)"
                    % (self.res_model, self.field_name, field.type)
                )
            violations = sum(
                1 for rec in records if rec[self.field_name] and not rec[self.field_name].exists()
            )
            return self._record(violations, total)

        return self._skip("unknown rule type %r" % self.rule_type)

    def action_evaluate(self):
        for rule in self:
            try:
                rule._evaluate_one()
            except Exception as exc:  # one bad rule must not stop the batch
                rule._error(exc)
        return True

    @api.model
    def cron_evaluate_dq_rules(self):
        """Pinned by the lead's ir.cron (daily): evaluate every active DQ rule
        and record the measured result on the rule. Never raises - a rule
        that cannot run is recorded as skipped/error, not a dead cron."""
        rules = self.sudo().search([("active", "=", True)])
        for rule in rules:
            try:
                rule.sudo().action_evaluate()
            except Exception:
                logger.exception("DQ cron: rule %s raised", rule.code)
        return True


class FixMdmCodeList(models.Model):
    _name = "fix.mdm.code.list"
    _description = "Governed Code List"
    _inherit = ["fix.guarded.mixin"]
    _order = "code"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    domain_area = fields.Char(string="Domain (e.g. currency, country, unit)")
    version = fields.Char(default="1.0", help="Semantic version of the list's contents")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    published_on = fields.Date(readonly=True, copy=False)
    entry_ids = fields.One2many("fix.mdm.code.entry", "list_id", string="Entries")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "published_on"}

    def action_publish(self):
        """P1-2: once published, a governed code list is FROZEN - its values
        are the contract other systems code against. Corrections ship as a
        new version, never as a silent edit."""
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft code list can be published (%s is %s)." % (rec.code, rec.state)
                )
            if not rec.entry_ids:
                raise UserError("Publish a code list with at least one entry.")
            rec._guarded().write(
                {"state": "published", "published_on": fields.Date.context_today(rec)}
            )

    def action_retire(self):
        for rec in self:
            if rec.state == "retired":
                raise UserError("The code list is already retired")
            rec._guarded().write({"state": "retired"})

    def action_new_version(self):
        """Copy this published list into a fresh draft with a bumped version:
        the frozen published list keeps serving while the successor is built."""
        new_lists = self.browse()
        for rec in self:
            if rec.state != "published":
                raise UserError(
                    "A new version is cut from the published list (%s is %s)."
                    % (rec.code, rec.state)
                )
            try:
                major = int((rec.version or "1").split(".")[0])
                new_version = "%d.0" % (major + 1)
            except ValueError:
                new_version = "2.0"
            new_list = rec.copy(
                {
                    "code": "%s-v%s" % (rec.code, new_version),
                    "name": "%s (v%s)" % (rec.name, new_version),
                    "version": new_version,
                    "state": "draft",
                    "published_on": False,
                }
            )
            rec.entry_ids.copy({"list_id": new_list.id})
            new_lists |= new_list
        return new_lists

    def _entries_frozen(self):
        """True when any list in self is published and no guard token is held."""
        frozen = self.filtered(lambda rec: rec.state == "published")
        return bool(frozen) and not frozen._fix_guard_open()


class FixMdmCodeEntry(models.Model):
    _name = "fix.mdm.code.entry"
    _description = "Code List Entry"
    _order = "list_id, value"

    list_id = fields.Many2one("fix.mdm.code.list", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="list_id.company_id", store=True, index=True)
    value = fields.Char(required=True)
    label = fields.Char(required=True)
    label_bn = fields.Char(string="Label (Bengali)")
    active = fields.Boolean(default=True)

    _value_unique = models.Constraint(
        "UNIQUE (list_id, value)", "A code value is unique inside its list"
    )

    def _check_lists_mutable(self, lists):
        frozen = lists.filtered(lambda rec: rec.state == "published")
        if frozen and not frozen._fix_guard_open():
            raise UserError(
                "Code list %s is published: its entries are frozen. Cut a new "
                "version (action_new_version) instead of editing the contract."
                % ", ".join(frozen.mapped("code")[:3])
            )

    @api.model_create_multi
    def create(self, vals_list):
        lists = self.env["fix.mdm.code.list"].browse(
            {vals["list_id"] for vals in vals_list if vals.get("list_id")}
        )
        self._check_lists_mutable(lists)
        return super().create(vals_list)

    def write(self, vals):
        if self:
            self._check_lists_mutable(self.mapped("list_id"))
        return super().write(vals)

    def unlink(self):
        if self:
            self._check_lists_mutable(self.mapped("list_id"))
        return super().unlink()


class FixLocalePack(models.Model):
    _name = "fix.locale.pack"
    _description = "Locale Pack"
    _inherit = ["fix.guarded.mixin"]
    _order = "code"

    code = fields.Char(required=True, help="e.g. bn_BD, en_US")
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    number_format = fields.Selection(
        [("en_in", "Indian grouping (1,00,000)"), ("en_us", "Western grouping (100,000)")],
        default="en_in",
        required=True,
    )
    first_day_of_week = fields.Selection(
        [("6", "Saturday"), ("0", "Monday")],
        default="6",
        required=True,
        string="First Day of Week",
    )
    date_format = fields.Char(default="DD/MM/YYYY", required=True)
    coverage_pct = fields.Integer(
        string="Translation Coverage %",
        help="Measured coverage of the pack against the source strings.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A locale code is unique per company"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    @api.model
    def _min_activation_coverage(self) -> int:
        # Business decision (M65 lc_02), tunable: the coverage an incomplete
        # pack must reach before it may serve users.
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fix_locale.min_activation_coverage_pct", "100")
        )

    def action_activate(self):
        """M65 lc_01: a guarded draft->active transition. Re-activating a
        retired pack or activating from active is refused - the pack's
        retirement/replacement is a decision, not a button away."""
        minimum = self._min_activation_coverage()
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft locale pack can be activated (%s is %s)." % (rec.code, rec.state)
                )
            if (rec.coverage_pct or 0) < minimum:
                raise UserError(
                    "Locale pack %s covers %s%% of source strings; activation "
                    "requires at least %s%% (ir.config_parameter "
                    "fix_locale.min_activation_coverage_pct)."
                    % (rec.code, rec.coverage_pct or 0, minimum)
                )
            rec._guarded().write({"state": "active"})

    def action_retire(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Retire an active locale pack (%s is %s)." % (rec.code, rec.state))
            rec._guarded().write({"state": "retired"})


class FixJurisdictionRule(models.Model):
    _name = "fix.jurisdiction.rule"
    _description = "Jurisdiction Rule"
    _order = "jurisdiction"

    jurisdiction = fields.Char(required=True, help="e.g. BD-NBR, BD-DIFE, City Corporation")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rule_area = fields.Selection(
        [
            ("tax", "Tax"),
            ("labour", "Labour"),
            ("fire", "Fire Safety"),
            ("environment", "Environment"),
            ("data", "Data Protection"),
        ],
        required=True,
        default="tax",
    )
    requirement = fields.Char(required=True)
    frequency = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
            ("event", "Event-Driven"),
        ],
        required=True,
        default="annual",
    )
    authority = fields.Char()
    penalty = fields.Char(string="Penalty for Non-Compliance")
    active = fields.Boolean(default=True)
