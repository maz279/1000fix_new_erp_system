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
    """A12 finish E15: the author no longer publishes alone, dates must make
    sense, a maintenance notice carries its lead time (BRU-ADM-19), and users
    acknowledge it on the announcement screen. That screen is the only consumer:
    no banner pushes an announcement into other screens."""

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
    kind = fields.Selection(
        [("general", "General"), ("maintenance", "Planned Maintenance")],
        required=True,
        default="general",
    )
    maintenance_start = fields.Datetime(
        help="When the maintenance window opens: publishing needs the configured lead time "
        "(ir.config_parameter fix_announcement.maintenance_lead_hours, default 72)."
    )
    published_by_id = fields.Many2one("res.users", string="Published By", readonly=True, copy=False)
    ack_ids = fields.One2many("fix.platform.announcement.ack", "announcement_id", readonly=True)
    acknowledged_count = fields.Integer(string="Acknowledged", compute="_compute_acknowledgements")
    acknowledged_by_me = fields.Boolean(
        string="Acknowledged By Me", compute="_compute_acknowledgements"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "published_by_id"}

    @api.depends_context("uid")
    def _compute_acknowledgements(self):
        Ack = self.env["fix.platform.announcement.ack"].sudo()
        for rec in self:
            acks = Ack.search([("announcement_id", "=", rec.id)]) if rec.id else Ack
            rec.acknowledged_count = len(acks)
            rec.acknowledged_by_me = self.env.uid in acks.user_id.ids

    @api.constrains("publish_on", "expires_on")
    def _check_dates(self):
        for rec in self:
            if rec.expires_on and rec.publish_on and rec.expires_on < rec.publish_on:
                raise ValidationError("An announcement cannot expire before it is published.")

    def action_publish(self):
        lead = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fix_announcement.maintenance_lead_hours", "72")
        )
        for rec in self:
            if rec.state != "draft":
                raise UserError("Publish a draft announcement")
            if not rec.env.su and rec.env.user == rec.create_uid:
                raise UserError(
                    "A second person publishes: you wrote '%s'. Ask another Platform Admin "
                    "to review and publish it." % rec.name
                )
            if rec.kind == "maintenance":
                if not rec.maintenance_start:
                    raise UserError("State when the maintenance window of '%s' opens." % rec.name)
                hours = (rec.maintenance_start - fields.Datetime.now()).total_seconds() / 3600.0
                if hours < lead:
                    raise UserError(
                        "Planned maintenance is announced %d hours ahead (BRU-ADM-19): "
                        "'%s' opens in %.0f hours. Move the window or the date."
                        % (lead, rec.name, hours)
                    )
            rec._guarded().write({"state": "published", "published_by_id": rec.env.uid})

    def action_retire(self):
        for rec in self:
            if rec.state == "retired":
                raise UserError("The announcement is already retired")
            rec._guarded().write({"state": "retired"})

    def action_acknowledge(self):
        """The reader says they have seen it. Sudo after the check: no user
        needs write access to the acknowledgement register."""
        Ack = self.env["fix.platform.announcement.ack"].sudo()
        for rec in self:
            if rec.state != "published":
                raise UserError("Only a published announcement can be acknowledged.")
            done = Ack.search_count(
                [("announcement_id", "=", rec.id), ("user_id", "=", self.env.uid)]
            )
            if not done:
                Ack.create({"announcement_id": rec.id, "user_id": self.env.uid})
        return True


