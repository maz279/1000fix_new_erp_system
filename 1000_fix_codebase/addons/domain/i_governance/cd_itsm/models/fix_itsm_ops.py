# fix_itsm_ops — M66 (IT change management + IT asset register) and M67
# (project stage-gate reviews). ITSM tickets live in fix_itsm.py; projects,
# milestones and tasks live in cd_ppm.
#
# A12 workflow audit (2026-11-04) P1-1: fix.itsm.change had a self-service
# `action_approve` — anyone approved his own change, and "implement" was a
# plain state flip. The change now rides the M63 routed approval engine:
#   - normal changes route to the coded Change Manager group,
#     emergency and high-risk changes to the CAB group (empty at install:
#     appoint members, or nobody can approve — by design);
#   - the risk score (probability x impact) at or above
#     cd_itsm.change_cab_risk_score (default 6) makes a change high-risk whatever
#     its type;
#   - requester and implementer never decide their own change (the engine
#     already excludes creator and amount-changer);
#   - implementing publishes itsm.change_implemented.
#
# Finish audit (2026-11-07) M66-1/2/3, N-M66-2/8/9, BRU-ITS-08/09/10:
#   - standard means a pre-authorised catalogue template (fix.itsm.change.template)
#     authorised by a Change Manager or CAB member, with the template's risk as a
#     floor; a self-declared standard routes like any other change;
#   - risk has an independent floor: the criticality of the linked CIs, and a
#     self-assessed score below cd_itsm.change_unverified_floor_score with nothing
#     linked goes to the CAB;
#   - the risk scores, plans, type, requester and scope are pinned to the approval;
#   - the acting user must be the implementer, requester and implementer compare
#     as employees, and implementing needs a recorded approval;
#   - the emergency path is explicit: action_emergency_implement implements first,
#     opens a retro approval task, and a cron chases the PIR;
#   - rollback works from implemented and reviewed, and a failed change owes a PIR;
#   - collisions on a CI or asset and freeze windows are checked (emergency exempt).
#
# M66-9/M66-10: the IT asset register let any write move an asset to "retired"
# with the data still on it. Retiring is now two people: the recorder supplies
# the certificate and a second person approves the write-off, which publishes
# itsm.asset_retired for M06. Allocation needs an active employee and his
# acceptance; a leaver's asset is recovery-due and blocks exit clearance.
# M67-6: a stage-gate review's decision is recorded by its reviewer (never the
# project's own manager) through an action, not a write.
import math

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_itsm import (
    itsm_activity,
    itsm_employee_of,
    itsm_param_float,
    itsm_require_superuser,
    itsm_resolve_employee,
)

AGENT_GROUP = "cd_itsm.group_itsm_agent"
CHANGE_MANAGER_GROUP = "cd_itsm.group_itsm_change_manager"
CAB_GROUP = "cd_itsm.group_itsm_cab_member"
SPONSOR_GROUP = "cd_ppm.group_ppm_sponsor"
CAB_RISK_SCORE_PARAM = "cd_itsm.change_cab_risk_score"
CAB_RISK_SCORE_DEFAULT = 6
UNVERIFIED_FLOOR_PARAM = "cd_itsm.change_unverified_floor_score"
UNVERIFIED_FLOOR_DEFAULT = 4
FREEZE_WINDOWS_PARAM = "cd_itsm.change_freeze_windows"
PIR_DUE_DAYS_PARAM = "cd_itsm.pir_due_days"
PIR_DUE_DAYS_DEFAULT = 2
CERTIFICATE_MIN_LENGTH_PARAM = "cd_itsm.wipe_certificate_min_length"
CERTIFICATE_MIN_LENGTH_DEFAULT = 5
REQUIRE_M06_DOCUMENT_PARAM = "cd_itsm.wipe_requires_m06_document"

_RISK_SCALE = [
    ("1", "1 - rare"),
    ("2", "2 - unlikely"),
    ("3", "3 - possible"),
    ("4", "4 - likely"),
    ("5", "5 - almost certain"),
]
_IMPACT_SCALE = [
    ("1", "1 - negligible"),
    ("2", "2 - minor"),
    ("3", "3 - moderate"),
    ("4", "4 - major"),
    ("5", "5 - severe"),
]
# A CI's criticality is a risk floor the requester cannot argue with.
_CI_RISK_FLOOR = {"low": 1, "medium": 4, "high": 9, "critical": 16}
_CHANGE_FROZEN_AFTER_IMPLEMENT = {
    "title",
    "change_type",
    "template_id",
    "planned_on",
    "implementation_plan",
    "test_plan",
    "rollback_plan",
    "change_window_hours",
    "asset_ids",
    "ci_ids",
    "risk",
    "risk_probability",
    "risk_impact",
    "requested_by_id",
    "implementer_id",
}
_TEMPLATE_PINNED = {
    "implementation_plan",
    "test_plan",
    "rollback_plan",
    "risk_probability",
    "risk_impact",
    "max_window_hours",
}
_ASSET_FROZEN_WHEN_RETIRED = {
    "name",
    "asset_tag",
    "asset_kind",
    "assigned_to_id",
    "serial_no",
    "warranty_end",
    "os_version",
}


def _cab_threshold(env):
    return int(itsm_param_float(env, CAB_RISK_SCORE_PARAM, CAB_RISK_SCORE_DEFAULT))


def _has_itsm_authority(user):
    return user.has_group(CHANGE_MANAGER_GROUP) or user.has_group(CAB_GROUP)


