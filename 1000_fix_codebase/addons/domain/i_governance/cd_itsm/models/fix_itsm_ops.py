# fix_itsm_ops — M66 (IT change management + IT asset register) and M67
# (project stage-gate reviews). ITSM tickets live in fix_itsm.py; projects,
# milestones and tasks live in cd_ppm.
#
# A12 workflow audit (2026-11-04) P1-1: fix.itsm.change had a self-service
# `action_approve` — anyone approved his own change, and "implement" was a
# plain state flip. The change now rides the M63 routed approval engine:
#   - standard (and not high-risk) changes are PRE-APPROVED by policy on
#     submit — that is what "standard" means in ITIL;
#   - normal changes route to the coded Change Manager group,
#     emergency and high-risk changes to the CAB group (empty at install:
#     appoint members, or nobody can approve — by design);
#   - the risk score (probability x impact) above cd_itsm.change_cab_risk_score
#     (default 6) makes a change high-risk whatever its type;
#   - requester and implementer never decide their own change (the engine
#     already excludes creator and amount-changer);
#   - editing the approved snapshot (title, planned_on, rollback_plan,
#     change_window_hours) voids the approval and returns it to draft;
#   - an emergency change needs its post-implementation review (PIR) before
#     it leaves the "implemented" state;
#   - implementing publishes itsm.change_implemented for the M30 platform
#     release register (consumer ships there).
#
# M66-9: the IT asset register let any write move an asset to "retired" with
# the data still on it. Retiring now needs the wipe certificate and an
# unassigned asset, and publishes itsm.asset_retired for the M06 asset
# module. M67-6: a stage-gate review's decision is recorded by its reviewer
# (never the project's own manager) through an action, not a write.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

