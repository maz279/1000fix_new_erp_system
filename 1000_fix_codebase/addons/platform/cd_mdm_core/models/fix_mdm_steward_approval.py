# fix.mdm.steward — the M63 routing extension (A12 P1-2).
#
# The steward-request MODEL lives in cd_entity_config (M64), which cannot
# depend on the workflow engine (cd_workflow_engine depends on
# cd_entity_config): the routed-approval wiring lives here, where the engine
# is importable. The base action (fix_platform_ops.py) already enforces the
# coded steward group and proposer/approver segregation in CODE; this adds
# the routed-decision requirement: an approval runs from the M63 inbox task
# of a steward, never from a button press on the record.
from odoo import fields, models
from odoo.exceptions import UserError

STEWARD_GROUP = "cd_entity_config.group_mdm_domain_steward"


class FixMdmStewardApproval(models.Model):
    # _name is REQUIRED: without it Odoo derives a phantom
    # 'fix.mdm.steward.approval' model from the class name instead of
    # extending the steward request, and the routing never attaches.
    _name = "fix.mdm.steward"
    _inherit = ["fix.approvable.mixin", "fix.mdm.steward"]
    _description = "Data Steward Request"

    _approval_domain = "other"
    _approval_apply_method = "action_approve"
    _approval_group = STEWARD_GROUP
    _approval_routed = True

    # No _approval_group_for override: the engine default resolves the coded
    # `_approval_group` above (A11 E1: the coded group IS the authority; a
    # matrix row may only NARROW it) and returns the res.groups record.

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
        }

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
