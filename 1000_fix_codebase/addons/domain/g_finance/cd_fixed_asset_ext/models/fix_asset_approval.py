# fix_asset_approval — the routed, amount-tiered approval of M49 documents
# (A08 workflow audit 2026-11-04, M49-1 / M49-4 / M49-5 / M49-6, P1-4).
#
# A 50,000,000 capex, a 40,000,000 write-off and a 780,000 revaluation surplus
# were each approved by one accounting manager; an accountant wrote
# state='approved'; a manager rewrote the readonly requested_by_id and
# approved his own request; approved figures were raised afterwards. Capex
# requests, disposals and revaluations now inherit fix.dofa.mixin
# (cd_workflow_engine): the tier comes from the amount (fix_asset_common
# ladders), the request is routed to the tier holders through the M63 inbox,
# and the requester, creator and whoever changed a pinned figure never decide
# it. The workflow fields are guarded; the approved terms are pinned.
from odoo import fields, models
from odoo.exceptions import UserError


class FixAssetDofaMixin(models.AbstractModel):
    _name = "fix.asset.dofa.mixin"
    _inherit = ["fix.dofa.mixin"]
    _description = "M49 routed approval (DOFA, M63)"

    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    # ---- per model --------------------------------------------------------
    def _fix_requester(self):
        """The user who raised the document (a guarded field)."""
        self.ensure_one()
        return self.requested_by_id

    def _fix_terms_fields(self) -> set:
        """Fields the approval covers: a change voids it. Override."""
        return set()

    def _fix_before_approve(self):
        """State and content checks that must hold to approve. Override."""
        return None

    def _fix_after_approve(self):
        """What the approval does beyond the DOFA stamp. Override."""
        return None

    # ---- the engine hooks -------------------------------------------------
    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | self._fix_terms_fields()

    def _approval_excluded(self):
        excluded = super()._approval_excluded()
        for rec in self:
            excluded |= rec.sudo()._fix_requester() | rec.sudo().create_uid
        return excluded.sudo()

    def action_dofa_approve(self):
        """The engine's apply method: only from the approver's inbox task, by
        a holder of the tier the amount needs who is neither the requester
        nor the creator. The stamp is written as the system after these
        checks (the approver need not hold the accountant's write rights);
        it still names the approver."""
        self._approval_assert_routed()
        for rec in self:
            if not self.env.su:
                task = rec._approval_task()
                deciders = self.env.user | task.on_behalf_of_id
                clash = deciders & (rec.sudo()._fix_requester() | rec.sudo().create_uid)
                if clash:
                    raise UserError(
                        "Segregation of duties: %s raised %s and cannot approve it."
                        % (", ".join(clash.mapped("name")), rec.display_name)
                    )
            rec._fix_before_approve()
        result = super(FixAssetDofaMixin, self.sudo()).action_dofa_approve()
        for rec in self:
            rec._fix_after_approve()
        return result

    def action_approve(self):
        """Kept for screens and old callers: approval is decided from the M63
        inbox, so a direct call is refused by the routing guard."""
        return self.action_dofa_approve()

    def _fix_stamp_approved(self, vals):
        self.sudo()._guarded().write(
            dict(vals, approved_by_id=self.env.uid) if "approved_by_id" in self._fields else vals
        )

    def _fix_approval_date(self):
        return fields.Date.context_today(self)