CHANGE_MANAGER_GROUP = "cd_itsm.group_itsm_change_manager"
CAB_GROUP = "cd_itsm.group_itsm_cab_member"
SPONSOR_GROUP = "cd_ppm.group_ppm_sponsor"
CAB_RISK_SCORE_PARAM = "cd_itsm.change_cab_risk_score"
CAB_RISK_SCORE_DEFAULT = 6

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
    risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    risk_probability = fields.Selection(
        _RISK_SCALE, string="Risk Probability", default="3", required=True
    )
    risk_impact = fields.Selection(_IMPACT_SCALE, string="Risk Impact", default="3", required=True)
    risk_score = fields.Integer(
        compute="_compute_risk_score",
        store=True,
        help="Probability x impact (1-25). At or above the CAB threshold "
        "(cd_itsm.change_cab_risk_score, default 6) the change is high-risk "
        "and goes to the CAB whatever its type.",
    )
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
    release_note = fields.Char(
        help="The platform release this change ships under (M30); recorded when "
        "the release register picks the change up."
    )
    implemented_on = fields.Datetime(readonly=True, copy=False)
    pir_notes = fields.Text(string="Post-Implementation Review", copy=False)
    pir_by_id = fields.Many2one("res.users", string="PIR By", readonly=True, copy=False)
    pir_on = fields.Datetime(string="PIR On", readonly=True, copy=False)
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
            "pir_notes",
            "pir_by_id",
            "pir_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state in ("implemented", "reviewed", "rolled_back") for rec in self):
            locked |= {
                "title",
                "change_type",
                "planned_on",
                "implementation_plan",
                "test_plan",
                "rollback_plan",
                "change_window_hours",
                "asset_ids",
                "risk",
                "risk_probability",
                "risk_impact",
            }
        return locked

    # ---- M63 hooks ---------------------------------------------------------
    def _cab_risk_threshold(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(CAB_RISK_SCORE_PARAM)
        try:
            return int(float(raw)) if raw else CAB_RISK_SCORE_DEFAULT
        except (TypeError, ValueError):
            return CAB_RISK_SCORE_DEFAULT

    @api.depends("risk_probability", "risk_impact", "risk")
    def _compute_risk_score(self):
        for rec in self:
            score = int(rec.risk_probability or "3") * int(rec.risk_impact or "3")
            rec.risk_score = score
            rec.high_risk = rec.risk == "high" or score >= rec._cab_risk_threshold()

    def _approval_needed(self) -> bool:
        # A standard change that is not high-risk is pre-approved by policy;
        # there is nothing to route.
        self.ensure_one()
        return not (self.change_type == "standard" and not self.high_risk)

    def _approval_group_xmlid(self):
        self.ensure_one()
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
        # The approval covers this snapshot; editing it voids the approval.
        return super()._approval_pinned_fields() | {
            "title",
            "planned_on",
            "rollback_plan",
            "change_window_hours",
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
        self.sudo()._guarded().write({"state": "rejected"})

    # ---- lifecycle ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.itsm.change") or "CHG/New"
        return super().create(vals_list)

    def action_submit(self):
        """Draft -> routed approval (normal / emergency / high-risk) or a
        policy pre-approval (standard, not high-risk)."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft change can be submitted.")
            if not rec.requested_by_id:
                raise UserError("Name the requester before submitting the change.")
            if not (rec.implementation_plan or "").strip() or not (rec.test_plan or "").strip():
                raise UserError(
                    "A submitted change carries its implementation and test plan (P1-1): "
                    "the approver signs off the plan, not a title."
                )
            if rec.change_type != "standard" and not (rec.rollback_plan or "").strip():
                raise UserError("A non-standard change needs a rollback plan before submission.")
            if (rec.change_type == "emergency" or rec.high_risk) and not (
                rec.rollback_plan or ""
            ).strip():
                raise UserError("An emergency or high-risk change needs a rollback plan.")
            if rec.change_window_hours < 1:
                raise UserError("The change window is at least one hour.")
            if rec.change_type == "standard" and not rec.high_risk:
                # Pre-approved by policy: that is what "standard" means. The
                # CAB never sees routine, low-risk, repeatable changes.
                rec._guarded().write({"state": "approved", "approval_state": "approved"})
                rec.message_post(
                    body="Standard change: pre-approved by catalogue policy; no CAB "
                    "review required."
                )
            else:
                rec.action_request_approval()

    def action_approve(self):
        """The engine's apply method: runs in the approver's env, from the
        inbox task only (P1-1)."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft change can be approved.")
            rec._guarded().write(
                {"state": "approved", "approved_by_id": rec._approval_authority_user().id}
            )

    def action_implement(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Implement an approved change (P1-1).")
            if not rec.implementer_id:
                raise UserError("Name the implementer before implementing the change.")
            if not (rec.rollback_plan or "").strip():
                raise UserError(
                    "No rollback plan on record: an implemented change must be reversible."
                )
            requester_user = rec.requested_by_id.sudo().user_id
            implementer_user = rec.implementer_id.sudo().user_id
            if requester_user and implementer_user and requester_user == implementer_user:
                raise UserError(
                    "The implementer is not the requester (P1-1 segregation of duties)."
                )
            if rec.approved_by_id and implementer_user and rec.approved_by_id == implementer_user:
                raise UserError("The implementer is not the approver (P1-1 segregation of duties).")
            rec._guarded().write({"state": "implemented", "implemented_on": fields.Datetime.now()})
            rec.message_post(body="Implemented by %s." % rec.implementer_id.sudo().display_name)
            publish(
                rec.env,
                "itsm.change_implemented",
                "fix.itsm.change",
                rec.id,
                {
                    "change": rec.name,
                    "title": rec.title,
                    "change_type": rec.change_type,
                    "risk": rec.risk,
                    "risk_score": rec.risk_score,
                    "high_risk": rec.high_risk,
                    "assets": list(rec.asset_ids.mapped("asset_tag")),
                    "implemented_on": rec.implemented_on.isoformat()
                    if rec.implemented_on
                    else None,
                },
            )

    def action_record_pir(self, pir_notes=None):
        """Post-implementation review: an emergency change may not leave the
        implemented state without one (P1-1)."""
        for rec in self:
            if rec.state != "implemented":
                raise UserError("Record the post-implementation review on an implemented change.")
            if not (pir_notes or "").strip():
                raise UserError("Write what the review found: the PIR notes are required.")
            rec._guarded().write(
                {
                    "state": "reviewed",
                    "pir_notes": pir_notes,
                    "pir_by_id": rec.env.uid,
                    "pir_on": fields.Datetime.now(),
                }
            )

    def action_rollback(self):
        for rec in self:
            if rec.state != "implemented":
                raise UserError("Roll back an implemented change.")
            if rec.change_type == "emergency" and not (rec.pir_notes or "").strip():
                raise UserError(
                    "An emergency change records its post-implementation review "
                    "before it leaves the implemented state (P1-1): roll back only "
                    "after the PIR."
                )
            rec._guarded().write({"state": "rolled_back"})
            rec.message_post(body="Rolled back per the rollback plan.")

    # ---- event consumer (FF-48; data record ships in cd_itsm/data, lead) ---
    @api.model
    def consume_change_implemented(self, event):
        """itsm.change_implemented: the M30 platform release register's pick-up
        trail on the change itself."""
        change = self.browse(event.get("aggregate_id") or 0).exists()
        if change:
            change.message_post(
                body="Implementation handed to the platform release register (M30); "
                "event %s." % event.get("event_id")
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
    assigned_to_id = fields.Many2one("hr.employee", string="Assigned To")
    serial_no = fields.Char()
    warranty_end = fields.Date()
    os_version = fields.Char(string="OS / Firmware")
    wipe_certificate = fields.Char(
        help="The data-wipe certificate reference (M66-9): an asset leaves the "
        "register as retired only after its data is provably destroyed."
    )
    state = fields.Selection(
        [
            ("in_service", "In Service"),
            ("in_stock", "In Stock"),
            ("repair", "Under Repair"),
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
        return super()._fix_guarded_fields() | {"state"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state == "retired" for rec in self):
            locked |= {
                "name",
                "asset_tag",
                "asset_kind",
                "assigned_to_id",
                "serial_no",
                "os_version",
                "wipe_certificate",
            }
        return locked

    @api.constrains("assigned_to_id")
    def _check_assignee_active(self):
        for rec in self:
            if rec.assigned_to_id and not rec.assigned_to_id.active:
                raise ValidationError(
                    "Asset %s is assigned to %s, who has left the company. Reassign "
                    "or retire the asset." % (rec.asset_tag, rec.assigned_to_id.display_name)
                )

    def action_allocate(self, assigned_to=None):
        for rec in self:
            if rec.state != "in_stock":
                raise UserError("Allocate an asset from stock.")
            employee = assigned_to or rec.assigned_to_id
            if not employee:
                raise UserError("Name the employee the asset is allocated to.")
            if not employee.active:
                raise UserError("Allocate the asset to an active employee.")
            rec._guarded().write({"state": "in_service", "assigned_to_id": employee.id})

    def action_send_repair(self):
        for rec in self:
            if rec.state not in ("in_service", "in_stock"):
                raise UserError("Only an in-service or in-stock asset goes to repair.")
            rec._guarded().write({"state": "repair"})

    def action_recover(self):
        """Back to stock from repair, unassigned (M66-9)."""
        for rec in self:
            if rec.state != "repair":
                raise UserError("Recover an asset that is under repair.")
            rec._guarded().write({"state": "in_stock", "assigned_to_id": False})

    def action_retire(self, wipe_certificate=None):
        """M66-9: retirement needs the data-wipe certificate and an unassigned
        asset; the retirement is published for the M06 asset module."""
        for rec in self:
            if rec.state == "retired":
                raise UserError("Asset is already retired.")
            certificate = (wipe_certificate or rec.wipe_certificate or "").strip()
            if not certificate:
                raise UserError(
                    "Record the data-wipe certificate before retiring %s: retired "
                    "hardware must provably carry no company data (M66-9)." % rec.asset_tag
                )
            if rec.assigned_to_id:
                raise UserError(
                    "%s is still assigned to %s; recover the asset before retiring it."
                    % (rec.asset_tag, rec.assigned_to_id.display_name)
                )
            rec._guarded().write(
                {"state": "retired", "wipe_certificate": certificate, "assigned_to_id": False}
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

    # ---- event consumer (FF-48; data record ships in cd_itsm/data, lead) ---
    @api.model
    def consume_asset_retired(self, event):
        """itsm.asset_retired: the M06 asset module's pick-up trail."""
        asset = self.browse(event.get("aggregate_id") or 0).exists()
        if asset:
            asset.message_post(
                body="Retirement handed to the fixed-asset register (M06); event %s."
                % event.get("event_id")
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

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state == "closed" for rec in self):
            locked |= {
                "gate",
                "review_on",
                "reviewer_id",
                "findings",
                "project_id",
            }
        return locked

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
        project manager himself does not (M67-6). Superuser code is trusted."""
        if self.env.su:
            return
        reviewers = self.mapped("reviewer_id").sudo().mapped("user_id")
        if self.env.user in reviewers or self.env.user.has_group(SPONSOR_GROUP):
            return
        raise UserError(
            "The gate decision is recorded by the gate's reviewer or a project "
            "sponsor, not by the project manager whose work is under review (M67-6)."
        )

    def action_record_decision(self, decision=None, checklist_passed=None, findings=None):
        if decision not in ("pass", "conditional", "fail"):
            raise UserError("Record the gate decision: pass, conditional or fail.")
        self._assert_reviewer()
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("The review is held; its decision is already recorded.")
            vals = {"decision": decision}
            if findings is not None:
                vals["findings"] = findings
            if checklist_passed is not None:
                vals["checklist_passed"] = bool(checklist_passed)
            if decision == "fail" and not (findings or rec.findings or "").strip():
                raise UserError("A failed gate records what failed: write the findings (M67-6).")
            rec._guarded().write(vals)
            rec.message_post(
                body="Decision recorded: %s." % dict(self._fields["decision"].selection)[decision]
            )

    def action_hold(self):
        self._assert_reviewer()
        for rec in self:
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
        self._assert_reviewer()
        for rec in self:
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
