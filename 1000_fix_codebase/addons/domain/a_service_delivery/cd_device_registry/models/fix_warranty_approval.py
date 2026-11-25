# fix.warranty verification as a routed M63 approval (A02 audit B1).
#
# Verify Proof turned pending cover into a free warranty job on one press by
# any Warranty Officer, with no request, deadline, delegate or history. The
# registrar now asks (Request Approval, the engine routes the request to the
# Warranty Officers, minus the registrar and the requester) and an officer
# verifies from the M63 inbox. action_verify still applies its own checks
# (officer role, not the registrar, proof on file) in the approver's env.
from odoo import fields, models
from odoo.exceptions import UserError

from .fix_warranty import WARRANTY_OFFICER_GROUP


class FixWarrantyRoutedVerification(models.Model):
    _inherit = "fix.warranty"

    _approval_domain = "warranty_verification"
    _approval_apply_method = "action_verify"
    _approval_group = WARRANTY_OFFICER_GROUP
    _approval_routed = True

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return self.status == "pending" and self.warranty_type != "none"

    def _fix_assert_officer(self, verb: str) -> None:
        """A delegate verifies on the absent officer's authority (M63
        substitution); otherwise the officer checks of fix_warranty apply."""
        self.ensure_one()
        task = self._approval_task()
        if self.env.su or not task.on_behalf_of_id:
            return super()._fix_assert_officer(verb)
        if not task.on_behalf_of_id.has_group(WARRANTY_OFFICER_GROUP):
            raise UserError("Only a Warranty Officer can %s a warranty." % verb)
        if self.create_uid in self._approval_acting_users():
            raise UserError(
                "Segregation of duties: the person who registered the warranty on %s "
                "cannot %s it." % (self.device_id.display_name, verb)
            )

    def action_request_approval(self, justification=None):
        # A07 P2 (2026-11-04): a request the officer could never apply is refused
        # when it is made: cover on a provisional identity (BRU-AST-03), or proof
        # filed against another record (M17-13). action_verify checks again.
        # A07 operability (2026-11-07): nor is the officer handed a vote that must
        # fail for want of proof.
        for rec in self:
            if rec.warranty_type != "none" and not rec.proof_document_id:
                raise UserError(
                    "Attach the purchase receipt or warranty card on the warranty form before "
                    "requesting verification of the warranty on %s." % rec.device_id.display_name
                )
            rec._a07_verify_checks()
        return super().action_request_approval(justification=justification)

    def action_verify(self):
        self._approval_assert_routed()
        return super().action_verify()


class FixApprovalMatrixWarrantyVerification(models.Model):
    _inherit = "fix.approval.matrix"

    # A02 audit B1: lets a DoA matrix row target this routed approval.
    decision_domain = fields.Selection(
        selection_add=[("warranty_verification", "Warranty Verification")],
        ondelete={"warranty_verification": "cascade"},
    )