class FixPlatformAnnouncementAck(models.Model):
    _name = "fix.platform.announcement.ack"
    _description = "Platform Announcement Acknowledgement"
    _order = "acknowledged_at desc"

    announcement_id = fields.Many2one(
        "fix.platform.announcement", required=True, ondelete="cascade", index=True
    )
    user_id = fields.Many2one("res.users", required=True, ondelete="cascade", index=True)
    acknowledged_at = fields.Datetime(required=True, default=fields.Datetime.now)

    _one_per_user = models.Constraint(
        "UNIQUE (announcement_id, user_id)", "A user acknowledges an announcement once."
    )


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
            # Refused at entry (cd_mdm_core): kept so old rows still read.
            ("create", "Create Record (not available)"),
            ("update", "Update Record"),
            ("merge", "Merge Duplicates"),
            ("deactivate", "Deactivate"),
        ],
        required=True,
        default="update",
        tracking=True,
    )
    res_model = fields.Char(string="Master Model", required=True, index=True)
    record_ref = fields.Char(string="Record ID", help="The target's database id")
    reason = fields.Text(required=True)
    proposed_changes = fields.Text(
        string="Proposed Changes",
        help="One field=value per line, or a JSON object, the steward is asked to approve",
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

    # Payload parsing, the governed register and the request-type checks are in
    # cd_mdm_core (fix_mdm_steward_approval.py), which holds the register.
    def _proposed_values(self) -> dict:
        raise UserError("The MDM governance core (cd_mdm_core) is not installed.")

    def _steward_review_stamp(self):
        raise UserError("The MDM governance core (cd_mdm_core) is not installed.")

    def _apply_to_target(self):
        raise UserError("The MDM governance core (cd_mdm_core) is not installed.")

    # ---- lifecycle ---------------------------------------------------------
    def action_review(self):
        """E14: another steward starts the review, never the requester. The
        request is complete from here on: target, payload and a snapshot."""
        _require_steward_group(self.env, "Reviewing a data steward request")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Review a submitted request")
            if not self.env.su and self.env.user in (rec.requested_by_id.user_id | rec.create_uid):
                raise UserError(
                    "Segregation of duties: you raised steward request %s, so a "
                    "different MDM domain steward starts its review." % rec.name
                )
            rec._guarded().write({"state": "in_review", **rec._steward_review_stamp()})

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
            outcome = rec._apply_to_target()
            rec._guarded().write(
                {
                    "state": "applied",
                    "applied_by": rec.env.uid,
                    "applied_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Applied by %s: %s." % (rec.env.user.name, outcome))


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
        if not self.env.su:
            raise UserError("The data-quality cron runs as the system only.")
        rules = self.sudo().search([("active", "=", True)])
        for rule in rules:
            try:
                rule.sudo().action_evaluate()
            except Exception:
                logger.exception("DQ cron: rule %s raised", rule.code)
        return True


class FixMdmCodeList(models.Model):
    """A governed list, versioned: one code, one live version.

    A12 finish audit (E24-E26): a published or retired list is frozen, header
    and values. A second person publishes (the author and contributors do not),
    and publishing a new version retires the one it supersedes. Other systems
    read through values_for / label_for rather than keeping private copies
    (BRU-MDM-14, BRU-MDM-17)."""

    _name = "fix.mdm.code.list"
    _description = "Governed Code List"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "code, version desc"

    _code_version_unique = models.Constraint(
        "UNIQUE (code, version, company_id)", "A list code carries each version once per company"
    )

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
    effective_from = fields.Date(
        help="First day this version applies. Blank at publication means the publication date."
    )
    effective_to = fields.Date(
        readonly=True, copy=False, help="Set when the version is superseded or retired."
    )
    superseded_by_id = fields.Many2one(
        "fix.mdm.code.list", string="Superseded By", readonly=True, copy=False
    )
    entry_ids = fields.One2many("fix.mdm.code.entry", "list_id", string="Entries")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "published_on",
            "effective_to",
            "superseded_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {"code", "name", "domain_area", "version", "effective_from"}
        return locked

    def write(self, vals):
        # E24: the frozen contract includes its header. Same-value posts pass:
        # the P03 form posts every field it shows.
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                changed = [
                    name
                    for name in vals
                    if name in rec._fields
                    and name not in self._FROZEN_LIST_FREE
                    and rec._fix_guard_differs(name, vals[name], rec[name])
                ]
                if changed:
                    raise UserError(
                        "Code list %s is %s: it is frozen. Cut a new version instead."
                        % (rec.code, rec.state)
                    )
        return super().write(vals)

    _FROZEN_LIST_FREE = frozenset(
        {"message_follower_ids", "message_ids", "message_main_attachment_id"}
    )

    def unlink(self):
        # BRU-MDM-13: a value that was ever published stays resolvable.
        frozen = self.filtered(lambda r: r.state != "draft")
        if frozen and not self._fix_guard_open():
            raise UserError(
                "Code list %s was published: it is retired, never deleted."
                % ", ".join(frozen.mapped("code")[:3])
            )
        return super().unlink()

    def _publication_conflict(self):
        """E25: who built this draft does not also publish it."""
        self.ensure_one()
        if self.env.su:
            return False
        builders = (
            self.create_uid
            | self.write_uid
            | self.entry_ids.mapped("create_uid")
            | self.entry_ids.mapped("write_uid")
        )
        return self.env.user in builders

    def action_publish(self):
        """P1-2: once published, a governed code list is FROZEN - its values
        are the contract other systems code against. Corrections ship as a
        new version, never as a silent edit. A second person publishes, and
        the version this one succeeds retires in the same step."""
        _require_steward_group(self.env, "Publishing a code list")
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft code list can be published (%s is %s)." % (rec.code, rec.state)
                )
            if not rec.entry_ids:
                raise UserError("Publish a code list with at least one entry.")
            if rec._publication_conflict():
                raise UserError(
                    "Segregation of duties: you built code list %s, so a different MDM "
                    "domain steward publishes it." % rec.code
                )
            today = fields.Date.context_today(rec)
            starts = rec.effective_from or today
            predecessors = self.search(
                [
                    ("code", "=", rec.code),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "published"),
                    ("id", "!=", rec.id),
                ]
            )
            predecessors._guarded().write(
                {"state": "retired", "effective_to": starts, "superseded_by_id": rec.id}
            )
            rec._guarded().write(
                {"state": "published", "published_on": today, "effective_from": starts}
            )
            rec.message_post(
                body="Published by %s, effective %s%s."
                % (
                    self.env.user.name,
                    starts,
                    "; supersedes version %s" % ", ".join(predecessors.mapped("version"))
                    if predecessors
                    else "",
                )
            )
            for old in predecessors:
                old.message_post(body="Superseded by version %s." % rec.version)

    def action_retire(self):
        _require_steward_group(self.env, "Retiring a code list")
        for rec in self:
            if rec.state == "retired":
                raise UserError("The code list is already retired")
            rec._guarded().write(
                {"state": "retired", "effective_to": fields.Date.context_today(rec)}
            )
            rec.message_post(body="Retired by %s." % self.env.user.name)

    # ---- the read API other modules use (BRU-MDM-14, BRU-MDM-17) -----------
    @api.model
    def _version_on(self, code, on_date=None, company=None):
        """The version of `code` in force on a date: published or later retired,
        so a historic document still resolves."""
        on_date = fields.Date.to_date(on_date) or fields.Date.context_today(self)
        company = company or self.env.company
        versions = self.sudo().search(
            [
                ("code", "=", code),
                ("company_id", "=", company.id),
                ("state", "in", ("published", "retired")),
            ]
        )
        in_force = versions.filtered(
            lambda v: (not v.effective_from or v.effective_from <= on_date)
            and (not v.effective_to or on_date < v.effective_to)
        )
        return in_force.sorted(lambda v: v.effective_from or fields.Date.to_date("1900-01-01"))[-1:]

    @api.model
    def values_for(self, code, on_date=None, company=None) -> list:
        """The values of `code` in force on a date: [{value, label, label_bn}]."""
        on_date = fields.Date.to_date(on_date) or fields.Date.context_today(self)
        entries = self._version_on(code, on_date, company).entry_ids.filtered(
            lambda e: e.active
            and (not e.effective_from or e.effective_from <= on_date)
            and (not e.effective_to or on_date < e.effective_to)
        )
        return [{"value": e.value, "label": e.label, "label_bn": e.label_bn} for e in entries]

    @api.model
    def label_for(self, code, value, company=None):
        """The label of a stored value, whichever version last held it: a value
        once published stays resolvable (BRU-MDM-13). None when it never existed."""
        company = company or self.env.company
        entry = (
            self.env["fix.mdm.code.entry"]
            .sudo()
            .with_context(active_test=False)
            .search(
                [
                    ("list_id.code", "=", code),
                    ("list_id.company_id", "=", company.id),
                    ("list_id.state", "in", ("published", "retired")),
                    ("value", "=", value),
                ],
                order="id desc",
                limit=1,
            )
        )
        return entry.label if entry else None

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
            if self.search_count(
                [
                    ("code", "=", rec.code),
                    ("company_id", "=", rec.company_id.id),
                    ("version", "=", new_version),
                ]
            ):
                raise UserError(
                    "Version %s of code list %s already exists: finish that one."
                    % (new_version, rec.code)
                )
            # E25: one code, many versions. The list name and code stay, so a
            # consumer keeps asking for the same list.
            new_list = rec.copy(
                {
                    "code": rec.code,
                    "name": rec.name,
                    "version": new_version,
                    "state": "draft",
                    "effective_from": False,
                }
            )
            rec.entry_ids.copy({"list_id": new_list.id})
            new_lists |= new_list
        return new_lists

    def _entries_frozen(self):
        """True when any list in self was published and no guard token is held."""
        frozen = self.filtered(lambda rec: rec.state != "draft")
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
    effective_from = fields.Date(help="First day the value applies, inside its list's version.")
    effective_to = fields.Date(help="First day the value no longer applies.")

    _value_unique = models.Constraint(
        "UNIQUE (list_id, value)", "A code value is unique inside its list"
    )

    @api.constrains("effective_from", "effective_to")
    def _check_effective_dates(self):
        for rec in self:
            if rec.effective_from and rec.effective_to and rec.effective_to <= rec.effective_from:
                raise ValidationError(
                    "Value %s must start before it ends (BRU-MDM-17)." % rec.value
                )

    def _check_lists_mutable(self, lists):
        # BRU-MDM-13: published and retired alike. A retired value still
        # resolves old documents, so it is neither rewritten nor deleted.
        frozen = lists.filtered(lambda rec: rec.state != "draft")
        if frozen and not frozen._fix_guard_open():
            raise UserError(
                "Code list %s is %s: its entries are frozen. Cut a new version "
                "(action_new_version) instead of editing the contract."
                % (", ".join(frozen.mapped("code")[:3]), frozen[0].state)
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
            lists = self.mapped("list_id")
            # E23: a value moved INTO a published list adds to the contract too.
            if vals.get("list_id"):
                lists |= self.env["fix.mdm.code.list"].browse(vals["list_id"])
            self._check_lists_mutable(lists)
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
    # A12 finish E16: this was a typed integer, so the activation gate was one
    # keystroke away while every report called it "measured". Now it is measured,
    # on every read, so it cannot be typed or go stale.
    coverage_pct = fields.Integer(
        string="Translation Coverage %",
        compute="_compute_coverage_pct",
        help="Measured: the share of menus and field labels holding a translation in "
        "this language. Strings inside code are not counted.",
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

    @api.depends("code")
    def _compute_coverage_pct(self):
        cr = self.env.cr
        for rec in self:
            rec.coverage_pct = 0
            if not rec.code:
                continue
            # Translated columns are JSONB keyed by language; `?` asks for the key.
            cr.execute(
                """
                SELECT count(*), count(*) FILTER (WHERE name ? %(lang)s) FROM ir_ui_menu
                UNION ALL
                SELECT count(*), count(*) FILTER (WHERE field_description ? %(lang)s)
                  FROM ir_model_fields
                """,
                {"lang": rec.code},
            )
            rows = cr.fetchall()
            total = sum(row[0] for row in rows)
            translated = sum(row[1] for row in rows)
            rec.coverage_pct = int(100 * translated / total) if total else 0

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
            # A12 finish E16: activating a locale makes the language available.
            # Sudo after the check: res.lang is system configuration. Translations
            # themselves are loaded by the language-install tool, not here.
            lang = self.env["res.lang"].sudo()._activate_lang(rec.code)
            if not lang:
                raise UserError(
                    "%s is not a language this system knows, so it cannot be activated." % rec.code
                )
            rec._guarded().write({"state": "active"})

    def action_retire(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Retire an active locale pack (%s is %s)." % (rec.code, rec.state))
            # Odoo refuses to archive a language in use, with its own message;
            # the pack does not then pretend it was retired.
            others = self.sudo().search_count(
                [("code", "=", rec.code), ("state", "=", "active"), ("id", "!=", rec.id)]
            )
            if not others:
                lang = self.env["res.lang"].sudo().search([("code", "=", rec.code)], limit=1)
                if lang:
                    lang.write({"active": False})
            rec._guarded().write({"state": "retired"})


class FixJurisdictionRule(models.Model):
    """A12 finish E17: a DOCUMENTATION register. Nothing reads it: tax, the VAT
    calendar and payroll carry their own rules, so editing a row changes no
    calculation. Changes are tracked; the screen says the same thing."""

    _name = "fix.jurisdiction.rule"
    _description = "Jurisdiction Rule"
    _inherit = ["mail.thread"]
    _order = "jurisdiction"

    jurisdiction = fields.Char(
        required=True, tracking=True, help="e.g. BD-NBR, BD-DIFE, City Corporation"
    )
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
        tracking=True,
    )
    requirement = fields.Char(required=True, tracking=True)
    frequency = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
            ("event", "Event-Driven"),
        ],
        required=True,
        default="annual",
        tracking=True,
    )
    authority = fields.Char(tracking=True)
    penalty = fields.Char(string="Penalty for Non-Compliance", tracking=True)
    active = fields.Boolean(default=True, tracking=True)
