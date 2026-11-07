# fix.payment.gateway — the M63 routing extension (A12 P1-4).
#
# The gateway MODEL lives in cd_entity_config (M65), which cannot depend on
# the workflow engine (cd_workflow_engine depends on cd_entity_config): the
# routed-approval wiring therefore lives here, in cd_multi_entity, which owns
# the localisation estate and MAY depend on the engine.
#
# Putting a gateway live (first activation, reactivation after suspension,
# sandbox->live) is a routed decision of the coded approver group
# (cd_entity_config.group_gateway_activation_approver - treasury + IT
# security). The approver is never the person who configured the gateway.
from odoo import models
from odoo.exceptions import UserError

GATEWAY_APPROVER_GROUP = "cd_entity_config.group_gateway_activation_approver"


class FixPaymentGatewayApproval(models.Model):
    # _name is REQUIRED: without it Odoo derives a phantom
    # 'fix.payment.gateway.approval' model from the class name instead of
    # extending the gateway, and the routed activation never attaches.
    _name = "fix.payment.gateway"
    _inherit = ["fix.approvable.mixin", "fix.payment.gateway"]
    _description = "Payment Gateway Configuration"

    _approval_domain = "other"
    _approval_apply_method = "action_activate"
    _approval_group = GATEWAY_APPROVER_GROUP
    _approval_routed = True

    # No _approval_group_for override: the engine default resolves the coded
    # `_approval_group` above (A11 E1: the coded group IS the authority; a
    # matrix row may only NARROW it) and returns the res.groups record.

    def _approval_needed(self) -> bool:
        # draft->active (first activation), suspended->active (reactivation)
        # or active/sandbox->live: each is a go-live decision.
        # A12 finish E8: and a requested rotation of a live credential.
        return (
            self.state in ("draft", "suspended")
            or (self.state == "active" and self.mode == "sandbox")
            or bool(self.sudo().pending_credential_ref)
        )

    def _approval_excluded(self):
        # The person who configured the gateway never signs off its go-live.
        return super()._approval_excluded() | self.create_uid

    def _approval_pinned_fields(self) -> set:
        # P1-4 pinning: the approval covered exactly this provider, country,
        # currency set and credential reference.
        pinned = super()._approval_pinned_fields() | {
            "provider",
            "country_code",
            "currencies",
            "credential_ref",
        }
        # The deciding task is applying a rotation it was asked to approve: that
        # write is the decision itself, not a change the approval did not cover.
        return pinned - {"credential_ref"} if self._approval_task() else pinned

    def _route_live_rotation(self):
        for rec in self:
            if rec.approval_state == "pending":
                raise UserError(
                    "%s already has an approval pending. Recall it before "
                    "requesting a rotation." % rec.display_name
                )
            rec.action_request_approval(
                justification="Credential rotation: %s" % rec.pending_credential_reason
            )

    def _approval_clear_stamp(self, reason):
        # A recalled or voided rotation request leaves nothing waiting.
        result = super()._approval_clear_stamp(reason)
        self._drop_pending_rotation()
        return result

    def _approval_on_rejected(self, comment):
        result = super()._approval_on_rejected(comment)
        self._drop_pending_rotation()
        return result

    def _drop_pending_rotation(self):
        waiting = self.sudo().filtered("pending_credential_ref")
        if waiting:
            waiting._guarded().write(
                {"pending_credential_ref": False, "pending_credential_reason": False}
            )

    def action_activate(self):
        """The M63 apply method: only a routed approver decision activates.

        The base state machine (cd_entity_config/models/fix_platform_ops2.py)
        runs the guarded transitions and writes the audit rows; this override
        adds the routing assertion and the coded-group authority check."""
        if not self._approval_task():
            # Superuser system code (data migrations, deploys) may activate a
            # gateway without a task; an interactive caller may not.
            if not self.env.su:
                raise UserError(
                    "Activating a payment gateway is a routed approval: press "
                    "Request Approval so a Payment Gateway Activation Approver "
                    "can decide it from the approver's inbox."
                )
        else:
            authority = self._approval_authority_user()
            if not authority.has_group(GATEWAY_APPROVER_GROUP):
                raise UserError(
                    "Activating a payment gateway requires the 'Payment Gateway "
                    "Activation Approver' role, which %s does not hold." % authority.name
                )
        return super().action_activate()
