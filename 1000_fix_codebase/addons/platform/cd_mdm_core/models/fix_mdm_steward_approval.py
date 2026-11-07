# fix.mdm.steward — the M63 routing extension (A12 P1-2).
#
# The steward-request MODEL lives in cd_entity_config (M64), which cannot
# depend on the workflow engine (cd_workflow_engine depends on
# cd_entity_config): the routed-approval wiring lives here, where the engine
# is importable. The base action (fix_platform_ops.py) already enforces the
# coded steward group and proposer/approver segregation in CODE; this adds
# the routed-decision requirement: an approval runs from the M63 inbox task
# of a steward, never from a button press on the record.
#
# A12 finish audit (2026-11-07): the request types and the payload checks live
# here too, because the governed-attribute register does (E2, E11, E12):
#   update      writes the payload to the target;
#   deactivate  sets active=False on the target;
#   merge       opens a fix.mdm.duplicate pair and routes its M33 merge;
#   create      refused at entry: no steward path creates a master record.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

STEWARD_GROUP = "cd_entity_config.group_mdm_domain_steward"


class FixMdmStewardApproval(models.Model):
    # _name is REQUIRED: without it Odoo derives a phantom
    # 'fix.mdm.steward.approval' model from the class name instead of
    # extending the steward request, and the routing never attaches.
    _name = "fix.mdm.steward"
    _inherit = ["fix.approvable.mixin", "fix.mdm.payload.mixin", "fix.mdm.steward"]
    _description = "Data Steward Request"

    _approval_domain = "other"
    _approval_apply_method = "action_approve"
    _approval_group = STEWARD_GROUP
    _approval_routed = True

    merge_with_ref = fields.Char(
        string="Merge Into (record id)",
        help="For a merge request: the database id of the record the Record ID duplicates.",
    )
    duplicate_id = fields.Many2one(
        "fix.mdm.duplicate", string="Duplicate Pair", readonly=True, copy=False
    )
    current_values = fields.Text(
        string="Current Values",
        readonly=True,
        copy=False,
        help="Snapshot of the proposed fields, taken when the review starts.",
    )

    # No _approval_group_for override: the engine default resolves the coded
    # `_approval_group` above (A11 E1: the coded group IS the authority; a
    # matrix row may only NARROW it) and returns the res.groups record.

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"duplicate_id", "current_values"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "submitted":
            locked |= {"merge_with_ref"}
        return locked

    def _approval_needed(self) -> bool:
        return self.state == "in_review"

    def _approval_excluded(self):
        # The requester (and whoever raised the record) never decides it.
        return (
            super()._approval_excluded() | self.requested_by_id.user_id | self.create_uid
        ).sudo()

    def _approval_pinned_fields(self) -> set:
        # The approval covered exactly this target and this payload.
        return super()._approval_pinned_fields() | {
            "res_model",
            "record_ref",
            "proposed_changes",
            "request_type",
            "merge_with_ref",
        }

    # ---- what each request type needs --------------------------------------
    def _proposed_values(self) -> dict:
        self.ensure_one()
        return self._mdm_parse_payload(self.proposed_changes, self.res_model, self.name)

    @api.constrains("request_type", "res_model", "record_ref", "proposed_changes", "merge_with_ref")
    def _check_request_shape(self):
        """E11/E12: what can never apply is refused when it is raised. A
        request may be raised before its target and payload are attached;
        action_review requires them (_assert_complete)."""
        for rec in self:
            if rec.request_type == "create":
                raise ValidationError(
                    "A steward request cannot create a master record: raise the new record "
                    "in its own module, then govern it (%s)." % rec.name
                )
            rec._mdm_assert_governed(rec.res_model, (), rec.name)
            for ref in (rec.record_ref, rec.merge_with_ref):
                if (ref or "").strip() and not ref.strip().isdigit():
                    raise ValidationError(
                        "%r is not a record id: steward request %s needs the target's "
                        "database id." % (ref, rec.name)
                    )
            if (rec.record_ref or "").strip():
                rec._target_record()
            if rec.request_type == "deactivate" and "active" not in self.env[rec.res_model]._fields:
                raise ValidationError(
                    "%s has no active flag, so it cannot be deactivated." % rec.res_model
                )
            if rec.request_type == "merge" and rec.res_model != "res.partner":
                raise ValidationError(
                    "Only the party master merges: %s has no supervised merge engine."
                    % rec.res_model
                )
            if rec.request_type == "update" and (rec.proposed_changes or "").strip():
                rec._mdm_assert_governed(rec.res_model, rec._proposed_values(), rec.name)

    def _assert_complete(self):
        """Everything apply will need, at the moment someone reviews it."""
        self.ensure_one()
        target = self._target_record()
        if self.request_type == "update":
            changes = self._proposed_values()
            self._mdm_check_payload(target, changes, self.company_id, self.name)
            self._mdm_dry_run(target, changes, self.name)
            return self._mdm_snapshot(target, changes)
        if self.request_type == "deactivate":
            self._mdm_assert_route(target, self.name)
            return self._mdm_snapshot(target, ["active"])
        if self.request_type == "merge":
            survivor = self._merge_survivor()
            if survivor == target:
                raise ValidationError("A record cannot merge into itself (%s)." % self.name)
            return False
        raise ValidationError(
            "A steward request of type %r cannot be worked: raise it in its own module (%s)."
            % (self.request_type, self.name)
        )

    def _merge_survivor(self):
        self.ensure_one()
        ref = (self.merge_with_ref or "").strip()
        survivor = (
            self.env[self.res_model].sudo().browse(int(ref)).exists() if ref.isdigit() else None
        )
        if not survivor:
            raise ValidationError(
                "Merge request %s must name the record it merges into (a database id)." % self.name
            )
        return survivor

    def _steward_review_stamp(self):
        return {"current_values": self._assert_complete()}

    def action_request_approval(self, justification=None):
        """BRU-MDM-22: the request's reason, if nothing more is typed."""
        for rec in self:
            if not (justification or rec.reason or "").strip():
                raise UserError("State why %s is needed." % rec.name)
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """The M63 apply method: only a routed steward decision approves.

        The base action (cd_entity_config) enforces the from-state, the coded
        group and proposer/approver segregation; this adds the routing
        assertion."""
        if not self._approval_task() and not self.env.su:
            raise UserError(
                "Approving a data steward request is a routed approval: press "
                "Request Approval so a different MDM Domain Steward decides it "
                "from the approver's inbox."
            )
        return super().action_approve()

    def _approval_on_rejected(self, comment):
        """A routed rejection lands here: the same base checks, terminal state."""
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Reject a request in review")
            rec._decision_checks(rec)
            if not (comment or rec.decision_note or "").strip():
                raise UserError("Give a decision note when rejecting a steward request.")
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decision_note": (comment or rec.decision_note or "")[:250],
                    "decided_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Rejected by %s: %s" % (self.env.user.name, comment or ""))

    # ---- apply, one branch per request type --------------------------------
    def _apply_to_target(self):
        """Called by action_apply after the state and group checks."""
        self.ensure_one()
        target = self._target_record()
        if self.request_type == "update":
            changes = self._proposed_values()
            self._mdm_check_payload(target, changes, self.company_id, self.name)
            self._mdm_assert_fresh(target, changes, self.current_values, self.name)
            self._mdm_write(target, changes, self.name)
            return "%s written to %s/%s" % (", ".join(sorted(changes)), self.res_model, target.id)
        if self.request_type == "deactivate":
            self._mdm_assert_route(target, self.name)
            self._mdm_write(target, {"active": False}, self.name)
            return "%s/%s deactivated" % (self.res_model, target.id)
        if self.request_type == "merge":
            survivor = self._merge_survivor()
            duplicate = self.env["fix.mdm.duplicate"].create(
                {
                    "res_model": self.res_model,
                    "record_a_ref": str(survivor.id),
                    "record_b_ref": str(target.id),
                    "match_factors": "steward request %s" % self.name,
                    "decision_note": (self.reason or "")[:250],
                }
            )
            duplicate.action_merge(justification=self.reason)
            self._guarded().write({"duplicate_id": duplicate.id})
            return (
                "pair %s opened and its M33 merge routed; the pair merges when a party data "
                "steward executes it" % duplicate.name
            )
        raise ValidationError(
            "A steward request of type %r cannot be applied (%s)." % (self.request_type, self.name)
        )