class FixItsmChangeTemplate(models.Model):
    """The pre-authorised standard change catalogue (M66-1): what "standard" means.
    A Change Manager or CAB member authorises the template; a change that follows
    it needs no further approval, and one that departs from it is not standard."""

    _name = "fix.itsm.change.template"
    _description = "Pre-Authorised Standard Change"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "code"

    code = fields.Char(required=True, index=True, tracking=True)
    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    description = fields.Text()
    implementation_plan = fields.Text(required=True, tracking=True)
    test_plan = fields.Text(required=True, tracking=True)
    rollback_plan = fields.Text(required=True, tracking=True)
    risk_probability = fields.Selection(
        _RISK_SCALE, string="Risk Probability (floor)", default="1", required=True, tracking=True
    )
    risk_impact = fields.Selection(
        _IMPACT_SCALE, string="Risk Impact (floor)", default="2", required=True, tracking=True
    )
    risk_score = fields.Integer(compute="_compute_risk_score", store=True)
    max_window_hours = fields.Integer(string="Maximum Window (hours)", default=2, tracking=True)
    authorised_by_id = fields.Many2one(
        "res.users", string="Authorised By", readonly=True, copy=False
    )
    authorised_on = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("authorised", "Authorised"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A standard change code is unique per company"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "authorised_by_id", "authorised_on"}

    @api.depends("risk_probability", "risk_impact")
    def _compute_risk_score(self):
        for rec in self:
            rec.risk_score = int(rec.risk_probability or "1") * int(rec.risk_impact or "1")

    def write(self, vals):
        result = super().write(vals)
        if _TEMPLATE_PINNED & set(vals) and not self.env.su:
            # What was authorised is the text and the risk it was authorised for.
            for rec in self.filtered(lambda r: r.state == "authorised"):
                rec._guarded().write(
                    {"state": "draft", "authorised_by_id": False, "authorised_on": False}
                )
                rec.message_post(body="Edited after authorisation: it must be authorised again.")
        return result

    def action_authorise(self):
        if not self.env.su and not _has_itsm_authority(self.env.user):
            raise UserError("A standard change is authorised by a Change Manager or CAB member.")
        threshold = _cab_threshold(self.env)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Authorise a draft template.")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError("You wrote this template: another person authorises it.")
            if rec.risk_score >= threshold:
                raise UserError(
                    "%s scores %d, at or above the CAB threshold %d: a change that risky is "
                    "never pre-authorised." % (rec.code, rec.risk_score, threshold)
                )
            rec._guarded().write(
                {
                    "state": "authorised",
                    "authorised_by_id": self.env.uid,
                    "authorised_on": fields.Datetime.now(),
                }
            )

    def action_retire_template(self):
        if not self.env.su and not _has_itsm_authority(self.env.user):
            raise UserError("A standard change is retired by a Change Manager or CAB member.")
        for rec in self:
            if rec.state == "retired":
                raise UserError("This template is already retired.")
            rec._guarded().write({"state": "retired"})


class FixItsmChange(models.Model):
    _name = "fix.itsm.change"
    _description = "IT Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "planned_on desc, id desc"

    # M63 wiring: the approve method only runs from the approver's inbox task.
    _approval_domain = "other"
    _approval_apply_method = "action_approve"
    _approval_routed = True

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    title = fields.Char(required=True)
    change_type = fields.Selection(
        [("standard", "Standard"), ("normal", "Normal"), ("emergency", "Emergency")],
        required=True,
        default="normal",
    )
    template_id = fields.Many2one(
        "fix.itsm.change.template",
        string="Standard Change Template",
        index=True,
        help="M66-1: a standard change is one that follows a pre-authorised template "
        "to the letter. Without one it routes for approval like any other change.",
    )
    risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    # N-M66-8: 2 x 2, so an untouched normal change reaches the Change Manager and
    # the CAB route is earned by the figures, not by leaving the defaults.
    risk_probability = fields.Selection(
        _RISK_SCALE, string="Risk Probability", default="2", required=True
    )
    risk_impact = fields.Selection(_IMPACT_SCALE, string="Risk Impact", default="2", required=True)
    risk_score = fields.Integer(
        compute="_compute_risk_score",
        store=True,
        help="Probability x impact (1-25). At or above the CAB threshold "
        "(cd_itsm.change_cab_risk_score, default 6) the change is high-risk "
        "and goes to the CAB whatever its type.",
    )
    risk_floor_score = fields.Integer(
        compute="_compute_risk_score",
        store=True,
        string="Risk Floor",
        help="The independent floor under the requester's own figures: the criticality "
        "of the linked CIs and the template's risk.",
    )
    risk_basis = fields.Char(compute="_compute_risk_score", store=True, string="Risk Basis")
    high_risk = fields.Boolean(compute="_compute_risk_score", store=True)
    requested_by_id = fields.Many2one("hr.employee", string="Requested By")
    implementer_id = fields.Many2one("hr.employee", string="Implementer")
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    planned_on = fields.Date(required=True, default=fields.Date.context_today)
    implementation_plan = fields.Text()
    test_plan = fields.Text()
    rollback_plan = fields.Text()
    change_window_hours = fields.Integer(default=2)
    asset_ids = fields.Many2many(
        "fix.itsm.asset",
        "fix_itsm_change_asset_rel",
        "change_id",
        "asset_id",
        string="Affected Assets",
    )
    ci_ids = fields.Many2many(
        "fix.itsm.ci",
        "fix_itsm_change_ci_rel",
        "change_id",
        "ci_id",
        string="Configuration Items",
        help="BRU-ITS-09: two changes on one configuration item cannot share a window.",
    )
    problem_ids = fields.One2many("fix.itsm.problem", "fix_change_id", string="Fixes Problems")
    freeze_conflict = fields.Boolean(
        compute="_compute_freeze_conflict",
        string="In Freeze Window",
        help="BRU-ITS-08: the planned date falls in a freeze window "
        "(cd_itsm.change_freeze_windows). Only the emergency path passes one.",
    )
    release_note = fields.Char(
        help="The platform release this change ships under (M30); recorded when "
        "the release register picks the change up."
    )
    implemented_on = fields.Datetime(readonly=True, copy=False)
    implemented_by_id = fields.Many2one(
        "res.users", string="Implemented By", readonly=True, copy=False
    )
    emergency_path = fields.Boolean(string="Implemented First", readonly=True, copy=False)
    emergency_reason = fields.Text(readonly=True, copy=False)
    retro_approval_state = fields.Selection(
        [
            ("none", "Not Applicable"),
            ("pending", "Pending"),
            ("unrouted", "No Approver Yet"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Retro Approval",
        default="none",
        readonly=True,
        copy=False,
        tracking=True,
        help="M66-3: an emergency change is implemented first and approved afterwards.",
    )
    retro_approval_group = fields.Selection(
        [("cab", "CAB"), ("cm", "Change Manager")], readonly=True, copy=False
    )
    pir_required = fields.Boolean(
        compute="_compute_pir_required",
        store=True,
        string="PIR Required",
        help="BRU-ITS-10: every emergency, failed and major change gets a review.",
    )
    pir_due_on = fields.Date(string="PIR Due", readonly=True, copy=False)
    pir_notes = fields.Text(string="Post-Implementation Review", copy=False)
    pir_by_id = fields.Many2one("res.users", string="PIR By", readonly=True, copy=False)
    pir_on = fields.Datetime(string="PIR On", readonly=True, copy=False)
    rolled_back_on = fields.Datetime(readonly=True, copy=False)
    rollback_reason = fields.Text(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("implemented", "Implemented"),
            ("reviewed", "Reviewed"),
            ("rolled_back", "Rolled Back"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "implemented_on",
            "implemented_by_id",
            "emergency_path",
            "emergency_reason",
            "retro_approval_state",
            "retro_approval_group",
            "pir_due_on",
            "pir_notes",
            "pir_by_id",
            "pir_on",
            "rolled_back_on",
            "rollback_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state in ("implemented", "reviewed", "rolled_back") for rec in self):
            locked |= _CHANGE_FROZEN_AFTER_IMPLEMENT
        return locked

    # ---- risk ----------------------------------------------------------------
    def _cab_risk_threshold(self):
        return _cab_threshold(self.env)

    @api.depends(
        "risk_probability",
        "risk_impact",
        "risk",
        "ci_ids",
        "ci_ids.criticality",
        "asset_ids",
        "template_id",
        "template_id.risk_score",
    )
    def _compute_risk_score(self):
        threshold = self._cab_risk_threshold()
        unverified_floor = int(
            itsm_param_float(self.env, UNVERIFIED_FLOOR_PARAM, UNVERIFIED_FLOOR_DEFAULT)
        )
        for rec in self:
            score = int(rec.risk_probability or "2") * int(rec.risk_impact or "2")
            cis = rec.sudo().ci_ids
            floors = [_CI_RISK_FLOOR.get(c, 1) for c in cis.mapped("criticality")]
            if rec.template_id:
                floors.append(rec.sudo().template_id.risk_score)
            floor = max(floors or [0])
            # M66-1: a score this low with nothing to check it against is the
            # requester's word alone, so it is not what decides the route.
            unverified = score < unverified_floor and not (cis or rec.asset_ids or rec.template_id)
            rec.risk_score = score
            rec.risk_floor_score = floor
            rec.high_risk = rec.risk == "high" or max(score, floor) >= threshold or unverified
            if unverified:
                rec.risk_basis = "Self-assessed %d with nothing linked: routed to the CAB" % score
            elif floor > score:
                rec.risk_basis = "Linked items set a floor of %d over the stated %d" % (
                    floor,
                    score,
                )
            else:
                rec.risk_basis = "Stated score %d" % score

    @api.depends("change_type", "high_risk", "state")
    def _compute_pir_required(self):
        for rec in self:
            rec.pir_required = (
                rec.change_type == "emergency" or rec.high_risk or rec.state == "rolled_back"
            )

    # ---- freeze and collision (BRU-ITS-08/09) --------------------------------
    @api.model
    def _freeze_windows(self):
        """[(from, to)] from cd_itsm.change_freeze_windows, written as
        2026-12-24:2027-01-02 and separated by commas. M30 declares no freeze
        register, so this parameter is the source. A malformed value refuses
        rather than switching the control off silently."""
        raw = self.env["ir.config_parameter"].sudo().get_param(FREEZE_WINDOWS_PARAM)
        windows = []
        for chunk in str(raw or "").replace(";", ",").split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            try:
                start, end = chunk.split(":")
                windows.append(
                    (fields.Date.to_date(start.strip()), fields.Date.to_date(end.strip()))
                )
            except ValueError as exc:
                raise UserError(
                    "%s is malformed (%r): write YYYY-MM-DD:YYYY-MM-DD, comma separated."
                    % (FREEZE_WINDOWS_PARAM, chunk)
                ) from exc
        return windows

    def _freeze_window_on(self, day):
        for start, end in self._freeze_windows():
            if start <= day <= end:
                return start, end
        return None

    @api.depends("planned_on")
    def _compute_freeze_conflict(self):
        try:
            windows = self._freeze_windows()
        except UserError:
            windows = None
        for rec in self:
            rec.freeze_conflict = (
                windows is None or any(start <= rec.planned_on <= end for start, end in windows)
                if rec.planned_on
                else False
            )

    def _assert_not_frozen(self, day, doing):
        window = self._freeze_window_on(day)
        if window:
            raise UserError(
                "%s falls in the freeze window %s to %s: a change is not %s during a freeze "
                "except through the emergency path (BRU-ITS-08)."
                % (day, window[0], window[1], doing)
            )

    def _schedule_span(self):
        self.ensure_one()
        days = max(1, math.ceil((self.change_window_hours or 1) / 24.0))
        return self.planned_on, fields.Date.add(self.planned_on, days=days - 1)

    def _collisions(self):
        """Changes already in the pipeline sharing a CI or asset and a window."""
        self.ensure_one()
        if not (self.ci_ids or self.asset_ids):
            return self.browse()
        domain = [
            ("id", "!=", self.id),
            ("company_id", "=", self.company_id.id),
            "|",
            ("state", "=", "approved"),
            "&",
            ("state", "=", "draft"),
            ("approval_state", "=", "pending"),
            "|",
            ("ci_ids", "in", self.ci_ids.ids),
            ("asset_ids", "in", self.asset_ids.ids),
        ]
        start, end = self._schedule_span()
        return (
            self.sudo()
            .search(domain)
            .filtered(
                lambda other: other._schedule_span()[0] <= end
                and start <= other._schedule_span()[1]
            )
        )

    def _assert_schedule_clear(self):
        self.ensure_one()
        self._assert_not_frozen(self.planned_on, "scheduled")
        collisions = self._collisions()
        if collisions:
            raise UserError(
                "%s collides with %s on the same configuration item or asset in the same "
                "window: move one of them (BRU-ITS-09)."
                % (self.name, ", ".join(collisions.mapped("name")))
            )

    # ---- M63 hooks -----------------------------------------------------------
    def _standard_gap(self):
        """Why this is not a pre-authorised standard change; empty when it is."""
        self.ensure_one()
        if self.change_type != "standard":
            return "it is not a standard change"
        template = self.sudo().template_id
        if not template:
            return "it names no pre-authorised template"
        if template.state != "authorised":
            return "template %s is not authorised" % template.code
        if self.high_risk:
            return "it is high-risk"
        for name in ("implementation_plan", "test_plan", "rollback_plan"):
            if (self[name] or "").strip() != (template[name] or "").strip():
                return "its %s departs from template %s" % (
                    self._fields[name].string,
                    template.code,
                )
        if (self.change_window_hours or 0) > (template.max_window_hours or 0):
            return "its window exceeds template %s" % template.code
        return ""

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return bool(self._standard_gap())

    def _approval_group_xmlid(self):
        self.ensure_one()
        if self.retro_approval_group == "cm":
            return CHANGE_MANAGER_GROUP
        if self.change_type == "emergency" or self.high_risk:
            return CAB_GROUP
        return CHANGE_MANAGER_GROUP

    def _approval_excluded(self):
        # P1-1: the requester AND the implementer never decide their own
        # change, on top of the engine's creator/amount-changer exclusions.
        self.ensure_one()
        excluded = super()._approval_excluded()
        return excluded | self.requested_by_id.sudo().user_id | self.implementer_id.sudo().user_id

    def _approval_pinned_fields(self) -> set:
        # M66-2: the approval covers this snapshot; editing it voids the approval.
        return super()._approval_pinned_fields() | {
            "title",
            "change_type",
            "template_id",
            "risk",
            "risk_probability",
            "risk_impact",
            "requested_by_id",
            "planned_on",
            "implementation_plan",
            "test_plan",
            "rollback_plan",
            "change_window_hours",
            "asset_ids",
            "ci_ids",
        }

    def _approval_clear_stamp(self, reason):
        """A voided/recalled/rejected approval leaves no approved change
        behind: an approved (not yet implemented) change returns to draft and
        must be submitted again. Implemented changes keep their trail."""
        for rec in self.sudo().filtered(lambda r: r.state == "approved"):
            rec._guarded().write({"state": "draft", "approved_by_id": False})
            rec.message_post(body="Approval withdrawn (%s); the change is a draft again." % reason)

    def _approval_on_rejected(self, comment):
        # Runs in the deciding user's env (or the escalation cron's); the
        # decision is already made and logged by the engine — mirroring it
        # onto the change's own state is bookkeeping.
        for rec in self.sudo():
            if rec.emergency_path:
                # It is already in. Refusing it afterwards means it comes out.
                rec._guarded().write({"retro_approval_state": "rejected"})
                rec.message_post(body="Retro approval refused: %s" % (comment or ""))
                for user in rec.implementer_id.user_id | rec._change_managers():
                    itsm_activity(
                        rec,
                        user,
                        "Retro approval refused: %s" % rec.name,
                        "Roll this emergency change back, or take it to the CAB again: %s"
                        % (comment or ""),
                    )
            else:
                rec._guarded().write({"state": "rejected"})

    def action_recall_approval(self):
        if any(rec.sudo().emergency_path for rec in self):
            raise UserError(
                "A retro approval cannot be recalled: the emergency change is already in."
            )
        return super().action_recall_approval()

    # ---- lifecycle -----------------------------------------------------------
    @api.model
    def _template_defaults(self, template, vals):
        """What a change takes from its template when the author left it blank."""
        for name in ("implementation_plan", "test_plan", "rollback_plan"):
            if not vals.get(name):
                vals[name] = template[name]
        vals.setdefault("change_type", "standard")
        vals.setdefault("risk_probability", template.risk_probability)
        vals.setdefault("risk_impact", template.risk_impact)
        vals.setdefault("change_window_hours", template.max_window_hours)
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        caller = itsm_employee_of(self.env)
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.itsm.change") or "CHG/New"
            if vals.get("template_id"):
                template = self.env["fix.itsm.change.template"].sudo().browse(vals["template_id"])
                self._template_defaults(template, vals)
            if not vals.get("requested_by_id") and caller and not self.env.su:
                vals["requested_by_id"] = caller.id
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = _CHANGE_FROZEN_AFTER_IMPLEMENT & set(vals)
            if frozen and any(
                rec.state in ("implemented", "reviewed", "rolled_back") for rec in self
            ):
                raise UserError(
                    "An implemented change stands as the record: raise another change "
                    "rather than rewriting this one."
                )
        result = super().write(vals)
        if vals.get("template_id"):
            for rec in self:
                filled = {
                    name: rec.sudo().template_id[name]
                    for name in ("implementation_plan", "test_plan", "rollback_plan")
                    if not rec[name]
                }
                if filled or rec.change_type != "standard":
                    filled["change_type"] = "standard"
                    super(FixItsmChange, rec).write(filled)
        return result

    def _assert_plans(self):
        self.ensure_one()
        if not (self.implementation_plan or "").strip() or not (self.test_plan or "").strip():
            raise UserError(
                "A submitted change carries its implementation and test plan (P1-1): "
                "the approver signs off the plan, not a title."
            )
        if not (self.rollback_plan or "").strip():
            raise UserError(
                "An emergency or high-risk change needs a rollback plan."
                if self.change_type == "emergency" or self.high_risk
                else "A change needs a rollback plan before submission (BRU-ITS-06)."
            )

    def action_submit(self):
        """Draft -> routed approval, or pre-approved when it follows an authorised
        standard change template to the letter. A self-declared standard is
        routed like any other change (M66-1)."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft change can be submitted.")
            if not rec.requested_by_id:
                raise UserError("Name the requester before submitting the change.")
            rec._assert_plans()
            if rec.change_window_hours < 1:
                raise UserError("The change window is at least one hour.")
            if rec.change_type != "emergency":
                rec._assert_schedule_clear()
            gap = rec._standard_gap()
            if not gap:
                # Pre-approved by the template's authorisation: that is what
                # "standard" means. No person signs this one, so no name is stamped.
                rec._guarded().write({"state": "approved", "approval_state": "approved"})
                rec.message_post(
                    body="Standard change: pre-approved by template %s, authorised by %s."
                    % (rec.sudo().template_id.code, rec.sudo().template_id.authorised_by_id.name)
                )
            else:
                if rec.change_type == "standard":
                    rec.message_post(body="Routed for approval: %s." % gap)
                rec.action_request_approval()

    def action_approve(self):
        """The engine's apply method: runs in the approver's env, from the
        inbox task only (P1-1)."""
        self._approval_assert_routed()
        for rec in self:
            if rec.emergency_path:
                # The retro approval of a change that is already in (M66-3).
                rec._guarded().write(
                    {
                        "retro_approval_state": "approved",
                        "approved_by_id": rec._approval_authority_user().id,
                    }
                )
                continue
            if rec.state != "draft":
                raise UserError("Only a draft change can be approved.")
            rec._guarded().write(
                {"state": "approved", "approved_by_id": rec._approval_authority_user().id}
            )

    def _assert_implementer_duties(self):
        """M66-1: requester, approver and implementer are different people. They
        compare as employees first: most employees have no login, so comparing
        users passed exactly when nobody could be told apart. The person pressing
        the button must be the named implementer. An implementer with no login is
        recorded by an agent who is neither requester nor approver."""
        self.ensure_one()
        implementer = self.implementer_id.sudo()
        requester = self.requested_by_id.sudo()
        implementer_user = implementer.user_id
        requester_user = requester.user_id
        if implementer == requester or (implementer_user and implementer_user == requester_user):
            raise UserError("The implementer is not the requester (P1-1 segregation of duties).")
        if self.approved_by_id and implementer_user and self.approved_by_id == implementer_user:
            raise UserError("The implementer is not the approver (P1-1 segregation of duties).")
        if self.env.su:
            return
        user = self.env.user
        if implementer_user:
            if user != implementer_user:
                raise UserError(
                    "%s is implemented by the named implementer, %s: you are not that person."
                    % (self.name, implementer.name)
                )
            return
        if not user.has_group(AGENT_GROUP):
            raise UserError("A change is implemented by the service desk.")
        if user == requester_user or user == self.approved_by_id:
            raise UserError(
                "The requester or approver does not record the implementation (P1-1 "
                "segregation of duties)."
            )

    def _mark_implemented(self, extra=None):
        self.ensure_one()
        now = fields.Datetime.now()
        vals = {"state": "implemented", "implemented_on": now, "implemented_by_id": self.env.uid}
        vals.update(extra or {})
        if self.change_type == "emergency" or self.high_risk:
            days = int(itsm_param_float(self.env, PIR_DUE_DAYS_PARAM, PIR_DUE_DAYS_DEFAULT))
            vals["pir_due_on"] = fields.Date.add(fields.Date.context_today(self), days=days)
        self._guarded().write(vals)
        self.message_post(body="Implemented by %s." % self.implementer_id.sudo().display_name)
        publish(
            self.env,
            "itsm.change_implemented",
            "fix.itsm.change",
            self.id,
            {
                "change": self.name,
                "title": self.title,
                "change_type": self.change_type,
                "risk": self.risk,
                "risk_score": self.risk_score,
                "high_risk": self.high_risk,
                "assets": list(self.sudo().asset_ids.mapped("asset_tag")),
                "implemented_on": now.isoformat(),
            },
        )

    def action_implement(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Implement an approved change (P1-1).")
            if rec.approval_state != "approved":
                raise UserError(
                    "%s says approved but carries no recorded approval: return it to draft and "
                    "submit it (M66-1)." % rec.name
                )
            if not rec.implementer_id:
                raise UserError("Name the implementer before implementing the change.")
            rec._assert_plans()
            rec._assert_implementer_duties()
            if rec.change_type != "emergency":
                rec._assert_not_frozen(fields.Date.context_today(rec), "implemented")
            rec._mark_implemented()

    def action_emergency_implement(self, reason=None):
        """M66-3: implement first. The emergency passes a freeze and a collision,
        but its implementer, back-out plan and reason are still on record, the
        retro approval goes to the CAB (or the Change Manager when the CAB is
        empty), and a cron chases the post-implementation review."""
        if not (reason or "").strip():
            raise UserError("Say why this cannot wait for the CAB: the reason is required.")
        caller = itsm_employee_of(self.env)
        for rec in self:
            if rec.change_type != "emergency":
                raise UserError("Only an emergency change is implemented before approval.")
            if rec.state != "draft":
                raise UserError("Implement first applies to a draft emergency change.")
            if not rec.requested_by_id:
                raise UserError("Name the requester before implementing the change.")
            if not (rec.implementation_plan or "").strip():
                raise UserError("Write what is being done: the implementation plan is required.")
            if not (rec.rollback_plan or "").strip():
                raise UserError("An emergency change still needs its rollback plan.")
            if not rec.implementer_id and caller:
                rec.write({"implementer_id": caller.id})
            if not rec.implementer_id:
                raise UserError("Name the implementer before implementing the change.")
            rec._assert_implementer_duties()
            notes = []
            if rec._freeze_window_on(fields.Date.context_today(rec)):
                notes.append("inside a freeze window")
            if rec._collisions():
                notes.append("colliding with %s" % ", ".join(rec._collisions().mapped("name")))
            rec._mark_implemented(
                {
                    "emergency_path": True,
                    "emergency_reason": reason,
                    "retro_approval_state": "pending",
                }
            )
            rec.message_post(
                body="Emergency path: implemented before approval%s. Reason: %s"
                % (" (%s)" % "; ".join(notes) if notes else "", reason)
            )
            rec._retro_route()

    def _retro_route(self):
        """Open the retro approval task; the CAB first, the Change Manager when
        nobody on the CAB can take it. A change nobody can approve yet stays
        visible as unrouted and the cron tries again."""
        for rec in self:
            if rec.approval_state == "pending":
                rec._guarded().write({"retro_approval_state": "pending"})
                continue
            routed = False
            for group in ("cab", "cm"):
                rec._guarded().write({"retro_approval_group": group})
                try:
                    with self.env.cr.savepoint():
                        rec.action_request_approval()
                    routed = True
                    break
                except UserError:
                    continue
            rec._guarded().write({"retro_approval_state": "pending" if routed else "unrouted"})
            if not routed:
                rec.message_post(body="Retro approval could not be routed: nobody holds the role.")

    def _assert_not_implementer(self):
        """The implementer is not the sole verifier of his own change (spec s13)."""
        if self.env.su:
            return
        user = self.env.user
        caller = itsm_employee_of(self.env)
        for rec in self:
            implementer = rec.implementer_id.sudo()
            if (implementer and caller == implementer) or user in (
                implementer.user_id | rec.implemented_by_id
            ):
                raise UserError(
                    "You implemented %s: another person writes its post-implementation review."
                    % rec.name
                )

    def action_record_pir(self, pir_notes=None):
        """Post-implementation review (BRU-ITS-10). On an implemented change it
        closes the change as reviewed; a rolled-back change stays rolled back and
        the review stands beside it."""
        for rec in self:
            if rec.state not in ("implemented", "rolled_back"):
                raise UserError("Record the post-implementation review on an implemented change.")
            if rec.pir_on:
                raise UserError("%s already has its review." % rec.name)
            if not (pir_notes or "").strip():
                raise UserError("Write what the review found: the PIR notes are required.")
            rec._assert_not_implementer()
            vals = {
                "pir_notes": pir_notes,
                "pir_by_id": rec.env.uid,
                "pir_on": fields.Datetime.now(),
            }
            if rec.state == "implemented":
                vals["state"] = "reviewed"
            rec._guarded().write(vals)

    def action_rollback(self, reason=None):
        """N-M66-2: a change comes out from implemented or reviewed. A failing
        emergency must not wait for a review: the reason goes on record now and the
        failed change then owes its review (BRU-ITS-10), chased by the cron."""
        days = int(itsm_param_float(self.env, PIR_DUE_DAYS_PARAM, PIR_DUE_DAYS_DEFAULT))
        for rec in self:
            if rec.state not in ("implemented", "reviewed"):
                raise UserError("Roll back an implemented change.")
            why = (reason or "").strip() or (rec.pir_notes or "").strip()
            if not why:
                raise UserError("Say why it is coming out: the rollback reason is required.")
            vals = {
                "state": "rolled_back",
                "rolled_back_on": fields.Datetime.now(),
                "rollback_reason": why,
            }
            if not rec.pir_on:
                vals["pir_due_on"] = fields.Date.add(fields.Date.context_today(rec), days=days)
            rec._guarded().write(vals)
            rec.message_post(body="Rolled back per the rollback plan: %s" % why)

    @api.model
    def _change_managers(self):
        group = self.env.ref(CHANGE_MANAGER_GROUP, raise_if_not_found=False)
        if not group:
            return self.env["res.users"]
        return group.sudo().all_user_ids.filtered(lambda u: u.active and u.id != 1)

    @api.model
    def cron_chase_pir(self):
        """Daily (M66-3, BRU-ITS-10): a change that owes a review is chased, and a
        retro approval nobody could take is routed again. The implementer cannot
        write the review, so the chase goes to the requester and Change Managers."""
        itsm_require_superuser(self.env, "The PIR chase")
        today = fields.Date.context_today(self)
        unrouted = self.sudo().search(
            [("emergency_path", "=", True), ("retro_approval_state", "=", "unrouted")]
        )
        unrouted._retro_route()
        owing = self.sudo().search(
            [
                ("pir_required", "=", True),
                ("pir_on", "=", False),
                ("state", "in", ("implemented", "rolled_back")),
            ]
        )
        chased = 0
        for rec in owing:
            if rec.pir_due_on and rec.pir_due_on > today:
                continue
            for user in rec.requested_by_id.user_id | rec._change_managers():
                itsm_activity(
                    rec,
                    user,
                    "Post-implementation review overdue: %s" % rec.name,
                    "%s is %s and has no review (BRU-ITS-10)." % (rec.name, rec.state),
                )
            chased += 1
        return chased

    # ---- event consumer (FF-48; data record ships in cd_itsm/data) -----------
    @api.model
    def consume_change_implemented(self, event):
        """itsm.change_implemented: the problems this change fixes are told their
        cause should now be gone, so their owners start verifying; any release
        linked to the change gets the trail. It creates no release: a release is
        the release manager's decision (M30)."""
        itsm_require_superuser(self.env, "The change consumer")
        change = self.browse(event.get("aggregate_id") or 0).exists()
        if not change:
            return True
        problems = change.problem_ids.filtered(
            lambda p: p.state in ("investigating", "known_error")
        )
        for problem in problems:
            itsm_activity(
                problem,
                problem.owner_id,
                "Fix implemented: %s" % problem.name,
                "%s is implemented. Resolve the problem and start verifying." % change.name,
            )
        release_model = self.env.registry.get("fix.platform.release")
        releases = self.env["fix.platform.release"].browse()
        if release_model is not None and "itsm_change_id" in release_model._fields:
            releases = (
                self.env["fix.platform.release"].sudo().search([("itsm_change_id", "=", change.id)])
            )
        for release in releases:
            release.message_post(body="ITSM change %s is implemented." % change.name)
        change.message_post(
            body="Implemented event %s: %d problem owner(s) told, %d linked release(s) noted."
            % (event.get("event_id"), len(problems), len(releases))
        )
        return True


class FixItsmAsset(models.Model):
    _name = "fix.itsm.asset"
    _description = "Internal IT Asset"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    asset_tag = fields.Char(required=True)
    asset_kind = fields.Selection(
        [
            ("laptop", "Laptop"),
            ("desktop", "Desktop"),
            ("phone", "Phone"),
            ("server", "Server"),
            ("network", "Network Gear"),
            ("peripheral", "Peripheral"),
        ],
        required=True,
        default="laptop",
    )
    assigned_to_id = fields.Many2one("hr.employee", string="Assigned To", tracking=True)
    recovery_from_id = fields.Many2one(
        "hr.employee",
        string="Recover From",
        readonly=True,
        copy=False,
        help="BRU-ITS-13: the leaver who still holds this asset. It blocks his exit "
        "clearance until the asset is back or its write-off is approved.",
    )
    acceptance_state = fields.Selection(
        [("none", "Not Allocated"), ("pending", "Awaiting Acceptance"), ("accepted", "Accepted")],
        string="Acceptance",
        default="none",
        readonly=True,
        copy=False,
        tracking=True,
    )
    accepted_on = fields.Datetime(readonly=True, copy=False)
    accepted_by_id = fields.Many2one(
        "res.users", string="Acceptance Recorded By", readonly=True, copy=False
    )
    acceptance_ref = fields.Char(string="Acceptance Reference", readonly=True, copy=False)
    serial_no = fields.Char()
    warranty_end = fields.Date()
    os_version = fields.Char(string="OS / Firmware")
    wipe_certificate = fields.Char(
        help="The data-wipe certificate reference (M66-9): an asset leaves the "
        "register as retired only after its data is provably destroyed."
    )
    wipe_document_id = fields.Many2one(
        "fix.document",
        string="M06 Certificate Document",
        readonly=True,
        copy=False,
        ondelete="restrict",
        help="BRU-ITS-14: the governed M06 document behind the certificate, when one "
        "is linked to this asset.",
    )
    writeoff_state = fields.Selection(
        [
            ("none", "None"),
            ("requested", "Awaiting Second Person"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Write-off",
        default="none",
        readonly=True,
        copy=False,
        tracking=True,
    )
    writeoff_requested_by_id = fields.Many2one(
        "res.users", string="Write-off Recorded By", readonly=True, copy=False
    )
    writeoff_requested_on = fields.Datetime(readonly=True, copy=False)
    writeoff_approved_by_id = fields.Many2one(
        "res.users", string="Write-off Approved By", readonly=True, copy=False
    )
    writeoff_note = fields.Text(string="Write-off Note", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("in_service", "In Service"),
            ("in_stock", "In Stock"),
            ("repair", "Under Repair"),
            ("recovery_due", "Recovery Due"),
            ("retired", "Retired"),
        ],
        required=True,
        default="in_stock",
        tracking=True,
    )

    _tag_unique = models.Constraint(
        "UNIQUE (asset_tag, company_id)", "An asset tag is unique per company"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "wipe_certificate",
            "wipe_document_id",
            "writeoff_state",
            "writeoff_requested_by_id",
            "writeoff_requested_on",
            "writeoff_approved_by_id",
            "writeoff_note",
            "recovery_from_id",
            "acceptance_state",
            "accepted_on",
            "accepted_by_id",
            "acceptance_ref",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "in_stock" for rec in self):
            # N-M66-11: allocation, return and recovery move the holder.
            locked.add("assigned_to_id")
        if any(rec.state == "retired" for rec in self):
            locked |= _ASSET_FROZEN_WHEN_RETIRED
        return locked

    def write(self, vals):
        if not self or self._fix_guard_has_token():
            return super().write(vals)
        if not self.env.su:
            if _ASSET_FROZEN_WHEN_RETIRED & set(vals) and any(
                rec.state == "retired" for rec in self
            ):
                raise UserError("A retired asset stands as the record: it is not edited.")
            if "assigned_to_id" in vals:
                new = vals["assigned_to_id"] or False
                for rec in self:
                    if rec.state != "in_stock" and (rec.assigned_to_id.id or False) != new:
                        raise UserError(
                            "%s is %s: its holder changes through Allocate, Return or Recover, "
                            "not by typing (N-M66-11)." % (rec.asset_tag, rec.state)
                        )
            return super().write(vals)
        # Trusted server code clearing a holder (the M29 leaver hand-off): the
        # asset has not physically come back, so it does not read as free.
        held = self.browse()
        if "assigned_to_id" in vals and not vals["assigned_to_id"]:
            held = self.filtered(lambda r: r.state == "in_service" and r.assigned_to_id)
        holders = {rec.id: rec.assigned_to_id for rec in held}
        result = super().write(vals)
        for rec in held:
            rec._start_recovery(holders[rec.id])
        return result

    def _start_recovery(self, holder):
        self.ensure_one()
        self._guarded().write(
            {"state": "recovery_due", "recovery_from_id": holder.id, "acceptance_state": "none"}
        )
        self.message_post(
            body="%s left holding this asset: recovery is due and it blocks exit clearance "
            "(BRU-ITS-13)." % holder.name
        )
        for user in self.env["fix.itsm.ticket"]._queue_agents(self.company_id)[:1]:
            itsm_activity(
                self,
                user,
                "Recover %s" % self.asset_tag,
                "%s has left. Recover this asset, or record its write-off." % holder.name,
            )

    @api.constrains("assigned_to_id")
    def _check_assignee_active(self):
        for rec in self:
            if rec.assigned_to_id and not rec.assigned_to_id.active:
                raise ValidationError(
                    "Asset %s is assigned to %s, who has left the company. Reassign "
                    "or retire the asset." % (rec.asset_tag, rec.assigned_to_id.display_name)
                )

    def _assert_agent(self):
        if not self.env.su and not self.env.user.has_group(AGENT_GROUP):
            raise UserError("The asset register is worked by the service desk.")

    def action_allocate(self, assigned_to=None):
        """BRU-ITS-12: to an active employee, whose acceptance is then recorded."""
        self._assert_agent()
        named = itsm_resolve_employee(self.env, assigned_to)
        for rec in self:
            if rec.state != "in_stock":
                raise UserError("Allocate an asset from stock.")
            employee = named or rec.assigned_to_id.sudo()
            if not employee:
                raise UserError("Name the employee the asset is allocated to.")
            if not employee.active:
                raise UserError("Allocate the asset to an active employee.")
            rec._guarded().write(
                {
                    "state": "in_service",
                    "assigned_to_id": employee.id,
                    "acceptance_state": "pending",
                    "accepted_on": False,
                    "accepted_by_id": False,
                    "acceptance_ref": False,
                }
            )
            itsm_activity(
                rec,
                employee.user_id,
                "Confirm you received %s" % rec.asset_tag,
                "%s was allocated to you. Accept it on the IT Asset screen." % rec.name,
            )

    def action_accept(self):
        """The holder's own acceptance. He holds no write access to the register,
        so the stamp runs as sudo once he is proven to be the holder."""
        for rec in self:
            target = rec.sudo()
            if target.state != "in_service" or target.acceptance_state != "pending":
                raise UserError("Only an allocated asset awaiting acceptance can be accepted.")
            if not self.env.su and target.assigned_to_id.user_id != self.env.user:
                raise UserError("%s is accepted by its holder." % target.asset_tag)
            target._guarded().write(
                {
                    "acceptance_state": "accepted",
                    "accepted_on": fields.Datetime.now(),
                    "accepted_by_id": self.env.uid,
                }
            )
            target.message_post(body="Accepted by %s." % self.env.user.name)

    def action_record_acceptance(self, reference=None):
        """A holder with no login signs on paper; the desk records the reference."""
        self._assert_agent()
        if not (reference or "").strip():
            raise UserError("Give the reference of the signed acceptance form.")
        for rec in self:
            if rec.state != "in_service" or rec.acceptance_state != "pending":
                raise UserError("Only an allocated asset awaiting acceptance can be accepted.")
            if rec.assigned_to_id.sudo().user_id == self.env.user:
                raise UserError("Accept your own asset with Accept, not as the desk.")
            rec._guarded().write(
                {
                    "acceptance_state": "accepted",
                    "accepted_on": fields.Datetime.now(),
                    "accepted_by_id": self.env.uid,
                    "acceptance_ref": reference,
                }
            )

    def action_return(self):
        """N-M66-11: an in-service asset comes back to stock, unassigned."""
        self._assert_agent()
        for rec in self:
            if rec.state != "in_service":
                raise UserError("Return an asset that is in service.")
            holder = rec.assigned_to_id.sudo().name
            rec._guarded().write(
                {"state": "in_stock", "assigned_to_id": False, "acceptance_state": "none"}
            )
            rec.message_post(body="Returned to stock by %s." % (holder or "its holder"))

    def action_send_repair(self):
        self._assert_agent()
        for rec in self:
            if rec.state not in ("in_service", "in_stock"):
                raise UserError("Only an in-service or in-stock asset goes to repair.")
            rec._guarded().write({"state": "repair"})

    def action_recover(self):
        """Back to stock, unassigned: from repair, or physically recovered from a
        leaver, which also lifts his exit clearance block (BRU-ITS-13)."""
        self._assert_agent()
        for rec in self:
            if rec.state not in ("repair", "recovery_due"):
                raise UserError("Recover an asset that is under repair or due for recovery.")
            rec._guarded().write(
                {
                    "state": "in_stock",
                    "assigned_to_id": False,
                    "recovery_from_id": False,
                    "acceptance_state": "none",
                }
            )

    def _linked_wipe_document(self, reference):
        """The governed M06 document for this asset that names the certificate, or
        the newest one linked to the asset."""
        self.ensure_one()
        docs = (
            self.env["fix.document"]
            .sudo()
            .search([("res_model", "=", self._name), ("res_id", "=", self.id)], order="id desc")
        )
        return docs.filtered(lambda d: reference.lower() in (d.name or "").lower())[:1] or docs[:1]

    def _in_service_cis(self):
        self.ensure_one()
        return (
            self.env["fix.itsm.ci"]
            .sudo()
            .search([("asset_id", "=", self.id), ("life_status", "=", "in_service")])
        )

    def _assert_retirable(self):
        self.ensure_one()
        if self.assigned_to_id:
            raise UserError(
                "%s is still assigned to %s; recover the asset before retiring it."
                % (self.asset_tag, self.assigned_to_id.sudo().display_name)
            )
        cis = self._in_service_cis()
        if cis:
            raise UserError(
                "%s still runs configuration item %s in service: retire or relink the CI first "
                "(M66-13)." % (self.asset_tag, ", ".join(cis.mapped("ci_key")))
            )

    def action_retire(self, wipe_certificate=None):
        """Step one of two (BRU-ITS-14, spec s13): the recorder supplies the
        data-wipe certificate. The asset retires when a SECOND person approves the
        write-off, not here. A governed M06 document linked to the asset is stamped
        on; cd_itsm.wipe_requires_m06_document = 1 makes that document mandatory."""
        self._assert_agent()
        min_length = int(
            itsm_param_float(self.env, CERTIFICATE_MIN_LENGTH_PARAM, CERTIFICATE_MIN_LENGTH_DEFAULT)
        )
        require_document = self.env["ir.config_parameter"].sudo().get_param(
            REQUIRE_M06_DOCUMENT_PARAM
        ) in ("1", "True", "true")
        for rec in self:
            if rec.state == "retired":
                raise UserError("Asset is already retired.")
            if rec.writeoff_state == "requested":
                raise UserError("%s is already awaiting its second person." % rec.asset_tag)
            certificate = (wipe_certificate or rec.wipe_certificate or "").strip()
            if not certificate:
                raise UserError(
                    "Record the data-wipe certificate before retiring %s: retired "
                    "hardware must provably carry no company data (M66-9)." % rec.asset_tag
                )
            rec._assert_retirable()
            document = rec._linked_wipe_document(certificate)
            if require_document and not document:
                raise UserError(
                    "Link the M06 data-destruction certificate document to %s first (BRU-ITS-14)."
                    % rec.asset_tag
                )
            if not document and len(certificate) < min_length:
                raise UserError(
                    "%r is not a certificate reference: give the number on the certificate "
                    "(M66-10)." % certificate
                )
            rec._guarded().write(
                {
                    "wipe_certificate": certificate,
                    "wipe_document_id": document.id or False,
                    "writeoff_state": "requested",
                    "writeoff_requested_by_id": self.env.uid,
                    "writeoff_requested_on": fields.Datetime.now(),
                    "writeoff_approved_by_id": False,
                    "writeoff_note": False,
                }
            )
            rec.message_post(
                body="Write-off recorded by %s with certificate %s%s; awaiting a second person."
                % (
                    self.env.user.name,
                    certificate,
                    " (M06 document %s)" % document.name if document else " (reference only)",
                )
            )
            group = self.env.ref(CHANGE_MANAGER_GROUP, raise_if_not_found=False)
            approvers = group.sudo().all_user_ids.filtered("active") if group else group
            for user in (approvers or self.env["res.users"]) - self.env.user:
                itsm_activity(
                    rec,
                    user,
                    "Approve write-off: %s" % rec.asset_tag,
                    "Certificate %s was recorded by %s." % (certificate, self.env.user.name),
                )

    def _assert_second_person(self):
        self.ensure_one()
        if self.env.su:
            return
        if not _has_itsm_authority(self.env.user):
            raise UserError("A write-off is decided by a Change Manager or CAB member.")
        if self.writeoff_requested_by_id == self.env.user:
            raise UserError("You recorded this write-off: a second person decides it (spec s13).")

    def action_approve_writeoff(self):
        """Step two: the second person retires the asset and M06 is told."""
        for rec in self:
            if rec.writeoff_state != "requested":
                raise UserError("%s has no write-off awaiting a decision." % rec.asset_tag)
            rec._assert_second_person()
            rec._assert_retirable()
            rec._guarded().write(
                {
                    "state": "retired",
                    "assigned_to_id": False,
                    "recovery_from_id": False,
                    "writeoff_state": "approved",
                    "writeoff_approved_by_id": self.env.uid,
                }
            )
            publish(
                rec.env,
                "itsm.asset_retired",
                "fix.itsm.asset",
                rec.id,
                {
                    "asset_tag": rec.asset_tag,
                    "asset_kind": rec.asset_kind,
                    "serial": rec.serial_no or "",
                },
            )

    def action_reject_writeoff(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say why the write-off is refused.")
        for rec in self:
            if rec.writeoff_state != "requested":
                raise UserError("%s has no write-off awaiting a decision." % rec.asset_tag)
            rec._assert_second_person()
            rec._guarded().write({"writeoff_state": "rejected", "writeoff_note": reason})
            rec.message_post(body="Write-off refused: %s" % reason)

    # ---- event consumer (FF-48; data record ships in cd_itsm/data) -----------
    @api.model
    def consume_asset_retired(self, event):
        """itsm.asset_retired: the asset's own trail of what M06 was handed. The
        documents themselves are stamped by fix.document.consume_itsm_asset_retired."""
        itsm_require_superuser(self.env, "The asset consumer")
        asset = self.browse(event.get("aggregate_id") or 0).exists()
        if asset:
            documents = (
                self.env["fix.document"]
                .sudo()
                .search_count([("res_model", "=", self._name), ("res_id", "=", asset.id)])
            )
            asset.message_post(
                body="Retirement handed to the M06 destruction review: %d linked document(s); "
                "event %s." % (documents, event.get("event_id"))
            )
        return True


class FixProjectGate(models.Model):
    _name = "fix.project.gate"
    _description = "Project Stage-Gate Review"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "review_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    project_id = fields.Many2one("fix.project", required=True, ondelete="cascade", index=True)
    gate = fields.Selection(
        [
            ("g1_initiation", "G1 Initiation"),
            ("g2_planning", "G2 Planning"),
            ("g3_execution", "G3 Execution"),
            ("g4_uat", "G4 UAT"),
            ("g5_closure", "G5 Closure"),
        ],
        required=True,
        default="g2_planning",
    )
    review_on = fields.Date(required=True, default=fields.Date.context_today)
    reviewer_id = fields.Many2one("hr.employee", string="Reviewer")
    checklist_passed = fields.Boolean(default=False)
    findings = fields.Text()
    decision = fields.Selection(
        [("pass", "Pass"), ("conditional", "Conditional Pass"), ("fail", "Fail")],
    )
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("held", "Held"), ("closed", "Closed")],
        required=True,
        default="scheduled",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        # checklist_passed stays a plain field: it is the reviewer's own
        # evidence flag, set while reviewing. The DECISION is what only an
        # action may set (M67-6) — the workspace prompts for it.
        return super()._fix_guarded_fields() | {"state", "decision"}

    def _gate_frozen_fields(self) -> set:
        """F10: what a decision was given about. A failed gate re-pointed at
        another project let the blocked project activate, so the subject of the
        review freezes at the decision and all of it at closure."""
        self.ensure_one()
        if self.state == "closed":
            return {
                "gate",
                "review_on",
                "reviewer_id",
                "findings",
                "project_id",
                "checklist_passed",
            }
        if self.decision:
            return {"gate", "reviewer_id", "project_id"}
        return set()

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        for rec in self:
            locked |= rec._gate_frozen_fields()
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                changed = {
                    name
                    for name in set(vals)
                    & (rec._gate_frozen_fields() | {"checklist_passed", "findings"})
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                }
                frozen = changed & rec._gate_frozen_fields()
                if frozen:
                    raise UserError(
                        "%s of gate %s cannot change: the gate is %s. A new review is a new "
                        "gate record (M67-3)."
                        % (
                            ", ".join(sorted(rec._fields[n].string for n in frozen)),
                            rec.name,
                            "closed" if rec.state == "closed" else "already decided",
                        )
                    )
                # The checklist and findings are the reviewer's evidence: the
                # manager who schedules the review does not write them.
                if changed:
                    rec._assert_reviewer()
        return super().write(vals)

    @api.constrains("reviewer_id", "project_id")
    def _check_reviewer_independent(self):
        """M67-6: the project's own manager never reviews his project's gate —
        the reviewer is independent of the work being reviewed."""
        for rec in self:
            manager = rec.project_id.manager_id
            if rec.reviewer_id and manager and rec.reviewer_id == manager:
                raise ValidationError(
                    "Gate %s is reviewed by %s, the project's own manager. Gate "
                    "review is independent (M67-6)." % (rec.name, manager.display_name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.project.gate") or "GATE/New"
                )
        return super().create(vals_list)

    def _assert_reviewer(self):
        """The named reviewer or a project sponsor records the decision; the
        project manager himself does not, even holding the sponsor role (M67-6,
        F10). Superuser code is trusted."""
        if self.env.su:
            return
        user = self.env.user
        for rec in self:
            gate = rec.sudo()
            delivering = user in gate.project_id._ppm_delivery_users()
            reviewing = user == gate.reviewer_id.user_id or user.has_group(SPONSOR_GROUP)
            if delivering or not reviewing:
                raise UserError(
                    "The gate decision is recorded by the gate's reviewer or a project "
                    "sponsor, not by the project manager whose work is under review (M67-6)."
                )

    def _gate_reviewer_records(self):
        """The check has passed. A named reviewer holds no write on the register,
        so his verdict is written by the service role (F10)."""
        self.check_access("read")
        self._assert_reviewer()
        return self.sudo()

    @staticmethod
    def _gate_flag(value):
        """The checklist answer, from the form's boolean or a typed yes/no."""
        if isinstance(value, str):
            text = value.strip().lower()
            if not text:
                return None
            return text in ("y", "yes", "true", "1", "pass", "passed")
        return None if value is None else bool(value)

    def action_record_decision(self, decision=None, checklist_passed=None, findings=None):
        decision = (decision or "").strip().lower()
        if decision not in ("pass", "conditional", "fail"):
            raise UserError("Record the gate decision: pass, conditional or fail.")
        checklist = self._gate_flag(checklist_passed)
        findings = (findings or "").strip() or None
        for rec in self._gate_reviewer_records():
            if rec.state != "scheduled":
                raise UserError("The review is held; its decision is already recorded.")
            vals = {"decision": decision}
            if findings is not None:
                vals["findings"] = findings
            if checklist is not None:
                vals["checklist_passed"] = checklist
            if decision == "fail" and not (findings or rec.findings or "").strip():
                raise UserError("A failed gate records what failed: write the findings (M67-6).")
            rec._guarded().write(vals)
            rec.message_post(
                body="Decision recorded by %s: %s."
                % (self.env.user.name, dict(self._fields["decision"].selection)[decision])
            )

    def action_hold(self):
        for rec in self._gate_reviewer_records():
            if rec.state != "scheduled":
                raise UserError("Hold a scheduled review.")
            if not rec.decision:
                raise UserError("Record the gate decision before holding the review")
            if rec.decision in ("pass", "conditional") and not rec.checklist_passed:
                raise UserError(
                    "A passing gate needs its checklist confirmed before the review "
                    "is held (M67-6)."
                )
            rec._guarded().write({"state": "held"})

    def action_close(self):
        for rec in self._gate_reviewer_records():
            if rec.state != "held":
                raise UserError("Close a review that has been held")
            rec._guarded().write({"state": "closed"})


class FixProjectStageGates(models.Model):
    """A12 (M67): the stage-gate reverse relation lives with the gate model,
    because cd_itsm already depends on cd_ppm (the gate's project_id is a
    Many2one to fix.project) — cd_ppm cannot reference fix.project.gate at
    its own load time. Fields resolve by name, so fix.project records expose
    gate_ids everywhere and cd_ppm's code reads it unchanged."""

    _inherit = "fix.project"
    gate_ids = fields.One2many("fix.project.gate", "project_id", string="Stage Gates")
